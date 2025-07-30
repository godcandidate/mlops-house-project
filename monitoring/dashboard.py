import streamlit as st
from pages import overview, data_drift, model_performance, ab_testing
import os

# Disable automatic page navigation by hiding the default Streamlit navigation
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="Fridomonitor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force light theme and modern navbar
st.markdown("""
<style>
    /* Force light theme */
    .stApp {
        background: #ffffff !important;
        color: #1f2937 !important;
    }
    
    /* Modern Sidebar */
    [data-testid="stSidebar"] {
        background: #f8fafc !important;
        border-right: 2px solid #e2e8f0 !important;
    }
    
    /* Modern Navigation Buttons */
    .stRadio > div {
        gap: 8px;
        display: flex;
        flex-direction: column;
        padding: 0.5rem 0;
    }
    
    /* All buttons - gray background */
    .stRadio > div > label {
        background: #f3f4f6 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 16px !important;
        padding: 18px 32px !important;
        margin: 6px 0 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        font-weight: 500 !important;
        color: #6b7280 !important;
        width: 100% !important;
        min-width: 220px !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        position: relative !important;
        text-align: left !important;
        font-size: 0.95rem !important;
    }
    
    .stRadio > div > label:hover {
        background: #e5e7eb !important;
        color: #374151 !important;
    }
    
    /* Active button - same gray background */
    .stRadio > div > label[data-checked="true"],
    .stRadio > div > label[aria-checked="true"],
    .stRadio input[type="radio"]:checked + label {
        background: #f3f4f6 !important;
        color: #374151 !important;
        border-color: #e5e7eb !important;
        font-weight: 600 !important;
    }
    
    /* Hide radio circles and add status indicators */
    .stRadio > div > label > div:first-child {
        display: none !important;
    }
    
    /* Left border indicator - gray by default */
    .stRadio > div > label::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 24px;
        border-radius: 0 4px 4px 0;
        background: #d1d5db;
        transition: all 0.3s ease;
    }
    
    /* Blue left border when active */
    .stRadio > div > label[data-checked="true"]::before,
    .stRadio > div > label[aria-checked="true"]::before,
    .stRadio input[type="radio"]:checked + label::before,
    .stRadio > div > label:has(input:checked)::before {
        background: #3b82f6 !important;
        height: 32px !important;
        box-shadow: 0 0 8px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Right status dot - gray by default */
    .stRadio > div > label::after {
        content: '';
        position: absolute;
        right: 20px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #d1d5db;
        transition: all 0.3s ease;
    }
    
    /* Blue dot when active */
    .stRadio > div > label[data-checked="true"]::after,
    .stRadio > div > label[aria-checked="true"]::after,
    .stRadio input[type="radio"]:checked + label::after,
    .stRadio > div > label:has(input:checked)::after {
        background: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
        transform: scale(1.1) !important;
    }
    
    /* Clean button styling for all pages */
    .stButton > button {
        background: white !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        color: #374151 !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton > button:hover {
        background: #f9fafb !important;
        border-color: #d1d5db !important;
        color: #1f2937 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    .stDownloadButton > button {
        background: white !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        color: #374151 !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stDownloadButton > button:hover {
        background: #f9fafb !important;
        border-color: #d1d5db !important;
        color: #1f2937 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Force light text for specific elements */
    .stMarkdown, .stText {
        color: #1f2937 !important;
    }
    
    /* Force navigation text to be black */
    .stRadio label span {
        color: #374151 !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #374151 !important;
    }
    
    /* Fix error and success message colors */
    .stAlert {
        color: #1f2937 !important;
    }
    
    .stAlert > div {
        color: #1f2937 !important;
    }
    
    .stError {
        color: #dc2626 !important;
    }
    
    .stSuccess {
        color: #16a34a !important;
    }
    
    h1, h2, h3 {
        color: #111827 !important;
    }
    
    .stApp [data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

# Modern sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0; margin-bottom: 1.5rem;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
        <h2 style="margin: 0; color: #111827; font-weight: 700;">Fridomonitor</h2>
        <p style="margin: 0.25rem 0 0 0; color: #6b7280; font-size: 0.9rem;">ML Monitoring Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    PAGES = {
        "Overview": overview,
        "Data Drift": data_drift,
        "Model Performance": model_performance,
        "A/B Testing": ab_testing
    }
    
    selection = st.radio(
        "Navigate to:",
        list(PAGES.keys()),
        label_visibility="visible"
    )

# Display the selected page
page = PAGES[selection]
page.app()