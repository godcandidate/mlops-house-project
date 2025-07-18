import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import socket
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import webbrowser
import time

def start_local_server(port=8000):
    """Start a local HTTP server"""
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('localhost', port), handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    return httpd

def find_available_port():
    """Find an available port"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def app():
    st.markdown("## 📈 Prediction Drift Analysis")
    st.markdown("""
    This page displays the detailed prediction drift analysis report.
    The report compares the current model predictions against the reference dataset.
    """)

    # Get the absolute path to the reports directory
    current_dir = Path(__file__).parent
    reports_dir = current_dir.parent / "reports"
    report_path = reports_dir / "prediction_target_drift_report.html"
    report_exists = report_path.exists()

    if report_exists:
        try:
            # Start a local server to serve the report
            port = find_available_port()
            os.chdir(str(reports_dir))
            httpd = start_local_server(port)
            report_url = f"http://localhost:{port}/prediction_target_drift_report.html"
            # Display the report with a clean layout
            st.markdown("### Detailed Drift Analysis Report")
            
            # Add a download button for the report
            with open(report_path, 'rb') as f:
                st.download_button(
                    label="Download Full Report",
                    data=f,
                    file_name="prediction_drift_report.html",
                    mime="text/html"
                )
            
            # Create an iframe that points to the local server
            iframe = f"""
            <div style="height: 800px; overflow: auto; border: 1px solid #e6e9ef; border-radius: 0.5rem;">
                <iframe src="{report_url}" 
                        style="width: 100%; height: 100%; border: none;">
                </iframe>
            </div>
            """
            components.html(iframe, height=800, scrolling=True)
            
            # Add a button to open in a new tab
            st.markdown(f"""
            <a href="{report_url}" target="_blank">
                <button style="margin-top: 10px;">Open in New Tab</button>
            </a>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error loading report: {str(e)}")
            if 'httpd' in locals():
                httpd.shutdown()
        finally:
            if 'httpd' in locals():
                httpd.shutdown()
    else:
        st.warning("No prediction drift report found. Please generate one using the command below.")
        st.code("cd evidently-report && python generate-prediction-drift.py", language="bash")
        
        if st.button("Generate Prediction Drift Report"):
            try:
                import subprocess
                with st.spinner("Generating report..."):
                    result = subprocess.run(
                        ["python", "evidently-report/generate-prediction-drift.py"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        st.success("Report generated successfully! Refreshing...")
                        st.rerun()
                    else:
                        st.error(f"Error generating report: {result.stderr}")
            except Exception as e:
                st.error(f"Failed to generate report: {str(e)}")

if __name__ == "__main__":
    app()