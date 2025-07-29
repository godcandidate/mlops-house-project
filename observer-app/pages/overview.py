import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from datetime import datetime, timedelta

def load_data():
    try:
        with open("logs/inference.json", 'r') as f:
            inf_data = json.load(f)
            inf_df = pd.json_normalize(inf_data)
            
        fed_df = pd.DataFrame()
        if os.path.exists("logs/feedback.json"):
            with open("logs/feedback.json", 'r') as f:
                fed_data = json.load(f)
                fed_df = pd.json_normalize(fed_data)
                
        return inf_df, fed_df
    except Exception as e:
        st.error(f"⚠️ Error loading data: {str(e)}")
        return None, None

def create_metric_card(icon, title, value, subtitle=None):
    subtitle_html = f'<div style="color: #64748b; font-size: 0.85rem; margin-top: 8px;">{subtitle}</div>' if subtitle else ''
    
    return f'''<div style="
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 24px rgba(0, 0, 0, 0.1)'" 
       onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 12px rgba(0, 0, 0, 0.05)'">
        <div style="display: flex; align-items: center; margin-bottom: 12px;">
            <div style="background: #f8fafc; padding: 8px; border-radius: 8px; margin-right: 12px;">
                <span style="font-size: 1.2rem;">{icon}</span>
            </div>
            <span style="font-size: 0.85rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">{title}</span>
        </div>
        <div style="font-size: 2rem; font-weight: 700; color: #1e293b; margin: 8px 0;">{value}</div>
        {subtitle_html}
    </div>'''

def app():
    # Clean header
    st.markdown("""
    <div style="
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    ">
        <h1 style="margin: 0; color: #1e293b; font-size: 2.2rem; font-weight: 700;">📊 System Overview</h1>
        <p style="margin: 0.5rem 0 0 0; color: #64748b; font-size: 1rem;">Monitor your Fridoma model performance and data quality</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    inf_df, fed_df = load_data()
    if inf_df is None:
        st.error("🚫 Unable to load data. Please check your log files.")
        return

    # Calculate metrics
    total_predictions = len(inf_df)
    positive = len(fed_df[fed_df["user_feedback"] == "positive"]) if not fed_df.empty else 0
    negative = len(fed_df[fed_df["user_feedback"] == "negative"]) if not fed_df.empty else 0
    feedback_total = positive + negative
    
    positive_rate = (positive / feedback_total * 100) if feedback_total > 0 else 0
    
    # Calculate average error
    avg_error = None
    if not fed_df.empty and "expected_price" in fed_df.columns:
        merged = pd.merge(inf_df, fed_df, on="prediction_id", how="inner")
        if not merged.empty:
            merged["error"] = abs(merged["predicted_price"] - merged["expected_price"])
            avg_error = merged["error"].mean()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.markdown(create_metric_card(
            "", "Predictions", f"{total_predictions:,}", 
            "Total processed"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "", "Feedback", f"{feedback_total:,}", 
            f"{positive_rate:.1f}% positive" if feedback_total > 0 else "Awaiting feedback"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "", "Avg Error", f"${avg_error:,.0f}" if avg_error else "N/A", 
            "Prediction accuracy"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "", "Model", "v1.0", 
            "Active version"
        ), unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 3rem 0 2rem 0;'></div>", unsafe_allow_html=True)
    
    # Charts section
    if not inf_df.empty:
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            # Prediction trends
            if 'prediction_time' in inf_df.columns:
                inf_df['date'] = pd.to_datetime(inf_df['prediction_time']).dt.date
            else:
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=30)
                inf_df['date'] = pd.date_range(start=start_date, periods=len(inf_df), freq='D').date
            
            daily_counts = inf_df.groupby('date').size().reset_index(name='count')
            
            fig = px.area(
                daily_counts, x='date', y='count',
                title='  Daily Predictions',
                color_discrete_sequence=['#3b82f6']
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                title_font_size=16,
                title_font_color='#1e293b',
                xaxis=dict(
                    showgrid=False, 
                    tickcolor='#1e293b',
                    tickfont=dict(color='#1e293b', size=12),
                    title_font=dict(color='#1e293b')
                ),
                yaxis=dict(
                    showgrid=True, 
                    gridcolor='#f1f5f9',
                    tickcolor='#1e293b',
                    tickfont=dict(color='#1e293b', size=12),
                    title_font=dict(color='#1e293b')
                ),
                height=350,
                margin=dict(t=40, b=40, l=40, r=40)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Feedback distribution
            if feedback_total > 0:
                fig = go.Figure(data=[go.Pie(
                    labels=['Positive', 'Negative'],
                    values=[positive, negative],
                    hole=.6,
                    marker_colors=['#3b82f6', '#ef4444']
                )])
                fig.update_layout(
                    title='  Feedback Distribution',
                    title_font_size=16,
                    title_font_color='#1e293b',
                    showlegend=True,
                    height=350,
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    margin=dict(t=40, b=40, l=40, r=40),
                    legend=dict(font=dict(color='#1e293b')),
                    annotations=[dict(text=f'{positive_rate:.1f}%<br>Positive', x=0.5, y=0.5, font_size=16, showarrow=False, font_color='#1e293b')]
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
                    border-radius: 16px;
                    padding: 2rem;
                    text-align: center;
                    height: 300px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                ">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
                    <h3 style="color: #6b7280; margin: 0;">No Feedback Yet</h3>
                    <p style="color: #9ca3af; margin: 0.5rem 0 0 0;">Waiting for user feedback...</p>
                </div>
                """, unsafe_allow_html=True)