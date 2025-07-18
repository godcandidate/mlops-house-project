import streamlit as st
from pages import overview, data_drift, prediction_drift, model_performance, user_feedback, ab_testing

# Page configuration
st.set_page_config(
    page_title="🏠 House Price Monitor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        max-width: 1800px;
        margin: 0 auto;
    }
    .sidebar .sidebar-content {
        background-color: #2c3e50;
        color: white;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 500;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 25px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with logo and navigation
st.sidebar.image("https://img.icons8.com/color/96/000000/price-tag-euro.png", width=80)
st.sidebar.title("House Price Monitor")
st.sidebar.markdown("---")

# Navigation
PAGES = {
    "📊 Overview": overview,
    "📈 Data Drift": data_drift,
    "📊 Prediction Drift": prediction_drift,
    "📊 Model Performance": model_performance,
    "💬 User Feedback": user_feedback,
    "🔍 A/B Testing": ab_testing
}

# Add navigation with icons
st.sidebar.markdown("### Navigation")
selection = st.sidebar.radio(
    "Navigation Menu",  # Add a descriptive label
    list(PAGES.keys()),
    label_visibility="collapsed"  # But keep it visually hidden
)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Last Updated:** Today  
**Version:** 1.0.0  
**Model:** House Price Predictor v2.1
""")

# Display the selected page
page = PAGES[selection]

# Add a nice header for the current page
st.markdown(f"# {selection.split(' ')[1]} {selection.split(' ')[0]}")
st.markdown("---")

# Run the page app
page.app()