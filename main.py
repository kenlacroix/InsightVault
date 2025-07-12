#!/usr/bin/env python3
"""
InsightVault - Personal Growth Reflection Tool
Main application launcher

Provides both GUI and CLI interfaces for exploring ChatGPT conversations
and generating personal growth insights.
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def setup_environment():
    """Set up the application environment"""
    print("🔧 Setting up InsightVault environment...")
    
    # Create necessary directories
    directories = ['data', 'data/cache', 'data/analytics_cache', 'output']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Check for config file
    config_path = 'config.json'
    if not os.path.exists(config_path):
        if os.path.exists('config.json.example'):
            print("⚠️  No config.json found. Please copy config.json.example to config.json and add your OpenAI API key.")
            print("   You can still use the application for basic features without AI capabilities.")
        else:
            print("⚠️  No config.json.example found. Please create a config.json file with your OpenAI API key.")
    
    # Check for sample data
    sample_data_path = 'data/sample_conversations.json'
    if not os.path.exists(sample_data_path):
        print("⚠️  No sample data found. You can still load your own conversations.")
    
    print("✅ Environment setup complete!")
    return True


def run_unified_dashboard():
    """Launch the unified web dashboard"""
    try:
        from dashboard import UnifiedDashboard
        
        print("🚀 Launching InsightVault Unified Dashboard...")
        print("📊 This is the new, beautiful web interface!")
        print("🌐 The dashboard will open in your default browser.")
        print("📁 You can upload your conversations.json file directly in the dashboard.")
        
        # Create dashboard instance
        dashboard = UnifiedDashboard()
        
        # Try to load sample data if available
        sample_path = 'data/sample_conversations.json'
        if os.path.exists(sample_path):
            from chat_parser import ChatParser
            parser = ChatParser()
            if parser.load_conversations(sample_path):
                dashboard.load_conversations(parser.conversations)
                print(f"📈 Loaded {len(parser.conversations)} sample conversations")
        
        # Run the dashboard
        dashboard.run_server(debug=False)
        return True
        
    except ImportError as e:
        print(f"❌ Error importing dashboard components: {e}")
        print("Please install required dependencies:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        return False


def run_legacy_gui():
    """Launch the legacy PySimpleGUI interface"""
    try:
        from gui import main as gui_main
        print("🚀 Launching InsightVault Legacy GUI...")
        print("⚠️  Note: This is the legacy interface. Consider using the new web dashboard instead.")
        gui_main()
        return True
    except ImportError as e:
        print(f"❌ Error importing GUI components: {e}")
        print("Please install required dependencies:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        return False


def run_cli():
    """Run the command-line interface"""
    try:
        from chat_parser import ChatParser
        from summarizer import ConversationSummarizer
        from insight_engine import InsightEngine
        
        print("💻 Starting InsightVault CLI...")
        
        # Initialize components
        parser = ChatParser()
        
        # Load conversations
        file_path = input("Enter path to conversations.json file: ").strip()
        if not file_path:
            file_path = 'data/sample_conversations.json'
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        
        if not parser.load_conversations(file_path):
            print("❌ Failed to load conversations")
            return False
        
        print(f"✅ Loaded {len(parser.conversations)} conversations")
        
        # Show basic stats
        print(f"\n📊 Basic Statistics:")
        print(f"   • Total conversations: {len(parser.conversations)}")
        print(f"   • Date range: {parser.conversations[0].create_date.strftime('%Y-%m-%d')} to {parser.conversations[-1].create_date.strftime('%Y-%m-%d')}")
        print(f"   • Total messages: {sum(len(conv.messages) for conv in parser.conversations)}")
        
        # Search functionality
        while True:
            query = input("\n🔍 Search conversations (or 'quit' to exit): ").strip()
            if query.lower() == 'quit':
                break
            
            if query:
                results = parser.search_conversations(query)
                print(f"\nFound {len(results)} conversations:")
                for i, conv in enumerate(results[:5], 1):
                    print(f"   {i}. {conv.title} ({conv.create_date.strftime('%Y-%m-%d')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in CLI: {e}")
        return False


def show_help():
    """Show detailed help information"""
    help_text = """
🧠 InsightVault - Personal Growth Reflection Tool

USAGE:
    python main.py                    # Launch unified web dashboard (recommended)
    python main.py --legacy-gui       # Launch legacy PySimpleGUI interface
    python main.py --cli              # Launch command-line interface
    python main.py --help-detailed    # Show this help

INTERFACES:

1. Unified Web Dashboard (Default)
   - Modern, beautiful web interface
   - File upload functionality
   - Interactive charts and analytics
   - All features in one place
   - Works on any device with a browser

2. Legacy GUI (--legacy-gui)
   - Traditional desktop application
   - Requires PySimpleGUI (licensing issues)
   - Basic interface with tabs

3. Command Line (--cli)
   - Text-based interface
   - Good for automation and scripting
   - Basic search and exploration

FEATURES:
   • Import ChatGPT conversation exports
   • AI-powered summarization and tagging
   • Advanced analytics and visualizations
   • Search and filter conversations
   • Generate personal growth insights
   • Export reports and summaries

SETUP:
   1. Copy config.json.example to config.json
   2. Add your OpenAI API key to config.json
   3. Export your ChatGPT conversations
   4. Run the application

EXAMPLES:
   # Launch the new web dashboard
   python main.py

   # Use legacy interface (if available)
   python main.py --legacy-gui

   # Command line interface
   python main.py --cli

For more information, visit: https://github.com/your-repo/InsightVault
    """
    print(help_text)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='InsightVault - Personal Growth Reflection Tool')
    parser.add_argument('--legacy-gui', action='store_true', help='Use legacy PySimpleGUI interface')
    parser.add_argument('--cli', action='store_true', help='Use command line interface')
    parser.add_argument('--help-detailed', action='store_true', help='Show detailed help')
    
    args = parser.parse_args()
    
    if args.help_detailed:
        show_help()
        return
    
    # Show banner
    print("🧠 InsightVault - Personal Growth Reflection Tool")
    print("=" * 55)
    print("🎨 Beautiful, Unified Web Interface")
    print("📊 Advanced Analytics & Insights")
    print("🔒 Privacy-First Design")
    print("=" * 55)
    
    # Set up environment
    if not setup_environment():
        print("\n❌ Environment setup failed. Please fix the issues above and try again.")
        return
    
    # Run appropriate interface
    success = False
    
    if args.legacy_gui:
        print("\n⚠️  Using legacy GUI interface...")
        success = run_legacy_gui()
    elif args.cli:
        print("\n💻 Using command-line interface...")
        success = run_cli()
    else:
        print("\n🚀 Using unified web dashboard (recommended)...")
        success = run_unified_dashboard()
    
    if success:
        print("\n✅ Thank you for using InsightVault!")
    else:
        print("\n❌ Application exited with errors.")
        sys.exit(1)


if __name__ == '__main__':
    main()