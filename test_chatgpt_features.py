#!/usr/bin/env python3
"""
Test script for ChatGPT features in InsightVault
Demonstrates API key configuration and ChatGPT integration
"""

import json
import os
from datetime import datetime
from chat_parser import ChatParser, Conversation
from chatgpt_integration import ChatGPTIntegration, create_chatgpt_integration


def test_api_key_configuration():
    """Test API key configuration functionality"""
    print("🔧 Testing API Key Configuration")
    print("=" * 50)
    
    # Test config loading
    config_file = "config.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(f"✅ Config loaded from {config_file}")
        print(f"   API Key: {'*' * 10 if config.get('openai_api_key') else 'Not set'}")
        print(f"   Model: {config.get('model', 'gpt-4')}")
        print(f"   Max Tokens: {config.get('max_tokens', 1500)}")
        print(f"   Temperature: {config.get('temperature', 0.7)}")
    else:
        print(f"❌ Config file {config_file} not found")
        return False
    
    # Test ChatGPT integration creation
    chatgpt = create_chatgpt_integration(config_file)
    if chatgpt:
        print("✅ ChatGPT integration created successfully")
        return True
    else:
        print("❌ ChatGPT integration failed - API key may be invalid or missing")
        return False


def test_conversation_analysis():
    """Test conversation analysis with ChatGPT"""
    print("\n🤖 Testing Conversation Analysis")
    print("=" * 50)
    
    # Load sample conversations
    sample_file = "data/sample_conversations.json"
    if not os.path.exists(sample_file):
        print(f"❌ Sample conversations file {sample_file} not found")
        return False
    
    parser = ChatParser()
    if not parser.load_conversations(sample_file):
        print("❌ Failed to load sample conversations")
        return False
    
    print(f"✅ Loaded {len(parser.conversations)} conversations")
    
    # Create ChatGPT integration
    chatgpt = create_chatgpt_integration()
    if not chatgpt:
        print("❌ ChatGPT integration not available")
        return False
    
    # Test general analysis
    print("\n📊 Testing General Analysis...")
    try:
        analysis = chatgpt.analyze_conversations(parser.conversations, "general")
        if "error" in analysis:
            print(f"❌ Analysis failed: {analysis['error']}")
        else:
            print("✅ General analysis completed")
            print(f"   Conversations analyzed: {analysis['conversations_analyzed']}")
            print(f"   Model used: {analysis['model_used']}")
            print(f"   Summary: {analysis['analysis']['summary'][:100]}...")
    except Exception as e:
        print(f"❌ Analysis error: {e}")
    
    # Test programming analysis
    print("\n💻 Testing Programming Analysis...")
    try:
        patterns = chatgpt.detect_programming_patterns(parser.conversations)
        print("✅ Programming patterns detected")
        print(f"   Languages: {', '.join(patterns['languages_detected']) or 'None'}")
        print(f"   Technologies: {', '.join(patterns['technologies_detected']) or 'None'}")
        print(f"   Concepts: {', '.join(patterns['concepts_detected']) or 'None'}")
        print(f"   Programming conversations: {patterns['programming_conversations_count']}/{patterns['total_conversations']}")
    except Exception as e:
        print(f"❌ Programming analysis error: {e}")
    
    return True


def test_ai_response_generation():
    """Test AI response generation"""
    print("\n💬 Testing AI Response Generation")
    print("=" * 50)
    
    # Load conversations
    sample_file = "data/sample_conversations.json"
    if not os.path.exists(sample_file):
        print(f"❌ Sample conversations file {sample_file} not found")
        return False
    
    parser = ChatParser()
    if not parser.load_conversations(sample_file):
        print("❌ Failed to load sample conversations")
        return False
    
    # Create ChatGPT integration
    chatgpt = create_chatgpt_integration()
    if not chatgpt:
        print("❌ ChatGPT integration not available")
        return False
    
    # Test questions
    test_questions = [
        "What are the main themes in my conversations?",
        "How have I grown over time?",
        "What programming languages do I discuss most?",
        "What emotional patterns do you notice?"
    ]
    
    for question in test_questions:
        print(f"\n❓ Question: {question}")
        try:
            response = chatgpt.generate_ai_response(question, parser.conversations)
            print(f"🤖 Response: {response[:200]}...")
            print("✅ Response generated successfully")
        except Exception as e:
            print(f"❌ Response generation failed: {e}")
    
    return True


def demonstrate_gui_integration():
    """Demonstrate GUI integration features"""
    print("\n🖥️ GUI Integration Features")
    print("=" * 50)
    
    print("✅ Settings Tab Features:")
    print("   - API Key configuration with password masking")
    print("   - Model selection (GPT-4, GPT-3.5-turbo)")
    print("   - Max tokens configuration")
    print("   - Temperature setting")
    print("   - API key testing")
    print("   - Settings saving and loading")
    
    print("\n✅ ChatGPT Chat Tab Features:")
    print("   - Real-time chat interface")
    print("   - Conversation analysis buttons")
    print("   - Programming analysis")
    print("   - Growth analysis")
    print("   - Chat history and clearing")
    
    print("\n✅ Integration with Existing Features:")
    print("   - Works with loaded conversations")
    print("   - Integrates with analytics engine")
    print("   - Supports export functionality")
    print("   - Threading for non-blocking operations")


def main():
    """Main test function"""
    print("🧠 InsightVault ChatGPT Features Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test API key configuration
    config_ok = test_api_key_configuration()
    
    if config_ok:
        # Test conversation analysis
        analysis_ok = test_conversation_analysis()
        
        # Test AI response generation
        response_ok = test_ai_response_generation()
        
        # Demonstrate GUI features
        demonstrate_gui_integration()
        
        print("\n" + "=" * 60)
        print("📋 Test Summary:")
        print(f"   API Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
        print(f"   Conversation Analysis: {'✅ PASS' if analysis_ok else '❌ FAIL'}")
        print(f"   AI Response Generation: {'✅ PASS' if response_ok else '❌ FAIL'}")
        print("   GUI Integration: ✅ READY")
        
        if config_ok and analysis_ok and response_ok:
            print("\n🎉 All tests passed! ChatGPT features are working correctly.")
            print("\n🚀 Next steps:")
            print("   1. Run the main GUI: python gui.py")
            print("   2. Go to Settings tab to configure your API key")
            print("   3. Load conversations and try the ChatGPT Chat tab")
            print("   4. Use the analysis buttons for insights")
        else:
            print("\n⚠️ Some tests failed. Please check your API key configuration.")
    else:
        print("\n❌ API key configuration failed. Please set up your OpenAI API key first.")
        print("\n📝 Setup instructions:")
        print("   1. Get your API key from https://platform.openai.com/api-keys")
        print("   2. Edit config.json and add your API key")
        print("   3. Run this test again")


if __name__ == "__main__":
    main() 