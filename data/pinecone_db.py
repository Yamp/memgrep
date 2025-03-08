"""
Pinecone vector database implementation for storing and searching meme embeddings.
This provides an alternative to the Redis implementation for better vector search performance.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any, Union

from loguru import logger
from pydantic import BaseModel

import settings
from data.redis_db import SearchRequest, ImageRecord


class PineconeDB:
    """
    Pinecone vector database for storing and searching meme embeddings.
    This class provides the same interface as RedisDB for easy switching.
    """
    
    def __init__(
            self,
            api_key: str = os.environ.get("PINECONE_API_KEY", ""),
            environment: str = os.environ.get("PINECONE_ENVIRONMENT", ""),
            index_name: str = os.environ.get("PINECONE_INDEX", "tg_memes"),
            dimension: int = 512,  # Default dimension for embeddings
    ):
        """
        Initialize the Pinecone database.
        
        Args:
            api_key: Pinecone API key
            environment: Pinecone environment
            index_name: Name of the Pinecone index
            dimension: Dimension of the embeddings
        """
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.dimension = dimension
        self.client = None
        self.index = None
        
        # Initialize Pinecone client if API key and environment are provided
        if api_key and environment:
            try:
                import pinecone
                pc = pinecone.Pinecone(api_key=api_key, environment=environment)
                
                # Check if index exists, create it if it doesn't
                if index_name not in pc.list_indexes().names():
                    pc.create_index(
                        name=index_name,
                        dimension=dimension,
                        metric="cosine",
                    )
                    logger.info(f"Created Pinecone index '{index_name}'")
                
                self.index = pc.Index(index_name)
                logger.info(f"Connected to Pinecone index '{index_name}'")
            except ImportError:
                logger.error("Failed to import Pinecone. Please install it with 'pip install pinecone-client'")
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone: {e}")
    
    def create_db(self) -> bool:
        """
        Create the Pinecone index if it doesn't exist.
        
        Returns:
            True if the index was created, False if it already exists
        """
        if not self.api_key or not self.environment:
            logger.error("Pinecone API key or environment not provided")
            return False
        
        try:
            import pinecone
            pc = pinecone.Pinecone(api_key=self.api_key, environment=self.environment)
            
            # Check if index exists
            if self.index_name in pc.list_indexes().names():
                logger.info(f"Pinecone index '{self.index_name}' already exists")
                return False
            
            # Create index
            pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
            )
            
            self.index = pc.Index(self.index_name)
            logger.info(f"Created Pinecone index '{self.index_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to create Pinecone index: {e}")
            return False
    
    def add_record(self, record: ImageRecord) -> bool:
        """
        Add a record to the Pinecone index.
        
        Args:
            record: Image record to add
        
        Returns:
            True if the record was added successfully, False otherwise
        """
        if not self.index:
            logger.error("Pinecone index not initialized")
            return False
        
        try:
            # Convert record to dictionary
            record_dict = record.dict()
            
            # Convert datetime to timestamp
            if record_dict.get("dt"):
                record_dict["dt"] = record_dict["dt"].timestamp()
            
            # Convert lists to strings
            record_dict["comments"] = json.dumps(record_dict.get("comments", []))
            record_dict["reactions"] = json.dumps(record_dict.get("reactions", []))
            
            # Use zero vector if semantic_vector is not provided
            vector = record_dict.get("semantic_vector", [0.0] * self.dimension)
            
            # Ensure vector has the correct dimension
            if len(vector) != self.dimension:
                logger.warning(f"Vector dimension mismatch: expected {self.dimension}, got {len(vector)}")
                # Pad or truncate vector to match the expected dimension
                if len(vector) < self.dimension:
                    vector = vector + [0.0] * (self.dimension - len(vector))
                else:
                    vector = vector[:self.dimension]
            
            # Upsert record to Pinecone
            self.index.upsert(
                vectors=[(str(record.id), vector, record_dict)],
            )
            
            logger.info(f"Added record {record.id} to Pinecone index")
            return True
        except Exception as e:
            logger.error(f"Failed to add record to Pinecone: {e}")
            return False
    
    def search(self, request: SearchRequest) -> List[ImageRecord]:
        """
        Search for records in the Pinecone index.
        
        Args:
            request: Search request
        
        Returns:
            List of matching image records
        """
        if not self.index:
            logger.error("Pinecone index not initialized")
            return []
        
        try:
            # If we have a semantic vector, use it for vector search
            if hasattr(request, "semantic_vector") and request.semantic_vector:
                vector = request.semantic_vector
                
                # Ensure vector has the correct dimension
                if len(vector) != self.dimension:
                    logger.warning(f"Vector dimension mismatch: expected {self.dimension}, got {len(vector)}")
                    # Pad or truncate vector to match the expected dimension
                    if len(vector) < self.dimension:
                        vector = vector + [0.0] * (self.dimension - len(vector))
                    else:
                        vector = vector[:self.dimension]
                
                # Build filter based on request parameters
                filter_dict = {}
                
                if request.dt_start:
                    filter_dict["dt"] = {"$gte": request.dt_start.timestamp()}
                if request.dt_end:
                    if "dt" not in filter_dict:
                        filter_dict["dt"] = {}
                    filter_dict["dt"]["$lte"] = request.dt_end.timestamp()
                
                if request.chats:
                    filter_dict["chat"] = {"$in": request.chats}
                
                if request.senders:
                    filter_dict["sender_id"] = {"$in": request.senders}
                
                # Perform vector search
                results = self.index.query(
                    vector=vector,
                    top_k=request.max_results,
                    filter=filter_dict if filter_dict else None,
                    include_metadata=True,
                )
                
                # Convert results to ImageRecord objects
                records = []
                for match in results.matches:
                    metadata = match.metadata
                    
                    # Convert timestamp to datetime
                    if "dt" in metadata:
                        metadata["dt"] = datetime.fromtimestamp(metadata["dt"])
                    
                    # Convert string lists to actual lists
                    if "comments" in metadata:
                        metadata["comments"] = json.loads(metadata["comments"])
                    if "reactions" in metadata:
                        metadata["reactions"] = json.loads(metadata["reactions"])
                    
                    records.append(ImageRecord(**metadata))
                
                return records
            else:
                # If we don't have a semantic vector, use metadata filtering
                # This is less efficient but allows text search
                
                # Build filter based on request parameters
                filter_dict = {}
                
                # Add text search filter
                if request.query:
                    # We'll search in multiple text fields
                    text_fields = ["msg_text", "ocr_rus", "ocr_eng", "semantic_data"]
                    text_conditions = []
                    
                    for field in text_fields:
                        text_conditions.append({field: {"$text": {"$search": request.query}}})
                    
                    filter_dict["$or"] = text_conditions
                
                if request.dt_start:
                    filter_dict["dt"] = {"$gte": request.dt_start.timestamp()}
                if request.dt_end:
                    if "dt" not in filter_dict:
                        filter_dict["dt"] = {}
                    filter_dict["dt"]["$lte"] = request.dt_end.timestamp()
                
                if request.chats:
                    filter_dict["chat"] = {"$in": request.chats}
                
                if request.senders:
                    filter_dict["sender_id"] = {"$in": request.senders}
                
                # Perform metadata search
                results = self.index.query(
                    vector=[0.0] * self.dimension,  # Dummy vector
                    top_k=request.max_results,
                    filter=filter_dict,
                    include_metadata=True,
                )
                
                # Convert results to ImageRecord objects
                records = []
                for match in results.matches:
                    metadata = match.metadata
                    
                    # Convert timestamp to datetime
                    if "dt" in metadata:
                        metadata["dt"] = datetime.fromtimestamp(metadata["dt"])
                    
                    # Convert string lists to actual lists
                    if "comments" in metadata:
                        metadata["comments"] = json.loads(metadata["comments"])
                    if "reactions" in metadata:
                        metadata["reactions"] = json.loads(metadata["reactions"])
                    
                    records.append(ImageRecord(**metadata))
                
                return records
        except Exception as e:
            logger.error(f"Failed to search Pinecone: {e}")
            return []
    
    def add_recognitions(self, recs: list) -> None:
        """
        Add recognitions to the Pinecone index.
        
        Args:
            recs: List of recognition objects
        """
        if not self.index:
            logger.error("Pinecone index not initialized")
            return
        
        try:
            for rec in recs:
                img = rec.image
                
                # Prepare metadata
                metadata = {
                    "message_id": img.message_id,
                    "chat": img.message.chat.chat_id,
                    "post_link": f"https://t.me/{img.message.chat.chat_name}/{img.message_id}",
                    "easy_ocr": rec.easy_ocr,
                    "blip": rec.blip,
                }
                
                # Use zero vector if no embedding is available
                vector = [0.0] * self.dimension
                
                # Upsert record to Pinecone
                self.index.upsert(
                    vectors=[(str(rec.image_id), vector, metadata)],
                )
            
            logger.info(f"Added {len(recs)} recognitions to Pinecone index")
        except Exception as e:
            logger.error(f"Failed to add recognitions to Pinecone: {e}")