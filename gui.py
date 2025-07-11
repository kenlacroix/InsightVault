"""
GUI Interface for InsightVault
Uses PySimpleGUI to provide a user-friendly interface for exploring conversations and generating insights
"""

import os
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
import PySimpleGUI as sg
from chat_parser import ChatParser, Conversation
from summarizer import ConversationSummarizer
from insight_engine import InsightEngine, SAMPLE_QUESTIONS


class InsightVaultGUI:
    """Main GUI application for InsightVault"""
    
    def __init__(self):
        self.parser = ChatParser()
        self.summarizer = None
        self.insight_engine = None
        self.current_conversations: List[Conversation] = []
        self.filtered_conversations: List[Conversation] = []
        
        # Set up PySimpleGUI theme
        sg.theme('DarkBlue3')
        
        # Initialize components when config is available
        self._try_initialize_ai_components()
    
    def _try_initialize_ai_components(self):
        """Try to initialize AI components if config exists"""
        try:
            if os.path.exists('config.json'):
                self.summarizer = ConversationSummarizer()
                self.insight_engine = InsightEngine()
                return True
        except Exception as e:
            print(f"Warning: Could not initialize AI components: {e}")
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
                key='-CONV_LIST-', 
                size=(50, 20), 
                enable_events=True,
                horizontal_scroll=True
            )],
            [sg.Text('Total: 0 conversations', key='-CONV_COUNT-')]
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
    
    def run(self):
        """Run the main GUI application"""
        layout = self.create_main_layout()
        window = sg.Window('InsightVault - Personal Growth Reflection Tool', 
                          layout, 
                          resizable=True, 
                          finalize=True)
        
        # Store current insight for export
        current_insight = None
        
        while True:
            event, values = window.read()
            
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            
            try:
                if event == 'Load Conversations':
                    self._handle_load_conversations(window)
                
                elif event == '-SEARCH-':
                    self._handle_search(window, values['-SEARCH-'])
                
                elif event == '-TAG_FILTER-':
                    self._handle_tag_filter(window, values['-TAG_FILTER-'])
                
                elif event == '-CONV_LIST-':
                    self._handle_conversation_selection(window, values['-CONV_LIST-'])
                
                elif event == 'Summarize All':
                    self._handle_summarize_all(window)
                
                elif event == 'Export Summaries':
                    self._handle_export_summaries(window)
                
                elif event == '-GENERATE_INSIGHT-':
                    current_insight = self._handle_generate_insight(window, values['-QUESTION-'])
                
                elif event == '-EXPORT_INSIGHT-':
                    if current_insight:
                        self._handle_export_insight(window, current_insight)
                
                elif event == 'Clear Cache':
                    self._handle_clear_cache(window)
                
                elif event == 'About':
                    self._show_about_dialog()
            
            except Exception as e:
                sg.popup_error(f"An error occurred: {str(e)}")
                window['-STATUS-'].update(f"Error: {str(e)}")
        
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
        
        window['-CONV_LIST-'].update(values=conv_display)
        window['-CONV_COUNT-'].update(f'Total: {len(self.filtered_conversations)} conversations')
    
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
        selected_index = window['-CONV_LIST-'].widget.curselection()[0]
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


def main():
    """Main entry point for the GUI application"""
    try:
        app = InsightVaultGUI()
        app.run()
    except Exception as e:
        sg.popup_error(f"Failed to start application: {e}")


if __name__ == "__main__":
    main()