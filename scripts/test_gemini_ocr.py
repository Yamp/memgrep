#!/usr/bin/env python3
"""
Script to test the Gemini OCR implementation.
"""

import os
import sys
from pathlib import Path
import argparse
import dotenv

# Load environment variables from .env.test file
dotenv.load_dotenv(".env.test")

# Add the project root to the Python path
sys.path.extend([".", "..", "../.."])

from loguru import logger
import google.generativeai as genai
from PIL import Image

# Set the Google API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyDpe5frmUP3wgI-5QLvJYfVBLls6u7jMYM"


def test_gemini_vision():
    """Test the Gemini Vision API."""
    try:
        # Configure the Gemini API
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        
        # Create a model (using the newer Gemini 1.5 Flash model)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create a test image with text
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a blank image
        img = Image.new('RGB', (500, 200), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        
        # Add text to the image
        try:
            font = ImageFont.truetype("Arial", 36)
        except IOError:
            font = ImageFont.load_default()
        
        d.text((50, 50), "Hello, Gemini OCR!", fill=(0, 0, 0), font=font)
        d.text((50, 100), "This is a test image.", fill=(0, 0, 0), font=font)
        
        # Save the image
        img_path = "test_ocr_image.png"
        img.save(img_path)
        
        logger.info(f"Created test image at {img_path}")
        
        # Generate prompt for Gemini
        prompt = "Extract all text visible in this image. Return only the text, no additional commentary."
        
        # Generate response from Gemini
        response = model.generate_content([prompt, Image.open(img_path)])
        
        # Extract text from response
        if response and response.text:
            extracted_text = response.text.strip()
            logger.info(f"Extracted text: {extracted_text}")
            return True
        else:
            logger.error("No text extracted from the image")
            return False
    except Exception as e:
        logger.error(f"Error testing Gemini Vision API: {e}")
        return False


def main():
    """Main function to test the Gemini OCR implementation."""
    logger.info("Testing the Gemini OCR implementation...")
    
    # Test Gemini Vision API
    if test_gemini_vision():
        logger.info("✅ Gemini Vision API test passed")
    else:
        logger.error("❌ Gemini Vision API test failed")


if __name__ == "__main__":
    main()