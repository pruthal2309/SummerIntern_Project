# 🤖 HR & Compliance RAG System
### Production-Ready Retrieval-Augmented Generation with Modern Web Interface

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 3. Run pipeline (first time only)
python main.py --pipeline

# 4. Start the complete system
python start_full_system.py
```

**Access the system:**
- 🌐 **Web Interface**: http://localhost:3000
- 📖 **API Docs**: http://localhost:8000/docs
- ❤️ **Health Check**: http://localhost:8000/health

---

## 📌 Overview

A complete **Retrieval-Augmented Generation (RAG) system** for querying legal and compliance documents with:

- ✅ **3000+ EU legal documents** indexed and searchable
- ✅ **Semantic search** using FAISS vector database
- ✅ **LLM-powered answers** via Groq API (Llama 3.3 70B)
- ✅ **Modern web interface** for easy interaction
- ✅ **FastAPI backend** with full documentation
- ✅ **Docker support** for easy deployment

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│  FastAPI     │─────▶│   Vector    │
│  (Port 3000)│      │  (Port 8000) │      │  Database   │
└─────────────┘      └──────────────┘      │   (FAISS)   │
                              │             └─────────────┘
                              │
                              ▼
                     ┌──────────────┐
                     │  Groq LLM    │
                     │  (Llama 3.3) │
                     └──────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Python 3.8+ | Core application |
| **API Framework** | FastAPI | REST API server |
| **Web Server** | Uvicorn | ASGI server |
| **Embeddings** | sentence-transformers | Semantic vectors |
| **Vector DB** | FAISS | Similarity search |
| **LLM** | Groq (Llama 3.3 70B) | Answer generation |
| **Frontend** | HTML/CSS/JS | User interface |

---

## 📁 Project Structure

```
hr-compliance-rag/
├── backend/                    # 🎯 All Python backend code
│   ├── api/                    # FastAPI application
│   │   ├── app.py             # Main FastAPI app
│   │   ├── routes.py          # API endpoints
│   │   └── schemas.py         # Pydantic models
│   ├── ingestion/             # Data processing
│   │   ├── loaders.py         # Document loaders
│   │   ├── chunker.py         # Text chunking
│   │   ├── validator.py       # Data validation
│   │   └── metadata_builder.py
│   ├── vectorstore/           # Vector operations
│   │   ├── embedding_generator.py
│   │   ├── build_index.py     # FAISS index builder
│   │   ├── retriever.py       # Semantic search
│   │   └── metadata_filter.py
│   ├── rag/                   # RAG pipeline
│   │   ├── rag_pipeline.py    # Main orchestrator
│   │   ├── retrieval_service.py
│   │   ├── llm_service.py     # Groq integration
│   │   ├── prompt_builder.py
│   │   └── evaluation.py
│   ├── config.py              # Configuration management
│   └── main.py                # Backend entry point
├── frontend/                   # Web interface
│   ├── index.html             # Main UI
│   ├── serve_frontend.py      # Frontend server
│   └── README.md
├── data/                       # Data storage
│   ├── raw/                   # Input documents (3000+ files)
│   └── processed/             # Generated embeddings & indexes
├── main.py                     # Root entry point
├── start_full_system.py        # Complete system launcher
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── Dockerfile                  # Docker configuration
└── README.md                   # This file
```

---

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- 4GB RAM minimum (8GB recommended)
- Internet connection for model downloads

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hr-compliance-rag
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env and add your Groq API key
   # Get key from: https://console.groq.com/
   ```

5. **Run the pipeline** (first time only)
   ```bash
   python main.py --pipeline
   ```
   
   This will:
   - Load and validate 3000+ documents
   - Generate semantic embeddings
   - Build FAISS vector index
   - Save processed data

6. **Start the system**
   ```bash
   python start_full_system.py
   ```

---

## 🎯 Usage

### Command Line Interface

```bash
# Run complete pipeline
python main.py --pipeline

# Skip Week 1 (if already done)
python main.py --pipeline --no-week1

# Start API server only
python main.py --serve

# Start API on custom host/port
python main.py --serve --host 0.0.0.0 --port 8080

# Show configuration
python main.py --config

# Validate configuration
python main.py --validate

# Start complete system (API + Frontend)
python start_full_system.py
```

### Web Interface

1. Open http://localhost:3000
2. Try example queries (click to auto-fill)
3. Ask questions about EU regulations
4. View results with sources and scores

### API Usage

**Query endpoint:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What does the council decision say about excessive deficit?",
    "top_k": 5
  }'
```

**Health check:**
```bash
curl http://localhost:8000/health
```

**Interactive API docs:**
Visit http://localhost:8000/docs for Swagger UI

---

## 📊 Dataset Information

### Content
- **3000+ document chunks** from EUR-Lex legal database
- **Topics**: EU regulations, council decisions, deficits, imports
- **Language**: English
- **Format**: Plain text files
- **Size**: ~500MB processed data

### Example Queries

✅ **Working queries** (match document content):
- "What does the council decision say about excessive deficit?"
- "What are the regulations about garlic import?"
- "Tell me about the commission regulation."
- "What is the council decision about Netherlands?"

❌ **Won't work** (content doesn't exist):
- "What is the maternity leave policy?"
- "Tell me about employee benefits"

---

## 🐳 Docker Deployment

### Build Docker image

```bash
docker build -t hr-compliance-rag .
```

### Run container

```bash
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key_here \
  -v $(pwd)/data:/app/data \
  hr-compliance-rag
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  frontend:
    image: python:3.10-slim
    working_dir: /app/frontend
    command: python -m http.server 3000
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app/frontend
    restart: unless-stopped
```

---

## 🔧 Configuration

All configuration is managed in `backend/config.py` and `.env` file:

```bash
# API Settings
API_HOST=localhost
API_PORT=8000

# Embedding Settings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
BATCH_SIZE=32

# LLM Settings
GROQ_API_KEY=your_key_here
GROQ_MODEL_NAME=llama-3.3-70b-versatile
LLM_MAX_TOKENS=1024
LLM_TEMPERATURE=0.1

# RAG Settings
RAG_TOP_K=5

# Processing Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

---

## 📈 Performance

- **Query Latency**: <2 seconds average
- **Vector Search**: <100ms
- **LLM Generation**: ~1-2 seconds
- **Index Size**: ~8MB for 3000 documents
- **Memory Usage**: ~2GB during operation

---

## 🐛 Troubleshooting

### Common Issues

**"API Offline" in web interface**
```bash
# Check if API is running
curl http://localhost:8000/health

# Restart API server
python main.py --serve
```

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
python main.py --pipeline
```

**Configuration errors**
```bash
# Validate configuration
python main.py --validate

# Check .env file has GROQ_API_KEY
```

---

## 🚀 Deployment Checklist

- [ ] Install Python 3.8+
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure `.env` with API keys
- [ ] Run pipeline: `python main.py --pipeline`
- [ ] Test API: `python main.py --serve`
- [ ] Test frontend: Open http://localhost:3000
- [ ] Configure firewall for ports 3000, 8000
- [ ] Set up reverse proxy (nginx/Apache)
- [ ] Configure SSL certificates
- [ ] Set up monitoring and logging
- [ ] Configure backup for `data/processed/`

---

## 📄 License

This project is for educational and research purposes.  
All datasets are publicly available from EUR-Lex.

---

## 🙏 Acknowledgments

- EUR-Lex for legal document database
- Hugging Face for sentence-transformers
- Groq for LLM API
- FastAPI framework
- FAISS vector database

---

## 📞 Support

- 📖 **Documentation**: See `INSTALLATION.md` and `SETUP_GUIDE.md`
- 🐛 **Issues**: Check troubleshooting section above
- 💬 **API Docs**: http://localhost:8000/docs

---

> **Built with ❤️ for efficient legal document retrieval**

**Version**: 2.0.0  
**Last Updated**: March 2026  
**Status**: ✅ Production Ready
