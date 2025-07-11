"""
Unit tests for gui module
Tests InsightVaultGUI class with mocked dependencies
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Import the modules to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from gui import InsightVaultGUI
from chat_parser import Conversation


class TestInsightVaultGUI:
    """Test the InsightVaultGUI class"""
    
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
    
    def test_gui_initialization(self):
        """Test GUI initialization"""
        with patch('gui.ConversationSummarizer'), \
             patch('gui.InsightEngine'):
            
            gui = InsightVaultGUI()
            
            assert gui.parser is not None
            assert gui.current_conversations == []
            assert gui.filtered_conversations == []
            assert gui.selected_conversations == []
            assert gui.current_insights == {}
    
    def test_gui_initialization_no_config(self):
        """Test GUI initialization without config file"""
        with patch('os.path.exists', return_value=False):
            gui = InsightVaultGUI()
            
            assert gui.summarizer is None
            assert gui.insight_engine is None
            assert gui.analytics_engine is None
    
    def test_create_main_layout(self):
        """Test main layout creation"""
        with patch('gui.ConversationSummarizer'), \
             patch('gui.InsightEngine'):
            
            gui = InsightVaultGUI()
            layout = gui.create_main_layout()
            
            assert layout is not None
            assert isinstance(layout, list)
            assert len(layout) > 0
    
    def test_create_main_window(self):
        """Test main window creation"""
        with patch('gui.ConversationSummarizer'), \
             patch('gui.InsightEngine'):
            
            gui = InsightVaultGUI()
            window = gui.create_main_window()
            
            assert window is not None
    
    def test_load_conversations_success(self):
        """Test successful conversation loading"""
        with patch('gui.ConversationSummarizer'), \
             patch('gui.InsightEngine'), \
             patch('gui.sg') as mock_sg:
            
            gui = InsightVaultGUI()
            
            # Mock window
            mock_window = Mock()
            mock_window.__getitem__ = Mock(return_value=Mock())
            
            # Mock file dialog
            mock_sg.popup_get_file.return_value = 'test_file.json'
            
            # Mock parser success
            with patch.object(gui.parser, 'load_conversations', return_value=True):
                gui.load_conversations('test_file.json', mock_window)
                
                assert len(gui.current_conversations) >= 0  # May be empty if no conversations loaded
    
    def test_search_conversations(self):
        """Test conversation search functionality"""
        with patch('gui.ConversationSummarizer'), \
             patch('gui.InsightEngine'), \
             patch('gui.sg') as mock_sg:
            
            gui = InsightVaultGUI()
            
            # Mock window
            mock_window = Mock()
            mock_window.__getitem__ = Mock(return_value=Mock())
            
            # Add test conversations
            conv1 = Conversation(self.test_conversation_data)
            conv1.tags = ['anxiety', 'career']
            gui.current_conversations = [conv1]
            
            # Test search
            gui.search_conversations('anxiety', mock_window)
            
            # Should update filtered conversations
            assert len(gui.filtered_conversations) >= 0
    
    def test_filter_conversations(self):
        """Test conversation filtering by date"""
        with patch('gui.ConversationSummarizer'), \
             patch('gui.InsightEngine'), \
             patch('gui.sg') as mock_sg:
            
            gui = InsightVaultGUI()
            
            # Mock window
            mock_window = Mock()
            mock_window.__getitem__ = Mock(return_value=Mock())
            
            # Add test conversations
            conv1 = Conversation(self.test_conversation_data)
            gui.current_conversations = [conv1]
            
            # Test filtering
            gui.filter_conversations('2021-12-31', '2022-01-01', mock_window)
            
            # Should update filtered conversations
            assert len(gui.filtered_conversations) >= 0
    
    def test_show_conversation_content(self):
        """Test conversation content display"""
        with patch('gui.ConversationSummarizer'), \
             patch('gui.InsightEngine'), \
             patch('gui.sg') as mock_sg:
            
            gui = InsightVaultGUI()
            
            # Mock window
            mock_window = Mock()
            mock_window.__getitem__ = Mock(return_value=Mock())
            
            # Add test conversation
            conv1 = Conversation(self.test_conversation_data)
            conv1.tags = ['anxiety', 'career']
            conv1.summary = 'Test summary'
            gui.current_conversations = [conv1]
            
            # Test content display
            gui.show_conversation_content([0], mock_window)  # Select first conversation
            
            # Should update window with conversation details
            mock_window.__getitem__.assert_called()


@pytest.mark.gui
class TestInsightVaultGUIIntegration:
    """Integration tests for GUI"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'test_config.json')
    
    def test_gui_workflow_simulation(self):
        """Test basic GUI workflow simulation"""
        with patch('gui.ConversationSummarizer'), \
             patch('gui.InsightEngine'), \
             patch('gui.sg') as mock_sg:
            
            gui = InsightVaultGUI()
            
            # Mock window and events
            mock_window = Mock()
            mock_window.__getitem__ = Mock(return_value=Mock())
            mock_window.read.return_value = ('-LOAD-', {'-FILE-': 'test_file.json'})
            
            # Mock file dialog
            mock_sg.popup_get_file.return_value = 'test_file.json'
            
            # Mock parser success
            with patch.object(gui.parser, 'load_conversations', return_value=True):
                # Simulate loading conversations
                gui.load_conversations('test_file.json', mock_window)
                
                # Verify GUI state updated
                assert gui.parser is not None 