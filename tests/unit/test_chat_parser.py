"""
Unit tests for chat_parser module
Tests ChatMessage, Conversation, and ChatParser classes
"""

import pytest
import json
import os
import tempfile
from datetime import datetime
from unittest.mock import patch, mock_open

# Import the modules to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from chat_parser import ChatMessage, Conversation, ChatParser


class TestChatMessage:
    """Test the ChatMessage class"""
    
    def test_chat_message_creation_valid_data(self):
        """Test creating a ChatMessage with valid data"""
        message_data = {
            'id': 'msg-123',
            'author': {'role': 'user'},
            'create_time': 1640995200,
            'content': {
                'content_type': 'text',
                'parts': ['Hello, how are you today?']
            }
        }
        
        message = ChatMessage(message_data)
        
        assert message.id == 'msg-123'
        assert message.role == 'user'
        assert message.create_time == 1640995200
        assert message.content == 'Hello, how are you today?'
        assert isinstance(message.timestamp, datetime)
    
    def test_chat_message_creation_missing_data(self):
        """Test ChatMessage handles missing data gracefully"""
        message_data = {}
        
        message = ChatMessage(message_data)
        
        assert message.id == ''
        assert message.role == 'unknown'
        assert message.create_time == 0
        assert message.content == ''
    
    def test_chat_message_multiple_content_parts(self):
        """Test ChatMessage with multiple content parts"""
        message_data = {
            'id': 'msg-456',
            'author': {'role': 'assistant'},
            'create_time': 1640995300,
            'content': {
                'content_type': 'text',
                'parts': ['First part. ', 'Second part.', ' Third part.']
            }
        }
        
        message = ChatMessage(message_data)
        
        assert message.content == 'First part.  Second part.  Third part.'
        assert message.role == 'assistant'
    
    def test_chat_message_non_text_content(self):
        """Test ChatMessage with non-text content"""
        message_data = {
            'id': 'msg-789',
            'author': {'role': 'user'},
            'create_time': 1640995400,
            'content': {
                'content_type': 'image',
                'parts': ['image_data']
            }
        }
        
        message = ChatMessage(message_data)
        
        assert message.content == ''  # Should be empty for non-text content
    
    def test_chat_message_string_representation(self):
        """Test ChatMessage string representation"""
        message_data = {
            'id': 'msg-123',
            'author': {'role': 'user'},
            'create_time': 1640995200,
            'content': {
                'content_type': 'text',
                'parts': ['This is a very long message that should be truncated when displayed as a string representation because it exceeds the character limit']
            }
        }
        
        message = ChatMessage(message_data)
        str_repr = str(message)
        
        assert 'user:' in str_repr
        assert len(str_repr) <= 110  # Should be truncated


class TestConversation:
    """Test the Conversation class"""
    
    def test_conversation_creation_valid_data(self):
        """Test creating a Conversation with valid data"""
        conversation_data = {
            'id': 'conv-123',
            'title': 'Test Conversation',
            'create_time': 1640995200,
            'update_time': 1640995800,
            'mapping': {
                'msg-1': {
                    'message': {
                        'id': 'msg-1',
                        'author': {'role': 'user'},
                        'create_time': 1640995200,
                        'content': {
                            'content_type': 'text',
                            'parts': ['Hello']
                        }
                    }
                },
                'msg-2': {
                    'message': {
                        'id': 'msg-2',
                        'author': {'role': 'assistant'},
                        'create_time': 1640995300,
                        'content': {
                            'content_type': 'text',
                            'parts': ['Hi there!']
                        }
                    }
                }
            }
        }
        
        conversation = Conversation(conversation_data)
        
        assert conversation.id == 'conv-123'
        assert conversation.title == 'Test Conversation'
        assert conversation.create_time == 1640995200
        assert conversation.update_time == 1640995800
        assert len(conversation.messages) == 2
        assert isinstance(conversation.create_date, datetime)
        assert isinstance(conversation.update_date, datetime)
    
    def test_conversation_empty_mapping(self):
        """Test Conversation with empty mapping"""
        conversation_data = {
            'id': 'conv-empty',
            'title': 'Empty Conversation',
            'create_time': 1640995200,
            'update_time': 1640995200,
            'mapping': {}
        }
        
        conversation = Conversation(conversation_data)
        
        assert len(conversation.messages) == 0
        assert conversation.title == 'Empty Conversation'
    
    def test_conversation_messages_sorted_by_time(self):
        """Test that messages are sorted by create_time"""
        conversation_data = {
            'id': 'conv-sorted',
            'title': 'Sorted Conversation',
            'create_time': 1640995200,
            'update_time': 1640995800,
            'mapping': {
                'msg-3': {
                    'message': {
                        'id': 'msg-3',
                        'author': {'role': 'user'},
                        'create_time': 1640995400,  # Latest
                        'content': {
                            'content_type': 'text',
                            'parts': ['Third message']
                        }
                    }
                },
                'msg-1': {
                    'message': {
                        'id': 'msg-1',
                        'author': {'role': 'user'},
                        'create_time': 1640995200,  # Earliest
                        'content': {
                            'content_type': 'text',
                            'parts': ['First message']
                        }
                    }
                },
                'msg-2': {
                    'message': {
                        'id': 'msg-2',
                        'author': {'role': 'assistant'},
                        'create_time': 1640995300,  # Middle
                        'content': {
                            'content_type': 'text',
                            'parts': ['Second message']
                        }
                    }
                }
            }
        }
        
        conversation = Conversation(conversation_data)
        
        assert len(conversation.messages) == 3
        assert conversation.messages[0].content == 'First message'
        assert conversation.messages[1].content == 'Second message'
        assert conversation.messages[2].content == 'Third message'
    
    def test_conversation_get_full_text(self):
        """Test get_full_text method"""
        conversation_data = {
            'id': 'conv-text',
            'title': 'Text Test',
            'create_time': 1640995200,
            'update_time': 1640995800,
            'mapping': {
                'msg-1': {
                    'message': {
                        'id': 'msg-1',
                        'author': {'role': 'user'},
                        'create_time': 1640995200,
                        'content': {
                            'content_type': 'text',
                            'parts': ['User message']
                        }
                    }
                },
                'msg-2': {
                    'message': {
                        'id': 'msg-2',
                        'author': {'role': 'assistant'},
                        'create_time': 1640995300,
                        'content': {
                            'content_type': 'text',
                            'parts': ['Assistant response']
                        }
                    }
                }
            }
        }
        
        conversation = Conversation(conversation_data)
        full_text = conversation.get_full_text()
        
        assert 'USER: User message' in full_text
        assert 'ASSISTANT: Assistant response' in full_text
        assert full_text.count('\n\n') == 1  # Two messages separated by double newline
    
    def test_conversation_get_user_messages_only(self):
        """Test get_user_messages_only method"""
        conversation_data = {
            'id': 'conv-user-only',
            'title': 'User Only Test',
            'create_time': 1640995200,
            'update_time': 1640995800,
            'mapping': {
                'msg-1': {
                    'message': {
                        'id': 'msg-1',
                        'author': {'role': 'user'},
                        'create_time': 1640995200,
                        'content': {
                            'content_type': 'text',
                            'parts': ['First user message']
                        }
                    }
                },
                'msg-2': {
                    'message': {
                        'id': 'msg-2',
                        'author': {'role': 'assistant'},
                        'create_time': 1640995300,
                        'content': {
                            'content_type': 'text',
                            'parts': ['Assistant response']
                        }
                    }
                },
                'msg-3': {
                    'message': {
                        'id': 'msg-3',
                        'author': {'role': 'user'},
                        'create_time': 1640995400,
                        'content': {
                            'content_type': 'text',
                            'parts': ['Second user message']
                        }
                    }
                }
            }
        }
        
        conversation = Conversation(conversation_data)
        user_text = conversation.get_user_messages_only()
        
        assert 'First user message' in user_text
        assert 'Second user message' in user_text
        assert 'Assistant response' not in user_text
    
    def test_conversation_string_representation(self):
        """Test Conversation string representation"""
        conversation_data = {
            'id': 'conv-str',
            'title': 'String Test',
            'create_time': 1640995200,
            'update_time': 1640995800,
            'mapping': {
                'msg-1': {
                    'message': {
                        'id': 'msg-1',
                        'author': {'role': 'user'},
                        'create_time': 1640995200,
                        'content': {
                            'content_type': 'text',
                            'parts': ['Test message']
                        }
                    }
                }
            }
        }
        
        conversation = Conversation(conversation_data)
        str_repr = str(conversation)
        
        assert 'String Test' in str_repr
        assert '1 messages' in str_repr


class TestChatParser:
    """Test the ChatParser class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = ChatParser()
        self.test_data = [
            {
                'id': 'conv-1',
                'title': 'Test Conversation 1',
                'create_time': 1640995200,
                'update_time': 1640995800,
                'mapping': {
                    'msg-1': {
                        'message': {
                            'id': 'msg-1',
                            'author': {'role': 'user'},
                            'create_time': 1640995200,
                            'content': {
                                'content_type': 'text',
                                'parts': ['Hello world']
                            }
                        }
                    }
                }
            }
        ]
    
    def test_chat_parser_initialization(self):
        """Test ChatParser initialization"""
        parser = ChatParser()
        assert parser.conversations == []
    
    def test_load_conversations_success(self):
        """Test successful conversation loading"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_data, f)
            temp_path = f.name
        
        try:
            result = self.parser.load_conversations(temp_path)
            
            assert result is True
            assert len(self.parser.conversations) == 1
            assert self.parser.conversations[0].title == 'Test Conversation 1'
        finally:
            os.unlink(temp_path)
    
    def test_load_conversations_file_not_found(self):
        """Test loading non-existent file"""
        result = self.parser.load_conversations('nonexistent_file.json')
        
        assert result is False
        assert len(self.parser.conversations) == 0
    
    def test_load_conversations_invalid_json(self):
        """Test loading invalid JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('invalid json content {')
            temp_path = f.name
        
        try:
            result = self.parser.load_conversations(temp_path)
            
            assert result is False
            assert len(self.parser.conversations) == 0
        finally:
            os.unlink(temp_path)
    
    def test_load_conversations_different_formats(self):
        """Test loading different conversation formats"""
        # Test single conversation format
        single_conv = self.test_data[0]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(single_conv, f)
            temp_path = f.name
        
        try:
            result = self.parser.load_conversations(temp_path)
            
            assert result is True
            assert len(self.parser.conversations) == 1
        finally:
            os.unlink(temp_path)
        
        # Test conversations wrapper format
        wrapped_format = {'conversations': self.test_data}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(wrapped_format, f)
            temp_path = f.name
        
        try:
            parser2 = ChatParser()
            result = parser2.load_conversations(temp_path)
            
            assert result is True
            assert len(parser2.conversations) == 1
        finally:
            os.unlink(temp_path)
    
    def test_get_conversations_by_date_range(self):
        """Test filtering conversations by date range"""
        # Set up test data with different dates
        self.parser.conversations = [
            Conversation({
                'id': 'conv-1',
                'title': 'Early Conversation',
                'create_time': 1640995200,  # 2022-01-01
                'update_time': 1640995200,
                'mapping': {}
            }),
            Conversation({
                'id': 'conv-2',
                'title': 'Middle Conversation',
                'create_time': 1641254400,  # 2022-01-04
                'update_time': 1641254400,
                'mapping': {}
            }),
            Conversation({
                'id': 'conv-3',
                'title': 'Late Conversation',
                'create_time': 1641513600,  # 2022-01-07
                'update_time': 1641513600,
                'mapping': {}
            })
        ]
        
        # Test filtering with start date only
        start_date = datetime(2022, 1, 3)
        filtered = self.parser.get_conversations_by_date_range(start_date=start_date)
        
        assert len(filtered) == 2
        assert all(conv.create_date >= start_date for conv in filtered)
        
        # Test filtering with end date only
        end_date = datetime(2022, 1, 5)
        filtered = self.parser.get_conversations_by_date_range(end_date=end_date)
        
        assert len(filtered) == 2
        assert all(conv.create_date <= end_date for conv in filtered)
        
        # Test filtering with both dates
        start_date = datetime(2022, 1, 2)
        end_date = datetime(2022, 1, 6)
        filtered = self.parser.get_conversations_by_date_range(start_date, end_date)
        
        assert len(filtered) == 1
        assert filtered[0].title == 'Middle Conversation'
    
    def test_search_conversations(self):
        """Test conversation search functionality"""
        # Set up test data
        self.parser.conversations = [
            Conversation({
                'id': 'conv-1',
                'title': 'Anxiety and Stress',
                'create_time': 1640995200,
                'update_time': 1640995200,
                'mapping': {
                    'msg-1': {
                        'message': {
                            'id': 'msg-1',
                            'author': {'role': 'user'},
                            'create_time': 1640995200,
                            'content': {
                                'content_type': 'text',
                                'parts': ['I am feeling anxious about my upcoming presentation']
                            }
                        }
                    }
                }
            }),
            Conversation({
                'id': 'conv-2',
                'title': 'Meditation Practice',
                'create_time': 1641081600,
                'update_time': 1641081600,
                'mapping': {
                    'msg-2': {
                        'message': {
                            'id': 'msg-2',
                            'author': {'role': 'user'},
                            'create_time': 1641081600,
                            'content': {
                                'content_type': 'text',
                                'parts': ['How can I improve my meditation routine?']
                            }
                        }
                    }
                }
            })
        ]
        
        # Add some tags for testing
        self.parser.conversations[0].tags = ['anxiety', 'stress', 'work']
        self.parser.conversations[1].tags = ['meditation', 'mindfulness']
        
        # Test title search
        results = self.parser.search_conversations('anxiety')
        assert len(results) == 1
        assert results[0].title == 'Anxiety and Stress'
        
        # Test content search
        results = self.parser.search_conversations('presentation')
        assert len(results) == 1
        assert results[0].title == 'Anxiety and Stress'
        
        # Test tag search
        results = self.parser.search_conversations('meditation')
        assert len(results) == 1
        assert results[0].title == 'Meditation Practice'
        
        # Test case insensitive search
        results = self.parser.search_conversations('ANXIETY')
        assert len(results) == 1
        
        # Test search with no results
        results = self.parser.search_conversations('nonexistent')
        assert len(results) == 0
    
    def test_get_stats(self):
        """Test conversation statistics"""
        # Test empty parser
        stats = self.parser.get_stats()
        assert stats == {}
        
        # Set up test data
        self.parser.conversations = [
            Conversation({
                'id': 'conv-1',
                'title': 'First Conversation',
                'create_time': 1640995200,  # 2022-01-01
                'update_time': 1640995200,
                'mapping': {
                    'msg-1': {
                        'message': {
                            'id': 'msg-1',
                            'author': {'role': 'user'},
                            'create_time': 1640995200,
                            'content': {
                                'content_type': 'text',
                                'parts': ['Hello']
                            }
                        }
                    },
                    'msg-2': {
                        'message': {
                            'id': 'msg-2',
                            'author': {'role': 'assistant'},
                            'create_time': 1640995300,
                            'content': {
                                'content_type': 'text',
                                'parts': ['Hi there!']
                            }
                        }
                    }
                }
            }),
            Conversation({
                'id': 'conv-2',
                'title': 'Second Conversation',
                'create_time': 1641340800,  # 2022-01-05
                'update_time': 1641340800,
                'mapping': {
                    'msg-3': {
                        'message': {
                            'id': 'msg-3',
                            'author': {'role': 'user'},
                            'create_time': 1641340800,
                            'content': {
                                'content_type': 'text',
                                'parts': ['Another conversation']
                            }
                        }
                    }
                }
            })
        ]
        
        stats = self.parser.get_stats()
        
        assert stats['total_conversations'] == 2
        assert stats['total_messages'] == 3
        assert stats['total_characters'] > 0
        assert isinstance(stats['earliest_date'], datetime)
        assert isinstance(stats['latest_date'], datetime)
        assert stats['date_range_days'] == 4  # 5 days difference


@pytest.mark.integration
class TestChatParserIntegration:
    """Integration tests for ChatParser with real fixture data"""
    
    def test_load_fixture_data(self):
        """Test loading the actual test fixture data"""
        parser = ChatParser()
        fixture_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'sample_conversations.json')
        
        result = parser.load_conversations(fixture_path)
        
        assert result is True
        assert len(parser.conversations) == 2  # Empty conversation should be filtered out
        
        # Verify specific conversation data
        anxiety_conv = next((c for c in parser.conversations if 'Anxiety' in c.title), None)
        assert anxiety_conv is not None
        assert len(anxiety_conv.messages) == 3
        
        meditation_conv = next((c for c in parser.conversations if 'Meditation' in c.title), None)
        assert meditation_conv is not None
        assert len(meditation_conv.messages) == 2
    
    def test_search_fixture_data(self):
        """Test searching through fixture data"""
        parser = ChatParser()
        fixture_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'sample_conversations.json')
        parser.load_conversations(fixture_path)
        
        # Test search functionality
        anxiety_results = parser.search_conversations('anxiety')
        assert len(anxiety_results) >= 1
        
        meditation_results = parser.search_conversations('meditation')
        assert len(meditation_results) >= 1
        
        spiritual_results = parser.search_conversations('spiritual')
        assert len(spiritual_results) >= 1