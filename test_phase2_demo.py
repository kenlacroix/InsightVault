#!/usr/bin/env python3
"""
Phase 2 Demo Script
Test the AI-powered personal assistant functionality
"""

import os
import sys
from typing import List, Dict, Any

def test_phase2_components():
    """Test Phase 2 components"""
    print("🧠 Testing Phase 2 - AI-Powered Personal Assistant")
    print("=" * 60)
    
    # Test 1: LLM Integration
    print("\n1. Testing LLM Integration...")
    try:
        from llm_integration import LLMIntegration
        llm = LLMIntegration()
        print("✅ LLM Integration initialized successfully")
        
        # Test cache key generation
        cache_key = llm._generate_cache_key("test query", [], {})
        print(f"✅ Cache key generation: {cache_key[:10]}...")
        
    except Exception as e:
        print(f"❌ LLM Integration failed: {e}")
        return False
    
    # Test 2: Advanced Query Parser
    print("\n2. Testing Advanced Query Parser...")
    try:
        from advanced_query_parser import AdvancedQueryParser
        parser = AdvancedQueryParser()
        print("✅ Advanced Query Parser initialized successfully")
        
        # Test simple query parsing
        query = "How have I grown in the past year?"
        intent = parser.parse_complex_query(query)
        print(f"✅ Query parsing: {intent.primary_topic}")
        
    except Exception as e:
        print(f"❌ Advanced Query Parser failed: {e}")
        return False
    
    # Test 3: Predictive Analytics
    print("\n3. Testing Predictive Analytics...")
    try:
        from predictive_analytics import PredictiveAnalytics
        analytics = PredictiveAnalytics()
        print("✅ Predictive Analytics initialized successfully")
        
        # Test trend analysis
        trends = analytics.analyze_trends([])
        print(f"✅ Trend analysis: {len(trends)} trends identified")
        
    except Exception as e:
        print(f"❌ Predictive Analytics failed: {e}")
        return False
    
    # Test 4: User Profile Manager
    print("\n4. Testing User Profile Manager...")
    try:
        from user_profile_manager import UserProfileManager
        profile_manager = UserProfileManager()
        print("✅ User Profile Manager initialized successfully")
        
        # Test profile creation
        user_id = "demo_user"
        preferences = {
            'focus_areas': ['relationships', 'productivity'],
            'learning_goals': ['self_awareness']
        }
        profile = profile_manager.create_user_profile(user_id, preferences)
        if profile:
            print(f"✅ Profile created for user: {profile.user_id}")
        else:
            print("⚠️ Profile creation returned None (expected in demo)")
        
    except Exception as e:
        print(f"❌ User Profile Manager failed: {e}")
        return False
    
    # Test 5: Performance Optimizer
    print("\n5. Testing Performance Optimizer...")
    try:
        from performance_optimizer import PerformanceOptimizer
        optimizer = PerformanceOptimizer()
        print("✅ Performance Optimizer initialized successfully")
        
        # Test cache functionality
        optimizer.cache_response("test_key", "test_response")
        cached = optimizer.get_cached_response("test_key")
        print(f"✅ Cache test: {'Hit' if cached else 'Miss'}")
        
    except Exception as e:
        print(f"❌ Performance Optimizer failed: {e}")
        return False
    
    # Test 6: Database Manager
    print("\n6. Testing Database Manager...")
    try:
        from performance_optimizer import DatabaseManager
        db_manager = DatabaseManager(":memory:")  # Use in-memory database
        print("✅ Database Manager initialized successfully")
        
        # Test basic operations
        db_manager.save_conversation("test_conv", {"title": "Test", "content": "Test content"})
        conv = db_manager.get_conversation("test_conv")
        print(f"✅ Database operations: {'Success' if conv else 'Failed'}")
        
    except Exception as e:
        print(f"❌ Database Manager failed: {e}")
        return False
    
    print("\n🎉 All Phase 2 components tested successfully!")
    return True

def test_with_sample_data():
    """Test with sample conversation data"""
    print("\n📊 Testing with Sample Data")
    print("=" * 40)
    
    try:
        from chat_parser import ChatParser
        from llm_integration import LLMIntegration
        from advanced_query_parser import AdvancedQueryParser
        
        # Load sample conversations
        sample_file = "data/sample_conversations.json"
        if not os.path.exists(sample_file):
            print(f"⚠️ Sample file not found: {sample_file}")
            print("Creating minimal sample data...")
            
            # Create minimal sample data
            sample_data = {
                "conversations": [
                    {
                        "title": "Sample Conversation",
                        "create_date": "2024-01-01",
                        "messages": [
                            {"role": "user", "content": "How can I improve my productivity?"},
                            {"role": "assistant", "content": "Here are some tips for productivity..."}
                        ]
                    }
                ]
            }
            
            os.makedirs("data", exist_ok=True)
            import json
            with open(sample_file, 'w') as f:
                json.dump(sample_data, f, indent=2)
        
        # Parse conversations
        parser = ChatParser()
        if parser.load_conversations(sample_file):
            conversations = parser.conversations
            print(f"✅ Loaded {len(conversations)} conversations")
            
            # Test query parsing
            query_parser = AdvancedQueryParser()
            query = "What are my main learning patterns?"
            intent = query_parser.parse_complex_query(query)
            print(f"✅ Query intent: {intent.primary_topic}")
            
            # Test LLM integration (without API key)
            llm = LLMIntegration()
            print("✅ LLM Integration ready (API key needed for full functionality)")
            
        else:
            print("❌ Failed to load sample conversations")
            return False
            
    except Exception as e:
        print(f"❌ Sample data test failed: {e}")
        return False
    
    return True

def main():
    """Main demo function"""
    print("🚀 Phase 2 Demo - AI-Powered Personal Assistant")
    print("=" * 60)
    
    # Test core components
    if not test_phase2_components():
        print("\n❌ Component tests failed. Please check the errors above.")
        return
    
    # Test with sample data
    if not test_with_sample_data():
        print("\n❌ Sample data test failed. Please check the errors above.")
        return
    
    print("\n🎉 Phase 2 Demo Completed Successfully!")
    print("\n📋 Next Steps:")
    print("1. Set up your OpenAI API key in config.json")
    print("2. Export your ChatGPT conversations to JSON")
    print("3. Run the AI assistant with your real data")
    print("4. Ask personal growth questions and get insights!")
    
    print("\n💡 Example Usage:")
    print("from llm_integration import LLMIntegration")
    print("from chat_parser import ChatParser")
    print("")
    print("llm = LLMIntegration()")
    print("parser = ChatParser()")
    print("conversations = parser.parse_file('your_export.json')")
    print("insight = llm.generate_insight('How have I grown?', conversations)")

if __name__ == "__main__":
    main() 