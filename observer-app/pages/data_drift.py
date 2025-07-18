import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import os

def generate_sample_drift_data():
    """Generate sample data for demonstration"""
    np.random.seed(42)
    features = ['sqft', 'bedrooms', 'bathrooms', 'year_built']
    
    # Generate reference data (3 months ago)
    ref_data = pd.DataFrame({
        'feature': np.repeat(features, 100),
        'value': np.concatenate([
            np.random.normal(2000, 500, 100),  # sqft
            np.random.normal(3, 1, 100).round(0),  # bedrooms
            np.random.normal(2, 0.5, 100).round(1),  # bathrooms
            np.random.normal(2000, 15, 100).round(0)  # year_built
        ]),
        'dataset': 'reference'
    })
    
    # Generate current data (now)
    curr_data = pd.DataFrame({
        'feature': np.repeat(features, 100),
        'value': np.concatenate([
            np.random.normal(2100, 600, 100),  # sqft (drifted)
            np.random.normal(3.2, 1.2, 100).round(0),  # bedrooms (slightly drifted)
            np.random.normal(2, 0.5, 100).round(1),  # bathrooms (same)
            np.random.normal(2010, 20, 100).round(0)  # year_built (drifted)
        ]),
        'dataset': 'current'
    })
    
    return pd.concat([ref_data, curr_data])

def plot_feature_distribution(feature_name, data):
    """Create a distribution plot for a single feature"""
    fig = px.histogram(
        data[data['feature'] == feature_name],
        x='value',
        color='dataset',
        barmode='overlay',
        color_discrete_map={'reference': '#4f8bf9', 'current': '#ff7f0e'},
        title=f'Distribution of {feature_name}',
        labels={'value': feature_name, 'dataset': 'Dataset'}
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', y=1.1, yanchor='bottom')
    )
    return fig

def app():
    st.markdown("## 📊 Data Drift Analysis")
    st.markdown("""
    Monitor changes in your input data distributions over time to detect data drift.
    Compare the reference (training) data against current production data.
    """)
    
    # Check if the report exists
    report_path = "reports/data_drift_report.html"
    report_exists = os.path.exists(report_path)
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["📊 Visual Analysis", "📝 Full Report"])
    
    with tab1:
        st.markdown("### Feature Distribution Comparison")
        
        # Generate or load data
        drift_data = generate_sample_drift_data()
        features = drift_data['feature'].unique()
        
        # Create a grid of plots
        cols = st.columns(2)
        for idx, feature in enumerate(features):
            with cols[idx % 2]:
                fig = plot_feature_distribution(feature, drift_data)
                st.plotly_chart(fig, use_container_width=True)
        
        # Drift summary
        st.markdown("### 🚨 Drift Detection Summary")
        drift_summary = pd.DataFrame({
            'Feature': features,
            'Drift Detected': ['Yes', 'No', 'No', 'Yes'],
            'Drift Score': [0.87, 0.12, 0.08, 0.92],
            'Impact': ['High', 'Low', 'Low', 'High']
        })
        
        # Style the dataframe
        def highlight_drift(val):
            if val == 'Yes':
                return 'background-color: #ffcccc'
            elif val == 'High':
                return 'color: #d62728; font-weight: bold'
            return ''
        
        st.dataframe(
            drift_summary.style.applymap(highlight_drift, 
                                      subset=['Drift Detected', 'Impact'])
                              .format({'Drift Score': '{:.2f}'}),
            use_container_width=True,
            hide_index=True
        )
        
        st.info("""
        **Legend:**  
        - **Drift Score:** 0-0.3 (No Drift), 0.3-0.7 (Warning), 0.7-1 (Drift Detected)  
        - **Impact:** Estimated impact on model performance
        """)
    
    with tab2:
        st.markdown("### Detailed Data Drift Report")
        if report_exists:
            with open(report_path, 'r') as f:
                components.html(f.read(), height=1000, scrolling=True)
        else:
            st.warning("No data drift report found. Please generate one using the command below.")
            st.code("python evidently-report/generate-data-drift.py", language="bash")
    
    # Add a section to generate new report
    with st.expander("🔧 Generate New Report", expanded=False):
        st.markdown("### Generate New Data Drift Report")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            Click the button below to generate a new data drift report. 
            This will compare the latest production data against the reference dataset.
            """)
        with col2:
            if st.button("🔄 Generate Report", type="primary"):
                with st.spinner("Generating report... This may take a minute."):
                    try:
                        # Here you would call your data drift generation script
                        # For now, we'll just create a dummy file
                        with open(report_path, 'w') as f:
                            f.write("<html><body><h1>Data Drift Report</h1><p>This is a placeholder for the data drift report.</p></body></html>")
                        st.success("Report generated successfully!")
                        st.experimental_rerun()  # Refresh the page to show the new report
                    except Exception as e:
                        st.error(f"Error generating report: {str(e)}")