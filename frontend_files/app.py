import os

import pandas as pd
import requests
import streamlit as st

# Backend API: the Hugging Face Space by default. Override with BACKEND_URL, e.g.
# http://superkart-backend:7860 when both containers run on a Docker network.
BACKEND_URL = os.environ.get("BACKEND_URL", "https://sutaneja-superkart-backend.hf.space").rstrip("/")

# Optional Hugging Face token - only needed while the backend Space is private
HF_TOKEN = os.environ.get("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

# Columns expected by the model (same schema as Batch_Data_SuperKart.csv)
FEATURES = ["Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area", "Product_MRP",
            "Store_Size", "Store_Location_City_Type", "Store_Type", "Product_Id_char",
            "Store_Age_Years", "Product_Type_Category"]


@st.cache_data(ttl=60)
def backend_status():
    """Call the API health check; cached for a minute so the page stays fast."""
    try:
        response = requests.get(f"{BACKEND_URL}/", headers=HEADERS, timeout=30)
        return response.status_code == 200, f"HTTP {response.status_code}"
    except requests.RequestException as e:
        return False, type(e).__name__


def show_api_error(response):
    """Display the error returned by the backend in a readable form."""
    try:
        detail = response.json().get("error", response.text)
    except ValueError:
        detail = response.text
    st.error(f"API error {response.status_code}: {str(detail)[:300]}")


st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒")
st.title("🛒 SuperKart Sales Forecast")
st.write("Forecast the quarterly sales revenue of a product in a SuperKart store.")

online, detail = backend_status()
if online:
    st.success(f"Backend API online: {BACKEND_URL}")
else:
    st.warning(f"Backend API not reachable ({detail}): {BACKEND_URL}. "
               "If the Space is private, make it public or set HF_TOKEN.")

tab_online, tab_batch = st.tabs(["Online prediction", "Batch prediction"])

# ---------------- Online prediction: one product-store record ----------------
with tab_online:
    with st.form("online_prediction"):
        col_product, col_store = st.columns(2)
        with col_product:
            st.subheader("Product")
            product_id_char = st.selectbox("Product category code", ["FD", "DR", "NC"],
                                           help="FD = food, DR = drinks, NC = non-consumable")
            product_type_category = st.selectbox("Product type category", ["Perishables", "Non Perishables"])
            product_sugar_content = st.selectbox("Sugar content", ["Low Sugar", "Regular", "No Sugar"])
            product_weight = st.number_input("Weight", min_value=0.0, max_value=50.0, value=12.66, step=0.1)
            product_mrp = st.number_input("MRP", min_value=0.0, max_value=1000.0, value=117.08, step=1.0)
            product_allocated_area = st.number_input("Allocated display area (ratio)", min_value=0.0,
                                                     max_value=1.0, value=0.027, step=0.001, format="%.3f")
        with col_store:
            st.subheader("Store")
            store_type = st.selectbox("Store type", ["Supermarket Type2", "Supermarket Type1",
                                                     "Departmental Store", "Food Mart"])
            store_size = st.selectbox("Store size", ["Medium", "High", "Small"])
            store_location_city_type = st.selectbox("City tier", ["Tier 2", "Tier 1", "Tier 3"])
            store_age_years = st.number_input("Store age (years)", min_value=0, max_value=100, value=16, step=1)
        submitted = st.form_submit_button("Predict sales", type="primary")

    if submitted:
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": int(store_age_years),
            "Product_Type_Category": product_type_category,
        }
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, headers=HEADERS, timeout=60)
        except requests.RequestException as e:
            st.error(f"Could not reach the backend API: {e}")
        else:
            if response.status_code == 200:
                prediction = response.json()["Predicted_Product_Store_Sales_Total"]
                st.metric("Predicted product-store sales", f"{prediction:,.2f}")
            else:
                show_api_error(response)

# ---------------- Batch prediction: CSV file of many records ----------------
with tab_batch:
    st.write("Upload a CSV in the `Batch_Data_SuperKart.csv` format with these columns:")
    st.code(", ".join(FEATURES), language=None)
    uploaded_file = st.file_uploader("Batch CSV file", type=["csv"])

    if uploaded_file is not None:
        batch = pd.read_csv(uploaded_file)
        missing = [c for c in FEATURES if c not in batch.columns]
        if missing:
            st.error(f"The file is missing these columns: {', '.join(missing)}")
        else:
            st.write(f"{len(batch)} rows loaded.")
            st.dataframe(batch.head(), use_container_width=True)

            if st.button("Predict batch", type="primary"):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/v1/predictbatch",
                        files={"file": ("batch.csv", uploaded_file.getvalue(), "text/csv")},
                        headers=HEADERS, timeout=120)
                except requests.RequestException as e:
                    st.error(f"Could not reach the backend API: {e}")
                else:
                    if response.status_code == 200:
                        predictions = response.json()  # {row index: predicted sales}
                        batch["Predicted_Sales"] = [predictions[str(i)] for i in range(len(batch))]
                        st.metric("Total predicted sales", f"{batch['Predicted_Sales'].sum():,.2f}")
                        st.dataframe(batch, use_container_width=True)
                        st.download_button("Download predictions as CSV",
                                           batch.to_csv(index=False).encode("utf-8"),
                                           file_name="superkart_predictions.csv", mime="text/csv")
                    else:
                        show_api_error(response)
