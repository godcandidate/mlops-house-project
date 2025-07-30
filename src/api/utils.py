import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ModelConfig:
    MODE = os.getenv("MODEL_MODE", "default")  # "default" or "ab"