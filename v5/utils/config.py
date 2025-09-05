#!/usr/bin/env python3
"""
Configuration settings for SAM
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LLM API Configuration
API_URL = os.getenv("API_URL", "http://127.0.0.1:1234")
MODEL_NAME = os.getenv("MODEL_NAME", "mistralai/mistral-nemo-instruct-2407")

# Google Calendar Configuration
SCOPES = os.getenv("GOOGLE_SCOPES", "https://www.googleapis.com/auth/calendar").split(",")
SCOPES = [scope.strip() for scope in SCOPES]  # Clean up any whitespace

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, os.getenv("DATA_DIR", "data"))
CRED_PATH = os.path.join(BASE_DIR, os.getenv("GOOGLE_CREDENTIALS_PATH", "data/credentials.json"))
TOKEN_PATH = os.path.join(BASE_DIR, os.getenv("GOOGLE_TOKEN_PATH", "data/token.pickle"))

# SAM Configuration
SAM_NAME = "SAM"
SAM_PERSONALITY = "assistant"
MAX_RESPONSE_LENGTH = 500  # Keep responses concise 

# Timezone Configuration
TIMEZONE = os.getenv("TIMEZONE", "America/Los_Angeles") 