"""
Unit tests for analytics_engine module
Tests AnalyticsEngine class with mocked dependencies
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the modules to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from analytics_engine import AnalyticsEngine, AnalyticsData
from chat_parser import Conversation


class TestAnalyticsEngine:
    """Test the AnalyticsEngine class"""
    
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
    
    def test_analytics_engine_initialization_success(self):
        """Test successful analytics engine initialization"""
        engine = AnalyticsEngine(self.config_path)
        
        assert engine.config is not None
        # The config should have analytics section (either from file or default)
        assert 'analytics' in engine.config or 'openai_api_key' in engine.config
        assert engine.cache_dir == 'data/analytics_cache'
    
    def test_analytics_engine_initialization_no_config(self):
        """Test analytics engine initialization with missing config file"""
        engine = AnalyticsEngine('nonexistent_config.json')
        
        # Should use default config
        assert engine.config is not None
        assert 'analytics' in engine.config
    
    def test_analytics_engine_cache_directory_creation(self):
        """Test that cache directory is created"""
        with patch('os.makedirs') as mock_makedirs:
            AnalyticsEngine(self.config_path)
            
            mock_makedirs.assert_called_with('data/analytics_cache', exist_ok=True)
    
    def test_analyze_conversations_basic_stats(self):
        """Test basic conversation statistics calculation"""
        engine = AnalyticsEngine(self.config_path)
        
        # Create test conversations
        conv1 = Conversation(self.test_conversation_data)
        conv2_data = self.test_conversation_data.copy()
        conv2_data['id'] = 'test-conv-2'
        conv2_data['create_time'] = 1641081600
        conv2 = Conversation(conv2_data)
        
        conversations = [conv1, conv2]
        
        # Mock cache to ensure fresh analysis
        with patch.object(engine, '_load_analytics_from_cache', return_value=None), \
             patch.object(engine, '_save_analytics_to_cache'):
            
            analytics_data = engine.analyze_conversations(conversations)
            
            assert analytics_data.conversation_count == 2
            assert analytics_data.total_messages == 4  # 2 messages per conversation
            assert len(analytics_data.date_range) == 2
            assert analytics_data.top_tags == []  # No tags yet
    
    def test_analyze_conversations_with_tags(self):
        """Test analytics with conversations that have tags"""
        engine = AnalyticsEngine(self.config_path)
        
        # Create conversations with tags
        conv1 = Conversation(self.test_conversation_data)
        conv1.tags = ['anxiety', 'career', 'stress']
        
        conv2_data = self.test_conversation_data.copy()
        conv2_data['id'] = 'test-conv-2'
        conv2 = Conversation(conv2_data)
        conv2.tags = ['anxiety', 'meditation', 'healing']
        
        conversations = [conv1, conv2]
        
        # Mock cache and sentiment analysis
        with patch.object(engine, '_load_analytics_from_cache', return_value=None), \
             patch.object(engine, '_save_analytics_to_cache'), \
             patch.object(engine, '_analyze_sentiment_trends', return_value={}), \
             patch.object(engine, '_analyze_emotional_patterns', return_value={}):
            
            analytics_data = engine.analyze_conversations(conversations)
            
            assert analytics_data.conversation_count == 2
            assert len(analytics_data.top_tags) > 0
            assert any(tag == 'anxiety' for tag, count in analytics_data.top_tags)
    
    def test_analyze_conversations_uses_cache(self):
        """Test that analytics uses cached results when available"""
        engine = AnalyticsEngine(self.config_path)
        
        # Create test conversations
        conv1 = Conversation(self.test_conversation_data)
        conversations = [conv1]
        
        # Mock cached data
        cached_data = AnalyticsData(
            conversation_count=1,
            total_messages=2,
            date_range=(datetime.now(), datetime.now()),
            top_tags=[('anxiety', 1)],
            sentiment_trends={},
            emotional_patterns={},
            growth_metrics={},
            engagement_stats={}
        )
        
        with patch.object(engine, '_load_analytics_from_cache', return_value=cached_data):
            analytics_data = engine.analyze_conversations(conversations)
            
            assert analytics_data.conversation_count == 1
            assert analytics_data.top_tags == [('anxiety', 1)]
    
    def test_export_analytics_data_csv(self):
        """Test CSV export of analytics data"""
        engine = AnalyticsEngine(self.config_path)
        
        # Create test analytics data
        analytics_data = AnalyticsData(
            conversation_count=2,
            total_messages=4,
            date_range=(datetime.now(), datetime.now()),
            top_tags=[('anxiety', 2), ('career', 1)],
            sentiment_trends={},
            emotional_patterns={},
            growth_metrics={'self_awareness': 0.75},
            engagement_stats={'avg_messages': 2.0}
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            result_path = engine.export_analytics_data(analytics_data, temp_path, 'csv')
            
            assert result_path == temp_path
            assert os.path.exists(result_path)
            
            # Verify CSV content
            with open(result_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert 'conversation_count' in content
            assert '2' in content
            assert 'anxiety' in content
            
        finally:
            os.unlink(temp_path)
    
    def test_export_analytics_data_json(self):
        """Test JSON export of analytics data"""
        engine = AnalyticsEngine(self.config_path)
        
        # Create test analytics data
        analytics_data = AnalyticsData(
            conversation_count=1,
            total_messages=2,
            date_range=(datetime.now(), datetime.now()),
            top_tags=[('anxiety', 1)],
            sentiment_trends={},
            emotional_patterns={},
            growth_metrics={'self_awareness': 0.5},
            engagement_stats={'avg_messages': 2.0}
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            result_path = engine.export_analytics_data(analytics_data, temp_path, 'json')
            
            assert result_path == temp_path
            assert os.path.exists(result_path)
            
            # Verify JSON content
            with open(result_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert data['conversation_count'] == 1
            assert data['total_messages'] == 2
            assert len(data['top_tags']) == 1
            
        finally:
            os.unlink(temp_path)


@pytest.mark.analytics
class TestAnalyticsEngineIntegration:
    """Integration tests for analytics engine"""
    
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
    
    def test_full_analytics_workflow(self):
        """Test complete analytics workflow"""
        engine = AnalyticsEngine(self.config_path)
        
        # Create test conversations
        conv1 = Conversation(self.test_conversation_data)
        conv1.tags = ['anxiety', 'career']
        conv1.summary = 'Discussion about career anxiety'
        
        conv2_data = self.test_conversation_data.copy()
        conv2_data['id'] = 'test-conv-2'
        conv2 = Conversation(conv2_data)
        conv2.tags = ['meditation', 'healing']
        conv2.summary = 'Discussion about meditation practice'
        
        conversations = [conv1, conv2]
        
        # Mock sentiment analysis to avoid TextBlob dependency
        with patch.object(engine, '_analyze_sentiment_trends', return_value={}), \
             patch.object(engine, '_analyze_emotional_patterns', return_value={}):
            
            analytics_data = engine.analyze_conversations(conversations)
            
            assert analytics_data.conversation_count == 2
            assert analytics_data.total_messages == 4
            assert len(analytics_data.top_tags) >= 2  # anxiety, career, meditation, healing 