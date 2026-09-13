
import os
import requests
import pandas as pd
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:7860").rstrip("/")

st.set_page_config(
    page_title="SuperKart Sales Forecast",
    page_icon="🛒",
    layout="centered"
)

st.title("🛒 Welcome to the SuperKart App Project")
st.success("Frontend is running: Streamlit → Flask Backend → Serialized ML Pipeline")
st.caption("SuperKart sales forecasting application")

st.subheader("Online prediction")

with st.form("prediction_form"):
    Product_Weight = st.number_input(
        "Product Weight", min_value=0.0, value=12.66
    )
    Product_Sugar_Content = st.selectbox(
        "Product Sugar Content",
        ["Low Sugar", "Regular", "No Sugar"]
    )
    Product_Allocated_Area = st.number_input(
        "Product Allocated Area", min_value=0.0, value=0.027
    )
    Product_MRP = st.number_input(
        "Product MRP", min_value=0.0, value=117.08
    )
    Store_Size = st.selectbox(
        "Store Size", ["Small", "Medium", "High"]
    )
    Store_Location_City_Type = st.selectbox(
        "City Tier", ["Tier 1", "Tier 2", "Tier 3"]
    )
    Store_Type = st.selectbox(
        "Store Type",
        [
            "Departmental Store",
            "Supermarket Type1",
            "Supermarket Type2",
            "Food Mart"
        ]
    )
    Product_Id_char = st.text_input(
        "Product ID prefix", value="FD", max_chars=2
    )
    Store_Age_Years = st.number_input(
        "Store Age (years)", min_value=0, value=16
    )
    Product_Type_Category = st.selectbox(
        "Product Type Category",
        ["Perishables", "Non Perishables"]
    )

    submitted = st.form_submit_button("Predict Sales")

if submitted:
    payload = {
        "Product_Weight": Product_Weight,
        "Product_Sugar_Content": Product_Sugar_Content,
        "Product_Allocated_Area": Product_Allocated_Area,
        "Product_MRP": Product_MRP,
        "Store_Size": Store_Size,
        "Store_Location_City_Type": Store_Location_City_Type,
        "Store_Type": Store_Type,
        "Product_Id_char": Product_Id_char.upper(),
        "Store_Age_Years": Store_Age_Years,
        "Product_Type_Category": Product_Type_Category
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/v1/predict",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        prediction = response.json()["prediction"]
        st.success(f"Predicted sales: {prediction:,.2f}")
    except Exception as exc:
        st.error(f"Backend request failed: {exc}")

st.divider()
st.subheader("Batch Prediction")
st.write("Drag and drop a CSV file below, or click Browse files. The uploaded file is sent to the Flask backend for batch inference.")

uploaded = st.file_uploader(
    "Drag and drop Batch_Data_SuperKart.csv here",
    type=["csv"],
    accept_multiple_files=False
)

if uploaded is not None:
    batch_df = pd.read_csv(uploaded)
    st.dataframe(batch_df.head(20), use_container_width=True)

    if st.button("Run Batch Prediction"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/v1/predictbatch",
                files={
                    "file": (
                        uploaded.name,
                        uploaded.getvalue(),
                        "text/csv"
                    )
                },
                timeout=120
            )
            response.raise_for_status()

            result_df = pd.DataFrame(
                response.json()["predictions"]
            )

            st.dataframe(result_df, use_container_width=True)

            st.download_button(
                "Download predictions CSV",
                data=result_df.to_csv(index=False).encode("utf-8"),
                file_name="superkart_predictions.csv",
                mime="text/csv"
            )
        except Exception as exc:
            st.error(f"Batch request failed: {exc}")
