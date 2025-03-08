"""
Tests for the modern OCR extraction functionality.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extraction.modern_ocr import ModernOCRExtractor


class TestModernOCRExtractor(unittest.TestCase):
    """Test cases for the ModernOCRExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mocks for the base OCR extractor
        self.mock_base_extractor = MagicMock()
        self.patcher_base = patch('extraction.ocr.OCRExtractor', return_value=self.mock_base_extractor)
        self.patcher_base.start()
        
        # Create mocks for the Google Cloud Vision API
        self.mock_vision_client = MagicMock()
        self.patcher_vision = patch('google.cloud.vision.ImageAnnotatorClient', return_value=self.mock_vision_client)
        self.patcher_vision.start()
        
        # Create mocks for the Gemini Pro Vision API
        self.mock_gemini_client = MagicMock()
        self.mock_genai = MagicMock()
        self.mock_genai.GenerativeModel.return_value = self.mock_gemini_client
        self.patcher_genai = patch('google.generativeai', self.mock_genai)
        self.patcher_genai.start()
        
        # Set environment variable for Gemini API key
        os.environ['GOOGLE_API_KEY'] = 'test_api_key'
        
        # Create ModernOCRExtractor instance
        self.ocr = ModernOCRExtractor(use_gemini=True, use_vision_api=True, check_dict=False)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher_base.stop()
        self.patcher_vision.stop()
        self.patcher_genai.stop()
        
        # Remove environment variable
        if 'GOOGLE_API_KEY' in os.environ:
            del os.environ['GOOGLE_API_KEY']
    
    def test_extract_gemini(self):
        """Test the _extract_gemini method."""
        # Mock the Gemini client response
        mock_response = MagicMock()
        mock_response.text = "Hello World"
        self.mock_gemini_client.generate_content.return_value = mock_response
        
        # Create a mock image path
        mock_image_path = MagicMock(spec=Path)
        
        # Test the method
        result = self.ocr._extract_gemini(mock_image_path)
        
        # Verify the result
        self.assertEqual(result, "Hello World")
        
        # Verify the mock was called correctly
        self.mock_gemini_client.generate_content.assert_called_once()
    
    def test_extract_vision_api(self):
        """Test the _extract_vision_api method."""
        # Mock the Vision API response
        mock_text_annotation = MagicMock()
        mock_text_annotation.description = "Hello World"
        mock_response = MagicMock()
        mock_response.text_annotations = [mock_text_annotation]
        self.mock_vision_client.text_detection.return_value = mock_response
        
        # Create a mock image path
        mock_image_path = MagicMock(spec=Path)
        
        # Test the method
        result = self.ocr._extract_vision_api(mock_image_path)
        
        # Verify the result
        self.assertEqual(result, "Hello World")
        
        # Verify the mock was called correctly
        self.mock_vision_client.text_detection.assert_called_once()
    
    def test_extract_fallback(self):
        """Test the extract method with fallback to base extractor."""
        # Mock the Gemini and Vision API methods to fail
        self.ocr._extract_gemini = MagicMock(return_value=None)
        self.ocr._extract_vision_api = MagicMock(return_value=None)
        
        # Mock the base extractor
        self.mock_base_extractor.extract.return_value = "Hello World"
        
        # Create a mock image path
        mock_image_path = MagicMock(spec=Path)
        
        # Test the method
        result = self.ocr.extract(mock_image_path)
        
        # Verify the result
        self.assertEqual(result, "Hello World")
        
        # Verify the mocks were called correctly
        self.ocr._extract_gemini.assert_called_once_with(mock_image_path)
        self.ocr._extract_vision_api.assert_called_once_with(mock_image_path)
        self.mock_base_extractor.extract.assert_called_once_with(mock_image_path)


if __name__ == '__main__':
    unittest.main()