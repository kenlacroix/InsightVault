#!/usr/bin/env python3
"""
ChatGPT Features Demonstration for InsightVault
Simple command-line demo of ChatGPT integration
"""

import json
import os
from chat_parser import ChatParser
from chatgpt_integration import create_chatgpt_integration


def check_config():
    """Check if configuration is set up"""
    config_file = "config.json"
    if not os.path.exists(config_file):
        print("❌ Config file not found. Creating example config...")
        example_config = {
            "openai_api_key": "your_openai_api_key_here",
            "model": "gpt-4",
            "max_tokens": 1500,
            "temperature": 0.7
        }
        with open(config_file, 'w') as f:
            json.dump(example_config, f, indent=4)
        print("✅ Created config.json.example")
        print("📝 Please edit config.json and add your OpenAI API key")
        return False
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    if not config.get('openai_api_key') or config['openai_api_key'] == "your_openai_api_key_here":
        print("❌ API key not configured")
        print("📝 Please edit config.json and add your OpenAI API key")
        return False
    
    print("✅ Configuration found")
    return True


def load_sample_data():
    """Load sample conversation data"""
    sample_file = "data/sample_conversations.json"
    if not os.path.exists(sample_file):
        print(f"❌ Sample data not found: {sample_file}")
        return None
    
    parser = ChatParser()
    if parser.load_conversations(sample_file):
        print(f"✅ Loaded {len(parser.conversations)} conversations")
        return parser.conversations
    else:
        print("❌ Failed to load sample conversations")
        return None


def interactive_chat(chatgpt, conversations):
    """Interactive chat session"""
    print("\n💬 Interactive Chat Session")
    print("Type 'quit' to exit, 'help' for commands")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("  analyze - Analyze all conversations")
                print("  programming - Analyze programming patterns")
                print("  growth - Analyze growth patterns")
                print("  quit - Exit chat")
                print("  help - Show this help")
                continue
            elif user_input.lower() == 'analyze':
                print("\n🤖 Analyzing conversations...")
                analysis = chatgpt.analyze_conversations(conversations, "general")
                if "error" not in analysis:
                    print(f"✅ Analysis complete: {analysis['analysis']['summary']}")
                else:
                    print(f"❌ Analysis failed: {analysis['error']}")
                continue
            elif user_input.lower() == 'programming':
                print("\n💻 Analyzing programming patterns...")
                patterns = chatgpt.detect_programming_patterns(conversations)
                print(f"✅ Programming analysis:")
                print(f"   Languages: {', '.join(patterns['languages_detected']) or 'None'}")
                print(f"   Technologies: {', '.join(patterns['technologies_detected']) or 'None'}")
                print(f"   Programming conversations: {patterns['programming_conversations_count']}/{patterns['total_conversations']}")
                continue
            elif user_input.lower() == 'growth':
                print("\n🌱 Analyzing growth patterns...")
                analysis = chatgpt.analyze_conversations(conversations, "growth")
                if "error" not in analysis:
                    print(f"✅ Growth analysis: {analysis['analysis']['summary']}")
                else:
                    print(f"❌ Growth analysis failed: {analysis['error']}")
                continue
            
            if not user_input:
                continue
            
            print("🤖 Thinking...")
            response = chatgpt.generate_ai_response(user_input, conversations)
            print(f"InsightVault: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main demonstration function"""
    print("🧠 InsightVault ChatGPT Features Demo")
    print("=" * 50)
    
    # Check configuration
    if not check_config():
        return
    
    # Create ChatGPT integration
    chatgpt = create_chatgpt_integration()
    if not chatgpt:
        print("❌ Failed to create ChatGPT integration")
        return
    
    print("✅ ChatGPT integration ready")
    
    # Load sample data
    conversations = load_sample_data()
    if not conversations:
        return
    
    # Start interactive chat
    interactive_chat(chatgpt, conversations)


if __name__ == "__main__":
    main() 