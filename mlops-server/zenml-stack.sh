# Installations
sudo apt update
sudo apt install -y python3-venv python3-pip python3-full
# Step 1: Create a virtual environment
python3 -m venv zenml-venv

# Step 2: Activate it
source zenml-venv/bin/activate

# Install ZenML and integrations
pip install zenml
zenml init
zenml integration install github s3
zenml integration install aws


zenml connect server_ip

# Set up artifact store
zenml artifact-store register s3_store \
  --flavor=s3 \
  --path=s3://mlops-house-project/zenml-artifact-store

# Optional: Create metadata store (or use default SQLite)
zenml metadata-store register local_metadata --type=sqlite --path=/home/ubuntu/zenml_metadata.db

# Save GitHub token securely
zenml secret create github_secret --pa_token=ghp_xxxxxYOURTOKENxxxxx

# Register code repository
zenml code-repository register mlops-house-project --type=github \
  --owner=godcandidate \
  --repository=mlops-house-project \
  --token={{github_secret.pa_token}}

# Register and set the stack
zenml stack register prod_stack \
  -a s3_store \
  -o local_orchestrator \
  --code=mlops-house-project

zenml stack set prod_stack
http://34.240.148.189/devices/verify?device_id=d09b6c3d-0242-474b-8a04-07bdc0904f8e&user_code=59e74b37456078e66876ece7db13c5b2
