import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Columns expected by the model (same schema as Batch_Data_SuperKart.csv)
FEATURES = ["Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area", "Product_MRP",
            "Store_Size", "Store_Location_City_Type", "Store_Type", "Product_Id_char",
            "Store_Age_Years", "Product_Type_Category"]

# Initialise the Flask app and load the serialized pipeline once at start-up
superkart_api = Flask("SuperKart Sales Predictor")
model = joblib.load("superkart_model.joblib")


def prepare(df):
    """Check that all features are present and normalise the sugar-content labels."""
    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    df = df[FEATURES].copy()
    df["Product_Sugar_Content"] = df["Product_Sugar_Content"].replace({"reg": "Regular"})
    return df


@superkart_api.get("/")
def home():
    """Health check."""
    return "Welcome to the SuperKart Sales Forecasting API!"


@superkart_api.post("/v1/predict")
def predict_sales():
    """Online inference: one JSON record in, one predicted sales value out."""
    try:
        features = prepare(pd.DataFrame([request.get_json()]))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    prediction = float(model.predict(features)[0])
    return jsonify({"Predicted_Product_Store_Sales_Total": round(prediction, 2)})


@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """Batch inference: CSV file in, {row index: predicted sales} out."""
    batch = pd.read_csv(request.files["file"])
    try:
        features = prepare(batch)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    predictions = model.predict(features)
    return jsonify({int(i): round(float(p), 2) for i, p in zip(batch.index, predictions)})


if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
