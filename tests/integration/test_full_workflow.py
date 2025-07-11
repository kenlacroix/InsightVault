"""
Integration tests for the complete InsightVault workflow
Tests end-to-end functionality with real fixture data
"""

import pytest
import os
import tempfile
import json
from unittest.mock import patch, Mock

# Import the modules to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from chat_parser import ChatParser
from summarizer import ConversationSummarizer
from insight_engine import InsightEngine


@pytest.mark.integration
class TestFullWorkflow:
    """Test complete InsightVault workflow"""
    
    def setup_method(self):
        """Set up integration test fixtures"""
        self.fixture_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'sample_conversations.json')
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'test_config.json')
    
    def test_conversation_loading_and_parsing(self):
        """Test loading and parsing conversation fixture data"""
        parser = ChatParser()
        
        # Load fixture data
        success = parser.load_conversations(self.fixture_path)
        
        assert success is True
        assert len(parser.conversations) >= 2  # Should have at least 2 valid conversations
        
        # Verify conversations have expected content
        anxiety_conv = next((c for c in parser.conversations if 'anxiety' in c.title.lower()), None)
        assert anxiety_conv is not None
        assert len(anxiety_conv.messages) > 0
        
        meditation_conv = next((c for c in parser.conversations if 'meditation' in c.title.lower()), None)
        assert meditation_conv is not None
        assert len(meditation_conv.messages) > 0
        
        # Test search functionality
        anxiety_results = parser.search_conversations('anxiety')
        assert len(anxiety_results) >= 1
        
        spiritual_results = parser.search_conversations('spiritual')
        assert len(spiritual_results) >= 1
        
        # Test statistics
        stats = parser.get_stats()
        assert stats['total_conversations'] >= 2
        assert stats['total_messages'] > 0
        assert stats['total_characters'] > 0
    
    @patch('summarizer.OpenAI')
    def test_conversation_summarization_workflow(self, mock_openai):
        """Test the complete summarization workflow"""
        # Set up mock OpenAI responses
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response1 = Mock()
        mock_response1.choices[0].message.content = """
AUTO_TITLE: Anxiety and Spiritual Growth Journey
SUMMARY: A deep conversation exploring the relationship between anxiety, spiritual practice, and personal growth through challenging times.
TAGS: anxiety, spiritual-growth, mindfulness, coping-strategies, personal-development
"""
        
        mock_response2 = Mock()
        mock_response2.choices[0].message.content = """
AUTO_TITLE: Self-Compassion Meditation Practice
SUMMARY: Discussion about developing self-compassion through meditation and treating oneself with kindness during difficult periods.
TAGS: meditation, self-compassion, mindfulness, healing, daily-practice
"""
        
        mock_client.chat.completions.create.side_effect = [mock_response1, mock_response2]
        
        # Load conversations
        parser = ChatParser()
        parser.load_conversations(self.fixture_path)
        
        # Summarize conversations
        summarizer = ConversationSummarizer(self.config_path)
        
        with patch.object(summarizer, '_load_from_cache', return_value=None), \
             patch.object(summarizer, '_save_to_cache'):
            
            results = summarizer.summarize_all_conversations(parser.conversations)
            
            # Verify summarization results
            successful_count = sum(1 for success in results.values() if success)
            assert successful_count == len(parser.conversations)
            
            # Verify conversations now have summaries and tags
            for conv in parser.conversations:
                assert conv.auto_title != ''
                assert conv.summary != ''
                assert len(conv.tags) > 0
                
                # Verify tags are lowercase and properly formatted
                for tag in conv.tags:
                    assert isinstance(tag, str)
                    assert tag == tag.lower()
            
            # Test tag frequency analysis
            tag_counts = summarizer.get_all_tags(parser.conversations)
            assert isinstance(tag_counts, dict)
            assert len(tag_counts) > 0
            
            # Test export functionality
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                temp_path = f.name
            
            try:
                export_success = summarizer.export_summaries(parser.conversations, temp_path)
                assert export_success is True
                
                # Verify exported content
                with open(temp_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                assert 'InsightVault - Conversation Summaries' in content
                assert 'Total Conversations:' in content
                assert 'Most Common Tags' in content
                
                # Should contain conversation titles and summaries
                for conv in parser.conversations:
                    assert conv.auto_title in content
                    assert conv.summary in content
                    
            finally:
                os.unlink(temp_path)
    
    @patch('insight_engine.OpenAI')  
    def test_insight_generation_workflow(self, mock_openai):
        """Test the complete insight generation workflow"""
        # Set up mock OpenAI response
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices[0].message.content = """
INSIGHT:
Your spiritual and emotional journey shows remarkable growth over time. In your conversations, there's a clear evolution from seeking external validation to developing internal wisdom and self-compassion. The integration of mindfulness practices with anxiety management demonstrates a holistic approach to personal healing.

Your willingness to explore difficult emotions while maintaining spiritual practices shows resilience and commitment to growth. The conversations reveal increasing self-awareness and the development of healthy coping strategies.

QUOTES:
"I've been struggling with anxiety lately and wondering how to connect with my spiritual practice during difficult times." - 2021-12-31
"I'm working on developing more self-compassion through meditation. Sometimes I feel like I'm being too hard on myself." - 2022-01-02
"That's really helpful. I've noticed that my anxiety often comes up when I'm trying to control outcomes instead of trusting the process." - 2021-12-31

THEMES:
Anxiety and spiritual practice integration
Self-compassion development through meditation
Mindfulness as anxiety management tool
Trust vs control in spiritual growth
Emotional awareness and pattern recognition

TIMELINE_INSIGHTS:
Early conversations focused on anxiety as obstacle to spiritual practice
Development of self-compassion marked significant turning point
Recognition of control patterns showed deepening self-awareness
Integration of mindfulness with daily challenges demonstrated practical application
Recent discussions indicate more balanced relationship with anxiety
"""
        mock_client.chat.completions.create.return_value = mock_response
        
        # Load and prepare conversations
        parser = ChatParser()
        parser.load_conversations(self.fixture_path)
        
        # Add some tags and summaries (simulating previous summarization)
        for i, conv in enumerate(parser.conversations):
            conv.tags = ['anxiety', 'spiritual-growth', 'meditation', 'self-compassion'][:(i % 4) + 1]
            conv.summary = f'Summary for conversation {i+1} about spiritual growth and healing'
            conv.auto_title = f'Spiritual Growth Conversation {i+1}'
        
        # Generate insight
        engine = InsightEngine(self.config_path)
        question = "How has my spiritual and emotional growth evolved over time?"
        
        with patch.object(engine, '_load_insight_from_cache', return_value=None), \
             patch.object(engine, '_save_insight_to_cache') as mock_save_cache:
            
            result = engine.generate_insight(question, parser.conversations)
            
            # Verify insight result structure
            assert result['question'] == question
            assert isinstance(result['insight'], str)
            assert len(result['insight']) > 100  # Should be substantial
            assert isinstance(result['quotes'], list)
            assert isinstance(result['themes'], list) 
            assert isinstance(result['timeline_insights'], list)
            assert result['conversations_analyzed'] > 0
            
            # Verify content quality
            insight_text = result['insight'].lower()
            assert 'spiritual' in insight_text or 'growth' in insight_text
            assert len(result['quotes']) >= 2
            assert len(result['themes']) >= 3
            assert len(result['timeline_insights']) >= 3
            
            # Verify caching was used
            mock_save_cache.assert_called_once()
            
            # Test insight export
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                temp_path = f.name
            
            try:
                export_path = engine.export_insight(result, temp_path)
                assert export_path == temp_path
                
                # Verify exported content
                with open(temp_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                assert 'InsightVault - Personal Reflection' in content
                assert result['question'] in content
                assert result['insight'] in content
                assert f"Conversations Analyzed: {result['conversations_analyzed']}" in content
                
                # Should contain all sections
                assert '## Reflection' in content
                assert '## Key Themes' in content if result['themes'] else True
                assert '## Meaningful Quotes' in content if result['quotes'] else True
                assert '## Timeline Insights' in content if result['timeline_insights'] else True
                
            finally:
                os.unlink(temp_path)
    
    @patch('summarizer.OpenAI')
    @patch('insight_engine.OpenAI')
    def test_complete_end_to_end_workflow(self, mock_insight_openai, mock_summary_openai):
        """Test the complete end-to-end InsightVault workflow"""
        # Set up mock OpenAI clients
        mock_summary_client = Mock()
        mock_summary_openai.return_value = mock_summary_client
        
        mock_insight_client = Mock()
        mock_insight_openai.return_value = mock_insight_client
        
        # Mock summarization responses
        mock_summary_response = Mock()
        mock_summary_response.choices[0].message.content = """
AUTO_TITLE: Complete Workflow Test
SUMMARY: A comprehensive test of the entire InsightVault workflow from conversation loading to insight generation.
TAGS: testing, workflow, comprehensive, integration, validation
"""
        mock_summary_client.chat.completions.create.return_value = mock_summary_response
        
        # Mock insight generation response
        mock_insight_response = Mock()
        mock_insight_response.choices[0].message.content = """
INSIGHT:
This comprehensive test demonstrates the complete InsightVault workflow. The system successfully processes conversations from initial loading through AI-powered analysis to final export. Each component works together to provide meaningful insights about personal growth and development.

QUOTES:
"Testing the complete workflow shows integration success" - 2024-01-01

THEMES:
Workflow validation and testing
System integration verification
End-to-end functionality confirmation

TIMELINE_INSIGHTS:
Initial conversation loading proceeded successfully
Summarization added meaningful metadata to conversations
Insight generation created comprehensive analysis
Export functionality preserved all generated content
"""
        mock_insight_client.chat.completions.create.return_value = mock_insight_response
        
        # Step 1: Load conversations
        parser = ChatParser()
        success = parser.load_conversations(self.fixture_path)
        assert success is True
        assert len(parser.conversations) >= 2
        
        # Step 2: Summarize conversations
        summarizer = ConversationSummarizer(self.config_path)
        
        with patch.object(summarizer, '_load_from_cache', return_value=None), \
             patch.object(summarizer, '_save_to_cache'):
            
            summary_results = summarizer.summarize_all_conversations(parser.conversations)
            
            # Verify all conversations were summarized
            assert all(summary_results.values())
            
            # Verify conversations have metadata
            for conv in parser.conversations:
                assert conv.auto_title != ''
                assert conv.summary != ''
                assert len(conv.tags) > 0
        
        # Step 3: Generate insight
        engine = InsightEngine(self.config_path)
        question = "What does this complete workflow test reveal about my development?"
        
        with patch.object(engine, '_load_insight_from_cache', return_value=None), \
             patch.object(engine, '_save_insight_to_cache'):
            
            insight_result = engine.generate_insight(question, parser.conversations)
            
            # Verify insight generation
            assert insight_result['question'] == question
            assert insight_result['conversations_analyzed'] > 0
            assert len(insight_result['insight']) > 50
        
        # Step 4: Export all results
        with tempfile.TemporaryDirectory() as temp_dir:
            # Export summaries
            summary_path = os.path.join(temp_dir, 'summaries.md')
            summary_export_success = summarizer.export_summaries(parser.conversations, summary_path)
            assert summary_export_success is True
            assert os.path.exists(summary_path)
            
            # Export insight
            insight_path = os.path.join(temp_dir, 'insight.md')
            insight_export_path = engine.export_insight(insight_result, insight_path)
            assert insight_export_path == insight_path
            assert os.path.exists(insight_path)
            
            # Verify both files have content
            with open(summary_path, 'r') as f:
                summary_content = f.read()
            assert len(summary_content) > 200
            assert 'InsightVault - Conversation Summaries' in summary_content
            
            with open(insight_path, 'r') as f:
                insight_content = f.read()
            assert len(insight_content) > 200
            assert 'InsightVault - Personal Reflection' in insight_content
        
        # Verify API calls were made appropriately
        assert mock_summary_client.chat.completions.create.call_count == len(parser.conversations)
        assert mock_insight_client.chat.completions.create.call_count == 1
    
    def test_error_handling_and_resilience(self):
        """Test system resilience with various error conditions"""
        # Test with non-existent file
        parser = ChatParser()
        success = parser.load_conversations('nonexistent.json')
        assert success is False
        assert len(parser.conversations) == 0
        
        # Test with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('invalid json content {')
            invalid_path = f.name
        
        try:
            success = parser.load_conversations(invalid_path)
            assert success is False
            assert len(parser.conversations) == 0
        finally:
            os.unlink(invalid_path)
        
        # Test insight engine with no conversations
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            result = engine.generate_insight("Test question", [])
            
            assert result['question'] == "Test question"
            assert 'No relevant conversations found' in result['insight']
            assert result['conversations_analyzed'] == 0
        
        # Test summarizer with invalid config
        with pytest.raises(FileNotFoundError):
            ConversationSummarizer('nonexistent_config.json')
    
    def test_performance_with_large_dataset(self):
        """Test system performance with larger conversation sets"""
        # Create a larger set of test conversations
        parser = ChatParser()
        large_conversations = []
        
        base_time = 1640995200
        for i in range(50):  # Create 50 conversations
            conv_data = {
                'id': f'perf-test-conv-{i}',
                'title': f'Performance Test Conversation {i}',
                'create_time': base_time + i * 3600,
                'update_time': base_time + i * 3600 + 300,
                'mapping': {
                    f'msg-{i}-1': {
                        'message': {
                            'id': f'msg-{i}-1',
                            'author': {'role': 'user'},
                            'create_time': base_time + i * 3600,
                            'content': {
                                'content_type': 'text',
                                'parts': [f'This is performance test message {i} about anxiety, meditation, and spiritual growth.']
                            }
                        }
                    }
                }
            }
            from chat_parser import Conversation
            conv = Conversation(conv_data)
            conv.tags = ['performance', 'test', 'anxiety', 'meditation'][:(i % 4) + 1]
            conv.summary = f'Performance test conversation {i}'
            conv.auto_title = f'Performance Test {i}'
            large_conversations.append(conv)
        
        parser.conversations = large_conversations
        
        # Test search performance
        search_results = parser.search_conversations('anxiety')
        assert len(search_results) > 0
        
        # Test stats calculation
        stats = parser.get_stats()
        assert stats['total_conversations'] == 50
        assert stats['total_messages'] == 50
        
        # Test insight relevance finding
        with patch('insight_engine.OpenAI'):
            engine = InsightEngine(self.config_path)
            
            relevant = engine.find_relevant_conversations('anxiety and meditation', large_conversations)
            assert len(relevant) <= 10  # Should respect max limit
            assert len(relevant) > 0   # Should find some matches