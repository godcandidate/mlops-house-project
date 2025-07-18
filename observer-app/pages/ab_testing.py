import streamlit as st
import pandas as pd

def app():
    st.title("🧪 A/B Testing Results")

    try:
        import json
        
        # Read inference logs
        with open("logs/inference.json", 'r') as f:
            inf_data = json.load(f)
            inf_df = pd.json_normalize(inf_data)
            
        # Read feedback logs
        with open("logs/feedback.json", 'r') as f:
            fed_data = json.load(f)
            fed_df = pd.json_normalize(fed_data)
            
        merged = pd.merge(inf_df, fed_df, on="prediction_id", how="inner")

        grouped = merged.groupby("model_version").agg(
            count=("prediction_id", "count"),
            pos_count=("user_feedback", lambda x: (x == "positive").sum()),
            avg_error=("error", "mean")
        ).reset_index()

        grouped["acceptance_rate"] = grouped["pos_count"] / grouped["count"]

        st.dataframe(grouped)

    except Exception as e:
        st.warning(f"Error generating A/B test results: {str(e)}")