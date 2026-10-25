import os
import requests
import pandas as pd
import streamlit as st

# Backend address inside the Docker network (the backend container is named "superkart-backend")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://superkart-backend:7860")

st.title("SuperKart Sales Forecast")
st.write("Predict the quarterly sales revenue of a product in a store.")

# ---------------- Online prediction ----------------
st.subheader("Online prediction")
product_id_char = st.selectbox("Product Category Code (Product_Id_char)", ["FD", "DR", "NC"])
product_type_category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])
product_weight = st.number_input("Product Weight", min_value=0.0, value=12.66)
product_sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
product_allocated_area = st.number_input("Product Allocated Area (ratio)", min_value=0.0, max_value=1.0,
                                         value=0.027, format="%.3f")
product_mrp = st.number_input("Product MRP", min_value=0.0, value=117.08)
store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
store_location_city_type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
store_type = st.selectbox("Store Type", ["Departmental Store", "Supermarket Type1",
                                         "Supermarket Type2", "Food Mart"])
store_age_years = st.number_input("Store Age (years)", min_value=0, max_value=100, value=16, step=1)

if st.button("Predict"):
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
    response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
    if response.status_code == 200:
        st.success(f"Predicted sales: {response.json()['Predicted_Product_Store_Sales_Total']:,.2f}")
    else:
        st.error(f"Error {response.status_code}: {response.text}")

# ---------------- Batch prediction ----------------
st.subheader("Batch prediction")
uploaded_file = st.file_uploader("Upload a CSV in the Batch_Data_SuperKart.csv format", type=["csv"])
if uploaded_file is not None and st.button("Predict batch"):
    response = requests.post(f"{BACKEND_URL}/v1/predictbatch",
                             files={"file": uploaded_file.getvalue()}, timeout=120)
    if response.status_code == 200:
        batch = pd.read_csv(uploaded_file)
        batch["Predicted_Sales"] = [response.json()[str(i)] for i in batch.index]
        st.dataframe(batch)
    else:
        st.error(f"Error {response.status_code}: {response.text}")
