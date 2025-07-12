"""
AI Assistant Integration for InsightVault
Phase 1: Integration with Existing Application

Integrates the AI assistant functionality into the existing InsightVault application,
providing seamless access to both traditional analytics and AI-powered insights.
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
import webbrowser
import threading
import time

# Import existing components
from chat_parser import ChatParser
from analytics_engine import AnalyticsEngine
from dashboard import AdvancedDashboard

# Import AI assistant components
from enhanced_chat_parser import EnhancedChatParser
from ai_assistant import AIAssistant
from ai_assistant_interface import AIAssistantInterface


class InsightVaultWithAI:
    """Enhanced InsightVault with AI assistant integration"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize existing components
        self.chat_parser = ChatParser()
        self.analytics_engine = AnalyticsEngine(config_path)
        self.dashboard = AdvancedDashboard(config_path)
        
        # Initialize AI components
        self.enhanced_parser = EnhancedChatParser()
        self.ai_assistant = AIAssistant(config_path)
        self.ai_interface = AIAssistantInterface(config_path)
        
        # State management
        self.conversations_loaded = False
        self.ai_ready = False
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'ai_assistant': {
                    'enabled': True,
                    'port': 8051,
                    'auto_start': False
                },
                'dashboard': {
                    'port': 8050,
                    'auto_start': False
                }
            }
    
    def load_conversations(self, file_path: str) -> bool:
        """Load conversations for both traditional and AI analysis"""
        print("Loading conversations for InsightVault with AI...")
        
        # Load for traditional analysis
        success1 = self.chat_parser.load_conversations(file_path)
        if success1:
            self.dashboard.load_conversations(self.chat_parser.conversations)
            print(f"✓ Loaded {len(self.chat_parser.conversations)} conversations for traditional analysis")
        
        # Load for AI analysis
        success2 = self.ai_assistant.load_conversations(file_path)
        if success2:
            self.ai_interface.load_conversations(file_path)
            print(f"✓ Loaded {len(self.ai_assistant.conversations)} conversations for AI analysis")
        
        self.conversations_loaded = success1 or success2
        self.ai_ready = success2
        
        if self.conversations_loaded:
            print("✓ Conversations loaded successfully")
            return True
        else:
            print("✗ Failed to load conversations")
            return False
    
    def start_dashboard(self, port: int = 8050) -> str:
        """Start the traditional analytics dashboard"""
        if not self.conversations_loaded:
            print("⚠️ No conversations loaded. Please load conversations first.")
            return ""
        
        print(f"Starting traditional dashboard on port {port}...")
        
        # Run dashboard in a separate thread
        def run_dashboard():
            self.dashboard.run_server(port=port, debug=False)
        
        dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        dashboard_thread.start()
        
        # Wait a moment for the server to start
        time.sleep(2)
        
        url = f"http://127.0.0.1:{port}"
        print(f"✓ Traditional dashboard started at {url}")
        return url
    
    def start_ai_assistant(self, port: int = 8051) -> str:
        """Start the AI assistant interface"""
        if not self.ai_ready:
            print("⚠️ AI assistant not ready. Please load conversations first.")
            return ""
        
        print(f"Starting AI assistant on port {port}...")
        
        # Run AI interface in a separate thread
        def run_ai_interface():
            self.ai_interface.run_server(port=port, debug=False)
        
        ai_thread = threading.Thread(target=run_ai_interface, daemon=True)
        ai_thread.start()
        
        # Wait a moment for the server to start
        time.sleep(2)
        
        url = f"http://127.0.0.1:{port}"
        print(f"✓ AI assistant started at {url}")
        return url
    
    def start_both_interfaces(self) -> Dict[str, str]:
        """Start both traditional dashboard and AI assistant"""
        urls = {}
        
        # Start traditional dashboard
        dashboard_url = self.start_dashboard()
        if dashboard_url:
            urls['dashboard'] = dashboard_url
        
        # Start AI assistant
        ai_url = self.start_ai_assistant()
        if ai_url:
            urls['ai_assistant'] = ai_url
        
        return urls
    
    def process_ai_query(self, query: str) -> str:
        """Process a query through the AI assistant"""
        if not self.ai_ready:
            return "AI assistant not ready. Please load conversations first."
        
        try:
            insight = self.ai_assistant.process_query(query)
            return self.ai_assistant.format_insight_response(insight)
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the system"""
        return {
            'conversations_loaded': self.conversations_loaded,
            'ai_ready': self.ai_ready,
            'conversation_count': len(self.chat_parser.conversations) if self.conversations_loaded else 0,
            'ai_conversation_count': len(self.ai_assistant.conversations) if self.ai_ready else 0,
            'config': self.config
        }
    
    def export_insights(self, output_path: Optional[str] = None) -> str:
        """Export insights from both traditional and AI analysis"""
        if not self.conversations_loaded:
            return "No conversations loaded"
        
        if not output_path:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = f"insightvault_export_{timestamp}.json"
        
        try:
            export_data = {
                'export_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                'conversation_count': len(self.chat_parser.conversations),
                'ai_ready': self.ai_ready,
                'traditional_analytics': {
                    'stats': self.chat_parser.get_stats() if self.conversations_loaded else {},
                },
                'ai_insights': {
                    'available': self.ai_ready,
                    'conversation_count': len(self.ai_assistant.conversations) if self.ai_ready else 0
                }
            }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✓ Insights exported to {output_path}")
            return output_path
            
        except Exception as e:
            print(f"✗ Export failed: {e}")
            return ""


def main():
    """Main function for InsightVault with AI"""
    print("🧠 InsightVault with AI Assistant")
    print("=" * 50)
    
    # Initialize the enhanced system
    insightvault = InsightVaultWithAI()
    
    # Check for conversation file
    conversation_file = 'data/conversations.json'
    if os.path.exists(conversation_file):
        print(f"Found conversation file: {conversation_file}")
        success = insightvault.load_conversations(conversation_file)
        
        if success:
            print("\n🎉 InsightVault with AI is ready!")
            print("\nAvailable options:")
            print("1. Start traditional dashboard only")
            print("2. Start AI assistant only")
            print("3. Start both interfaces")
            print("4. Process a single AI query")
            print("5. Export insights")
            print("6. Exit")
            
            while True:
                try:
                    choice = input("\nEnter your choice (1-6): ").strip()
                    
                    if choice == '1':
                        url = insightvault.start_dashboard()
                        if url:
                            print(f"Opening dashboard at {url}")
                            webbrowser.open(url)
                    
                    elif choice == '2':
                        url = insightvault.start_ai_assistant()
                        if url:
                            print(f"Opening AI assistant at {url}")
                            webbrowser.open(url)
                    
                    elif choice == '3':
                        urls = insightvault.start_both_interfaces()
                        if urls:
                            print("Opening both interfaces...")
                            for name, url in urls.items():
                                print(f"  {name}: {url}")
                                webbrowser.open(url)
                    
                    elif choice == '4':
                        query = input("Enter your question: ").strip()
                        if query:
                            print("\n" + "="*50)
                            response = insightvault.process_ai_query(query)
                            print(response)
                            print("="*50)
                    
                    elif choice == '5':
                        output_file = insightvault.export_insights()
                        if output_file and output_file != "No conversations loaded":
                            print(f"Insights exported to: {output_file}")
                    
                    elif choice == '6':
                        print("Goodbye!")
                        break
                    
                    else:
                        print("Invalid choice. Please enter 1-6.")
                
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break
                except Exception as e:
                    print(f"Error: {e}")
        
        else:
            print("Failed to load conversations. Please check your data file.")
    else:
        print(f"Conversation file not found: {conversation_file}")
        print("Please place your ChatGPT conversation export in the data/ folder.")
        print("You can still use the AI assistant with the interface directly.")


if __name__ == "__main__":
    main()