"""
LLM Logic and Decision Engine for Edvora
Handles OpenAI GPT-4 integration and structured decision generation
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import openai
from openai import AsyncOpenAI
import re
import requests
import asyncio

logger = logging.getLogger(__name__)

class LLMDecisionEngine:
    """Decision engine using OpenAI GPT or Hugging Face for policy reasoning and structured output"""

    def __init__(self, api_key: str, use_huggingface: bool = False, hf_api_key: str = None):
        self.use_huggingface = use_huggingface
        if use_huggingface:
            self.hf_api_key = hf_api_key
            self.hf_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        else:
            self.client = AsyncOpenAI(api_key=api_key)
        self.model_name = os.getenv("MODEL_NAME", "gpt-4")
        self.max_tokens = int(os.getenv("MAX_TOKENS", 2000))
        self.temperature = float(os.getenv("TEMPERATURE", 0.1))
        
        # Decision templates and patterns
        self.decision_patterns = {
            'approved': ['approved', 'accept', 'eligible', 'covered', 'valid', 'allowed'],
            'rejected': ['rejected', 'deny', 'ineligible', 'not covered', 'invalid', 'not allowed']
        }

    async def query_huggingface(self, prompt: str) -> str:
        """Query Hugging Face API for text generation"""
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        payload = {"inputs": prompt, "parameters": {"max_length": 200, "temperature": 0.1}}

        def make_request():
            response = requests.post(self.hf_url, headers=headers, json=payload)
            return response.json()

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, make_request)

        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', prompt)
        return "Unable to generate response"
        
    async def generate_decision(self, question: str, context_chunks: List[Dict[str, Any]], document_url: str) -> Dict[str, str]:
        """
        Generate structured decision based on question and context
        
        Args:
            question: Natural language query
            context_chunks: Relevant document chunks from retriever
            document_url: Source document URL
            
        Returns:
            Structured decision with decision, amount, justification, and source_clause
        """
        try:
            logger.info(f"Generating decision for question: {question[:100]}...")
            
            # Prepare context from chunks
            context_text = self._prepare_context(context_chunks)
            
            # Create decision prompt
            prompt = self._create_decision_prompt(question, context_text, document_url)
            
            # Generate response using selected model
            if self.use_huggingface:
                response = await self.query_huggingface(prompt)
            else:
                response = await self._call_openai(prompt)
            
            # Parse and structure the response
            structured_decision = self._parse_decision_response(response, context_chunks)
            
            logger.info("Decision generated successfully")
            return structured_decision
            
        except Exception as e:
            logger.error(f"Error generating decision: {str(e)}")
            raise
    
    def _prepare_context(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Prepare context text from retrieved chunks"""
        if not context_chunks:
            return "No relevant context found in the document."
        
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            chunk_text = chunk.get('content', '')
            similarity = chunk.get('similarity_score', 0)
            
            context_parts.append(
                f"[Context {i} - Relevance: {similarity:.3f}]\n{chunk_text}\n"
            )
        
        return "\n".join(context_parts)
    
    def _create_decision_prompt(self, question: str, context: str, document_url: str) -> str:
        """Create comprehensive prompt for decision generation"""
        
        prompt = f"""Analyze document and answer question. Return JSON only.

QUESTION: {question}

CONTEXT:
{context}

OUTPUT FORMAT:
{{
    "decision": "Approved/Rejected",
    "amount": "₹X,XXX or Not specified",
    "justification": "Brief explanation based on document",
    "source_clause": "Relevant quote from document"
}}

Return valid JSON only."""

        return prompt
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API with the decision prompt"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert document analysis AI that provides structured decisions in JSON format. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise
    
    def _parse_decision_response(self, response: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, str]:
        """Parse and validate the LLM response"""
        try:
            # Try to parse JSON response
            decision_data = json.loads(response)
            
            # Validate required fields
            required_fields = ['decision', 'amount', 'justification', 'source_clause']
            for field in required_fields:
                if field not in decision_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate and normalize decision
            decision = self._normalize_decision(decision_data['decision'])
            
            # Validate and format amount
            amount = self._format_amount(decision_data['amount'])
            
            # Ensure justification is comprehensive
            justification = self._enhance_justification(
                decision_data['justification'], 
                decision, 
                context_chunks
            )
            
            # Validate source clause
            source_clause = self._validate_source_clause(
                decision_data['source_clause'], 
                context_chunks
            )
            
            return {
                'decision': decision,
                'amount': amount,
                'justification': justification,
                'source_clause': source_clause
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            # Fallback to text parsing
            return self._fallback_parse_response(response, context_chunks)
        except Exception as e:
            logger.error(f"Error parsing decision response: {str(e)}")
            raise
    
    def _normalize_decision(self, decision: str) -> str:
        """Normalize decision to Approved/Rejected"""
        decision_lower = decision.lower().strip()
        
        for pattern in self.decision_patterns['approved']:
            if pattern in decision_lower:
                return "Approved"
        
        for pattern in self.decision_patterns['rejected']:
            if pattern in decision_lower:
                return "Rejected"
        
        # Default to Rejected if unclear
        logger.warning(f"Unclear decision '{decision}', defaulting to Rejected")
        return "Rejected"
    
    def _format_amount(self, amount: str) -> str:
        """Format amount in Indian Rupees"""
        if not amount or amount.lower() in ['not specified', 'not mentioned', 'n/a', 'na']:
            return "Not specified"
        
        # Extract numeric value
        amount_match = re.search(r'[\d,]+', amount.replace('₹', '').replace(',', ''))
        if amount_match:
            numeric_amount = amount_match.group()
            # Format with Indian Rupees symbol
            return f"₹{numeric_amount}"
        
        return amount
    
    def _enhance_justification(self, justification: str, decision: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Enhance justification with additional context if needed"""
        if len(justification) < 50:  # If justification is too short
            context_summary = f"Based on analysis of {len(context_chunks)} relevant document sections, "
            justification = context_summary + justification
        
        return justification
    
    def _validate_source_clause(self, source_clause: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Validate that source clause exists in the context"""
        if not source_clause or len(source_clause) < 10:
            # Try to extract a relevant clause from context
            if context_chunks:
                # Use the most relevant chunk as source
                best_chunk = context_chunks[0]
                content = best_chunk.get('content', '')
                # Extract first sentence or meaningful portion
                sentences = content.split('.')
                if sentences:
                    return sentences[0].strip() + "."
        
        return source_clause
    
    def _fallback_parse_response(self, response: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, str]:
        """Fallback parsing when JSON parsing fails"""
        logger.warning("Using fallback response parsing")
        
        # Try to extract decision
        decision = "Rejected"  # Default
        if any(word in response.lower() for word in self.decision_patterns['approved']):
            decision = "Approved"
        
        # Try to extract amount
        amount_match = re.search(r'₹[\d,]+', response)
        amount = amount_match.group() if amount_match else "Not specified"
        
        # Use response as justification
        justification = response[:500] + "..." if len(response) > 500 else response
        
        # Use first context chunk as source
        source_clause = "Document analysis based on provided context"
        if context_chunks:
            content = context_chunks[0].get('content', '')
            if content:
                source_clause = content[:200] + "..." if len(content) > 200 else content
        
        return {
            'decision': decision,
            'amount': amount,
            'justification': justification,
            'source_clause': source_clause
        }
