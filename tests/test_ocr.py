"""
Tests for the OCR extraction functionality.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extraction.ocr import OCRExtractor


class TestOCRExtractor(unittest.TestCase):
    """Test cases for the OCRExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for easyocr.Reader
        self.mock_reader = MagicMock()
        self.patcher = patch('easyocr.Reader', return_value=self.mock_reader)
        self.patcher.start()
        
        # Create OCRExtractor instance
        self.ocr = OCRExtractor(check_dict=False)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()
    
    def test_extract_easy_ocr(self):
        """Test the _extract_easy_ocr method."""
        # Mock the readtext method to return some text
        self.mock_reader.readtext.return_value = ["Hello", "World"]
        
        # Create a mock image path
        mock_image_path = MagicMock(spec=Path)
        
        # Test the method
        result = self.ocr._extract_easy_ocr(mock_image_path)
        
        # Verify the result
        self.assertEqual(result, "Hello World")
        
        # Verify the mock was called correctly
        self.mock_reader.readtext.assert_called_once()
    
    def test_extract(self):
        """Test the extract method."""
        # Mock the _extract_easy_ocr method to return some text
        self.ocr._extract_easy_ocr = MagicMock(return_value="Hello World")
        
        # Create a mock image path
        mock_image_path = MagicMock(spec=Path)
        
        # Test the method
        result = self.ocr.extract(mock_image_path)
        
        # Verify the result
        self.assertEqual(result, "hello world")
        
        # Verify the mock was called correctly
        self.ocr._extract_easy_ocr.assert_called_once_with(mock_image_path)


if __name__ == '__main__':
    unittest.main()