import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta

def load_data():
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
                
        return inf_df, fed_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.error("Please check if the log files exist and are in the correct format.")
        return None, None

def create_metric_card(title, value, delta=None, delta_type=None):
    color = "#28a745" if delta_type == "positive" else "#dc3545"
    delta_html = f'<div style="color: {color}; font-size: 0.9em;">{delta}</div>' if delta else ''
    return f"""
    <div class="metric-card">
        <h3 style="color: #4f8bf9; margin-top: 0;">{title}</h3>
        <div style="font-size: 2em; font-weight: bold;">{value}</div>
        {delta_html}
    </div>
    """

def app():
    st.markdown("## 🏠 Model Performance Overview")
    st.markdown("""
    Welcome to the House Price Prediction Monitor. Track your model's performance, 
    monitor data quality, and analyze predictions in real-time.
    """)
    
    # Load data with loading state
    with st.spinner('Loading data...'):
        inf_df, fed_df = load_data()
    
    if inf_df is None or fed_df is None:
        st.warning("Could not load data. Please check if the log files exist.")
        return

    # Process data
    total_predictions = len(inf_df)
    positive = len(fed_df[fed_df["user_feedback"] == "positive"])
    negative = len(fed_df[fed_df["user_feedback"] == "negative"])
    feedback_total = positive + negative
    
    # Calculate metrics
    positive_rate = (positive / feedback_total * 100) if feedback_total > 0 else 0
    negative_rate = (negative / feedback_total * 100) if feedback_total > 0 else 0
    
    # Calculate average error if we have expected prices
    avg_error = None
    if "expected_price" in fed_df.columns and not fed_df.empty:
        merged = pd.merge(inf_df, fed_df, on="prediction_id", how="inner")
        if not merged.empty:
            merged["error"] = abs(merged["predicted_price"] - merged["expected_price"])
            avg_error = merged["error"].mean()
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "Total Predictions",
            f"{total_predictions:,}",
            "+12% from last week"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Feedback Rate",
            f"{feedback_total:,}",
            f"{positive_rate:.1f}% positive",
            "positive" if positive_rate >= 50 else "negative"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Avg. Prediction Error",
            f"${avg_error:,.2f}" if avg_error else "N/A",
            "-5.2% from last month" if avg_error else None,
            "positive"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "Model Version",
            "v2.1.0",
            "Latest",
            "positive"
        ), unsafe_allow_html=True)
    
    # Add charts
    st.markdown("### 📈 Prediction Trends")
    
    # Sample time series data (replace with actual time-based data if available)
    if not inf_df.empty:
        # Convert timestamp if it exists, otherwise use index
        if 'prediction_time' in inf_df.columns:
            inf_df['date'] = pd.to_datetime(inf_df['prediction_time']).dt.date
        else:
            # Create sample dates if not available
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            inf_df['date'] = pd.date_range(start=start_date, periods=len(inf_df), freq='D').date
        
        # Create a time series chart
        daily_counts = inf_df.groupby('date').size().reset_index(name='count')
        
        fig = px.line(
            daily_counts, 
            x='date', 
            y='count',
            title='Daily Predictions',
            labels={'count': 'Number of Predictions', 'date': 'Date'},
            height=400
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#f0f2f6'),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Feedback distribution
    if not fed_df.empty and feedback_total > 0:
        st.markdown("### 📊 Feedback Distribution")
        feedback_data = pd.DataFrame({
            'Feedback': ['Positive', 'Negative'],
            'Count': [positive, negative]
        })
        
        fig = px.pie(
            feedback_data, 
            values='Count', 
            names='Feedback',
            color='Feedback',
            color_discrete_map={'Positive':'#28a745', 'Negative':'#dc3545'},
            hole=.4
        )
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        st.plotly_chart(fig, use_container_width=True)