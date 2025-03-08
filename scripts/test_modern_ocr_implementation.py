#!/usr/bin/env python3
"""
Script to test the modern OCR implementation.
This script tests the ModernOCRExtractor class with the Gemini 1.5 Flash model.
"""

import os
import sys
from pathlib import Path
import dotenv

# Load environment variables from .env.test file
dotenv.load_dotenv(".env.test")

# Add the project root to the Python path
sys.path.extend([".", "..", "../.."])

from loguru import logger
from PIL import Image, ImageDraw, ImageFont

# Set the Google API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyDpe5frmUP3wgI-5QLvJYfVBLls6u7jMYM"


def create_test_image(text, filename="test_ocr_image.png"):
    """Create a test image with the given text."""
    # Create a blank image
    img = Image.new('RGB', (500, 200), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Add text to the image
    try:
        font = ImageFont.truetype("Arial", 36)
    except IOError:
        font = ImageFont.load_default()
    
    # Split text into lines
    lines = text.split('\n')
    y_position = 50
    for line in lines:
        d.text((50, y_position), line, fill=(0, 0, 0), font=font)
        y_position += 50
    
    # Save the image
    img.save(filename)
    logger.info(f"Created test image at {filename}")
    return filename


def test_modern_ocr():
    """Test the SimplifiedOCRExtractor class."""
    try:
        # Import the SimplifiedOCRExtractor class
        from scripts.simplified_ocr import SimplifiedOCRExtractor
        
        # Create a test image
        test_text = "Hello, Modern OCR!\nThis is a test image."
        image_path = create_test_image(test_text)
        
        # Create a SimplifiedOCRExtractor instance
        extractor = SimplifiedOCRExtractor()
        
        # Extract text from the image
        extracted_text = extractor.extract(image_path)
        
        # Check if the extracted text matches the original text
        if extracted_text:
            logger.info(f"Extracted text: {extracted_text}")
            if test_text.lower() in extracted_text.lower():
                logger.info("✅ Text extraction successful")
                return True
            else:
                logger.warning("⚠️ Extracted text doesn't match the original text")
                return False
        else:
            logger.error("❌ No text extracted from the image")
            return False
    except Exception as e:
        logger.error(f"Error testing SimplifiedOCRExtractor: {e}")
        return False


def main():
    """Main function to test the modern OCR implementation."""
    logger.info("Testing the modern OCR implementation...")
    
    # Test the ModernOCRExtractor class
    if test_modern_ocr():
        logger.info("✅ Modern OCR implementation test passed")
    else:
        logger.error("❌ Modern OCR implementation test failed")


if __name__ == "__main__":
    main()