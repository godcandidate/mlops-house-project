import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def format_currency(x):
    return "N/A" if pd.isna(x) else f"${x:,.0f}"

def format_percent(x):
    return "N/A" if pd.isna(x) else f"{x:.1%}"

def create_comparison_card(model_version, metrics_row):
    """Create a modern comparison card for each model version"""
    acceptance_rate = metrics_row.get('Acceptance Rate', 0)
    total_predictions = metrics_row.get('Total Predictions', 0)
    mean_error = metrics_row.get('Mean Error ($)', 'N/A')
    
    # Format the values properly
    formatted_acceptance = format_percent(acceptance_rate)
    formatted_error = format_currency(mean_error) if mean_error != 'N/A' else 'N/A'
    
    return f'''<div style="background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%); border: 2px solid #e5e7eb; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="background: #667eea; color: white; padding: 8px 12px; border-radius: 8px; font-weight: 600; margin-right: 12px;">{model_version}</div>
            <div style="color: #6b7280; font-size: 0.9rem;">Model Version</div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
            <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.7); border-radius: 12px;">
                <div style="font-size: 1.5rem; font-weight: 700; color: #1f2937;">{total_predictions:,}</div>
                <div style="font-size: 0.8rem; color: #6b7280; margin-top: 4px;">PREDICTIONS</div>
            </div>
            <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.7); border-radius: 12px;">
                <div style="font-size: 1.5rem; font-weight: 700; color: #1f2937;">{formatted_acceptance}</div>
                <div style="font-size: 0.8rem; color: #6b7280; margin-top: 4px;">ACCEPTANCE</div>
            </div>
        </div>
        <div style="margin-top: 1rem; padding: 1rem; background: rgba(255, 255, 255, 0.7); border-radius: 12px; text-align: center;">
            <div style="font-size: 1.2rem; font-weight: 600; color: #1f2937;">{formatted_error}</div>
            <div style="font-size: 0.8rem; color: #6b7280; margin-top: 4px;">AVG ERROR</div>
        </div>
    </div>'''

def app():
    # Clean header
    st.markdown("""
    <div style="
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    ">
        <h1 style="margin: 0; color: #1e293b; font-size: 1.8rem; font-weight: 700;">🔬 A/B Testing</h1>
        <p style="margin: 0.5rem 0 0 0; color: #64748b;">Compare model versions and performance metrics</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Load data
        with open("logs/inference.json", 'r') as f:
            inf_data = json.load(f)
            inf_df = pd.json_normalize(inf_data)
        
        with open("logs/feedback.json", 'r') as f:
            fed_data = json.load(f)
            fed_df = pd.json_normalize(fed_data)
        
        # Process data
        merged = pd.merge(inf_df[['prediction_id', 'model_version']], 
                         fed_df, on="prediction_id", how="inner")
        
        # Calculate metrics
        metrics = pd.DataFrame()
        metrics['Total Predictions'] = inf_df.groupby('model_version').size()
        metrics['Total Feedbacks'] = merged.groupby('model_version').size()
        metrics['Positive Feedbacks'] = merged[merged['user_feedback'] == 'positive'].groupby('model_version').size()
        metrics['Acceptance Rate'] = (metrics['Positive Feedbacks'] / metrics['Total Feedbacks']).round(3)
        
        # Calculate error metrics
        valid_feedback = fed_df.dropna(subset=['expected_price'])
        if not valid_feedback.empty:
            error_df = pd.merge(inf_df[['prediction_id', 'model_version', 'predicted_price']],
                              valid_feedback[['prediction_id', 'expected_price']],
                              on="prediction_id", how="inner")
            if not error_df.empty:
                error_df['error'] = abs(error_df['predicted_price'] - error_df['expected_price'])
                metrics['Mean Error ($)'] = error_df.groupby('model_version')['error'].mean().round(0)
        
        metrics = metrics.reset_index().rename(columns={'model_version': 'Model Version'})
        
        # Overall stats
        total_predictions = len(inf_df)
        total_feedbacks = len(fed_df)
        overall_acceptance = (metrics['Positive Feedbacks'].sum() / metrics['Total Feedbacks'].sum()) if metrics['Total Feedbacks'].sum() > 0 else 0
        
        # Test summary at the top
        st.markdown(f"""
        <div style="
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        ">
            <h3 style="margin: 0 0 1rem 0; color: #1e293b;">Test Summary</h3>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;">
                <div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #3b82f6; margin-bottom: 0.25rem;">{total_predictions:,}</div>
                    <div style="color: #64748b; font-weight: 500;">Total Predictions</div>
                </div>
                <div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #3b82f6; margin-bottom: 0.25rem;">{total_feedbacks:,}</div>
                    <div style="color: #64748b; font-weight: 500;">Total Feedback</div>
                </div>
                <div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #3b82f6; margin-bottom: 0.25rem;">{overall_acceptance:.1%}</div>
                    <div style="color: #64748b; font-weight: 500;">Overall Acceptance</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 3rem 0 2rem 0;'></div>", unsafe_allow_html=True)
        
        # Model comparison section
        st.markdown("""
        <div style="
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1.5rem;
            margin: 2rem 0;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        ">
            <h2 style="margin: 0; color: #1e293b; font-size: 1.3rem; font-weight: 700;">🔬 Model Comparison</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if not metrics.empty:
            # Create comparison cards
            cols = st.columns(len(metrics), gap="medium")
            for idx, (_, row) in enumerate(metrics.iterrows()):
                with cols[idx]:
                    card_html = create_comparison_card(row['Model Version'], row.to_dict())
                    st.markdown(card_html, unsafe_allow_html=True)
            
            # Additional insights
            if len(metrics) > 1:
                st.markdown("<div style='margin: 3rem 0 2rem 0;'></div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2, gap="large")
                
                with col1:
                    # Traffic distribution
                    fig1 = px.pie(
                        metrics, values='Total Predictions', names='Model Version',
                        title='Traffic Distribution',
                        color_discrete_sequence=['#3b82f6', '#ef4444', '#10b981']
                    )
                    fig1.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        title_font_size=16,
                        title_font_color='#1e293b',
                        height=350,
                        margin=dict(t=40, b=40, l=40, r=40),
                        legend=dict(font=dict(color='#1e293b'))
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Win rate comparison
                    best_model = metrics.loc[metrics['Acceptance Rate'].idxmax(), 'Model Version']
                    st.markdown(f"""
                    <div style="
                        background: white;
                        border: 1px solid #e2e8f0;
                        border-radius: 16px;
                        padding: 2rem;
                        text-align: center;
                        height: 350px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                    ">
                        <h3 style="margin: 0 0 1rem 0; color: #1e293b;">🏆 Current Leader</h3>
                        <div style="font-size: 2.5rem; margin: 1rem 0; color: #3b82f6;">{best_model}</div>
                        <div style="color: #64748b; font-size: 1.1rem;">Highest acceptance rate</div>
                        <div style="margin-top: 1rem; padding: 0.5rem; background: #f8fafc; border-radius: 8px; color: #1e293b;">
                            <strong>{metrics.loc[metrics['Acceptance Rate'].idxmax(), 'Acceptance Rate']:.1%}</strong> acceptance
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


        else:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                border: 1px solid #f59e0b;
                border-radius: 12px;
                padding: 2rem;
                text-align: center;
                margin: 2rem 0;
            ">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⚡</div>
                <h3 style="color: #92400e; margin: 0 0 0.5rem 0;">No A/B Test Data</h3>
                <p style="color: #a16207; margin: 0;">Deploy multiple model versions to start A/B testing</p>
            </div>
            """, unsafe_allow_html=True)
    
    except FileNotFoundError:
        st.error("🚫 Log files not found. Ensure `inference.json` and `feedback.json` exist in the `logs/` folder.")
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")

if __name__ == "__main__":
    app()