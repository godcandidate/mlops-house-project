import streamlit as st
import pandas as pd

def app():
    st.title("💬 User Feedback")

    try:
        import json
        
        with open("logs/feedback.json", 'r') as f:
            feedback_data = json.load(f)
            df = pd.json_normalize(feedback_data)
            
        st.dataframe(df)
    except Exception as e:
        st.warning(f"Error loading feedback logs: {str(e)}")