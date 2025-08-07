# HackRx 6.0 - Bajaj Finserv AI Document Processing API

## 🏆 Official Submission for Bajaj Finserv HackRx 6.0 Competition

This is a production-ready AI-powered document processing system specifically built for the HackRx 6.0 competition. It implements advanced RAG (Retrieval-Augmented Generation) pipeline with FAISS vector store and OpenAI GPT-4 to analyze insurance policy documents and provide accurate, detailed answers to natural language queries.

## 🎯 HackRx 6.0 Compliance Features

- ✅ **Official `/hackrx/run` Endpoint**: Exact API specification compliance
- ✅ **Bearer Token Authentication**: Secure API access as required
- ✅ **Policy Document Analysis**: Specialized for insurance policy understanding
- ✅ **Detailed Answer Generation**: Comprehensive responses with policy specifics
- ✅ **HTTPS Deployment**: Production-ready on Render platform
- ✅ **Sub-30s Response Time**: Optimized for competition requirements
- ✅ **RAG Pipeline**: Advanced document retrieval and generation
- ✅ **Vector Search**: FAISS-powered semantic search
- ✅ **GPT-4 Integration**: State-of-the-art language model

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

## 🔗 Official HackRx 6.0 API Specification

### 🎯 Submission URL
```
https://edvora-api.onrender.com/hackrx/run
```

### 📋 Endpoint: `/hackrx/run`
**Method**: POST
**Authentication**: Bearer Token Required

**Request Headers**:
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer <api_key>
```

**Request Format** (Official HackRx Example):
```json
{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?"
    ]
}
```

**Response Format** (Official HackRx Example):
```json
{
    "answers": [
        "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
        "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
        "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period."
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
