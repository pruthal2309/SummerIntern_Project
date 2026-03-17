# 🚀 Deployment Guide

This project is designed to run locally without Docker.

---

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (optional)
- 4GB RAM minimum (8GB recommended)
- Groq API Key (https://console.groq.com/)

---

## 🖥️ Local Deployment

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Groq API key
# GROQ_API_KEY=your_actual_api_key_here
```

### 3. Run Pipeline (First Time)

```bash
# Process documents and build vector database
python -m backend.main --pipeline
```

### 4. Start the System

```bash
# Start the Streamlit application
streamlit run streamlit_app.py
```

---

## 🐛 Troubleshooting

### Common Issues

**Import errors**
```bash
pip install -r requirements.txt
```

**No results for queries**
- Use queries about EU regulations, not HR policies
- Try the provided example queries first

**Missing data files**
```bash
# Run the complete pipeline
python -m backend.main --pipeline
```

### Environment Variables

Create a `.env` file with:

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_NAME=llama-3.3-70b-versatile

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# RAG Configuration
RAG_TOP_K=5
LLM_MAX_TOKENS=1024
LLM_TEMPERATURE=0.1

# Paths
DATA_RAW_PATH=data/raw
DATA_PROCESSED_PATH=data/processed
METADATA_PATH=data/metadata.csv

# Embedding Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
BATCH_SIZE=32
FAISS_INDEX_TYPE=flat
```

### Security Best Practices

1. **API Key Management:**
   - Never commit `.env` to version control
   - Use secrets management (AWS Secrets Manager, Azure Key Vault)
   - Rotate keys regularly

2. **Network Security:**
   - Use HTTPS in production
   - Configure firewall rules
   - Implement rate limiting

3. **Access Control:**
   - Add authentication to API endpoints
   - Implement role-based access control
   - Use API keys for client authentication

---

## 📊 Monitoring & Logging

### Health Checks

```bash
# API Health
curl http://localhost:8000/health
```

### View Logs

When running locally, logs stream directly to the terminal where the API is running:

```bash
python -m backend.main --serve
```

To capture logs to a file:

```bash
python -m backend.main --serve 2>&1 | tee api.log
```

---

## 🔄 Updates & Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Restart the API server (stop and rerun)
```

### Backup Data

```bash
# Backup processed data
tar -czf backup-$(date +%Y%m%d).tar.gz data/processed/

# Backup to S3 (AWS)
aws s3 cp backup-$(date +%Y%m%d).tar.gz s3://your-bucket/backups/
```

### Database Maintenance

```bash
# Rebuild vector index
python -m backend.main --pipeline --no-week1
```

---

## 🐛 Troubleshooting

### Application Won't Start

```bash
# Check if the API is running
curl http://localhost:8000/health

# Restart the API
python -m backend.main --serve
```
### API Not Responding

```bash
# Check health
curl http://localhost:8000/health

# Restart API
python -m backend.main --serve
```
### Out of Memory

```bash
# Reduce batch size in .env
BATCH_SIZE=16
```
---

## ✅ Production Checklist

- [ ] Environment variables configured
- [ ] API keys secured
- [ ] HTTPS enabled
- [ ] Firewall configured
- [ ] Monitoring setup
- [ ] Backup strategy implemented
- [ ] Health checks working
- [ ] Logs accessible
- [ ] Documentation updated
- [ ] Team trained

---

## 📞 Support

For deployment issues:
1. Check logs in the terminal where the API is running
2. Verify environment variables
3. Check system resources
4. Review error messages

---

**Your RAG system is now deployment-ready! 🚀**