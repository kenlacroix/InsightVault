"""
Unit tests for summarizer module
Tests ConversationSummarizer class with mocked OpenAI API calls
"""

import pytest
import json
import os
import tempfile
import pickle
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the modules to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from summarizer import ConversationSummarizer
from chat_parser import Conversation


class TestConversationSummarizer:
    """Test the ConversationSummarizer class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'test_config.json')
        self.test_conversation_data = {
            'id': 'test-conv-1',
            'title': 'Anxiety Discussion',
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
                            'parts': ['I have been struggling with anxiety about my career path.']
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
                            'parts': ['Career anxiety is very common. What specific aspects worry you most?']
                        }
                    }
                }
            }
        }
    
    def test_summarizer_initialization_success(self):
        """Test successful summarizer initialization"""
        with patch('summarizer.OpenAI') as mock_openai:
            summarizer = ConversationSummarizer(self.config_path)
            
            assert summarizer.config['openai_api_key'] == 'test-api-key-12345'
            assert summarizer.config['model'] == 'gpt-4'
            mock_openai.assert_called_once_with(api_key='test-api-key-12345')
    
    def test_summarizer_initialization_no_config(self):
        """Test summarizer initialization with missing config file"""
        with pytest.raises(FileNotFoundError, match="Config file .* not found"):
            ConversationSummarizer('nonexistent_config.json')
    
    def test_summarizer_cache_directory_creation(self):
        """Test that cache directory is created"""
        with patch('summarizer.OpenAI'), \
             patch('os.makedirs') as mock_makedirs:
            ConversationSummarizer(self.config_path)
            
            mock_makedirs.assert_called_with('data/cache', exist_ok=True)
    
    @patch('summarizer.OpenAI')
    def test_summarize_conversation_success(self, mock_openai):
        """Test successful conversation summarization"""
        # Set up mock OpenAI response
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices[0].message.content = """
AUTO_TITLE: Career Anxiety and Planning
SUMMARY: A discussion about career-related anxiety and strategies for managing uncertainty about professional direction.
TAGS: anxiety, career, planning, uncertainty, professional-development
"""
        mock_client.chat.completions.create.return_value = mock_response
        
        summarizer = ConversationSummarizer(self.config_path)
        conversation = Conversation(self.test_conversation_data)
        
        # Mock cache to ensure fresh API call
        with patch.object(summarizer, '_load_from_cache', return_value=None), \
             patch.object(summarizer, '_save_to_cache') as mock_save_cache:
            
            result = summarizer.summarize_conversation(conversation)
            
            assert result is True
            assert conversation.auto_title == 'Career Anxiety and Planning'
            assert 'career-related anxiety' in conversation.summary
            assert 'anxiety' in conversation.tags
            assert 'career' in conversation.tags
            
            # Verify API was called
            mock_client.chat.completions.create.assert_called_once()
            
            # Verify caching
            mock_save_cache.assert_called_once()
    
    @patch('summarizer.OpenAI')
    def test_summarize_conversation_uses_cache(self, mock_openai):
        """Test that summarization uses cached results when available"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        summarizer = ConversationSummarizer(self.config_path)
        conversation = Conversation(self.test_conversation_data)
        
        # Mock cached data
        cached_data = {
            'summary': 'Cached summary about anxiety',
            'tags': ['anxiety', 'cached'],
            'auto_title': 'Cached Title',
            'generated_at': datetime.now().isoformat()
        }
        
        with patch.object(summarizer, '_load_from_cache', return_value=cached_data):
            result = summarizer.summarize_conversation(conversation)
            
            assert result is True
            assert conversation.summary == 'Cached summary about anxiety'
            assert conversation.auto_title == 'Cached Title'
            assert conversation.tags == ['anxiety', 'cached']
            
            # Verify API was NOT called
            mock_client.chat.completions.create.assert_not_called()
    
    @patch('summarizer.OpenAI')
    def test_summarize_conversation_force_refresh(self, mock_openai):
        """Test force refresh bypasses cache"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices[0].message.content = """
AUTO_TITLE: Fresh Analysis
SUMMARY: This is a fresh analysis bypassing cache.
TAGS: fresh, analysis, bypass
"""
        mock_client.chat.completions.create.return_value = mock_response
        
        summarizer = ConversationSummarizer(self.config_path)
        conversation = Conversation(self.test_conversation_data)
        
        # Mock cache to return something (should be ignored)
        cached_data = {'summary': 'Old cached data'}
        
        with patch.object(summarizer, '_load_from_cache', return_value=cached_data), \
             patch.object(summarizer, '_save_to_cache'):
            
            result = summarizer.summarize_conversation(conversation, force_refresh=True)
            
            assert result is True
            assert conversation.auto_title == 'Fresh Analysis'
            assert 'fresh analysis' in conversation.summary
            
            # Verify API was called despite cache
            mock_client.chat.completions.create.assert_called_once()
    
    @patch('summarizer.OpenAI')
    def test_summarize_conversation_handles_long_content(self, mock_openai):
        """Test handling of very long conversations"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices[0].message.content = """
AUTO_TITLE: Long Conversation Summary
SUMMARY: A summary of a very long conversation that was truncated.
TAGS: long, conversation, truncated
"""
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create a conversation with very long content
        long_content_data = self.test_conversation_data.copy()
        long_content_data['mapping']['msg-1']['message']['content']['parts'] = ['A' * 10000]  # Very long message
        
        summarizer = ConversationSummarizer(self.config_path)
        conversation = Conversation(long_content_data)
        
        with patch.object(summarizer, '_load_from_cache', return_value=None), \
             patch.object(summarizer, '_save_to_cache'):
            
            result = summarizer.summarize_conversation(conversation)
            
            assert result is True
            
            # Verify API was called with truncated content
            call_args = mock_client.chat.completions.create.call_args
            prompt = call_args[1]['messages'][1]['content']
            
            # Content should be truncated or user-only
            assert len(prompt) < 15000  # Should be much shorter than original
    
    @patch('summarizer.OpenAI')
    def test_summarize_conversation_api_error(self, mock_openai):
        """Test handling of API errors"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Mock API to raise an exception
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        summarizer = ConversationSummarizer(self.config_path)
        conversation = Conversation(self.test_conversation_data)
        
        with patch.object(summarizer, '_load_from_cache', return_value=None):
            result = summarizer.summarize_conversation(conversation)
            
            assert result is False
            # Conversation should remain unchanged
            assert conversation.summary == ''
            assert conversation.auto_title == ''
            assert conversation.tags == []
    
    def test_parse_summary_response_success(self):
        """Test successful parsing of GPT response"""
        with patch('summarizer.OpenAI'):
            summarizer = ConversationSummarizer(self.config_path)
            
            response_text = """
AUTO_TITLE: Mindfulness and Meditation
SUMMARY: A deep conversation about developing a consistent meditation practice and using mindfulness to manage daily stress and anxiety.
TAGS: meditation, mindfulness, stress, anxiety, daily-practice
"""
            
            result = summarizer._parse_summary_response(response_text)
            
            assert result['auto_title'] == 'Mindfulness and Meditation'
            assert 'meditation practice' in result['summary']
            assert 'meditation' in result['tags']
            assert 'mindfulness' in result['tags']
            assert len(result['tags']) == 5
    
    def test_parse_summary_response_fallback(self):
        """Test parsing fallback when response format is invalid"""
        with patch('summarizer.OpenAI'):
            summarizer = ConversationSummarizer(self.config_path)
            
            # Invalid response format
            response_text = "This is not the expected format"
            
            result = summarizer._parse_summary_response(response_text)
            
            assert result['auto_title'] == 'Personal Conversation'
            assert result['summary'] == 'A personal conversation covering various topics.'
            assert result['tags'] == ['personal', 'conversation']
    
    def test_parse_summary_response_partial_data(self):
        """Test parsing when only some fields are present"""
        with patch('summarizer.OpenAI'):
            summarizer = ConversationSummarizer(self.config_path)
            
            response_text = """
AUTO_TITLE: Partial Response
SUMMARY: Only title and summary provided.
"""
            
            result = summarizer._parse_summary_response(response_text)
            
            assert result['auto_title'] == 'Partial Response'
            assert 'Only title and summary' in result['summary']
            assert result['tags'] == ['personal', 'conversation']  # Fallback tags
    
    @patch('summarizer.OpenAI')
    def test_summarize_all_conversations(self, mock_openai):
        """Test batch summarization of multiple conversations"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Mock successful API responses
        mock_response1 = Mock()
        mock_response1.choices[0].message.content = """
AUTO_TITLE: First Conversation
SUMMARY: First summary
TAGS: first, test
"""
        
        mock_response2 = Mock()
        mock_response2.choices[0].message.content = """
AUTO_TITLE: Second Conversation  
SUMMARY: Second summary
TAGS: second, test
"""
        
        mock_client.chat.completions.create.side_effect = [mock_response1, mock_response2]
        
        summarizer = ConversationSummarizer(self.config_path)
        
        # Create multiple conversations
        conv1 = Conversation(self.test_conversation_data)
        conv2_data = self.test_conversation_data.copy()
        conv2_data['id'] = 'test-conv-2'
        conv2 = Conversation(conv2_data)
        
        conversations = [conv1, conv2]
        
        with patch.object(summarizer, '_load_from_cache', return_value=None), \
             patch.object(summarizer, '_save_to_cache'):
            
            results = summarizer.summarize_all_conversations(conversations)
            
            assert len(results) == 2
            assert results['test-conv-1'] is True
            assert results['test-conv-2'] is True
            
            # Verify both conversations were processed
            assert conv1.auto_title == 'First Conversation'
            assert conv2.auto_title == 'Second Conversation'
    
    def test_get_all_tags(self):
        """Test tag frequency counting"""
        with patch('summarizer.OpenAI'):
            summarizer = ConversationSummarizer(self.config_path)
            
            # Create conversations with tags
            conv1 = Conversation(self.test_conversation_data)
            conv1.tags = ['anxiety', 'career', 'stress']
            
            conv2_data = self.test_conversation_data.copy()
            conv2_data['id'] = 'test-conv-2'
            conv2 = Conversation(conv2_data)
            conv2.tags = ['anxiety', 'meditation', 'healing']
            
            conv3_data = self.test_conversation_data.copy()
            conv3_data['id'] = 'test-conv-3'
            conv3 = Conversation(conv3_data)
            conv3.tags = ['anxiety', 'therapy']
            
            conversations = [conv1, conv2, conv3]
            
            tag_counts = summarizer.get_all_tags(conversations)
            
            assert tag_counts['anxiety'] == 3  # Most frequent
            assert tag_counts['career'] == 1
            assert tag_counts['meditation'] == 1
            assert tag_counts['healing'] == 1
            assert tag_counts['therapy'] == 1
            
            # Should be sorted by frequency (anxiety first)
            tag_list = list(tag_counts.keys())
            assert tag_list[0] == 'anxiety'
    
    def test_export_summaries_success(self):
        """Test successful export of summaries to markdown"""
        with patch('summarizer.OpenAI'):
            summarizer = ConversationSummarizer(self.config_path)
            
            # Create conversations with summaries
            conv1 = Conversation(self.test_conversation_data)
            conv1.auto_title = 'Career Anxiety Discussion'
            conv1.summary = 'A conversation about career-related anxiety and planning.'
            conv1.tags = ['anxiety', 'career']
            
            conv2_data = self.test_conversation_data.copy()
            conv2_data['id'] = 'test-conv-2'
            conv2_data['create_time'] = 1641081600
            conv2 = Conversation(conv2_data)
            conv2.auto_title = 'Meditation Practice'
            conv2.summary = 'Discussion about developing a meditation routine.'
            conv2.tags = ['meditation', 'mindfulness']
            
            conversations = [conv1, conv2]
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                temp_path = f.name
            
            try:
                result = summarizer.export_summaries(conversations, temp_path)
                
                assert result is True
                
                # Verify file content
                with open(temp_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                assert 'InsightVault - Conversation Summaries' in content
                assert 'Career Anxiety Discussion' in content
                assert 'Meditation Practice' in content
                assert 'anxiety' in content
                assert 'meditation' in content
                assert 'Total Conversations: 2' in content
                
            finally:
                os.unlink(temp_path)
    
    def test_export_summaries_error_handling(self):
        """Test export error handling"""
        with patch('summarizer.OpenAI'):
            summarizer = ConversationSummarizer(self.config_path)
            
            conversations = [Conversation(self.test_conversation_data)]
            
            # Try to export to invalid path
            result = summarizer.export_summaries(conversations, '/invalid/path/summaries.md')
            
            assert result is False
    
    def test_cache_operations(self):
        """Test cache loading and saving operations"""
        with patch('summarizer.OpenAI'):
            summarizer = ConversationSummarizer(self.config_path)
            
            # Test saving to cache
            test_data = {
                'summary': 'Test summary',
                'tags': ['test', 'cache'],
                'auto_title': 'Test Title',
                'generated_at': datetime.now().isoformat()
            }
            
            with tempfile.TemporaryDirectory() as temp_dir:
                summarizer.cache_dir = temp_dir
                
                # Save to cache
                summarizer._save_to_cache('test-conv-123', 'summary', test_data)
                
                # Load from cache
                loaded_data = summarizer._load_from_cache('test-conv-123', 'summary')
                
                assert loaded_data is not None
                assert loaded_data['summary'] == 'Test summary'
                assert loaded_data['tags'] == ['test', 'cache']
                assert loaded_data['auto_title'] == 'Test Title'
    
    def test_cache_corruption_handling(self):
        """Test handling of corrupted cache files"""
        with patch('summarizer.OpenAI'):
            summarizer = ConversationSummarizer(self.config_path)
            
            with tempfile.TemporaryDirectory() as temp_dir:
                summarizer.cache_dir = temp_dir
                
                # Create a corrupted cache file
                cache_path = summarizer._get_cache_path('test-conv-corrupted', 'summary')
                with open(cache_path, 'w') as f:
                    f.write('corrupted data')
                
                # Should handle corruption gracefully
                result = summarizer._load_from_cache('test-conv-corrupted', 'summary')
                assert result is None


@pytest.mark.api
class TestConversationSummarizerAPI:
    """Tests that require actual API access (marked for optional running)"""
    
    def test_create_summary_prompt(self):
        """Test the prompt creation for GPT"""
        with patch('summarizer.OpenAI'):
            summarizer = ConversationSummarizer()
            
            conversation_text = "USER: I'm feeling anxious about work.\nASSISTANT: Can you tell me more about what's causing the anxiety?"
            original_title = "Work Anxiety"
            
            prompt = summarizer._create_summary_prompt(conversation_text, original_title)
            
            assert 'Work Anxiety' in prompt
            assert 'feeling anxious about work' in prompt
            assert 'AUTO_TITLE:' in prompt
            assert 'SUMMARY:' in prompt
            assert 'TAGS:' in prompt
            assert 'personal growth' in prompt.lower()