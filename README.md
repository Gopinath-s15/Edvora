# Edvora - AI-Powered Document Reasoning System

## Overview
Edvora is an AI-powered Document Reasoning System built for the Bajaj HackRx 2025 Hackathon. It implements a Retrieval-Augmented Generation (RAG) pipeline using LangChain, FAISS, and OpenAI GPT-4 to process documents and answer natural language queries with explainable decisions.

## Features
- **Document Processing**: Supports PDF and DOCX files from URLs
- **RAG Pipeline**: Advanced retrieval-augmented generation with FAISS vector store
- **Explainable AI**: Provides transparent decisions with source clause references
- **FastAPI Backend**: Production-ready API with async processing
- **Compliance**: 100% compliant with HackRx API specifications

## Project Structure
```
edvora/
├── main.py              # FastAPI application and /hackrx/run endpoint
├── retriever.py         # RAG retriever with FAISS vector store
├── llm_logic.py         # OpenAI GPT-4 integration and decision logic
├── utils.py             # Document processing and utility functions
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── README.md           # Project documentation
└── tests/              # Test files and examples
    └── test_examples.py
```

## API Specification

### Endpoint: `/hackrx/run`
**Method**: POST

**Input Format**:
```json
{
  "documents": "<url_to_pdf_or_docx>",
  "questions": ["natural language query about the document"]
}
```

**Output Format**:
```json
{
  "answers": [
    {
      "decision": "Approved/Rejected",
      "amount": "₹50,000",
      "justification": "Detailed explanation with policy reasoning",
      "source_clause": "Specific clause reference from document"
    }
  ]
}
```

## Setup Instructions and Quick Start Guide

### 1. Prerequisites
- Python 3.11 or higher
- OpenAI API key
- Git

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-username/edvora.git
cd edvora

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Run the Application
```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Verify Installation
Open your browser and navigate to:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Root Endpoint: http://localhost:8000/

## Usage Examples

### 1. Basic API Test
```bash
# Test with sample PDF document
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://www.africau.edu/images/default/sample.pdf",
    "questions": ["What is the main topic of this document?"]
  }'
```

### 2. Insurance Policy Analysis
```bash
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/insurance-policy.pdf",
    "questions": [
      "What is the maximum claim amount for medical expenses?",
      "Are dental treatments covered under this policy?",
      "What is the deductible amount?"
    ]
  }'
```

### 3. Using Python Requests
```python
import requests
import json

url = "http://localhost:8000/hackrx/run"
data = {
    "documents": "https://example.com/document.pdf",
    "questions": ["What are the key terms and conditions?"]
}

response = requests.post(url, json=data)
result = response.json()
print(json.dumps(result, indent=2))
```

### 4. Expected Response Format
```json
{
  "answers": [
    {
      "decision": "Approved",
      "amount": "₹50,000",
      "justification": "Based on the policy terms, medical expenses up to ₹50,000 are covered under Section 3.2 of the insurance policy. The claim meets all eligibility criteria.",
      "source_clause": "Section 3.2: Medical expenses coverage includes hospitalization, surgery, and emergency treatments up to the policy limit of ₹50,000 per year."
    }
  ]
}
```

## Deployment Options

### Option 1: Railway (Recommended)
1. **Connect Repository**: Link your GitHub repository to Railway
2. **Environment Variables**: Set `OPENAI_API_KEY` in Railway dashboard
3. **Deploy**: Automatic deployment on push to main branch
4. **Configuration**: Uses `railway.json` for build settings

```bash
# Railway CLI deployment (optional)
railway login
railway link
railway up
```

### Option 2: Render
1. **Connect Repository**: Link your GitHub repository to Render
2. **Environment Variables**: Set `OPENAI_API_KEY` in Render dashboard
3. **Configuration**: Uses `render.yaml` for deployment settings
4. **Deploy**: Automatic deployment on push

### Option 3: Vercel (Serverless)
1. **Connect Repository**: Link your GitHub repository to Vercel
2. **Environment Variables**: Set `OPENAI_API_KEY` in Vercel dashboard
3. **Configuration**: Uses `vercel.json` for serverless deployment
4. **Note**: May have timeout limitations for large documents

### Option 4: Docker Deployment
```bash
# Build Docker image
docker build -t edvora .

# Run container
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key edvora
```

### Option 5: Local Production
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Technical Architecture

### RAG Pipeline
1. **Document Loading**: Async download and parsing of PDF/DOCX files
2. **Text Chunking**: 800 tokens with 100 token overlap for optimal retrieval
3. **Embedding Generation**: OpenAI embeddings for semantic search
4. **Vector Storage**: FAISS for efficient similarity search
5. **LLM Reasoning**: GPT-4 for policy analysis and decision making

### Key Components
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **LangChain**: Framework for building LLM applications
- **FAISS**: Facebook AI Similarity Search for vector operations
- **OpenAI GPT-4**: Advanced language model for reasoning
- **PyPDF2/python-docx**: Document parsing libraries

## Contributing
This project is built for the Bajaj HackRx 2025 Hackathon. For questions or improvements, please contact the development team.

## License
MIT License - see LICENSE file for details.
