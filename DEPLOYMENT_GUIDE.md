# Edvora Deployment Guide
## Complete Guide for Bajaj HackRx 2025 Submission

### 🎯 Quick Deployment Checklist

- [ ] OpenAI API key obtained
- [ ] Repository pushed to GitHub
- [ ] Environment variables configured
- [ ] Deployment platform selected
- [ ] Public HTTPS endpoint verified
- [ ] API compliance validated

---

## 🚀 Deployment Options

### Option 1: Railway (Recommended for Hackathon)

**Why Railway?**
- Free tier with generous limits
- Automatic HTTPS
- Easy GitHub integration
- Fast deployment
- Reliable uptime

**Steps:**
1. **Sign up**: Go to [railway.app](https://railway.app) and sign up with GitHub
2. **New Project**: Click "New Project" → "Deploy from GitHub repo"
3. **Select Repository**: Choose your Edvora repository
4. **Environment Variables**: 
   - Go to Variables tab
   - Add `OPENAI_API_KEY` with your API key
5. **Deploy**: Railway will automatically build and deploy
6. **Get URL**: Copy the generated URL (e.g., `https://edvora-production.up.railway.app`)

**Configuration File**: `railway.json` (already included)

---

### Option 2: Render

**Steps:**
1. **Sign up**: Go to [render.com](https://render.com) and sign up with GitHub
2. **New Web Service**: Click "New" → "Web Service"
3. **Connect Repository**: Select your Edvora repository
4. **Configuration**:
   - Name: `edvora-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**: Add `OPENAI_API_KEY`
6. **Deploy**: Click "Create Web Service"

**Configuration File**: `render.yaml` (already included)

---

### Option 3: Vercel (Serverless)

**Steps:**
1. **Install Vercel CLI**: `npm i -g vercel`
2. **Login**: `vercel login`
3. **Deploy**: `vercel --prod`
4. **Environment Variables**: Set via Vercel dashboard

**Note**: May have timeout limitations for large documents

---

## 🔧 Environment Configuration

### Required Environment Variables

```bash
# Essential
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional (with defaults)
MODEL_NAME=gpt-4
MAX_TOKENS=2000
TEMPERATURE=0.1
CHUNK_SIZE=800
CHUNK_OVERLAP=100
VECTOR_DIMENSION=1536
SIMILARITY_THRESHOLD=0.7
```

### Getting OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up/Login
3. Go to API Keys section
4. Create new secret key
5. Copy the key (starts with `sk-`)

---

## 🧪 Testing Your Deployment

### 1. Basic Health Check
```bash
curl https://your-deployment-url.com/health
```

### 2. API Documentation
Visit: `https://your-deployment-url.com/docs`

### 3. Test HackRx Endpoint
```bash
curl -X POST "https://your-deployment-url.com/hackrx/run" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://www.africau.edu/images/default/sample.pdf",
    "questions": ["What is this document about?"]
  }'
```

### 4. Automated Validation
```bash
# Run compliance validation
python validate_hackrx_compliance.py
```

---

## 📋 HackRx Submission Requirements

### ✅ Compliance Checklist

- [x] **FastAPI Application**: ✅ Implemented with main.py
- [x] **Mandatory Endpoint**: ✅ `/hackrx/run` with POST method
- [x] **Input Format**: ✅ `{"documents": "url", "questions": ["query"]}`
- [x] **Output Format**: ✅ `{"answers": [{"decision": "...", "amount": "...", "justification": "...", "source_clause": "..."}]}`
- [x] **RAG Pipeline**: ✅ LangChain + FAISS + OpenAI GPT-4
- [x] **Document Processing**: ✅ PDF/DOCX from URLs
- [x] **Vector Store**: ✅ FAISS for similarity search
- [x] **LLM Integration**: ✅ OpenAI GPT-4 for reasoning
- [x] **Public HTTPS**: ✅ Available via deployment platforms
- [x] **Explainable AI**: ✅ Source clause references included

---

## 🏆 Submission Preparation

### 1. Final Code Review
```bash
# Run all tests
python tests/test_examples.py

# Validate compliance
python validate_hackrx_compliance.py

# Check code quality
python -m flake8 --max-line-length=100 *.py
```

### 2. Documentation Check
- [ ] README.md is comprehensive
- [ ] API documentation is accessible
- [ ] Usage examples are provided
- [ ] Deployment instructions are clear

### 3. Deployment Verification
- [ ] Public HTTPS URL is accessible
- [ ] All endpoints respond correctly
- [ ] Environment variables are set
- [ ] Error handling works properly

### 4. Performance Optimization
- [ ] Response times are reasonable (<30 seconds)
- [ ] Memory usage is optimized
- [ ] Error messages are informative
- [ ] Logging is comprehensive

---

## 🚨 Troubleshooting

### Common Issues

**1. OpenAI API Errors**
- Check API key is valid
- Ensure sufficient credits
- Verify model access (GPT-4)

**2. Document Processing Failures**
- Check URL accessibility
- Verify file format (PDF/DOCX)
- Check file size limits

**3. Deployment Issues**
- Verify all dependencies in requirements.txt
- Check environment variables
- Review deployment logs

**4. Performance Issues**
- Optimize chunk size
- Reduce similarity threshold
- Use caching for repeated requests

---

## 📞 Support

For deployment issues:
1. Check deployment platform documentation
2. Review application logs
3. Test locally first
4. Validate API compliance

---

## 🎉 Success Metrics

Your deployment is ready for HackRx submission when:

✅ Public HTTPS endpoint is accessible  
✅ `/hackrx/run` endpoint works correctly  
✅ Response format matches specification exactly  
✅ Document processing handles PDF/DOCX from URLs  
✅ RAG pipeline provides accurate answers  
✅ Source clause references are included  
✅ Error handling is robust  
✅ API documentation is available  

**Good luck with your HackRx 2025 submission! 🚀**
