"""
Simplified OCR implementation for testing purposes.
This module provides a simplified version of the ModernOCRExtractor class.
"""

import os
from pathlib import Path
from typing import Union, Optional

from loguru import logger
from PIL import Image


class SimplifiedOCRExtractor:
    """
    Simplified OCR extractor using Gemini 1.5 Flash.
    """
    
    def __init__(self):
        """Initialize the simplified OCR extractor."""
        # Initialize Gemini Pro Vision client if available
        self.gemini_client = None
        try:
            import google.generativeai as genai
            api_key = os.environ.get("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_client = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini 1.5 Flash client initialized successfully.")
            else:
                logger.warning("GOOGLE_API_KEY not found in environment variables.")
        except (ImportError, Exception) as e:
            logger.warning(f"Failed to initialize Gemini 1.5 Flash client: {e}")
    
    def extract(self, image: Union[Path, str, Image.Image]) -> str:
        """
        Extract text from an image using Gemini 1.5 Flash.
        
        Args:
            image: Path to the image or PIL Image object
        
        Returns:
            Extracted text from the image
        """
        if self.gemini_client:
            try:
                result = self._extract_gemini(image)
                if result:
                    return result
            except Exception as e:
                logger.error(f"Error using Gemini 1.5 Flash: {e}")
        
        return "No text extracted"
    
    def _extract_gemini(self, image: Union[Path, str, Image.Image]) -> Optional[str]:
        """
        Extract text from an image using Gemini 1.5 Flash.
        
        Args:
            image: Path to the image or PIL Image object
        
        Returns:
            Extracted text from the image or None if extraction failed
        """
        if not self.gemini_client:
            return None
        
        # Convert image to PIL Image if it's a path
        if isinstance(image, (str, Path)):
            image = Image.open(image)
        
        # Generate prompt for Gemini
        prompt = "Extract all text visible in this image. Return only the text, no additional commentary."
        
        # Generate response from Gemini
        response = self.gemini_client.generate_content([prompt, image])
        
        # Extract text from response
        if response and response.text:
            return response.text.strip()
        
        return None