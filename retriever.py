"""
RAG Retriever Implementation for Edvora
Handles document chunking, embedding generation, and similarity search using FAISS
"""

import os
import logging
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
import tiktoken

logger = logging.getLogger(__name__)

class DocumentRetriever:
    """RAG retriever with FAISS vector store for document similarity search"""
    
    def __init__(self):
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 800))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 100))
        self.vector_dimension = int(os.getenv("VECTOR_DIMENSION", 1536))
        self.similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", 0.7))
        
        # Initialize components
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="text-embedding-ada-002"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self._count_tokens,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Vector store components
        self.vector_store = None
        self.document_chunks = []
        self.chunk_metadata = []
        
        # Initialize tokenizer for accurate token counting
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return len(self.tokenizer.encode(text))
    
    async def create_vector_store(self, document_text: str) -> None:
        """
        Create FAISS vector store from document text
        
        Args:
            document_text: Full text content of the document
        """
        try:
            logger.info("Creating vector store from document text...")
            
            # Step 1: Split document into chunks
            chunks = await self._create_chunks(document_text)
            
            if not chunks:
                raise ValueError("No chunks created from document text")
            
            logger.info(f"Created {len(chunks)} chunks from document")
            
            # Step 2: Generate embeddings for chunks
            embeddings_matrix = await self._generate_embeddings(chunks)
            
            # Step 3: Create FAISS index
            self._create_faiss_index(embeddings_matrix)
            
            logger.info("Vector store created successfully")
            
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise
    
    async def _create_chunks(self, document_text: str) -> List[str]:
        """Split document into chunks with metadata"""
        try:
            # Create Document object for LangChain text splitter
            doc = Document(page_content=document_text)
            
            # Split into chunks
            chunk_docs = self.text_splitter.split_documents([doc])
            
            # Extract text and create metadata
            chunks = []
            self.chunk_metadata = []
            
            for i, chunk_doc in enumerate(chunk_docs):
                chunk_text = chunk_doc.page_content.strip()
                
                if chunk_text:  # Only include non-empty chunks
                    chunks.append(chunk_text)
                    
                    # Create metadata for each chunk
                    metadata = {
                        'chunk_id': i,
                        'chunk_length': len(chunk_text),
                        'token_count': self._count_tokens(chunk_text),
                        'start_char': document_text.find(chunk_text[:50]) if len(chunk_text) >= 50 else document_text.find(chunk_text),
                        'preview': chunk_text[:100] + "..." if len(chunk_text) > 100 else chunk_text
                    }
                    self.chunk_metadata.append(metadata)
            
            self.document_chunks = chunks
            return chunks
            
        except Exception as e:
            logger.error(f"Error creating chunks: {str(e)}")
            raise
    
    async def _generate_embeddings(self, chunks: List[str]) -> np.ndarray:
        """Generate embeddings for document chunks"""
        try:
            logger.info(f"Generating embeddings for {len(chunks)} chunks...")
            
            # Generate embeddings using OpenAI
            embeddings_list = await self.embeddings.aembed_documents(chunks)
            
            # Convert to numpy array
            embeddings_matrix = np.array(embeddings_list, dtype=np.float32)
            
            logger.info(f"Generated embeddings matrix with shape: {embeddings_matrix.shape}")
            
            return embeddings_matrix
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def _create_faiss_index(self, embeddings_matrix: np.ndarray) -> None:
        """Create FAISS index from embeddings matrix"""
        try:
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings_matrix)
            
            # Create FAISS index
            index = faiss.IndexFlatIP(self.vector_dimension)  # Inner product for cosine similarity
            index.add(embeddings_matrix)
            
            self.vector_store = index
            
            logger.info(f"FAISS index created with {index.ntotal} vectors")
            
        except Exception as e:
            logger.error(f"Error creating FAISS index: {str(e)}")
            raise
    
    async def retrieve_relevant_chunks(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant chunks for a query
        
        Args:
            query: Search query
            top_k: Number of top chunks to retrieve
            
        Returns:
            List of relevant chunks with metadata and similarity scores
        """
        try:
            if not self.vector_store:
                raise ValueError("Vector store not initialized. Call create_vector_store first.")
            
            logger.info(f"Retrieving relevant chunks for query: {query[:100]}...")
            
            # Generate query embedding
            query_embedding = await self.embeddings.aembed_query(query)
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Normalize query vector
            faiss.normalize_L2(query_vector)
            
            # Search for similar chunks
            similarities, indices = self.vector_store.search(query_vector, top_k)
            
            # Prepare results
            relevant_chunks = []
            
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if idx < len(self.document_chunks):  # Ensure valid index
                    chunk_data = {
                        'rank': i + 1,
                        'chunk_id': idx,
                        'content': self.document_chunks[idx],
                        'similarity_score': float(similarity),
                        'metadata': self.chunk_metadata[idx] if idx < len(self.chunk_metadata) else {},
                        'is_relevant': similarity >= self.similarity_threshold
                    }
                    relevant_chunks.append(chunk_data)
            
            # Filter by similarity threshold
            filtered_chunks = [chunk for chunk in relevant_chunks if chunk['is_relevant']]
            
            if not filtered_chunks:
                # If no chunks meet threshold, return top 3 anyway
                filtered_chunks = relevant_chunks[:3]
                logger.warning(f"No chunks met similarity threshold {self.similarity_threshold}, returning top 3")
            
            logger.info(f"Retrieved {len(filtered_chunks)} relevant chunks")
            
            return filtered_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving relevant chunks: {str(e)}")
            raise
    
    def get_chunk_context(self, chunk_id: int, context_window: int = 1) -> str:
        """
        Get expanded context around a specific chunk
        
        Args:
            chunk_id: ID of the target chunk
            context_window: Number of chunks before and after to include
            
        Returns:
            Expanded context text
        """
        try:
            if not self.document_chunks:
                return ""
            
            start_idx = max(0, chunk_id - context_window)
            end_idx = min(len(self.document_chunks), chunk_id + context_window + 1)
            
            context_chunks = self.document_chunks[start_idx:end_idx]
            return "\n\n".join(context_chunks)
            
        except Exception as e:
            logger.warning(f"Error getting chunk context: {str(e)}")
            return self.document_chunks[chunk_id] if chunk_id < len(self.document_chunks) else ""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get retriever statistics"""
        return {
            'total_chunks': len(self.document_chunks),
            'vector_store_size': self.vector_store.ntotal if self.vector_store else 0,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'vector_dimension': self.vector_dimension,
            'similarity_threshold': self.similarity_threshold,
            'average_chunk_length': np.mean([len(chunk) for chunk in self.document_chunks]) if self.document_chunks else 0,
            'total_tokens': sum([self._count_tokens(chunk) for chunk in self.document_chunks]) if self.document_chunks else 0
        }
