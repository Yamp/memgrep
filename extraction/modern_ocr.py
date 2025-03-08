"""
Modern OCR implementation using Google Cloud Vision API and Gemini Pro Vision.
This module provides improved OCR capabilities compared to the original implementation.
"""

import os
from pathlib import Path
from typing import List, Optional, Union

from loguru import logger
from PIL import Image

# Import base OCR extractor for fallback
from extraction.ocr import OCRExtractor as BaseOCRExtractor


class ModernOCRExtractor:
    """
    Modern OCR extractor using Google Cloud Vision API and Gemini Pro Vision.
    Falls back to the base OCR extractor if the APIs are not available.
    """
    
    def __init__(self, use_gemini: bool = True, use_vision_api: bool = True, check_dict: bool = False):
        """
        Initialize the modern OCR extractor.
        
        Args:
            use_gemini: Whether to use Gemini Pro Vision for OCR
            use_vision_api: Whether to use Google Cloud Vision API for OCR
            check_dict: Whether to check if extracted words are in the dictionary
        """
        self.use_gemini = use_gemini
        self.use_vision_api = use_vision_api
        self._check_dict = check_dict
        
        # Initialize the base OCR extractor for fallback
        self.base_extractor = BaseOCRExtractor(check_dict=check_dict)
        
        # Initialize Google Cloud Vision API client if available
        self.vision_client = None
        if use_vision_api:
            try:
                from google.cloud import vision
                self.vision_client = vision.ImageAnnotatorClient()
                logger.info("Google Cloud Vision API client initialized successfully.")
            except (ImportError, Exception) as e:
                logger.warning(f"Failed to initialize Google Cloud Vision API client: {e}")
                logger.warning("Will fall back to base OCR extractor.")
        
        # Initialize Gemini Pro Vision client if available
        self.gemini_client = None
        if use_gemini:
            try:
                import google.generativeai as genai
                api_key = os.environ.get("GOOGLE_API_KEY")
                if api_key:
                    genai.configure(api_key=api_key)
                    self.gemini_client = genai.GenerativeModel('gemini-pro-vision')
                    logger.info("Gemini Pro Vision client initialized successfully.")
                else:
                    logger.warning("GOOGLE_API_KEY not found in environment variables.")
                    logger.warning("Will fall back to base OCR extractor or Vision API.")
            except (ImportError, Exception) as e:
                logger.warning(f"Failed to initialize Gemini Pro Vision client: {e}")
                logger.warning("Will fall back to base OCR extractor or Vision API.")
    
    def extract(self, image: Union[Path, str, Image.Image]) -> str:
        """
        Extract text from an image using the best available method.
        
        Args:
            image: Path to the image or PIL Image object
        
        Returns:
            Extracted text from the image
        """
        # Try Gemini Pro Vision first if available
        if self.use_gemini and self.gemini_client:
            try:
                result = self._extract_gemini(image)
                if result:
                    return result
            except Exception as e:
                logger.error(f"Error using Gemini Pro Vision: {e}")
        
        # Try Google Cloud Vision API if available
        if self.use_vision_api and self.vision_client:
            try:
                result = self._extract_vision_api(image)
                if result:
                    return result
            except Exception as e:
                logger.error(f"Error using Google Cloud Vision API: {e}")
        
        # Fall back to base OCR extractor
        logger.info("Falling back to base OCR extractor.")
        return self.base_extractor.extract(image)
    
    def _extract_gemini(self, image: Union[Path, str, Image.Image]) -> Optional[str]:
        """
        Extract text from an image using Gemini Pro Vision.
        
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
    
    def _extract_vision_api(self, image: Union[Path, str, Image.Image]) -> Optional[str]:
        """
        Extract text from an image using Google Cloud Vision API.
        
        Args:
            image: Path to the image or PIL Image object
        
        Returns:
            Extracted text from the image or None if extraction failed
        """
        if not self.vision_client:
            return None
        
        from google.cloud import vision
        
        # Convert image to bytes if it's a PIL Image
        if isinstance(image, Image.Image):
            import io
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            content = img_byte_arr.getvalue()
        # Load image from path if it's a path
        elif isinstance(image, (str, Path)):
            with open(image, 'rb') as image_file:
                content = image_file.read()
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")
        
        # Create image object
        vision_image = vision.Image(content=content)
        
        # Perform text detection
        response = self.vision_client.text_detection(image=vision_image)
        
        # Extract text from response
        if response and response.text_annotations:
            return response.text_annotations[0].description
        
        return None
    
    def extract_dir(self, image_dir: Path) -> dict:
        """
        Extract text from all images in a directory.
        
        Args:
            image_dir: Path to the directory containing images
        
        Returns:
            Dictionary mapping image names to extracted text
        """
        if not os.path.isdir(image_dir):
            logger.warning(f"Not a valid dir: {image_dir}")
            return {}
        
        result = {}
        for image_path in os.listdir(image_dir):
            if image_path.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
                image_name = os.path.splitext(image_path)[0]
                full_path = os.path.join(image_dir, image_path)
                result[image_name] = self.extract(full_path)
        
        return result