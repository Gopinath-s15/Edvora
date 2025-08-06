"""
Edvora - AI-Powered Document Reasoning System
Main FastAPI application for Bajaj HackRx 2025 Hackathon
"""

import os
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import uvicorn
from dotenv import load_dotenv

from retriever import DocumentRetriever
from llm_logic import LLMDecisionEngine
from utils import DocumentProcessor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Edvora - AI Document Reasoning System",
    description="AI-powered Document Reasoning System for Bajaj HackRx 2025",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class HackRxRequest(BaseModel):
    """Request model for /hackrx/run endpoint"""
    documents: str = Field(..., description="URL to PDF or DOCX document")
    questions: List[str] = Field(..., description="List of natural language queries")
    
    @validator('documents')
    def validate_document_url(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("Document URL must be a non-empty string")
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError("Document URL must be a valid HTTP/HTTPS URL")
        return v
    
    @validator('questions')
    def validate_questions(cls, v):
        if not v or not isinstance(v, list):
            raise ValueError("Questions must be a non-empty list")
        if len(v) == 0:
            raise ValueError("At least one question is required")
        for question in v:
            if not isinstance(question, str) or not question.strip():
                raise ValueError("Each question must be a non-empty string")
        return v

class AnswerResponse(BaseModel):
    """Individual answer response model"""
    decision: str = Field(..., description="Approved/Rejected decision")
    amount: str = Field(..., description="Amount in Indian Rupees format")
    justification: str = Field(..., description="Detailed explanation with policy reasoning")
    source_clause: str = Field(..., description="Specific clause reference from document")

class HackRxResponse(BaseModel):
    """Response model for /hackrx/run endpoint"""
    answers: List[str] = Field(..., description="List of string answers corresponding to questions")

# Global components (initialized on startup)
document_processor = None
retriever = None
llm_engine = None

@app.on_event("startup")
async def startup_event():
    """Initialize components on application startup"""
    global document_processor, retriever, llm_engine
    
    logger.info("Initializing Edvora components...")
    
    try:
        # Validate OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize components
        document_processor = DocumentProcessor()
        retriever = DocumentRetriever()
        llm_engine = LLMDecisionEngine(api_key=openai_api_key)
        
        logger.info("Edvora components initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {str(e)}")
        raise

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Edvora - AI-Powered Document Reasoning System",
        "version": "1.0.0",
        "status": "active",
        "hackathon": "Bajaj HackRx 2025",
        "endpoints": {
            "main": "/hackrx/run",
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "components": {
            "document_processor": document_processor is not None,
            "retriever": retriever is not None,
            "llm_engine": llm_engine is not None
        }
    }

@app.post("/hackrx/run", response_model=HackRxResponse)
async def hackrx_run(request: HackRxRequest):
    """
    Main endpoint for document reasoning as per HackRx specifications
    
    Processes documents from URLs and answers natural language queries
    with explainable AI decisions and source clause references.
    """
    try:
        logger.info(f"Processing request for document: {request.documents}")
        logger.info(f"Questions: {request.questions}")
        
        # Step 1: Download and process document
        logger.info("Step 1: Processing document...")
        document_text = await document_processor.process_document_from_url(request.documents)
        
        if not document_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to extract text from document"
            )
        
        # Step 2: Create vector store and retriever
        logger.info("Step 2: Creating vector store...")
        await retriever.create_vector_store(document_text)
        
        # Step 3: Process each question
        logger.info("Step 3: Processing questions...")
        answers = []
        
        for question in request.questions:
            logger.info(f"Processing question: {question}")
            
            # Retrieve relevant context
            relevant_chunks = await retriever.retrieve_relevant_chunks(question)
            
            # Generate decision using LLM
            decision_result = await llm_engine.generate_decision(
                question=question,
                context_chunks=relevant_chunks,
                document_url=request.documents
            )

            # Create simple string answer
            answer_text = f"{decision_result.get('decision', 'Unknown')} - {decision_result.get('justification', 'No justification provided')}"
            answers.append(answer_text)
        
        logger.info(f"Successfully processed {len(answers)} questions")
        
        return HackRxResponse(answers=answers)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    # Run the application
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
