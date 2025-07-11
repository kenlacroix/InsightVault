"""
Unit tests for main module
Tests main application launcher and CLI functionality
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Import the modules to test
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import main


class TestMainModule:
    """Test the main module functions"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'test_config.json')
    
    def test_setup_environment_success(self):
        """Test successful environment setup"""
        with patch('os.path.exists', return_value=True), \
             patch('os.makedirs') as mock_makedirs:
            
            result = main.setup_environment()
            
            assert result is True
            mock_makedirs.assert_called()
    
    def test_setup_environment_no_config(self):
        """Test environment setup without config file"""
        with patch('os.path.exists', side_effect=lambda x: x != 'config.json'), \
             patch('builtins.print') as mock_print:
            
            result = main.setup_environment()
            
            assert result is False
            mock_print.assert_called()
    
    def test_setup_environment_no_example_config(self):
        """Test environment setup without example config"""
        with patch('os.path.exists', return_value=False), \
             patch('builtins.print') as mock_print:
            
            result = main.setup_environment()
            
            assert result is False
            mock_print.assert_called()
    
    def test_run_gui_success(self):
        """Test successful GUI launch"""
        with patch('builtins.__import__') as mock_import, \
             patch('builtins.print') as mock_print:
            
            # Mock the gui module import
            mock_gui_module = Mock()
            mock_gui_main = Mock()
            mock_gui_module.main = mock_gui_main
            mock_import.return_value = mock_gui_module
            
            result = main.run_gui()
            
            assert result is True
            mock_gui_main.assert_called_once()
            mock_print.assert_called_with("🚀 Launching InsightVault GUI...")
    
    def test_run_gui_import_error(self):
        """Test GUI launch with import error"""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'gui'")), \
             patch('builtins.print') as mock_print:
            
            result = main.run_gui()
            
            assert result is False
            mock_print.assert_called()
    
    def test_run_gui_exception(self):
        """Test GUI launch with general exception"""
        with patch('builtins.__import__', side_effect=Exception("GUI error")), \
             patch('builtins.print') as mock_print:
            
            result = main.run_gui()
            
            assert result is False
            mock_print.assert_called()
    
    def test_run_cli_success(self):
        """Test successful CLI launch"""
        with patch('builtins.__import__') as mock_import, \
             patch('builtins.input', side_effect=['6']), \
             patch('builtins.print') as mock_print:
            
            # Mock the module imports
            mock_chat_parser_module = Mock()
            mock_chat_parser_class = Mock()
            mock_chat_parser_instance = Mock()
            mock_chat_parser_instance.load_conversations.return_value = True
            mock_chat_parser_instance.conversations = []
            mock_chat_parser_class.return_value = mock_chat_parser_instance
            mock_chat_parser_module.ChatParser = mock_chat_parser_class
            
            # Mock other modules
            mock_summarizer_module = Mock()
            mock_insight_module = Mock()
            
            # Set up import side effect to return different modules
            def import_side_effect(name, *args, **kwargs):
                if 'chat_parser' in name:
                    return mock_chat_parser_module
                elif 'summarizer' in name:
                    return mock_summarizer_module
                elif 'insight_engine' in name:
                    return mock_insight_module
                else:
                    return Mock()
            
            mock_import.side_effect = import_side_effect
            
            # Mock the input for file path
            with patch('builtins.input', side_effect=['', '6']):  # Empty file path, then exit
                result = main.run_cli()
                
                assert result is True
    
    def test_run_cli_import_error(self):
        """Test CLI launch with import error"""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'chat_parser'")), \
             patch('builtins.print') as mock_print:
            
            result = main.run_cli()
            
            assert result is False
            mock_print.assert_called()
    
    def test_run_cli_exception(self):
        """Test CLI launch with general exception"""
        with patch('builtins.__import__', side_effect=Exception("CLI error")), \
             patch('builtins.print') as mock_print:
            
            result = main.run_cli()
            
            assert result is False
            mock_print.assert_called()
    
    def test_show_help(self):
        """Test help display"""
        with patch('builtins.print') as mock_print:
            main.show_help()
            
            mock_print.assert_called()
            # Verify help text contains expected content
            call_args = mock_print.call_args[0][0]
            assert 'InsightVault' in call_args
            assert 'DESCRIPTION:' in call_args
            assert 'USAGE:' in call_args
    
    def test_main_with_help_detailed(self):
        """Test main function with detailed help"""
        with patch('sys.argv', ['main.py', '--help-detailed']), \
             patch('builtins.print') as mock_print:
            
            main.main()
            
            mock_print.assert_called()
    
    def test_main_with_cli(self):
        """Test main function with CLI mode"""
        with patch('sys.argv', ['main.py', '--cli']), \
             patch('main.setup_environment', return_value=True), \
             patch('main.run_cli', return_value=True), \
             patch('builtins.print') as mock_print:
            
            main.main()
            
            mock_print.assert_called()
    
    def test_main_with_gui(self):
        """Test main function with GUI mode (default)"""
        with patch('sys.argv', ['main.py']), \
             patch('main.setup_environment', return_value=True), \
             patch('main.run_gui', return_value=True), \
             patch('builtins.print') as mock_print:
            
            main.main()
            
            mock_print.assert_called()
    
    def test_main_setup_failure(self):
        """Test main function with setup failure"""
        with patch('sys.argv', ['main.py']), \
             patch('main.setup_environment', return_value=False), \
             patch('builtins.print') as mock_print:
            
            main.main()
            
            mock_print.assert_called()
            # Should show setup failure message
            call_args = mock_print.call_args_list
            assert any('setup failed' in str(call) for call in call_args)
    
    def test_main_gui_failure(self):
        """Test main function with GUI failure"""
        with patch('sys.argv', ['main.py']), \
             patch('main.setup_environment', return_value=True), \
             patch('main.run_gui', return_value=False), \
             patch('builtins.print') as mock_print, \
             patch('sys.exit') as mock_exit:
            
            main.main()
            
            mock_exit.assert_called_with(1)


@pytest.mark.integration
class TestMainIntegration:
    """Integration tests for main module"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'test_config.json')
    
    def test_main_argument_parsing(self):
        """Test argument parsing functionality"""
        with patch('sys.argv', ['main.py', '--cli']), \
             patch('argparse.ArgumentParser') as mock_parser:
            
            mock_args = Mock()
            mock_args.cli = True
            mock_args.help_detailed = False
            mock_parser.return_value.parse_args.return_value = mock_args
            
            with patch('main.setup_environment', return_value=True), \
                 patch('main.run_cli', return_value=True):
                
                main.main()
                
                mock_parser.assert_called()
    
    def test_main_banner_display(self):
        """Test banner display in main function"""
        with patch('sys.argv', ['main.py']), \
             patch('main.setup_environment', return_value=True), \
             patch('main.run_gui', return_value=True), \
             patch('builtins.print') as mock_print:
            
            main.main()
            
            # Should display banner
            call_args = mock_print.call_args_list
            assert any('InsightVault' in str(call) for call in call_args)
            assert any('=' in str(call) for call in call_args)  # Banner line 