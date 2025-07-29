import streamlit as st
import streamlit.components.v1 as components
import subprocess
import os
from pathlib import Path

def generate_prediction_drift_report():
    """Generate prediction drift report using evidently"""
    try:
        # Change to the correct directory and run the script
        current_dir = Path(__file__).parent.parent
        result = subprocess.run(
            ["python", "evidently-report/generate-prediction-drift.py"],
            cwd=current_dir,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def app():
    # Page header
    st.markdown("""
    <div style="
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    ">
        <h1 style="margin: 0; color: #1e293b; font-size: 1.8rem; font-weight: 700;">🎯 Prediction Drift Analysis</h1>
        <p style="margin: 0.5rem 0 0 0; color: #64748b;">Track changes in model prediction patterns</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get the absolute path to the report
    current_dir = Path(__file__).parent
    report_path = current_dir.parent / "reports" / "prediction_target_drift_report.html"
    report_exists = report_path.exists()

    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("⚡ Generate Report", use_container_width=True):
            with st.spinner("Generating prediction drift report..."):
                success, stdout, stderr = generate_prediction_drift_report()
                if success:
                    st.success("✅ Report updated successfully!")
                    st.rerun()
                else:
                    st.error(f"⚠️ Failed to generate report: {stderr}")
                    if stdout:
                        st.code(stdout)
    with col3:
        if report_exists:
            with open(report_path, 'rb') as f:
                st.download_button(
                    label="📥 Download",
                    data=f,
                    file_name="prediction_drift_report.html",
                    mime="text/html",
                    use_container_width=True
                )

    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
    
    if report_exists:
        try:
            # Status indicator
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
                border: 1px solid #22c55e;
                border-radius: 12px;
                padding: 1rem;
                margin-bottom: 1.5rem;
                text-align: center;
            ">
                <span style="color: #166534; font-weight: 600;">🟢 Report Available</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Read and display the HTML content
            with open(report_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Display the full HTML report
            components.html(html_content, height=800, scrolling=True)
            
        except Exception as e:
            st.error(f"⚠️ Error loading report: {str(e)}")
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
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
            <h3 style="color: #92400e; margin: 0 0 0.5rem 0;">No Report Available</h3>
            <p style="color: #a16207; margin: 0;">Click 'Generate Report' to analyze prediction drift patterns</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    app()