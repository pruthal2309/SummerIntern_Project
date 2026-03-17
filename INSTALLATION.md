# 🚀 Installation Guide

## Quick Setup

### 1. Prerequisites
- Python 3.8+
- Virtual environment activated
- Internet connection (for model downloads)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create/edit `.env` file and add your Groq API key:
```bash
# Copy example file
cp .env.example .env

# Edit .env file and add:
GROQ_API_KEY=your_actual_api_key_here
```

Get your API key from: https://console.groq.com/

### 4. Run the System
```bash
# First time: Run complete pipeline
python main.py

# Start the system (API + Frontend)
python start_full_system.py
```

### 5. Access the System
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Troubleshooting

### Import Errors
```bash
pip install -r requirements.txt
```

### Missing API Key
Edit `.env` file and add your Groq API key from https://console.groq.com/

### No Data Files
Run the complete pipeline first:
```bash
python main.py
```

That's it! The system should now be running with a modern web interface. 