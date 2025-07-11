#!/usr/bin/env python3
"""
InsightVault - Personal Growth Reflection Tool
Main application launcher

Usage:
    python main.py                  # Launch GUI
    python main.py --cli            # Use command line interface
    python main.py --help           # Show help
"""

import sys
import argparse
import os
from typing import Optional

def setup_environment():
    """Set up the environment and check dependencies"""
    # Check for required config file
    if not os.path.exists('config.json'):
        if os.path.exists('config.json.example'):
            print("⚠️  Config file not found!")
            print("Please copy config.json.example to config.json and add your OpenAI API key.")
            print("\nExample:")
            print("cp config.json.example config.json")
            print("# Then edit config.json with your API key")
            return False
        else:
            print("⚠️  No config file found. Please create config.json with your OpenAI API key.")
            return False
    
    # Check for data directory
    os.makedirs('data/cache', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    
    return True

def run_gui():
    """Launch the GUI application"""
    try:
        from gui import main as gui_main
        print("🚀 Launching InsightVault GUI...")
        gui_main()
    except ImportError as e:
        print(f"❌ Error importing GUI components: {e}")
        print("Please install required dependencies:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        return False
    
    return True

def run_cli():
    """Run basic CLI interface for testing"""
    try:
        from chat_parser import ChatParser
        from summarizer import ConversationSummarizer
        from insight_engine import InsightEngine
        
        print("🧠 InsightVault Command Line Interface")
        print("=" * 50)
        
        # Load conversations
        conv_file = input("Enter path to conversations.json file: ").strip()
        if not conv_file:
            conv_file = "data/sample_conversations.json"
        
        parser = ChatParser()
        if not parser.load_conversations(conv_file):
            print("❌ Failed to load conversations")
            return False
        
        print(f"✅ Loaded {len(parser.conversations)} conversations")
        
        # Show options
        while True:
            print("\nOptions:")
            print("1. List conversations")
            print("2. Search conversations") 
            print("3. Summarize conversations")
            print("4. Generate insight")
            print("5. Export summaries")
            print("6. Exit")
            
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == "1":
                for i, conv in enumerate(parser.conversations):
                    print(f"{i+1}. {conv.title} ({conv.create_date.strftime('%Y-%m-%d')})")
            
            elif choice == "2":
                query = input("Search query: ").strip()
                results = parser.search_conversations(query)
                print(f"Found {len(results)} matching conversations:")
                for conv in results:
                    print(f"  - {conv.title}")
            
            elif choice == "3":
                summarizer = ConversationSummarizer()
                print("Summarizing conversations...")
                results = summarizer.summarize_all_conversations(parser.conversations)
                successful = sum(1 for success in results.values() if success)
                print(f"✅ Summarized {successful}/{len(parser.conversations)} conversations")
            
            elif choice == "4":
                engine = InsightEngine()
                question = input("Enter your reflective question: ").strip()
                if question:
                    print("Generating insight...")
                    result = engine.generate_insight(question, parser.conversations)
                    print(f"\n📝 Insight for: {result['question']}")
                    print("=" * 50)
                    print(result['insight'])
                    if result['themes']:
                        print(f"\n🏷️  Themes: {', '.join(result['themes'])}")
            
            elif choice == "5":
                summarizer = ConversationSummarizer()
                output_path = input("Output file (default: output/summaries.md): ").strip()
                if not output_path:
                    output_path = "output/summaries.md"
                
                if summarizer.export_summaries(parser.conversations, output_path):
                    print(f"✅ Summaries exported to {output_path}")
                else:
                    print("❌ Failed to export summaries")
            
            elif choice == "6":
                break
            
            else:
                print("Invalid choice. Please enter 1-6.")
        
    except ImportError as e:
        print(f"❌ Error importing components: {e}")
        print("Please install required dependencies:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error in CLI: {e}")
        return False
    
    return True

def show_help():
    """Show help information"""
    help_text = """
🧠 InsightVault - Personal Growth Reflection Tool

DESCRIPTION:
    A local desktop application that helps you explore and reflect on your 
    personal growth using exported ChatGPT conversations.

SETUP:
    1. Install dependencies:
       pip install -r requirements.txt
    
    2. Configure API key:
       cp config.json.example config.json
       # Edit config.json with your OpenAI API key
    
    3. Prepare your data:
       # Export conversations from ChatGPT and place in data/ folder
       # Or use the provided sample data

USAGE:
    python main.py              # Launch GUI (recommended)
    python main.py --cli        # Use command line interface
    python main.py --help       # Show this help

FEATURES:
    • Import and parse ChatGPT conversations
    • AI-powered summarization and tagging  
    • Search and filter conversations
    • Generate deep insights and reflections
    • Export insights and summaries to Markdown

FILES:
    • conversations.json        # Your ChatGPT export file
    • config.json              # API configuration
    • data/                     # Data and cache directory
    • output/                   # Generated insights and summaries

SAMPLE QUESTIONS:
    • "How have I grown spiritually over time?"
    • "What emotional patterns have I been working through?"
    • "How has my relationship with anxiety evolved?"
    • "What insights have I gained about my life purpose?"

For more information, see the README.md file.
    """
    print(help_text)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='InsightVault - Personal Growth Reflection Tool')
    parser.add_argument('--cli', action='store_true', help='Use command line interface')
    parser.add_argument('--help-detailed', action='store_true', help='Show detailed help')
    
    args = parser.parse_args()
    
    if args.help_detailed:
        show_help()
        return
    
    # Show banner
    print("🧠 InsightVault - Personal Growth Reflection Tool")
    print("=" * 55)
    
    # Set up environment
    if not setup_environment():
        print("\n❌ Environment setup failed. Please fix the issues above and try again.")
        return
    
    # Run appropriate interface
    if args.cli:
        success = run_cli()
    else:
        success = run_gui()
    
    if success:
        print("\n✅ Thank you for using InsightVault!")
    else:
        print("\n❌ Application exited with errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()