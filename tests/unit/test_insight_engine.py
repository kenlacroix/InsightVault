"""
Unit tests for insight_engine module
Tests InsightEngine class with mocked OpenAI API calls
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch
from datetime import datetime

# Import the modules to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from insight_engine import InsightEngine, SAMPLE_QUESTIONS
from chat_parser import Conversation


class TestInsightEngine:
    """Test the InsightEngine class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'test_config.json')
        self.test_conversations = [
            Conversation({
                'id': 'conv-anxiety-1',
                'title': 'Managing Work Anxiety',
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
                                'parts': ['I have been struggling with work-related anxiety. It affects my performance and sleep.']
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
                                'parts': ['Work anxiety is very common. What specific aspects of work trigger your anxiety most?']
                            }
                        }
                    }
                }
            }),
            Conversation({
                'id': 'conv-meditation-1',
                'title': 'Developing Meditation Practice',
                'create_time': 1641081600,
                'update_time': 1641082200,
                'mapping': {
                    'msg-3': {
                        'message': {
                            'id': 'msg-3',
                            'author': {'role': 'user'},
                            'create_time': 1641081600,
                            'content': {
                                'content_type': 'text',
                                'parts': ['I want to develop a consistent meditation practice to help with stress and spiritual growth.']
                            }
                        }
                    }
                }
            }),
            Conversation({
                'id': 'conv-therapy-1',
                'title': 'Therapy Progress',
                'create_time': 1641168000,
                'update_time': 1641168600,
                'mapping': {
                    'msg-4': {
                        'message': {
                            'id': 'msg-4',
                            'author': {'role': 'user'},
                            'create_time': 1641168000,
                            'content': {
                                'content_type': 'text',
                                'parts': ['My therapist helped me understand my anxiety patterns. I am making progress.']
                            }
                        }
                    }
                }
            })
        ]
        
        # Add tags and summaries to conversations
        self.test_conversations[0].tags = ['anxiety', 'work', 'stress', 'performance']
        self.test_conversations[0].summary = 'Discussion about work-related anxiety and its impact'
        self.test_conversations[0].auto_title = 'Work Anxiety Management'
        
        self.test_conversations[1].tags = ['meditation', 'mindfulness', 'spiritual-growth', 'stress']
        self.test_conversations[1].summary = 'Exploring meditation practice for stress relief and spiritual development'
        self.test_conversations[1].auto_title = 'Building Meditation Practice'
        
        self.test_conversations[2].tags = ['therapy', 'healing', 'anxiety', 'progress']
        self.test_conversations[2].summary = 'Reflecting on therapy progress and anxiety pattern awareness'
        self.test_conversations[2].auto_title = 'Therapy Breakthrough'
    
    def test_insight_engine_initialization(self):
        """Test InsightEngine initialization"""
        with patch('insight_engine.OpenAI') as mock_openai:
            engine = InsightEngine(self.config_path)
            
            assert engine.config['openai_api_key'] == 'test-api-key-12345'
            assert engine.config['model'] == 'gpt-4'
            mock_openai.assert_called_once_with(api_key='test-api-key-12345')
    
    def test_find_relevant_conversations_keyword_matching(self):
        """Test finding relevant conversations by keyword matching"""
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            
            # Test anxiety-related query
            anxiety_query = "How has my relationship with anxiety evolved?"
            relevant = engine.find_relevant_conversations(anxiety_query, self.test_conversations)
            
            # Should find anxiety-related conversations
            anxiety_convs = [c for c in relevant if 'anxiety' in c.get_full_text().lower()]
            assert len(anxiety_convs) >= 2  # Work anxiety and therapy conversations
            
            # Test meditation-related query
            meditation_query = "How has my meditation practice developed?"
            relevant = engine.find_relevant_conversations(meditation_query, self.test_conversations)
            
            meditation_convs = [c for c in relevant if 'meditation' in c.get_full_text().lower()]
            assert len(meditation_convs) >= 1
    
    def test_find_relevant_conversations_tag_matching(self):
        """Test finding relevant conversations by tag matching"""
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            
            # Query that should match tags
            query = "spiritual growth and mindfulness"
            relevant = engine.find_relevant_conversations(query, self.test_conversations)
            
            # Should prioritize conversations with matching tags
            spiritual_conv = next((c for c in relevant if 'spiritual-growth' in c.tags), None)
            assert spiritual_conv is not None
    
    def test_find_relevant_conversations_empty_result(self):
        """Test finding relevant conversations with no matches"""
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            
            # Query that shouldn't match anything
            query = "unrelated topic that doesn't exist"
            relevant = engine.find_relevant_conversations(query, self.test_conversations)
            
            assert len(relevant) == 0
    
    def test_find_relevant_conversations_max_limit(self):
        """Test max conversation limit in relevance finding"""
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            
            # Create many conversations that would match
            many_conversations = []
            for i in range(20):
                conv_data = {
                    'id': f'conv-{i}',
                    'title': f'Anxiety Discussion {i}',
                    'create_time': 1640995200 + i * 3600,
                    'update_time': 1640995800 + i * 3600,
                    'mapping': {
                        f'msg-{i}': {
                            'message': {
                                'id': f'msg-{i}',
                                'author': {'role': 'user'},
                                'create_time': 1640995200 + i * 3600,
                                'content': {
                                    'content_type': 'text',
                                    'parts': [f'This is about anxiety topic {i}']
                                }
                            }
                        }
                    }
                }
                conv = Conversation(conv_data)
                conv.tags = ['anxiety']
                many_conversations.append(conv)
            
            query = "anxiety"
            relevant = engine.find_relevant_conversations(query, many_conversations, max_conversations=5)
            
            assert len(relevant) <= 5
    
    @patch('insight_engine.OpenAI')
    def test_generate_insight_success(self, mock_openai):
        """Test successful insight generation"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices[0].message.content = """
INSIGHT:
Your relationship with anxiety has shown significant evolution over time. In your earlier conversations, you described work-related anxiety as overwhelming and affecting your performance and sleep. However, through therapy and developing coping strategies, you've gained valuable insights into your anxiety patterns.

The progression from feeling overwhelmed by work anxiety to understanding patterns suggests meaningful growth in self-awareness. Your exploration of meditation as a stress management tool shows a proactive approach to healing.

QUOTES:
"I have been struggling with work-related anxiety. It affects my performance and sleep." - 2022-01-01
"My therapist helped me understand my anxiety patterns. I am making progress." - 2022-01-03

THEMES:
Work-related anxiety
Therapy and professional support
Pattern recognition and self-awareness
Meditation as coping strategy
Performance anxiety management

TIMELINE_INSIGHTS:
Early conversations showed anxiety as overwhelming and unmanaged
Development of therapy relationship provided professional guidance
Recognition of anxiety patterns marked a turning point in understanding
Introduction of meditation practice shows evolution toward holistic healing
"""
        mock_client.chat.completions.create.return_value = mock_response
        
        engine = InsightEngine(self.config_path)
        
        question = "How has my relationship with anxiety evolved over time?"
        
        with patch.object(engine, '_load_insight_from_cache', return_value=None), \
             patch.object(engine, '_save_insight_to_cache'):
            
            result = engine.generate_insight(question, self.test_conversations)
            
            assert result['question'] == question
            assert 'relationship with anxiety' in result['insight']
            assert len(result['quotes']) >= 2
            assert len(result['themes']) >= 4
            assert len(result['timeline_insights']) >= 3
            assert result['conversations_analyzed'] > 0
            
            # Verify API was called
            mock_client.chat.completions.create.assert_called_once()
    
    @patch('insight_engine.OpenAI')
    def test_generate_insight_no_relevant_conversations(self, mock_openai):
        """Test insight generation when no relevant conversations found"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        engine = InsightEngine(self.config_path)
        
        # Query that won't match any conversations
        question = "How has my relationship with unicorns evolved?"
        
        result = engine.generate_insight(question, self.test_conversations)
        
        assert result['question'] == question
        assert 'No relevant conversations found' in result['insight']
        assert result['conversations_analyzed'] == 0
        assert len(result['quotes']) == 0
        assert len(result['themes']) == 0
        
        # Verify API was NOT called
        mock_client.chat.completions.create.assert_not_called()
    
    @patch('insight_engine.OpenAI')
    def test_generate_insight_uses_cache(self, mock_openai):
        """Test that insight generation uses cached results"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        engine = InsightEngine(self.config_path)
        
        # Mock cached result
        cached_result = {
            'question': 'Test question',
            'insight': 'Cached insight about your growth',
            'quotes': ['Cached quote'],
            'themes': ['cached-theme'],
            'timeline_insights': ['Cached timeline insight'],
            'conversations_analyzed': 3,
            'generated_at': datetime.now().isoformat()
        }
        
        question = "Test question"
        
        with patch.object(engine, '_load_insight_from_cache', return_value=cached_result):
            result = engine.generate_insight(question, self.test_conversations)
            
            assert result == cached_result
            
            # Verify API was NOT called
            mock_client.chat.completions.create.assert_not_called()
    
    @patch('insight_engine.OpenAI')
    def test_generate_insight_api_error(self, mock_openai):
        """Test insight generation with API error"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Mock API to raise an exception
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        engine = InsightEngine(self.config_path)
        
        question = "How has my anxiety evolved?"
        
        with patch.object(engine, '_load_insight_from_cache', return_value=None):
            result = engine.generate_insight(question, self.test_conversations)
            
            assert result['question'] == question
            assert 'Error generating insight' in result['insight']
            assert result['conversations_analyzed'] == 0
    
    def test_parse_insight_response_success(self):
        """Test successful parsing of insight response"""
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            
            response_text = """
INSIGHT:
Your spiritual journey shows remarkable growth through meditation and mindfulness practices. You've developed from someone seeking stress relief to embracing deeper spiritual connection.

The evolution is evident in your language and approach to challenges.

QUOTES:
- "I want to develop meditation practice for stress relief" - 2022-01-02  
- "Meditation has become a spiritual anchor in my daily life" - 2022-01-15

THEMES:
- Spiritual development through meditation
- Stress management evolution
- Daily practice consistency
- Mind-body connection awareness

TIMELINE_INSIGHTS:
- Initial focus was primarily on stress reduction
- Gradual recognition of spiritual benefits emerged
- Development of consistent daily practice routine
- Integration of mindfulness into daily activities
"""
            
            result = engine._parse_insight_response(response_text)
            
            assert 'spiritual journey' in result['insight']
            assert 'remarkable growth' in result['insight']
            assert len(result['quotes']) == 2
            assert 'stress relief' in result['quotes'][0]
            assert len(result['themes']) == 4
            assert 'Spiritual development' in result['themes'][0]
            assert len(result['timeline_insights']) == 4
            assert 'stress reduction' in result['timeline_insights'][0]
    
    def test_parse_insight_response_malformed(self):
        """Test parsing of malformed insight response"""
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            
            # Malformed response
            response_text = "This is not a properly formatted insight response"
            
            result = engine._parse_insight_response(response_text)
            
            # Should return empty structures for missing sections
            assert result['insight'] == ''
            assert result['quotes'] == []
            assert result['themes'] == []
            assert result['timeline_insights'] == []
    
    def test_parse_insight_response_partial(self):
        """Test parsing of partially complete insight response"""
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            
            response_text = """
INSIGHT:
Your growth in self-awareness is evident.

QUOTES:
- "I understand my patterns better now"

THEMES:
- Self-awareness development
"""
            # Missing TIMELINE_INSIGHTS section
            
            result = engine._parse_insight_response(response_text)
            
            assert 'self-awareness' in result['insight']
            assert len(result['quotes']) == 1
            assert len(result['themes']) == 1
            assert result['timeline_insights'] == []  # Missing section should be empty
    
    def test_export_insight(self):
        """Test exporting insight to markdown file"""
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            
            insight_data = {
                'question': 'How has my spiritual growth evolved?',
                'insight': 'Your spiritual journey shows remarkable progression from initial seeking to deep practice.',
                'quotes': [
                    'I am looking for spiritual meaning in my life',
                    'Meditation has become central to my spiritual practice'
                ],
                'themes': [
                    'Spiritual seeking and exploration',
                    'Meditation practice development',
                    'Inner peace cultivation'
                ],
                'timeline_insights': [
                    'Early conversations focused on spiritual seeking',
                    'Middle period showed practice development',
                    'Recent conversations indicate deeper integration'
                ],
                'conversations_analyzed': 5,
                'conversation_titles': [
                    'Spiritual Seeking',
                    'Meditation Practice',
                    'Inner Peace Journey'
                ],
                'generated_at': '2024-01-01T10:00:00'
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                temp_path = f.name
            
            try:
                result_path = engine.export_insight(insight_data, temp_path)
                
                assert result_path == temp_path
                
                # Verify file content
                with open(temp_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                assert 'InsightVault - Personal Reflection' in content
                assert insight_data['question'] in content
                assert insight_data['insight'] in content
                assert 'Spiritual seeking and exploration' in content
                assert 'Early conversations focused' in content
                assert '> I am looking for spiritual meaning' in content
                
            finally:
                os.unlink(temp_path)
    
    def test_export_insight_auto_filename(self):
        """Test exporting insight with automatic filename generation"""
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            
            insight_data = {
                'question': 'Test question',
                'insight': 'Test insight',
                'quotes': [],
                'themes': [],
                'timeline_insights': [],
                'conversations_analyzed': 1
            }
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Change to temp directory so auto-generated file goes there
                original_cwd = os.getcwd()
                try:
                    os.chdir(temp_dir)
                    os.makedirs('output', exist_ok=True)
                    
                    result_path = engine.export_insight(insight_data)
                    
                    assert result_path.startswith('output/insight_')
                    assert result_path.endswith('.md')
                    assert os.path.exists(result_path)
                    
                finally:
                    os.chdir(original_cwd)
    
    def test_export_insight_error_handling(self):
        """Test export insight error handling"""
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            
            insight_data = {'question': 'Test'}
            
            # Try to export to invalid path
            result_path = engine.export_insight(insight_data, '/invalid/path/insight.md')
            
            assert result_path == ""  # Should return empty string on error
    
    def test_get_insight_system_prompt(self):
        """Test the system prompt for insight generation"""
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            
            prompt = engine._get_insight_system_prompt()
            
            assert 'compassionate AI therapist' in prompt
            assert 'personal growth coach' in prompt
            assert 'patterns of growth' in prompt
            assert 'empathetic' in prompt
            assert 'non-judgmental' in prompt
    
    def test_prepare_conversation_data(self):
        """Test preparation of conversation data for prompts"""
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            
            prepared_data = engine._prepare_conversation_data(self.test_conversations[:2])
            
            assert 'CONVERSATION 1' in prepared_data
            assert 'CONVERSATION 2' in prepared_data
            assert 'Work Anxiety Management' in prepared_data
            assert 'Building Meditation Practice' in prepared_data
            assert 'anxiety, work, stress' in prepared_data
            assert 'meditation, mindfulness' in prepared_data
    
    def test_create_insight_prompt(self):
        """Test creation of insight prompt for GPT"""
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            
            question = "How has my spiritual growth evolved?"
            conversation_data = "Sample conversation data"
            
            prompt = engine._create_insight_prompt(question, conversation_data)
            
            assert question in prompt
            assert conversation_data in prompt
            assert 'INSIGHT:' in prompt
            assert 'QUOTES:' in prompt
            assert 'THEMES:' in prompt
            assert 'TIMELINE_INSIGHTS:' in prompt
            assert 'compassionate' in prompt
    
    def test_cache_operations(self):
        """Test insight caching operations"""
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            
            test_insight = {
                'question': 'Test question',
                'insight': 'Test insight content',
                'quotes': ['Test quote'],
                'themes': ['test-theme'],
                'timeline_insights': ['Test timeline'],
                'conversations_analyzed': 2
            }
            
            with tempfile.TemporaryDirectory() as temp_dir:
                engine.cache_dir = temp_dir
                
                # Save to cache
                cache_key = 'test_insight_123'
                engine._save_insight_to_cache(cache_key, test_insight)
                
                # Load from cache
                loaded_insight = engine._load_insight_from_cache(cache_key)
                
                assert loaded_insight is not None
                assert loaded_insight['question'] == 'Test question'
                assert loaded_insight['insight'] == 'Test insight content'
                assert loaded_insight['quotes'] == ['Test quote']
    
    def test_sample_questions_available(self):
        """Test that sample questions are available"""
        assert len(SAMPLE_QUESTIONS) > 0
        assert isinstance(SAMPLE_QUESTIONS, list)
        
        # Check some expected question types
        question_text = ' '.join(SAMPLE_QUESTIONS).lower()
        assert 'spiritual' in question_text
        assert 'anxiety' in question_text or 'emotional' in question_text
        assert 'growth' in question_text
        assert 'relationship' in question_text


@pytest.mark.integration
class TestInsightEngineIntegration:
    """Integration tests for InsightEngine with realistic scenarios"""
    
    def setup_method(self):
        """Set up integration test fixtures"""
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'test_config.json')
    
    @patch('insight_engine.OpenAI')
    def test_end_to_end_insight_generation(self, mock_openai):
        """Test complete insight generation workflow"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Mock a realistic GPT response
        mock_response = Mock()
        mock_response.choices[0].message.content = """
INSIGHT:
Your journey with anxiety management shows significant evolution over the past year. Initially, you described feeling overwhelmed by work-related stress and performance anxiety. Through therapy and the development of mindfulness practices, you've gained valuable tools for managing anxiety.

The progression from reactive anxiety management to proactive stress prevention demonstrates meaningful personal growth. Your integration of meditation into daily routines shows commitment to long-term wellness.

QUOTES:
"Work anxiety affects my performance and sleep patterns" - 2022-01-01
"My therapist helped me understand my anxiety triggers" - 2022-01-03  
"Meditation has become my anchor during stressful periods" - 2022-01-04

THEMES:
Work-related anxiety and performance concerns
Therapeutic relationship and professional support
Mindfulness and meditation practice development
Sleep and physical health awareness
Pattern recognition and self-awareness growth

TIMELINE_INSIGHTS:
Early conversations showed anxiety as overwhelming and unmanaged
Therapy introduction marked beginning of structured support
Recognition of anxiety patterns represented breakthrough moment  
Meditation practice development showed proactive approach to wellness
Recent conversations indicate integration of multiple coping strategies
"""
        mock_client.chat.completions.create.return_value = mock_response
        
        engine = InsightEngine(self.config_path)
        
        # Create realistic test conversations
        conversations = []
        
        # Conversation 1: Initial anxiety
        conv1_data = {
            'id': 'conv-anxiety-initial',
            'title': 'Work Stress and Performance Anxiety',
            'create_time': 1640995200,  # 2022-01-01
            'update_time': 1640995800,
            'mapping': {
                'msg-1': {
                    'message': {
                        'id': 'msg-1',
                        'author': {'role': 'user'},
                        'create_time': 1640995200,
                        'content': {
                            'content_type': 'text',
                            'parts': ['I have been experiencing severe work anxiety that affects my performance and sleep patterns. I feel overwhelmed by deadlines and perfectionist tendencies.']
                        }
                    }
                }
            }
        }
        conv1 = Conversation(conv1_data)
        conv1.tags = ['anxiety', 'work', 'stress', 'performance', 'sleep']
        conv1.summary = 'Discussion about overwhelming work anxiety and its impacts'
        conv1.auto_title = 'Work Anxiety and Performance Stress'
        conversations.append(conv1)
        
        # Conversation 2: Therapy introduction
        conv2_data = {
            'id': 'conv-therapy-start',
            'title': 'Starting Therapy for Anxiety',
            'create_time': 1641254400,  # 2022-01-04
            'update_time': 1641255000,
            'mapping': {
                'msg-2': {
                    'message': {
                        'id': 'msg-2',
                        'author': {'role': 'user'},
                        'create_time': 1641254400,
                        'content': {
                            'content_type': 'text',
                            'parts': ['I started seeing a therapist who helped me understand my anxiety triggers and patterns. This feels like a breakthrough.']
                        }
                    }
                }
            }
        }
        conv2 = Conversation(conv2_data)
        conv2.tags = ['therapy', 'anxiety', 'patterns', 'breakthrough', 'professional-help']
        conv2.summary = 'Beginning therapy and gaining insight into anxiety patterns'
        conv2.auto_title = 'Therapy Breakthrough on Anxiety Patterns'
        conversations.append(conv2)
        
        # Conversation 3: Meditation development
        conv3_data = {
            'id': 'conv-meditation-practice',
            'title': 'Developing Meditation for Anxiety',
            'create_time': 1641340800,  # 2022-01-05
            'update_time': 1641341400,
            'mapping': {
                'msg-3': {
                    'message': {
                        'id': 'msg-3',
                        'author': {'role': 'user'},
                        'create_time': 1641340800,
                        'content': {
                            'content_type': 'text',
                            'parts': ['Meditation has become my anchor during stressful periods. I practice daily and notice significant improvements in my anxiety management.']
                        }
                    }
                }
            }
        }
        conv3 = Conversation(conv3_data)
        conv3.tags = ['meditation', 'mindfulness', 'anxiety', 'daily-practice', 'improvement']
        conv3.summary = 'Establishing meditation as primary anxiety management tool'
        conv3.auto_title = 'Meditation as Anxiety Anchor'
        conversations.append(conv3)
        
        # Generate insight
        question = "How has my approach to managing anxiety evolved over time?"
        
        with patch.object(engine, '_load_insight_from_cache', return_value=None), \
             patch.object(engine, '_save_insight_to_cache') as mock_save_cache:
            
            result = engine.generate_insight(question, conversations)
            
            # Verify comprehensive result
            assert result['question'] == question
            assert 'evolution' in result['insight'].lower()
            assert 'anxiety management' in result['insight']
            assert result['conversations_analyzed'] == 3
            
            # Verify timeline insights show progression
            assert len(result['timeline_insights']) >= 4
            timeline_text = ' '.join(result['timeline_insights']).lower()
            assert 'early' in timeline_text or 'initial' in timeline_text
            assert 'therapy' in timeline_text
            assert 'meditation' in timeline_text
            
            # Verify themes capture key areas
            themes_text = ' '.join(result['themes']).lower()
            assert 'anxiety' in themes_text
            assert 'therapy' in themes_text or 'therapeutic' in themes_text
            assert 'meditation' in themes_text or 'mindfulness' in themes_text
            
            # Verify quotes from different time periods
            assert len(result['quotes']) >= 3
            
            # Verify caching occurred
            mock_save_cache.assert_called_once()
            
            # Test export functionality
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                temp_path = f.name
            
            try:
                export_path = engine.export_insight(result, temp_path)
                assert export_path == temp_path
                
                # Verify exported content
                with open(temp_path, 'r', encoding='utf-8') as f:
                    exported_content = f.read()
                
                assert question in exported_content
                assert 'Conversations Analyzed: 3' in exported_content
                assert result['insight'] in exported_content
                
            finally:
                os.unlink(temp_path)