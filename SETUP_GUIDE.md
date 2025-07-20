# SAM Setup Guide

## Google Calendar API Setup

To use SAM's calendar features, you need to set up Google Calendar API credentials:

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click on it and press "Enable"

### 2. Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application" as the application type
4. Give it a name (e.g., "SAM Assistant")
5. Click "Create"

### 3. Download Credentials

1. After creating the OAuth client, click "Download JSON"
2. Save the file as `credentials.json` in the `data/` directory of your SAM project
3. The path should be: `~/SAM/data/credentials.json`

### 4. First Run Authentication

When you first run SAM with calendar features:
1. SAM will open a browser window
2. Sign in with your Google account
3. Grant permission to access your calendar
4. The authentication token will be saved automatically

### 5. Verify Setup

You can test the calendar integration by asking SAM:
- "What are my upcoming events?"
- "Create a test event for tomorrow at 2pm"

## LM Studio Setup

### 1. Download and Install

1. Download LM Studio from [lmstudio.ai](https://lmstudio.ai)
2. Install and launch the application

### 2. Load the Model

1. In LM Studio, go to the "Models" tab
2. Search for: `mistralai/mistral-nemo-instruct-2407-q3_k_l`
3. Download and load the model

### 3. Start the API Server

1. Go to the "Local Server" tab
2. Make sure the port is set to `1234`
3. Click "Start Server"
4. Verify the server is running by visiting: `http://127.0.0.1:1234/v1/models`

## Running SAM

### Quick Start

```bash
cd ~/SAM
./start_sam.sh
```

### Manual Start

```bash
cd ~/SAM
source sam_env/bin/activate
python main.py
```

## Troubleshooting

### Calendar Issues

- **"No module named 'google.auth'"**: Run `pip install -r requirements.txt`
- **"Invalid credentials"**: Delete `data/token.pickle` and re-authenticate
- **"Permission denied"**: Check that `credentials.json` is in the `data/` directory

### LM Studio Issues

- **"Connection refused"**: Make sure LM Studio API server is running on port 1234
- **"Model not found"**: Ensure the correct model is loaded in LM Studio
- **"Timeout"**: Try increasing the timeout in `llm_client.py` or check your model size

### General Issues

- **Import errors**: Make sure you're in the virtual environment: `source sam_env/bin/activate`
- **Permission errors**: Make sure the startup script is executable: `chmod +x start_sam.sh`

## Testing

Run the test suite to verify everything is working:

```bash
cd ~/SAM
source sam_env/bin/activate
python test_sam.py
```

This will test all components except the LLM integration (which requires LM Studio to be running). 