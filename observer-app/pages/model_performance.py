import streamlit as st
import pandas as pd
import plotly.express as px
import os

def app():
    st.title("📊 Model Performance")

    try:
        import json
        
        # Read inference logs
        with open("logs/inference.json", 'r') as f:
            inf_data = json.load(f)
            inf_df = pd.json_normalize(inf_data)
            
        # Read feedback logs if they exist
        fed_df = pd.DataFrame()
        if os.path.exists("logs/feedback.json"):
            with open("logs/feedback.json", 'r') as f:
                fed_data = json.load(f)
                fed_df = pd.json_normalize(fed_data)
        merged = pd.merge(inf_df, fed_df, on="prediction_id", how="inner")
        merged["error"] = abs(merged["predicted_price"] - merged["expected_price"])

        st.subheader("📈 Acceptance Rate")
        st.bar_chart(fed_df["user_feedback"].value_counts())

        st.subheader("📉 Prediction Errors")
        fig = px.histogram(merged, x="error", nbins=20, title="Prediction Error Distribution")
        st.plotly_chart(fig)

        st.subheader("🔢 Avg Error")
        st.metric("Average Error", f"${merged['error'].mean():,.2f}")

    except Exception as e:
        st.warning(f"Error loading performance data: {str(e)}")