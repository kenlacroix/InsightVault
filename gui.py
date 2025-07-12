"""
GUI Interface for InsightVault
Uses PySimpleGUI to provide a user-friendly interface for exploring conversations and generating insights
"""

import os
import threading
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import PySimpleGUI as sg
import time
from chat_parser import ChatParser, Conversation
from summarizer import ConversationSummarizer
from insight_engine import InsightEngine, SAMPLE_QUESTIONS
from performance_optimizer import PerformanceOptimizer, BackgroundProcessor
from search_engine import search_manager, SearchFilter


class InsightVaultGUI:
    """Main GUI application for InsightVault"""
    
    def __init__(self):
        self.parser = ChatParser()
        self.summarizer = None
        self.insight_engine = None
        self.analytics_engine = None
        self.current_conversations: List[Conversation] = []
        self.filtered_conversations: List[Conversation] = []
        
        # GUI State
        self.selected_conversations = []
        self.current_insights = {}
        
        # Analytics state
        self.analytics_data = None
        
        # Phase 4: Performance optimization state
        self.current_page = 0
        self.total_pages = 0
        self.search_results = []
        self.is_loading = False
        
        # Configuration
        self.config_file = 'config.json'
        self.config = self._load_config()
        
        # Initialize AI components if config exists
        self._initialize_ai_components()
        
        # Set theme
        sg.theme('LightBlue3')
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "openai_api_key": "",
            "model": "gpt-4",
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"Error loading config: {e}")
                return default_config
        else:
            return default_config
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            self.config = config
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def _initialize_ai_components(self):
        """Initialize AI components if configuration is available"""
        if self.config.get('openai_api_key') and self.config['openai_api_key'] != "your_openai_api_key_here":
            try:
                # Test if we can initialize with the current config
                self.summarizer = ConversationSummarizer(self.config_file)
                self.insight_engine = InsightEngine(self.config_file)
                
                # Add analytics engine initialization
                from analytics_engine import AnalyticsEngine
                self.analytics_engine = AnalyticsEngine(self.config_file)
                
                print("AI components initialized successfully")
                return
            except Exception as e:
                print(f"Could not initialize AI components: {e}")
        
        print("AI components not available - API key needed")
    
    def _test_api_key(self, api_key: str) -> bool:
        """Test if the API key is valid"""
        if not api_key or api_key == "your_openai_api_key_here":
            return False
        
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            # Make a simple test call
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            print(f"API key test failed: {e}")
            return False
    
    def _try_initialize_ai_components(self) -> bool:
        """Try to initialize AI components and return success status"""
        try:
            if self.config.get('openai_api_key') and self.config['openai_api_key'] != "your_openai_api_key_here":
                self.summarizer = ConversationSummarizer(self.config_file)
                self.insight_engine = InsightEngine(self.config_file)
                
                # Add analytics engine initialization
                from analytics_engine import AnalyticsEngine
                self.analytics_engine = AnalyticsEngine(self.config_file)
                
                return True
        except Exception as e:
            print(f"Could not initialize AI components: {e}")
        return False
    
    def create_main_layout(self) -> List[List[Any]]:
        """Create the main window layout"""
        # Menu bar
        menu_def = [
            ['File', ['Load Conversations', 'Exit']],
            ['Tools', ['Summarize All', 'Export Summaries', 'Clear Cache']],
            ['Help', ['About']]
        ]
        
        # Conversation list column
        conv_list_column = [
            [sg.Text('Conversations', font=('Arial', 12, 'bold'))],
            [sg.Text('Search:'), sg.Input(key='-SEARCH-', size=(30, 1), enable_events=True)],
            [sg.Text('Filter by tag:'), sg.Combo([], key='-TAG_FILTER-', size=(20, 1), enable_events=True)],
            [sg.Listbox(
                values=[], 
                key='-CONVERSATION-LIST-', 
                size=(50, 20), 
                enable_events=True,
                horizontal_scroll=True
            )],
            [sg.Text('Total: 0 conversations', key='-CONV-COUNT-')],
            # Phase 4: Pagination controls
            [sg.Button('← Previous', key='-PREV_PAGE-', disabled=True),
             sg.Text('Page 1/1', key='-PAGE_INFO-'),
             sg.Button('Next →', key='-NEXT_PAGE-', disabled=True)],
            [sg.Text('Performance:', font=('Arial', 9, 'bold'))],
            [sg.Text('Memory: 0MB', key='-MEMORY_INFO-', size=(20, 1)),
             sg.Text('Search: 0ms', key='-SEARCH_TIME-', size=(15, 1))]
        ]
        
        # Conversation details column
        details_column = [
            [sg.Text('Conversation Details', font=('Arial', 12, 'bold'))],
            [sg.Text('Title:'), sg.Text('', key='-CONV_TITLE-', size=(40, 1))],
            [sg.Text('Date:'), sg.Text('', key='-CONV_DATE-', size=(20, 1))],
            [sg.Text('Tags:'), sg.Text('', key='-CONV_TAGS-', size=(40, 2))],
            [sg.Text('Summary:', size=(10, 1))],
            [sg.Multiline('', key='-CONV_SUMMARY-', size=(50, 5), disabled=True)],
            [sg.Text('Content:', size=(10, 1))],
            [sg.Multiline('', key='-CONV_CONTENT-', size=(50, 10), disabled=True)]
        ]
        
        # Insight generation section
        insight_column = [
            [sg.Text('Generate Insights', font=('Arial', 12, 'bold'))],
            [sg.Text('Ask a reflective question:')],
            [sg.Combo(
                SAMPLE_QUESTIONS, 
                key='-QUESTION-', 
                size=(60, 1), 
                default_value=SAMPLE_QUESTIONS[0]
            )],
            [sg.Button('Generate Insight', key='-GENERATE_INSIGHT-', size=(15, 1))],
            [sg.ProgressBar(100, orientation='h', size=(40, 20), key='-PROGRESS-', visible=False)],
            [sg.Text('Insight Result:', size=(12, 1))],
            [sg.Multiline('', key='-INSIGHT_RESULT-', size=(60, 12), disabled=True)],
            [sg.Button('Export Insight', key='-EXPORT_INSIGHT-', size=(12, 1), disabled=True)]
        ]
        
        # Main layout
        layout = [
            [sg.Menu(menu_def)],
            [sg.Column(conv_list_column), sg.VSeparator(), sg.Column(details_column)],
            [sg.HSeparator()],
            [sg.Column(insight_column)],
            [sg.StatusBar('Ready', key='-STATUS-')]
        ]
        
        return layout
    
    def create_main_window(self):
        """Create the main application window"""
        # File management frame
        file_frame = [
            [sg.Text('Conversation File:', font=('Arial', 10, 'bold'))],
            [sg.Input(key='-FILE-', enable_events=True, expand_x=True), 
             sg.FileBrowse(file_types=(("JSON files", "*.json"),))],
            [sg.Button('Load Conversations', key='-LOAD-'), 
             sg.Button('Reload', key='-RELOAD-')]
        ]
        
        # Conversation list frame
        conversation_frame = [
            [sg.Text('Conversations:', font=('Arial', 10, 'bold')),
             sg.Text('', key='-CONV-COUNT-', text_color='blue')],
            [sg.Listbox(values=[], key='-CONVERSATION-LIST-', 
                       enable_events=True, expand_x=True, expand_y=True, 
                       select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED)]
        ]
        
        # Search and filter frame
        search_frame = [
            [sg.Text('Search:', font=('Arial', 10, 'bold'))],
            [sg.Input(key='-SEARCH-', enable_events=True, expand_x=True)],
            [sg.Text('Date Range:')],
            [sg.Input(key='-START-DATE-', size=(12, 1)), 
             sg.Text('to'), 
             sg.Input(key='-END-DATE-', size=(12, 1)),
             sg.Button('Filter', key='-FILTER-')]
        ]
        
        # Statistics frame
        stats_frame = [
            [sg.Text('Statistics:', font=('Arial', 10, 'bold'))],
            [sg.Multiline(key='-STATUS-', size=(40, 8), disabled=True)]
        ]
        
        # Content display frame
        content_frame = [
            [sg.Text('Selected Conversation:', font=('Arial', 10, 'bold'))],
            [sg.Multiline(key='-CONTENT-', size=(60, 20), disabled=True, expand_x=True, expand_y=True)]
        ]
        
        # AI Features Tab
        ai_tab = [
            [sg.Frame('Conversation Summary', [
                [sg.Button('Summarize Selected', key='-SUMMARIZE-', disabled=True),
                 sg.Button('Summarize All', key='-SUMMARIZE-ALL-', disabled=True)],
                [sg.Multiline(key='-SUMMARY-', size=(70, 8), disabled=True)]
            ], expand_x=True)],
            
            [sg.Frame('Insight Generation', [
                [sg.Text('Ask a question about your conversations:')],
                [sg.Combo(values=[], key='-QUESTION-', size=(50, 1), enable_events=True),
                 sg.Button('Generate Insight', key='-INSIGHT-', disabled=True)],
                [sg.Multiline(key='-INSIGHT-RESULT-', size=(70, 12), disabled=True)]
            ], expand_x=True)],
            
            [sg.Frame('Export', [
                [sg.Button('Export Summaries', key='-EXPORT-SUMMARIES-', disabled=True),
                 sg.Button('Export Insight', key='-EXPORT-INSIGHT-', disabled=True)]
            ], expand_x=True)]
        ]
        
        # Analytics Tab (NEW)
        analytics_tab = [
            [sg.Frame('Analytics Overview', [
                [sg.Button('Generate Analytics', key='-GENERATE-ANALYTICS-', disabled=True),
                 sg.Button('Refresh Analytics', key='-REFRESH-ANALYTICS-', disabled=True)],
                [sg.Multiline(key='-ANALYTICS-SUMMARY-', size=(70, 8), disabled=True)]
            ], expand_x=True)],
            
            [sg.Frame('Visualizations', [
                [sg.Button('Sentiment Timeline', key='-SENTIMENT-CHART-', disabled=True),
                 sg.Button('Emotional Patterns', key='-EMOTIONAL-CHART-', disabled=True)],
                [sg.Button('Growth Metrics', key='-GROWTH-CHART-', disabled=True),
                 sg.Button('Topic Analysis', key='-TOPIC-CHART-', disabled=True)],
                [sg.Button('Create Dashboard', key='-CREATE-DASHBOARD-', disabled=True)]
            ], expand_x=True)],
            
            [sg.Frame('Phase 3 Advanced Features', [
                [sg.Button('Breakthrough Detection', key='-BREAKTHROUGH-DETECT-', disabled=True),
                 sg.Button('Writing Style Analysis', key='-WRITING-STYLE-', disabled=True)],
                [sg.Button('Goal Achievement Tracking', key='-GOAL-TRACKING-', disabled=True),
                 sg.Button('Concept Relationships', key='-CONCEPT-MAP-', disabled=True)]
            ], expand_x=True)],
            
            [sg.Frame('Data Export', [
                [sg.Button('Export Analytics (CSV)', key='-EXPORT-CSV-', disabled=True),
                 sg.Button('Export Analytics (JSON)', key='-EXPORT-JSON-', disabled=True)],
                [sg.Text('Export Status:', key='-EXPORT-STATUS-', text_color='green')]
            ], expand_x=True)]
        ]
        
        # Settings Tab
        settings_tab = [
            [sg.Frame('OpenAI API Configuration', [
                [sg.Text('API Key:'), sg.Input(self.config.get('openai_api_key', ''), key='-NEW_API_KEY-', size=(50, 1), password_char='*')],
                [sg.Button('Test API Key', key='-TEST_API_KEY-'), sg.Button('Save Settings', key='-SAVE_SETTINGS-')],
                [sg.Text('Model:'), sg.Combo(['gpt-4', 'gpt-3.5-turbo'], default_value=self.config.get('model', 'gpt-4'), key='-MODEL-', size=(20, 1))],
                [sg.Text('Max Tokens:'), sg.Spin([100, 200, 500, 1000, 1500, 2000, 5000], initial_value=self.config.get('max_tokens', 1500), key='-MAX_TOKENS-')],
                [sg.Text('Temperature:'), sg.Spin([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], initial_value=self.config.get('temperature', 0.7), key='-TEMPERATURE-')],
                [sg.Text('Status:', key='-API_STATUS-', text_color='red')]
            ], expand_x=True)]
        ]
        
        # ChatGPT Chat Tab
        chat_tab = [
            [sg.Frame('AI Chat Interface', [
                [sg.Multiline('Welcome to InsightVault Chat! Load conversations and start chatting with AI.\n\n', 
                             key='-CHAT_DISPLAY-', size=(70, 20), disabled=True, expand_x=True, expand_y=True)],
                [sg.Input(key='-CHAT_INPUT-', size=(60, 1), expand_x=True), sg.Button('Send', key='-SEND_CHAT-')],
                [sg.Button('Analyze Conversations', key='-ANALYZE_CONV-'), 
                 sg.Button('Programming Analysis', key='-PROG_ANALYSIS-'),
                 sg.Button('Growth Analysis', key='-GROWTH_ANALYSIS-'),
                 sg.Button('Clear Chat', key='-CLEAR_CHAT-')]
            ], expand_x=True, expand_y=True)]
        ]

        # Left column
        left_column = [
            [sg.Frame('File Management', file_frame, expand_x=True)],
            [sg.Frame('Search & Filter', search_frame, expand_x=True)],
            [sg.Frame('Statistics', stats_frame, expand_x=True, expand_y=True)]
        ]
        
        # Right column
        right_column = [
            [sg.Frame('Conversations', conversation_frame, expand_x=True, expand_y=True)],
            [sg.Frame('Content', content_frame, expand_x=True, expand_y=True)]
        ]
        
        # Main layout with tabs
        layout = [
            [sg.Column(left_column, vertical_alignment='top', expand_y=True),
             sg.Column(right_column, vertical_alignment='top', expand_x=True, expand_y=True)],
            [sg.TabGroup([[
                sg.Tab('AI Features', ai_tab),
                sg.Tab('Analytics', analytics_tab),  # NEW analytics tab
                sg.Tab('ChatGPT Chat', chat_tab),  # NEW chat tab
                sg.Tab('Settings', settings_tab) # NEW settings tab
            ]], expand_x=True, expand_y=True)]
        ]
        
        return sg.Window('InsightVault - Personal Growth Conversation Analyzer', 
                        layout, resizable=True, size=(1200, 800), finalize=True)
    
    def run(self):
        """Main application loop"""
        window = self.create_main_window()
        
        # Load sample questions if insight engine is available
        if self.insight_engine:
            from insight_engine import SAMPLE_QUESTIONS
            window['-QUESTION-'].update(values=SAMPLE_QUESTIONS)
        
        while True:
            event, values = window.read()
            
            if event == sg.WIN_CLOSED:
                break
            
            # File operations
            elif event == '-LOAD-' or event == '-FILE-':
                self.load_conversations(values['-FILE-'], window)
            
            elif event == '-RELOAD-':
                if values['-FILE-']:
                    self.load_conversations(values['-FILE-'], window)
            
            # Conversation selection
            elif event == '-CONVERSATION-LIST-':
                self.show_conversation_content(values['-CONVERSATION-LIST-'], window)
            
            # Search and filter
            elif event == '-SEARCH-':
                self.search_conversations(values['-SEARCH-'], window)
            
            elif event == '-FILTER-':
                self.filter_conversations(values['-START-DATE-'], values['-END-DATE-'], window)
            
            # AI Features
            elif event in ['-SUMMARIZE-', '-SUMMARIZE-ALL-', '-INSIGHT-', '-EXPORT-SUMMARIES-', '-EXPORT-INSIGHT-']:
                self.handle_ai_events(event, values, window)
            
            # Analytics Features (NEW)
            elif event in ['-GENERATE-ANALYTICS-', '-REFRESH-ANALYTICS-', '-SENTIMENT-CHART-', 
                          '-EMOTIONAL-CHART-', '-GROWTH-CHART-', '-TOPIC-CHART-', '-CREATE-DASHBOARD-',
                          '-BREAKTHROUGH-DETECT-', '-WRITING-STYLE-', '-GOAL-TRACKING-', '-CONCEPT-MAP-',
                          '-EXPORT-CSV-', '-EXPORT-JSON-']:
                self.handle_analytics_events(event, values, window)
            
            # ChatGPT Chat Events
            elif event == '-SEND_CHAT-':
                self.handle_chat_input(values['-CHAT_INPUT-'], window)
            elif event == '-ANALYZE_CONV-':
                self.handle_analyze_conversations(window)
            elif event == '-PROG_ANALYSIS-':
                self.handle_programming_analysis(window)
            elif event == '-GROWTH_ANALYSIS-':
                self.handle_growth_analysis(window)
            elif event == '-CLEAR_CHAT-':
                self.clear_chat_display(window)

            # Settings events
            elif event == '-TEST_API_KEY-':
                api_key = values['-NEW_API_KEY-']
                if self._test_api_key(api_key):
                    if window and window['-API_STATUS-']:
                        window['-API_STATUS-'].update(value='API Key is valid!')
                    sg.popup('API Key is valid!', title='API Key Test')
                else:
                    if window and window['-API_STATUS-']:
                        window['-API_STATUS-'].update(value='API Key is invalid!')
                    sg.popup_error('API Key is invalid. Please check your API key.', title='API Key Error')
            
            elif event == '-SAVE_SETTINGS-':
                # Update config with new values
                self.config['openai_api_key'] = values['-NEW_API_KEY-']
                self.config['model'] = values['-MODEL-']
                self.config['max_tokens'] = values['-MAX_TOKENS-']
                self.config['temperature'] = values['-TEMPERATURE-']
                
                if self._save_config(self.config):
                    # Reinitialize AI components with new config
                    self._initialize_ai_components()
                    if window and window['-API_STATUS-']:
                        window['-API_STATUS-'].update(value='Settings saved successfully!')
                    sg.popup('Settings saved successfully!', title='Settings Saved')
                else:
                    if window and window['-API_STATUS-']:
                        window['-API_STATUS-'].update(value='Error saving settings!')
                    sg.popup_error('Error saving settings!', title='Settings Error')
            
            # Phase 4: Performance features
            elif event in ['-PREV_PAGE-', '-NEXT_PAGE-']:
                self.handle_pagination_events(event, window)
        
        window.close()
    
    def _handle_load_conversations(self, window):
        """Handle loading conversations from file"""
        file_path = sg.popup_get_file(
            'Select conversations.json file',
            file_types=(('JSON Files', '*.json'), ('All Files', '*.*'))
        )
        
        if file_path:
            window['-STATUS-'].update('Loading conversations...')
            window.refresh()
            
            if self.parser.load_conversations(file_path):
                self.current_conversations = self.parser.conversations
                self.filtered_conversations = self.current_conversations.copy()
                
                # Update the conversation list
                self._update_conversation_list(window)
                self._update_tag_filter(window)
                
                stats = self.parser.get_stats()
                window['-STATUS-'].update(
                    f"Loaded {stats['total_conversations']} conversations "
                    f"({stats['total_messages']} messages)"
                )
                
                sg.popup(
                    f"Successfully loaded {len(self.current_conversations)} conversations!\n\n"
                    f"Date range: {stats['earliest_date'].strftime('%Y-%m-%d')} to "
                    f"{stats['latest_date'].strftime('%Y-%m-%d')}\n"
                    f"Total messages: {stats['total_messages']:,}\n"
                    f"Total characters: {stats['total_characters']:,}"
                )
            else:
                window['-STATUS-'].update('Failed to load conversations')
                sg.popup_error('Failed to load conversations. Please check the file format.')
    
    def _update_conversation_list(self, window):
        """Update the conversation list display"""
        conv_display = []
        for conv in self.filtered_conversations:
            title = conv.auto_title or conv.title
            date_str = conv.create_date.strftime('%Y-%m-%d')
            display_text = f"{date_str} | {title}"
            conv_display.append(display_text)
        
        window['-CONVERSATION-LIST-'].update(values=conv_display)
        window['-CONV-COUNT-'].update(f'Total: {len(self.filtered_conversations)} conversations')
    
    def _update_tag_filter(self, window):
        """Update the tag filter dropdown"""
        all_tags = set()
        for conv in self.current_conversations:
            all_tags.update(conv.tags)
        
        sorted_tags = ['All'] + sorted(all_tags)
        window['-TAG_FILTER-'].update(values=sorted_tags, value='All')
    
    def _handle_search(self, window, search_query: str):
        """Handle search functionality"""
        if not search_query.strip():
            self.filtered_conversations = self.current_conversations.copy()
        else:
            self.filtered_conversations = self.parser.search_conversations(search_query.strip())
        
        self._update_conversation_list(window)
    
    def _handle_tag_filter(self, window, selected_tag: str):
        """Handle tag filtering"""
        if selected_tag == 'All' or not selected_tag:
            self.filtered_conversations = self.current_conversations.copy()
        else:
            self.filtered_conversations = [
                conv for conv in self.current_conversations 
                if selected_tag in conv.tags
            ]
        
        self._update_conversation_list(window)
    
    def _handle_conversation_selection(self, window, selection):
        """Handle conversation selection from list"""
        if not selection:
            return
        
        # Find the selected conversation
        selected_index = window['-CONVERSATION-LIST-'].widget.curselection()[0]
        if selected_index < len(self.filtered_conversations):
            conv = self.filtered_conversations[selected_index]
            
            # Update details display
            window['-CONV_TITLE-'].update(conv.auto_title or conv.title)
            window['-CONV_DATE-'].update(conv.create_date.strftime('%Y-%m-%d %H:%M'))
            window['-CONV_TAGS-'].update(', '.join(conv.tags))
            window['-CONV_SUMMARY-'].update(conv.summary)
            window['-CONV_CONTENT-'].update(conv.get_full_text())
    
    def _handle_summarize_all(self, window):
        """Handle summarizing all conversations"""
        if not self.summarizer:
            if not self._try_initialize_ai_components():
                sg.popup_error(
                    "AI components not available. Please ensure you have:\n"
                    "1. Created config.json with your OpenAI API key\n"
                    "2. Installed the openai package"
                )
                return
        
        if not self.current_conversations:
            sg.popup_error("No conversations loaded. Please load conversations first.")
            return
        
        # Confirm action
        if not sg.popup_yes_no(f"Summarize {len(self.current_conversations)} conversations?\n"
                               "This may take a while and use OpenAI API credits."):
            return
        
        window['-STATUS-'].update('Summarizing conversations...')
        window['-PROGRESS-'].update(visible=True)
        
        def summarize_thread():
            try:
                results = self.summarizer.summarize_all_conversations(self.current_conversations)
                successful = sum(1 for success in results.values() if success)
                
                window.write_event_value('-SUMMARIZE_COMPLETE-', {
                    'successful': successful,
                    'total': len(self.current_conversations)
                })
            except Exception as e:
                window.write_event_value('-SUMMARIZE_ERROR-', str(e))
        
        threading.Thread(target=summarize_thread, daemon=True).start()
    
    def _handle_generate_insight(self, window, question: str) -> Optional[Dict[str, Any]]:
        """Handle insight generation"""
        if not self.insight_engine:
            if not self._try_initialize_ai_components():
                sg.popup_error("AI components not available. Please check your config.json file.")
                return None
        
        if not self.current_conversations:
            sg.popup_error("No conversations loaded. Please load conversations first.")
            return None
        
        if not question.strip():
            sg.popup_error("Please enter a question.")
            return None
        
        window['-STATUS-'].update('Generating insight...')
        window['-PROGRESS-'].update(visible=True)
        window['-GENERATE_INSIGHT-'].update(disabled=True)
        
        def insight_thread():
            try:
                result = self.insight_engine.generate_insight(question, self.current_conversations)
                window.write_event_value('-INSIGHT_COMPLETE-', result)
            except Exception as e:
                window.write_event_value('-INSIGHT_ERROR-', str(e))
        
        threading.Thread(target=insight_thread, daemon=True).start()
        return None  # Will be set when thread completes
    
    def _handle_export_summaries(self, window):
        """Handle exporting summaries"""
        if not self.summarizer:
            sg.popup_error("Summarizer not available. Please check your config.json file.")
            return
        
        if not self.current_conversations:
            sg.popup_error("No conversations loaded.")
            return
        
        output_path = sg.popup_get_file(
            'Save summaries as',
            save_as=True,
            file_types=(('Markdown Files', '*.md'), ('All Files', '*.*')),
            default_filename='summaries.md'
        )
        
        if output_path:
            if self.summarizer.export_summaries(self.current_conversations, output_path):
                sg.popup(f"Summaries exported to {output_path}")
                window['-STATUS-'].update(f"Exported summaries to {output_path}")
            else:
                sg.popup_error("Failed to export summaries.")
    
    def _handle_export_insight(self, window, insight_data: Dict[str, Any]):
        """Handle exporting insight"""
        if not self.insight_engine:
            sg.popup_error("Insight engine not available.")
            return
        
        output_path = sg.popup_get_file(
            'Save insight as',
            save_as=True,
            file_types=(('Markdown Files', '*.md'), ('All Files', '*.*')),
            default_filename=f"insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        
        if output_path:
            result_path = self.insight_engine.export_insight(insight_data, output_path)
            if result_path:
                sg.popup(f"Insight exported to {result_path}")
                window['-STATUS-'].update(f"Exported insight to {result_path}")
            else:
                sg.popup_error("Failed to export insight.")
    
    def _handle_clear_cache(self, window):
        """Handle clearing cache"""
        if sg.popup_yes_no("Clear all cached summaries and insights?\n"
                           "This will force regeneration of all AI content."):
            try:
                cache_dir = 'data/cache'
                if os.path.exists(cache_dir):
                    for file in os.listdir(cache_dir):
                        if file.endswith('.pkl'):
                            os.remove(os.path.join(cache_dir, file))
                
                sg.popup("Cache cleared successfully!")
                window['-STATUS-'].update("Cache cleared")
            except Exception as e:
                sg.popup_error(f"Error clearing cache: {e}")
    
    def _show_about_dialog(self):
        """Show about dialog"""
        about_text = """
InsightVault - Personal Growth Reflection Tool

A local desktop application that helps you explore and reflect on your personal growth using ChatGPT conversation exports.

Features:
• Import and parse ChatGPT conversations
• AI-powered summarization and tagging
• Search and filter conversations
• Generate deep insights and reflections
• Export insights and summaries

Version: 1.0
License: MIT
        """
        sg.popup(about_text, title='About InsightVault')

    def handle_analytics_events(self, event, values, window):
        """Handle analytics-related events"""
        if not self.analytics_engine:
            sg.popup_error('Analytics engine not available. Please check your configuration.')
            return
        
        if event == '-GENERATE-ANALYTICS-':
            self.generate_analytics(window)
        
        elif event == '-REFRESH-ANALYTICS-':
            self.generate_analytics(window, use_cache=False)
        
        elif event == '-SENTIMENT-CHART-':
            self.create_sentiment_chart()
        
        elif event == '-EMOTIONAL-CHART-':
            self.create_emotional_chart()
        
        elif event == '-GROWTH-CHART-':
            self.create_growth_chart()
        
        elif event == '-TOPIC-CHART-':
            self.create_topic_chart()
        
        elif event == '-CREATE-DASHBOARD-':
            self.create_dashboard()
        
        elif event == '-BREAKTHROUGH-DETECT-':
            self.create_breakthrough_analysis()
        
        elif event == '-WRITING-STYLE-':
            self.create_writing_style_analysis()
        
        elif event == '-GOAL-TRACKING-':
            self.create_goal_tracking_analysis()
        
        elif event == '-CONCEPT-MAP-':
            self.create_concept_relationship_analysis()
        
        elif event == '-EXPORT-CSV-':
            self.export_analytics('csv', window)
        
        elif event == '-EXPORT-JSON-':
            self.export_analytics('json', window)

    def generate_analytics(self, window, use_cache=True):
        """Generate comprehensive analytics for loaded conversations"""
        if not self.current_conversations:
            sg.popup_error('No conversations loaded. Please load conversations first.')
            return
        
        try:
            window['-GENERATE-ANALYTICS-'].update(disabled=True)
            window.refresh()
            
            # Generate analytics
            self.analytics_data = self.analytics_engine.analyze_conversations(
                self.current_conversations, use_cache=use_cache
            )
            
            # Update analytics summary
            summary = self.format_analytics_summary(self.analytics_data)
            window['-ANALYTICS-SUMMARY-'].update(summary)
            
            # Enable analytics buttons
            analytics_buttons = [
                '-REFRESH-ANALYTICS-', '-SENTIMENT-CHART-', '-EMOTIONAL-CHART-',
                '-GROWTH-CHART-', '-TOPIC-CHART-', '-CREATE-DASHBOARD-',
                '-BREAKTHROUGH-DETECT-', '-WRITING-STYLE-', '-GOAL-TRACKING-', '-CONCEPT-MAP-',
                '-EXPORT-CSV-', '-EXPORT-JSON-'
            ]
            
            for button in analytics_buttons:
                if button in window.AllKeysDict:
                    window[button].update(disabled=False)
            
            sg.popup('Analytics generated successfully!', title='Success')
            
        except Exception as e:
            sg.popup_error(f'Error generating analytics: {str(e)}')
        
        finally:
            window['-GENERATE-ANALYTICS-'].update(disabled=False)

    def format_analytics_summary(self, analytics_data):
        """Format analytics data for display in GUI"""
        if not analytics_data:
            return "No analytics data available."
        
        start_date = analytics_data.date_range[0].strftime('%Y-%m-%d')
        end_date = analytics_data.date_range[1].strftime('%Y-%m-%d')
        
        summary = f"""📊 ANALYTICS SUMMARY
─────────────────────────────

📈 Basic Statistics:
• Total Conversations: {analytics_data.conversation_count:,}
• Total Messages: {analytics_data.total_messages:,}
• Date Range: {start_date} to {end_date}
• Total Characters: {analytics_data.engagement_stats.get('total_characters', 0):,}

🏷️ Top Topics:
"""
        
        # Add top 5 tags
        for i, (tag, count) in enumerate(analytics_data.top_tags[:5], 1):
            summary += f"  {i}. {tag.title()}: {count} conversations\n"
        
        # Add growth metrics if available
        if analytics_data.growth_metrics:
            summary += f"\n📊 Growth Metrics:\n"
            for metric, value in list(analytics_data.growth_metrics.items())[:5]:
                direction = "↗️" if value > 0 else "↘️" if value < 0 else "➡️"
                metric_name = metric.replace('_growth', '').replace('_', ' ').title()
                summary += f"  {direction} {metric_name}: {value:.1%}\n"
        
        # Add engagement stats
        avg_gap = analytics_data.engagement_stats.get('avg_conversation_gap_days', 0)
        most_active = analytics_data.engagement_stats.get('most_active_month', 'N/A')
        
        summary += f"""
💬 Engagement Insights:
• Average days between conversations: {avg_gap:.1f}
• Most active month: {most_active}
• Average message length: {analytics_data.engagement_stats.get('avg_message_length', 0):.0f} chars

🎯 Ready for visualization and export!"""
        
        return summary

    def create_sentiment_chart(self):
        """Create and open sentiment timeline chart"""
        if not self.analytics_data or not self.analytics_data.sentiment_trends:
            sg.popup_error('No sentiment data available. Sentiment analysis may be disabled or no conversations found.')
            return
        
        try:
            chart_path = self.analytics_engine.create_sentiment_timeline_chart(
                self.analytics_data.sentiment_trends
            )
            
            if chart_path and os.path.exists(chart_path):
                import webbrowser
                webbrowser.open('file://' + os.path.abspath(chart_path))
                sg.popup(f'Sentiment timeline chart created!\nFile: {chart_path}', title='Chart Created')
            else:
                sg.popup_error('Failed to create sentiment chart.')
                
        except Exception as e:
            sg.popup_error(f'Error creating sentiment chart: {str(e)}')

    def create_emotional_chart(self):
        """Create and open emotional patterns chart"""
        if not self.analytics_data or not self.analytics_data.emotional_patterns:
            sg.popup_error('No emotional patterns data available.')
            return
        
        try:
            chart_path = self.analytics_engine.create_emotional_patterns_chart(
                self.analytics_data.emotional_patterns
            )
            
            if chart_path and os.path.exists(chart_path):
                import webbrowser
                webbrowser.open('file://' + os.path.abspath(chart_path))
                sg.popup(f'Emotional patterns chart created!\nFile: {chart_path}', title='Chart Created')
            else:
                sg.popup_error('Failed to create emotional patterns chart.')
                
        except Exception as e:
            sg.popup_error(f'Error creating emotional patterns chart: {str(e)}')

    def create_growth_chart(self):
        """Create and open growth metrics chart"""
        if not self.analytics_data or not self.analytics_data.growth_metrics:
            sg.popup_error('No growth metrics data available.')
            return
        
        try:
            chart_path = self.analytics_engine.create_growth_metrics_chart(
                self.analytics_data.growth_metrics
            )
            
            if chart_path and os.path.exists(chart_path):
                import webbrowser
                webbrowser.open('file://' + os.path.abspath(chart_path))
                sg.popup(f'Growth metrics chart created!\nFile: {chart_path}', title='Chart Created')
            else:
                sg.popup_error('Failed to create growth metrics chart.')
                
        except Exception as e:
            sg.popup_error(f'Error creating growth metrics chart: {str(e)}')

    def create_topic_chart(self):
        """Create and open topic analysis chart"""
        if not self.analytics_data or not self.analytics_data.top_tags:
            sg.popup_error('No topic data available.')
            return
        
        try:
            chart_path = self.analytics_engine.create_tag_analysis_chart(
                self.analytics_data.top_tags
            )
            
            if chart_path and os.path.exists(chart_path):
                import webbrowser
                webbrowser.open('file://' + os.path.abspath(chart_path))
                sg.popup(f'Topic analysis chart created!\nFile: {chart_path}', title='Chart Created')
            else:
                sg.popup_error('Failed to create topic analysis chart.')
                
        except Exception as e:
            sg.popup_error(f'Error creating topic analysis chart: {str(e)}')

    def create_dashboard(self):
        """Create and open comprehensive analytics dashboard"""
        if not self.analytics_data:
            sg.popup_error('No analytics data available. Please generate analytics first.')
            return
        
        try:
            dashboard_path = self.analytics_engine.create_comprehensive_dashboard(
                self.analytics_data
            )
            
            if dashboard_path and os.path.exists(dashboard_path):
                import webbrowser
                webbrowser.open('file://' + os.path.abspath(dashboard_path))
                sg.popup(f'Analytics dashboard created!\nFile: {dashboard_path}', title='Dashboard Created')
            else:
                sg.popup_error('Failed to create analytics dashboard.')
                
        except Exception as e:
            sg.popup_error(f'Error creating analytics dashboard: {str(e)}')
    
    def create_breakthrough_analysis(self):
        """Create breakthrough moments analysis"""
        if not self.analytics_data:
            sg.popup_error('No analytics data available. Please generate analytics first.')
            return
        
        try:
            breakthroughs = self.analytics_data.breakthrough_moments
            
            if not breakthroughs:
                sg.popup('No breakthrough moments detected in your conversations.', title='Breakthrough Analysis')
                return
            
            # Create breakthrough report
            report = "🔍 BREAKTHROUGH MOMENTS DETECTED\n\n"
            report += f"Total breakthroughs found: {len(breakthroughs)}\n\n"
            
            for i, breakthrough in enumerate(breakthroughs[:5], 1):
                report += f"{i}. {breakthrough['title']}\n"
                report += f"   Date: {breakthrough['date'][:10]}\n"
                report += f"   Score: {breakthrough['breakthrough_score']:.1f}\n"
                report += f"   Keywords: {', '.join(breakthrough['detected_keywords'][:3])}\n"
                report += f"   Summary: {breakthrough['summary']}\n\n"
            
            # Save report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_path = f"output/breakthrough_analysis_{timestamp}.txt"
            
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            sg.popup(f'Breakthrough analysis completed!\nReport saved to: {report_path}', title='Breakthrough Analysis')
            
        except Exception as e:
            sg.popup_error(f'Error creating breakthrough analysis: {str(e)}')
    
    def create_writing_style_analysis(self):
        """Create writing style evolution analysis"""
        if not self.analytics_data:
            sg.popup_error('No analytics data available. Please generate analytics first.')
            return
        
        try:
            style_data = self.analytics_data.writing_style_evolution
            
            if not style_data:
                sg.popup('No writing style data available for analysis.', title='Writing Style Analysis')
                return
            
            # Create writing style report
            report = "✍️ WRITING STYLE EVOLUTION ANALYSIS\n\n"
            
            for period, metrics in style_data.items():
                report += f"📊 {period.upper()} PERIOD:\n"
                for metric, value in metrics.items():
                    if isinstance(value, float):
                        report += f"   {metric.replace('_', ' ').title()}: {value:.3f}\n"
                    else:
                        report += f"   {metric.replace('_', ' ').title()}: {value}\n"
                report += "\n"
            
            # Save report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_path = f"output/writing_style_analysis_{timestamp}.txt"
            
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            sg.popup(f'Writing style analysis completed!\nReport saved to: {report_path}', title='Writing Style Analysis')
            
        except Exception as e:
            sg.popup_error(f'Error creating writing style analysis: {str(e)}')
    
    def create_goal_tracking_analysis(self):
        """Create goal achievement tracking analysis"""
        if not self.analytics_data:
            sg.popup_error('No analytics data available. Please generate analytics first.')
            return
        
        try:
            goal_data = self.analytics_data.goal_achievement
            
            if not goal_data:
                sg.popup('No goal achievement data available for analysis.', title='Goal Tracking Analysis')
                return
            
            # Create goal tracking report
            report = "🎯 GOAL ACHIEVEMENT TRACKING\n\n"
            report += f"Total goals mentioned: {goal_data.get('total_goals_mentioned', 0)}\n"
            report += f"Total achievements: {goal_data.get('total_achievements', 0)}\n"
            report += f"Achievement rate: {goal_data.get('achievement_rate', 0):.1%}\n\n"
            
            if goal_data.get('goal_mentions'):
                report += "📋 RECENT GOAL MENTIONS:\n"
                for goal in goal_data['goal_mentions'][:5]:
                    report += f"   • {goal['title']} ({goal['date'][:10]})\n"
                report += "\n"
            
            if goal_data.get('achievement_patterns'):
                report += "🏆 RECENT ACHIEVEMENTS:\n"
                for achievement in goal_data['achievement_patterns'][:5]:
                    report += f"   • {achievement['title']} ({achievement['date'][:10]})\n"
                report += "\n"
            
            # Save report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_path = f"output/goal_tracking_analysis_{timestamp}.txt"
            
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            sg.popup(f'Goal tracking analysis completed!\nReport saved to: {report_path}', title='Goal Tracking Analysis')
            
        except Exception as e:
            sg.popup_error(f'Error creating goal tracking analysis: {str(e)}')
    
    def create_concept_relationship_analysis(self):
        """Create concept relationship analysis"""
        if not self.analytics_data:
            sg.popup_error('No analytics data available. Please generate analytics first.')
            return
        
        try:
            concept_data = self.analytics_data.concept_relationships
            
            if not concept_data:
                sg.popup('No concept relationship data available for analysis.', title='Concept Relationship Analysis')
                return
            
            # Create concept relationship report
            report = "🧠 CONCEPT RELATIONSHIP ANALYSIS\n\n"
            
            if concept_data.get('top_concepts'):
                report += "🔝 TOP CONCEPTS:\n"
                for i, concept in enumerate(concept_data['top_concepts'][:10], 1):
                    report += f"   {i}. {concept}\n"
                report += "\n"
            
            if concept_data.get('concept_clusters'):
                report += "📊 CONCEPT CLUSTERS:\n"
                for cluster_name, cluster_data in concept_data['concept_clusters'].items():
                    report += f"   {cluster_name} ({cluster_data['size']} conversations):\n"
                    for topic in cluster_data['topics'][:3]:
                        report += f"     • {topic}\n"
                    report += "\n"
            
            # Save report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_path = f"output/concept_relationship_analysis_{timestamp}.txt"
            
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            sg.popup(f'Concept relationship analysis completed!\nReport saved to: {report_path}', title='Concept Relationship Analysis')
            
        except Exception as e:
            sg.popup_error(f'Error creating concept relationship analysis: {str(e)}')

    def export_analytics(self, format_type, window):
        """Export analytics data in specified format"""
        if not self.analytics_data:
            sg.popup_error('No analytics data available. Please generate analytics first.')
            return
        
        try:
            export_path = self.analytics_engine.export_analytics_data(
                self.analytics_data, format=format_type
            )
            
            if export_path and os.path.exists(export_path):
                window['-EXPORT-STATUS-'].update(f'Exported: {os.path.basename(export_path)}')
                sg.popup(f'Analytics data exported successfully!\nFile: {export_path}', title='Export Complete')
            else:
                sg.popup_error(f'Failed to export analytics data as {format_type.upper()}.')
                
        except Exception as e:
            sg.popup_error(f'Error exporting analytics data: {str(e)}')

    # Bridge methods for new interface compatibility
    def load_conversations(self, file_path, window):
        """Load conversations from file using paginated loader"""
        if file_path and os.path.exists(file_path):
            window['-STATUS-'].update('Loading conversations...')
            window.refresh()
            
            # Use paginated loader for better performance
            if paginated_loader.load_conversations_from_file(file_path):
                self.current_page = 0
                conversations, page_info = paginated_loader.load_page(0)
                self.current_conversations = conversations
                self.total_pages = page_info.total_pages
                
                # Update conversation list
                self._update_conversation_list(window)
                
                # Update status with performance info
                stats = paginated_loader.get_stats()
                memory_stats = memory_optimizer.get_memory_stats()
                window['-STATUS-'].update(
                    f'Loaded {len(self.current_conversations)} conversations '
                    f'(Page 1/{self.total_pages}) | '
                    f'Memory: {memory_stats["rss"] // (1024*1024)}MB'
                )
            else:
                window['-STATUS-'].update('Error loading conversations')

    def show_conversation_content(self, selection, window):
        """Show content of selected conversations"""
        self._handle_conversation_selection(window, selection)

    def search_conversations(self, query, window):
        """Search conversations using optimized search engine"""
        if not query.strip():
            return
        
        window['-STATUS-'].update('Searching...')
        window.refresh()
        
        try:
            # Use search manager for fast search
            search_results = search_manager.search(query, limit=50)
            
            if search_results:
                self.search_results = search_results
                conversations = [result.conversation for result in search_results]
                self.current_conversations = conversations
                
                # Update conversation list with search results
                conv_list = []
                for i, result in enumerate(search_results):
                    score_text = f"[{result.score:.1f}] "
                    conv_list.append(f"{score_text}{result.conversation.title}")
                
                window['-CONVERSATION-LIST-'].update(values=conv_list)
                window['-CONV-COUNT-'].update(f'Found {len(search_results)} results')
                window['-STATUS-'].update(f'Search completed: {len(search_results)} results found')
            else:
                window['-CONVERSATION-LIST-'].update(values=[])
                window['-CONV-COUNT-'].update('No results found')
                window['-STATUS-'].update('Search completed: No results found')
                
        except Exception as e:
            window['-STATUS-'].update(f'Search error: {str(e)}')
            sg.popup_error(f'Search error: {str(e)}')

    def filter_conversations(self, start_date, end_date, window):
        """Filter conversations by date range"""
        # Simple implementation - can be enhanced later
        if start_date or end_date:
            sg.popup('Date filtering not yet implemented in analytics interface')

    def handle_ai_events(self, event, values, window):
        """Handle AI-related events"""
        if event == '-SUMMARIZE-ALL-':
            self._handle_summarize_all(window)
        elif event == '-EXPORT-SUMMARIES-':
            self._handle_export_summaries(window)
        elif event == '-INSIGHT-':
            question = values.get('-QUESTION-', '')
            self._handle_generate_insight(window, question)
        else:
            sg.popup('AI event handling not yet fully implemented')
    
    def handle_pagination_events(self, event, window):
        """Handle pagination events"""
        if event == '-PREV_PAGE-':
            if self.current_page > 0:
                self.current_page -= 1
                self._load_page(window)
        elif event == '-NEXT_PAGE-':
            if self.current_page < self.total_pages - 1:
                self.current_page += 1
                self._load_page(window)
    
    def _load_page(self, window):
        """Load a specific page of conversations"""
        window['-STATUS-'].update(f'Loading page {self.current_page + 1}...')
        window.refresh()
        
        try:
            conversations, page_info = paginated_loader.load_page(self.current_page)
            self.current_conversations = conversations
            
            # Update conversation list
            conv_list = [conv.title for conv in conversations]
            window['-CONVERSATION-LIST-'].update(values=conv_list)
            
            # Update pagination controls
            window['-PAGE_INFO-'].update(f'Page {page_info.page_number + 1}/{page_info.total_pages}')
            window['-PREV_PAGE-'].update(disabled=not page_info.has_previous)
            window['-NEXT_PAGE-'].update(disabled=not page_info.has_next)
            window['-CONV-COUNT-'].update(f'Page {page_info.page_number + 1}: {len(conversations)} conversations')
            
            # Update performance info
            memory_stats = memory_optimizer.get_memory_stats()
            window['-MEMORY_INFO-'].update(f'Memory: {memory_stats["rss"] // (1024*1024)}MB')
            window['-STATUS-'].update(f'Page {page_info.page_number + 1} loaded successfully')
            
        except Exception as e:
            window['-STATUS-'].update(f'Error loading page: {str(e)}')
            sg.popup_error(f'Error loading page: {str(e)}')

    def handle_chat_input(self, input_text, window):
        """Handle user input in the ChatGPT chat tab"""
        if not input_text.strip():
            return
        
        window['-CHAT_INPUT-'].update('') # Clear input field
        window['-CHAT_DISPLAY-'].update(window['-CHAT_DISPLAY-'].get() + f"You: {input_text}\n")
        window['-CHAT_DISPLAY-'].update(window['-CHAT_DISPLAY-'].get() + "InsightVault: Thinking...\n")
        window['-CHAT_DISPLAY-'].update(window['-CHAT_DISPLAY-'].get() + "InsightVault: ") # Indicate thinking
        window.refresh()

        # Simulate AI thinking
        time.sleep(1) # Simulate network delay

        # In a real application, you would send this to your backend
        # For now, we'll just append a placeholder response
        window['-CHAT_DISPLAY-'].update(window['-CHAT_DISPLAY-'].get() + "This is a placeholder response.\n")
        window['-CHAT_DISPLAY-'].update(window['-CHAT_DISPLAY-'].get() + "InsightVault: ") # Indicate thinking
        window.refresh()

    def handle_analyze_conversations(self, window):
        """Placeholder for analyzing conversations"""
        sg.popup("Analyze Conversations functionality not yet implemented.")

    def handle_programming_analysis(self, window):
        """Placeholder for programming analysis"""
        sg.popup("Programming Analysis functionality not yet implemented.")

    def handle_growth_analysis(self, window):
        """Placeholder for growth analysis"""
        sg.popup("Growth Analysis functionality not yet implemented.")

    def clear_chat_display(self, window):
        """Clear the chat display"""
        window['-CHAT_DISPLAY-'].update('')
        window['-CHAT_INPUT-'].update('')
        window['-CHAT_DISPLAY-'].update("Welcome to InsightVault Chat! Load conversations and start chatting with AI.\n\n")
        window.refresh()


def main():
    """Main entry point for the GUI application"""
    try:
        app = InsightVaultGUI()
        app.run()
    except Exception as e:
        sg.popup_error(f"Failed to start application: {e}")


if __name__ == "__main__":
    main()