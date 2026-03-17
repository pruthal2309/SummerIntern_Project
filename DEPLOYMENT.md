# 🚀 Deployment Guide

Complete guide for deploying the HR & Compliance RAG System to production.

---

## 📋 Prerequisites

### Required Software
- **Docker** (20.10+)
- **Docker Compose** (2.0+)
- **Git**

### Required Configuration
- **Groq API Key** from https://console.groq.com/
- **Minimum 4GB RAM** (8GB recommended)
- **2GB free disk space**

---

## 🐳 Docker Deployment (Recommended)

### Quick Start

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```powershell
.\deploy.ps1
```

### Manual Docker Deployment

1. **Build the images:**
```bash
docker-compose build
```

2. **Start the services:**
```bash
docker-compose up -d
```

3. **Check status:**
```bash
docker-compose ps
docker-compose logs -f
```

4. **Access the application:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

---

## 🖥️ Local Deployment (Without Docker)

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
python main.py
```

### 4. Start the System

```bash
# Start API + Frontend
python start_full_system.py
```

---

## ☁️ Cloud Deployment

### AWS Deployment

#### Using EC2

1. **Launch EC2 Instance:**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.medium (minimum)
   - Storage: 20GB
   - Security Group: Open ports 80, 443, 8000, 3000

2. **Connect and Setup:**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone <your-repo-url>
cd enterprise-hr-compliance-RAG-pipeline-system-main

# Setup environment
cp .env.example .env
nano .env  # Add your API key

# Deploy
./deploy.sh
```

#### Using ECS (Elastic Container Service)

1. **Push image to ECR:**
```bash
aws ecr create-repository --repository-name hr-compliance-rag
docker tag hr-compliance-rag:latest <account-id>.dkr.ecr.<region>.amazonaws.com/hr-compliance-rag:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/hr-compliance-rag:latest
```

2. **Create ECS Task Definition and Service**

### Google Cloud Platform (GCP)

#### Using Cloud Run

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/<project-id>/hr-compliance-rag

# Deploy to Cloud Run
gcloud run deploy hr-compliance-rag \
  --image gcr.io/<project-id>/hr-compliance-rag \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GROQ_API_KEY=<your-key>
```

### Azure Deployment

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name hr-rag-rg --location eastus

# Create container
az container create \
  --resource-group hr-rag-rg \
  --name hr-compliance-rag \
  --image <your-registry>/hr-compliance-rag:latest \
  --dns-name-label hr-rag-app \
  --ports 8000 3000 \
  --environment-variables GROQ_API_KEY=<your-key>
```

### Heroku Deployment

```bash
# Login to Heroku
heroku login

# Create app
heroku create hr-compliance-rag

# Set environment variables
heroku config:set GROQ_API_KEY=your_key

# Deploy
git push heroku main
```

---

## 🔒 Production Configuration

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

# Docker Health
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f rag-api

# Last 100 lines
docker-compose logs --tail=100
```

### Monitoring Tools

- **Prometheus** for metrics
- **Grafana** for visualization
- **ELK Stack** for log aggregation

---

## 🔄 Updates & Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
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
docker-compose exec rag-api python main.py --no-week1
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs rag-api

# Check if ports are in use
netstat -an | grep 8000
netstat -an | grep 3000

# Restart services
docker-compose restart
```

### API Not Responding

```bash
# Check health
curl http://localhost:8000/health

# Check container status
docker-compose ps

# Restart API
docker-compose restart rag-api
```

### Out of Memory

```bash
# Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory

# Or reduce batch size in .env
BATCH_SIZE=16
```

---

## 📈 Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  rag-api:
    deploy:
      replicas: 3
```

### Load Balancing

Use Nginx or cloud load balancers to distribute traffic across multiple instances.

### Caching

Implement Redis for caching frequent queries:

```yaml
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
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
1. Check logs: `docker-compose logs -f`
2. Verify environment variables
3. Check system resources
4. Review error messages

---

**Your RAG system is now deployment-ready! 🚀**