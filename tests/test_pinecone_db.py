"""
Tests for the Pinecone database implementation.
"""

import os
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.pinecone_db import PineconeDB
from data.redis_db import ImageRecord, SearchRequest


class TestPineconeDB(unittest.TestCase):
    """Test cases for the PineconeDB class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mocks for Pinecone
        self.mock_index = MagicMock()
        self.mock_pinecone = MagicMock()
        self.mock_pinecone.list_indexes.return_value = []
        self.mock_pinecone.Index.return_value = self.mock_index
        self.patcher = patch('pinecone', self.mock_pinecone)
        self.patcher.start()
        
        # Set environment variables for Pinecone
        os.environ['PINECONE_API_KEY'] = 'test_api_key'
        os.environ['PINECONE_ENVIRONMENT'] = 'test_environment'
        os.environ['PINECONE_INDEX'] = 'test_index'
        
        # Create PineconeDB instance
        self.db = PineconeDB()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()
        
        # Remove environment variables
        for var in ['PINECONE_API_KEY', 'PINECONE_ENVIRONMENT', 'PINECONE_INDEX']:
            if var in os.environ:
                del os.environ[var]
    
    def test_create_db(self):
        """Test the create_db method."""
        # Mock the Pinecone list_indexes method to return an empty list
        self.mock_pinecone.list_indexes.return_value = []
        
        # Test the method
        result = self.db.create_db()
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the mocks were called correctly
        self.mock_pinecone.init.assert_called_once()
        self.mock_pinecone.list_indexes.assert_called_once()
        self.mock_pinecone.create_index.assert_called_once()
    
    def test_create_db_existing(self):
        """Test the create_db method when the index already exists."""
        # Mock the Pinecone list_indexes method to return the index
        self.mock_pinecone.list_indexes.return_value = ['test_index']
        
        # Test the method
        result = self.db.create_db()
        
        # Verify the result
        self.assertFalse(result)
        
        # Verify the mocks were called correctly
        self.mock_pinecone.init.assert_called_once()
        self.mock_pinecone.list_indexes.assert_called_once()
        self.mock_pinecone.create_index.assert_not_called()
    
    def test_add_record(self):
        """Test the add_record method."""
        # Create a test record
        record = ImageRecord(
            id=1,
            message_id=123,
            chat="test_chat",
            sender_id=456,
            dt=datetime.now(),
            msg_text="Test message",
            ocr_rus="Тестовое сообщение",
            ocr_eng="Test message",
            semantic_data="A test message",
            comments=[],
            reactions=[],
            data_link="http://example.com/data",
            post_link="http://example.com/post",
        )
        
        # Test the method
        result = self.db.add_record(record)
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the mock was called correctly
        self.mock_index.upsert.assert_called_once()
    
    def test_search(self):
        """Test the search method."""
        # Create a test search request
        request = SearchRequest(
            query="test",
            max_results=5,
        )
        
        # Mock the Pinecone query method
        mock_match = MagicMock()
        mock_match.metadata = {
            "id": 1,
            "message_id": 123,
            "chat": "test_chat",
            "sender_id": 456,
            "dt": datetime.now().timestamp(),
            "msg_text": "Test message",
            "ocr_rus": "Тестовое сообщение",
            "ocr_eng": "Test message",
            "semantic_data": "A test message",
            "comments": "[]",
            "reactions": "[]",
            "data_link": "http://example.com/data",
            "post_link": "http://example.com/post",
        }
        mock_results = MagicMock()
        mock_results.matches = [mock_match]
        self.mock_index.query.return_value = mock_results
        
        # Test the method
        results = self.db.search(request)
        
        # Verify the results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, 1)
        self.assertEqual(results[0].message_id, 123)
        self.assertEqual(results[0].chat, "test_chat")
        
        # Verify the mock was called correctly
        self.mock_index.query.assert_called_once()


if __name__ == '__main__':
    unittest.main()