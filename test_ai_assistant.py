"""
Test Script for AI Assistant
Phase 1: Demonstration and Testing

This script demonstrates the AI assistant functionality with sample data
and provides a way to test the system without requiring real conversation data.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

from enhanced_chat_parser import EnhancedChatParser, EnhancedConversation, EnhancedChatMessage
from ai_assistant import AIAssistant


def create_sample_conversations() -> List[Dict[str, Any]]:
    """Create sample conversation data for testing"""
    
    sample_conversations = [
        {
            "id": "conv_001",
            "title": "Setting Boundaries in Relationships",
            "create_time": int((datetime.now() - timedelta(days=30)).timestamp()),
            "update_time": int((datetime.now() - timedelta(days=30)).timestamp()),
            "mapping": {
                "0": {
                    "message": {
                        "id": "msg_001",
                        "author": {"role": "user"},
                        "create_time": int((datetime.now() - timedelta(days=30)).timestamp()),
                        "content": {
                            "content_type": "text",
                            "parts": ["I'm having trouble saying no to people. I always feel guilty when I set boundaries."]
                        }
                    }
                },
                "1": {
                    "message": {
                        "id": "msg_002",
                        "author": {"role": "assistant"},
                        "create_time": int((datetime.now() - timedelta(days=30)).timestamp()),
                        "content": {
                            "content_type": "text",
                            "parts": ["Setting boundaries is an essential part of self-care. It's not selfish to prioritize your well-being."]
                        }
                    }
                },
                "2": {
                    "message": {
                        "id": "msg_003",
                        "author": {"role": "user"},
                        "create_time": int((datetime.now() - timedelta(days=30)).timestamp()),
                        "content": {
                            "content_type": "text",
                            "parts": ["I realized I don't owe anyone my time or energy. This is a breakthrough moment for me!"]
                        }
                    }
                }
            }
        },
        {
            "id": "conv_002",
            "title": "Productivity and Work-Life Balance",
            "create_time": int((datetime.now() - timedelta(days=20)).timestamp()),
            "update_time": int((datetime.now() - timedelta(days=20)).timestamp()),
            "mapping": {
                "0": {
                    "message": {
                        "id": "msg_004",
                        "author": {"role": "user"},
                        "create_time": int((datetime.now() - timedelta(days=20)).timestamp()),
                        "content": {
                            "content_type": "text",
                            "parts": ["I've been working 12-hour days and I'm exhausted. How can I be more productive without burning out?"]
                        }
                    }
                },
                "1": {
                    "message": {
                        "id": "msg_005",
                        "author": {"role": "assistant"},
                        "create_time": int((datetime.now() - timedelta(days=20)).timestamp()),
                        "content": {
                            "content_type": "text",
                            "parts": ["Productivity isn't about working more hours, it's about working smarter. Rest is essential for creativity and focus."]
                        }
                    }
                },
                "2": {
                    "message": {
                        "id": "msg_006",
                        "author": {"role": "user"},
                        "create_time": int((datetime.now() - timedelta(days=20)).timestamp()),
                        "content": {
                            "content_type": "text",
                            "parts": ["I'm most productive when I'm well-rested. Quality over quantity in everything I do."]
                        }
                    }
                }
            }
        },
        {
            "id": "conv_003",
            "title": "Emotional Growth and Self-Compassion",
            "create_time": int((datetime.now() - timedelta(days=10)).timestamp()),
            "update_time": int((datetime.now() - timedelta(days=10)).timestamp()),
            "mapping": {
                "0": {
                    "message": {
                        "id": "msg_007",
                        "author": {"role": "user"},
                        "create_time": int((datetime.now() - timedelta(days=10)).timestamp()),
                        "content": {
                            "content_type": "text",
                            "parts": ["I'm learning to be kinder to myself. My emotions are valid, even when uncomfortable."]
                        }
                    }
                },
                "1": {
                    "message": {
                        "id": "msg_008",
                        "author": {"role": "assistant"},
                        "create_time": int((datetime.now() - timedelta(days=10)).timestamp()),
                        "content": {
                            "content_type": "text",
                            "parts": ["That's a beautiful realization. Self-compassion is the foundation of emotional resilience."]
                        }
                    }
                },
                "2": {
                    "message": {
                        "id": "msg_009",
                        "author": {"role": "user"},
                        "create_time": int((datetime.now() - timedelta(days=10)).timestamp()),
                        "content": {
                            "content_type": "text",
                            "parts": ["I can feel sad without being broken. Self-compassion isn't self-pity, it's self-care."]
                        }
                    }
                }
            }
        },
        {
            "id": "conv_004",
            "title": "Friendship Patterns and Social Energy",
            "create_time": int((datetime.now() - timedelta(days=5)).timestamp()),
            "update_time": int((datetime.now() - timedelta(days=5)).timestamp()),
            "mapping": {
                "0": {
                    "message": {
                        "id": "msg_010",
                        "author": {"role": "user"},
                        "create_time": int((datetime.now() - timedelta(days=5)).timestamp()),
                        "content": {
                            "content_type": "text",
                            "parts": ["I've been trying to be friends with everyone, but I'm spreading myself too thin."]
                        }
                    }
                },
                "1": {
                    "message": {
                        "id": "msg_011",
                        "author": {"role": "assistant"},
                        "create_time": int((datetime.now() - timedelta(days=5)).timestamp()),
                        "content": {
                            "content_type": "text",
                            "parts": ["Quality friendships require mutual effort. It's okay to be selective about who you invest time in."]
                        }
                    }
                },
                "2": {
                    "message": {
                        "id": "msg_012",
                        "author": {"role": "user"},
                        "create_time": int((datetime.now() - timedelta(days=5)).timestamp()),
                        "content": {
                            "content_type": "text",
                            "parts": ["I don't need to be friends with everyone. My social energy is finite and valuable."]
                        }
                    }
                }
            }
        }
    ]
    
    return sample_conversations


def save_sample_data(conversations: List[Dict[str, Any]], file_path: str = 'data/sample_conversations.json'):
    """Save sample conversation data to file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(conversations, f, indent=2)
    
    print(f"✓ Sample data saved to {file_path}")


def test_ai_assistant():
    """Test the AI assistant with sample data"""
    print("🧠 Testing InsightVault AI Assistant")
    print("=" * 50)
    
    # Create and save sample data
    sample_conversations = create_sample_conversations()
    save_sample_data(sample_conversations)
    
    # Initialize AI assistant
    print("\nInitializing AI assistant...")
    ai_assistant = AIAssistant()
    
    # Load sample conversations
    print("Loading sample conversations...")
    success = ai_assistant.load_conversations('data/sample_conversations.json')
    
    if not success:
        print("❌ Failed to load sample conversations")
        return
    
    print(f"✓ Loaded {len(ai_assistant.conversations)} sample conversations")
    
    # Test queries
    test_queries = [
        "What have I learned about my relationships and boundaries?",
        "How has my understanding of productivity evolved?",
        "What patterns do you see in my emotional growth?",
        "What have I discovered about friendship and social connections?",
        "How has my self-compassion developed over time?"
    ]
    
    print("\n" + "="*50)
    print("TESTING AI ASSISTANT QUERIES")
    print("="*50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test Query {i}: {query}")
        print("-" * 50)
        
        try:
            # Process query
            insight = ai_assistant.process_query(query)
            
            # Format and display response
            response = ai_assistant.format_insight_response(insight)
            print(response)
            
            # Display confidence score
            confidence = int(insight.confidence_score * 100)
            print(f"\nConfidence Score: {confidence}%")
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
        
        print("\n" + "="*50)
    
    print("\n🎉 AI Assistant testing completed!")
    print("\nKey Features Demonstrated:")
    print("✓ Natural language query processing")
    print("✓ Semantic search and conversation analysis")
    print("✓ Insight generation with structured format")
    print("✓ Breakthrough moment detection")
    print("✓ Evolution timeline analysis")
    print("✓ Actionable next steps generation")
    print("✓ Confidence scoring")


def test_semantic_search():
    """Test semantic search functionality"""
    print("\n🔍 Testing Semantic Search")
    print("=" * 30)
    
    # Initialize enhanced parser
    parser = EnhancedChatParser()
    
    # Load sample data
    success = parser.load_conversations('data/sample_conversations.json')
    if not success:
        print("❌ Failed to load sample data for search testing")
        return
    
    # Test search queries
    search_queries = [
        "boundaries",
        "productivity",
        "self-compassion",
        "friendships",
        "emotional growth"
    ]
    
    for query in search_queries:
        print(f"\nSearching for: '{query}'")
        results = parser.semantic_search(query, limit=3)
        
        if results:
            for conv, score in results:
                print(f"  - {conv.title} (score: {score:.3f})")
        else:
            print("  No results found")


def main():
    """Main test function"""
    print("🧠 InsightVault AI Assistant - Test Suite")
    print("=" * 60)
    
    # Test AI assistant
    test_ai_assistant()
    
    # Test semantic search
    test_semantic_search()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("\nNext steps:")
    print("1. Install required dependencies: pip install -r requirements.txt")
    print("2. Run the AI assistant interface: python ai_assistant_interface.py")
    print("3. Or use the integrated version: python ai_assistant_integration.py")
    print("4. Load your own ChatGPT conversation exports for real analysis")


if __name__ == "__main__":
    main()