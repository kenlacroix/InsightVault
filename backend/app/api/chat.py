from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import json
import os
import asyncio
from ..database import get_sync_db
from ..models import User, Conversation, UserSession, UserInteraction
from ..context_fusion import ContextFusionEngine
from ..auth import get_current_user
import openai
from ..config import Config
import hashlib
import pickle
from pathlib import Path

# Initialize OpenAI client
openai_client = None
try:
    if Config.OPENAI_API_KEY:
        openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        print("[SUCCESS] OpenAI client initialized successfully")
    else:
        print("[WARNING] OpenAI API key not configured - using fallback responses")
except Exception as e:
    print(f"[ERROR] OpenAI client initialization failed: {e}")

# Cache configuration
CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "chat_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_EXPIRY_HOURS = 24  # Cache for 24 hours

def get_cache_key(user_message: str, conversations_hash: str) -> str:
    """Generate a cache key based on user message and conversation data hash."""
    content = f"{user_message}:{conversations_hash}"
    return hashlib.md5(content.encode()).hexdigest()

def get_conversations_hash(conversations: List[Conversation]) -> str:
    """Generate a hash of conversation data for cache invalidation."""
    # Create a hash based on conversation IDs, content lengths, and modification times
    hash_data = []
    for conv in conversations:
        # Use created_at if updated_at doesn't exist
        timestamp = conv.updated_at.isoformat() if hasattr(conv, 'updated_at') and conv.updated_at else conv.created_at.isoformat() if conv.created_at else 'unknown'
        hash_data.append(f"{conv.id}:{len(conv.content)}:{timestamp}")
    return hashlib.md5(":".join(hash_data).encode()).hexdigest()

def get_cached_response(cache_key: str) -> Optional[str]:
    """Get cached response if it exists and is not expired."""
    cache_file = CACHE_DIR / f"{cache_key}.pkl"
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'rb') as f:
            cached_data = pickle.load(f)
        
        # Check if cache is expired
        if (datetime.now() - cached_data['timestamp']).total_seconds() > CACHE_EXPIRY_HOURS * 3600:
            cache_file.unlink()  # Delete expired cache
            return None
        
        return cached_data['response']
    except Exception:
        # If cache is corrupted, delete it
        if cache_file.exists():
            cache_file.unlink()
        return None

def save_cached_response(cache_key: str, response: str):
    """Save response to cache."""
    try:
        cache_file = CACHE_DIR / f"{cache_key}.pkl"
        cached_data = {
            'response': response,
            'timestamp': datetime.now()
        }
        with open(cache_file, 'wb') as f:
            pickle.dump(cached_data, f)
    except Exception as e:
        print(f"Failed to save cache: {e}")

def get_or_create_session(db: Session, user_id: int) -> UserSession:
    """Get the current active session or create a new one."""
    # Check for existing active session
    session = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.session_end.is_(None)
    ).first()
    
    if not session:
        # Create new session
        session = UserSession()
        session.user_id = user_id
        db.add(session)
        db.commit()
        db.refresh(session)
    
    return session

def store_interaction(db: Session, session_id: int, user_question: str, ai_response: str, context_used: Optional[List[str]] = None, metadata: Optional[dict] = None):
    """Store a user interaction in the database."""
    interaction = UserInteraction()
    interaction.session_id = session_id
    interaction.user_question = user_question
    interaction.ai_response = ai_response
    interaction.context_used = context_used or []
    interaction.interaction_metadata = metadata or {}
    
    db.add(interaction)
    db.commit()
    return interaction

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None  # If specified, focus on that conversation

class ChatResponse(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    insights: Optional[dict] = None
    timestamp: datetime
    processing_status: Optional[str] = None  # New field for status updates
    processing_stage: Optional[str] = None   # New field for current stage

def detect_dynamic_topics_from_content(content: str) -> dict:
    """
    Dynamically detect topics from conversation content using keyword analysis and context.
    This adapts to whatever topics the user actually discusses.
    """
    content_lower = content.lower()
    detected_topics = {}
    
    # Dynamic keyword detection with context
    topic_patterns = {
        # Technology & Programming
        'programming': {
            'keywords': ['code', 'programming', 'python', 'javascript', 'java', 'c++', 'algorithm', 'function', 'variable', 'debug', 'error', 'bug', 'git', 'repository', 'api', 'database', 'server', 'client', 'framework', 'library', 'package', 'install', 'compile', 'deploy', 'test', 'unit test', 'integration'],
            'context_words': ['developer', 'software', 'application', 'website', 'app', 'system', 'platform', 'tool', 'technology', 'tech', 'coding', 'development']
        },
        
        # Business & Career
        'business': {
            'keywords': ['business', 'startup', 'entrepreneur', 'company', 'market', 'customer', 'revenue', 'profit', 'investment', 'funding', 'strategy', 'planning', 'management', 'leadership', 'team', 'project', 'goal', 'objective', 'target', 'success', 'growth', 'scale', 'competition', 'industry'],
            'context_words': ['work', 'career', 'job', 'professional', 'enterprise', 'organization', 'venture', 'initiative']
        },
        
        # Health & Wellness
        'health': {
            'keywords': ['health', 'fitness', 'exercise', 'workout', 'gym', 'nutrition', 'diet', 'food', 'sleep', 'rest', 'recovery', 'energy', 'vitality', 'strength', 'endurance', 'wellness', 'medical', 'doctor', 'treatment', 'therapy', 'healing', 'pain', 'symptom', 'condition', 'medication'],
            'context_words': ['body', 'physical', 'mental', 'wellbeing', 'lifestyle', 'routine', 'habit', 'self-care']
        },
        
        # Relationships & Social
        'relationships': {
            'keywords': ['relationship', 'partner', 'boyfriend', 'girlfriend', 'spouse', 'marriage', 'dating', 'family', 'friend', 'social', 'communication', 'trust', 'love', 'intimacy', 'connection', 'bond', 'support', 'care', 'understanding', 'conflict', 'argument', 'resolution', 'boundary'],
            'context_words': ['people', 'person', 'human', 'interaction', 'social', 'emotional', 'personal']
        },
        
        # Spirituality & Personal Growth
        'spirituality': {
            'keywords': ['spiritual', 'meditation', 'mindfulness', 'zen', 'buddhism', 'consciousness', 'awareness', 'energy', 'chakra', 'aura', 'vibration', 'manifestation', 'law of attraction', 'abundance', 'gratitude', 'forgiveness', 'healing', 'purpose', 'meaning', 'enlightenment', 'awakening', 'grounding', 'centered'],
            'context_words': ['soul', 'spirit', 'inner', 'divine', 'sacred', 'transcendence', 'transformation', 'growth']
        },
        
        # Education & Learning
        'education': {
            'keywords': ['learn', 'learning', 'education', 'study', 'course', 'class', 'school', 'university', 'college', 'degree', 'certificate', 'skill', 'knowledge', 'wisdom', 'research', 'reading', 'writing', 'analysis', 'understanding', 'comprehension', 'mastery', 'expertise'],
            'context_words': ['academic', 'intellectual', 'cognitive', 'mental', 'brain', 'mind', 'thinking', 'knowledge']
        },
        
        # Creativity & Arts
        'creativity': {
            'keywords': ['creative', 'creativity', 'art', 'artist', 'design', 'designer', 'music', 'musician', 'writing', 'writer', 'poetry', 'poem', 'story', 'novel', 'painting', 'drawing', 'photography', 'film', 'video', 'performance', 'expression', 'inspiration', 'imagination', 'innovation'],
            'context_words': ['aesthetic', 'beauty', 'expression', 'craft', 'talent', 'skill', 'passion', 'vision']
        },
        
        # Finance & Money
        'finance': {
            'keywords': ['money', 'finance', 'financial', 'budget', 'saving', 'investment', 'stock', 'market', 'trading', 'banking', 'credit', 'debt', 'loan', 'mortgage', 'insurance', 'tax', 'income', 'expense', 'wealth', 'rich', 'poor', 'economy', 'economic'],
            'context_words': ['cash', 'dollar', 'currency', 'payment', 'transaction', 'account', 'portfolio']
        },
        
        # Travel & Adventure
        'travel': {
            'keywords': ['travel', 'trip', 'vacation', 'journey', 'adventure', 'explore', 'destination', 'country', 'city', 'place', 'location', 'hotel', 'flight', 'booking', 'reservation', 'tour', 'guide', 'culture', 'experience', 'memory', 'sightseeing'],
            'context_words': ['world', 'global', 'international', 'foreign', 'local', 'visit', 'see', 'discover']
        },
        
        # Politics & Society
        'politics': {
            'keywords': ['politics', 'political', 'government', 'policy', 'law', 'legal', 'rights', 'freedom', 'democracy', 'election', 'vote', 'candidate', 'party', 'social', 'society', 'community', 'culture', 'tradition', 'change', 'reform', 'justice', 'equality'],
            'context_words': ['public', 'civil', 'national', 'international', 'global', 'social', 'cultural']
        },
        
        # Science & Research
        'science': {
            'keywords': ['science', 'scientific', 'research', 'study', 'experiment', 'data', 'analysis', 'theory', 'hypothesis', 'evidence', 'discovery', 'innovation', 'technology', 'biology', 'chemistry', 'physics', 'mathematics', 'statistics', 'methodology'],
            'context_words': ['empirical', 'objective', 'factual', 'evidence-based', 'systematic', 'analytical']
        }
    }
    
    # Score each topic based on keyword presence and context
    for topic, pattern in topic_patterns.items():
        score = 0
        keyword_matches = []
        context_matches = []
        
        # Check for keyword matches
        for keyword in pattern['keywords']:
            if keyword in content_lower:
                score += 2  # Higher weight for specific keywords
                keyword_matches.append(keyword)
        
        # Check for context word matches
        for context_word in pattern['context_words']:
            if context_word in content_lower:
                score += 1  # Lower weight for context words
                context_matches.append(context_word)
        
        # Only include topics with significant relevance
        if score >= 2:
            detected_topics[topic] = {
                'score': score,
                'keyword_matches': keyword_matches,
                'context_matches': context_matches,
                'confidence': min(score / 5.0, 1.0)  # Normalize confidence
            }
    
    # Sort by score (highest first)
    detected_topics = dict(sorted(detected_topics.items(), key=lambda x: x[1]['score'], reverse=True))
    
    return detected_topics

def analyze_conversation_content(content: str) -> dict:
    """
    Analyze conversation content and extract comprehensive insights using dynamic topic detection.
    """
    insights = {
        "word_count": len(content.split()),
        "character_count": len(content),
        "sentences": len([s for s in content.split('.') if s.strip()]),
        "topics": [],
        "dynamic_topics": {},
        "sentiment": "neutral",
        "key_insights": [],
        "programming_languages": [],
        "technologies": [],
        "concepts": [],
        "difficulty_level": "intermediate",
        "life_areas": [],
        "emotional_themes": [],
        "personal_growth_aspects": []
    }
    
    content_lower = content.lower()
    
    # Dynamic topic detection
    dynamic_topics = detect_dynamic_topics_from_content(content)
    insights["dynamic_topics"] = dynamic_topics
    
    # Convert dynamic topics to topic list
    topics = list(dynamic_topics.keys())
    insights["topics"] = topics
    
    # Enhanced sentiment analysis with more nuanced detection
    positive_words = [
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'happy', 'love', 'enjoy', 'solved', 'working', 'success',
        'grateful', 'blessed', 'peaceful', 'content', 'fulfilled', 'inspired', 'motivated', 'confident', 'strong', 
        'healed', 'transformed', 'breakthrough', 'excited', 'thrilled', 'elated', 'joyful', 'delighted', 'satisfied',
        'proud', 'accomplished', 'achieved', 'progress', 'improvement', 'growth', 'development', 'advancement'
    ]
    
    negative_words = [
        'bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry', 'frustrated', 'error', 'bug', 'broken', 'stuck',
        'anxious', 'depressed', 'overwhelmed', 'lost', 'confused', 'hurt', 'pain', 'suffering', 'struggle', 'difficult', 
        'challenging', 'worried', 'scared', 'afraid', 'terrified', 'hopeless', 'despair', 'disappointed', 'upset',
        'irritated', 'annoyed', 'bothered', 'troubled', 'concerned', 'stressed', 'tired', 'exhausted', 'drained'
    ]
    
    positive_count = sum(1 for word in positive_words if word in content_lower)
    negative_count = sum(1 for word in negative_words if word in content_lower)
    
    if positive_count > negative_count:
        insights["sentiment"] = "positive"
    elif negative_count > positive_count:
        insights["sentiment"] = "negative"
    
    # Programming-specific analysis (only if programming topics detected)
    if 'programming' in dynamic_topics:
        programming_languages = []
        technologies = []
        concepts = []
        
        # Programming languages
        languages = {
            'python': ['python', 'py', 'django', 'flask', 'pandas', 'numpy', 'matplotlib'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue', 'angular', 'typescript'],
            'java': ['java', 'spring', 'android', 'kotlin'],
            'c++': ['c++', 'cpp', 'c plus plus'],
            'c#': ['c#', 'csharp', '.net', 'asp.net'],
            'go': ['go', 'golang'],
            'rust': ['rust'],
            'php': ['php', 'laravel', 'wordpress'],
            'ruby': ['ruby', 'rails'],
            'swift': ['swift', 'ios', 'xcode'],
            'sql': ['sql', 'mysql', 'postgresql', 'sqlite', 'mongodb']
        }
        
        for lang, keywords in languages.items():
            if any(keyword in content_lower for keyword in keywords):
                programming_languages.append(lang)
        
        # Technologies and frameworks
        tech_keywords = {
            'web_development': ['html', 'css', 'bootstrap', 'tailwind', 'responsive', 'frontend', 'backend'],
            'databases': ['database', 'sql', 'nosql', 'redis', 'elasticsearch', 'firebase'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'microservices'],
            'ai_ml': ['machine learning', 'ai', 'neural network', 'tensorflow', 'pytorch', 'scikit-learn'],
            'mobile': ['mobile', 'ios', 'android', 'react native', 'flutter'],
            'devops': ['ci/cd', 'jenkins', 'git', 'github', 'gitlab', 'deployment']
        }
        
        for tech, keywords in tech_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                technologies.append(tech)
        
        # Programming concepts
        concept_keywords = {
            'algorithms': ['algorithm', 'data structure', 'sorting', 'searching', 'complexity'],
            'design_patterns': ['design pattern', 'singleton', 'factory', 'observer', 'mvc'],
            'testing': ['test', 'unit test', 'integration test', 'tdd', 'bdd'],
            'security': ['security', 'authentication', 'authorization', 'encryption', 'oauth'],
            'performance': ['performance', 'optimization', 'caching', 'scalability'],
            'architecture': ['architecture', 'microservices', 'monolith', 'api', 'rest']
        }
        
        for concept, keywords in concept_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                concepts.append(concept)
        
        insights["programming_languages"] = programming_languages
        insights["technologies"] = technologies
        insights["concepts"] = concepts
    
    # Enhanced key insights based on dynamic topics
    if insights["word_count"] > 500:
        insights["key_insights"].append("This is a substantial conversation with detailed content")
    
    if len(topics) > 2:
        insights["key_insights"].append(f"Covers multiple areas: {', '.join(topics[:3])}")
    elif len(topics) == 1:
        insights["key_insights"].append(f"Focused on {topics[0]}")
    
    if insights["sentiment"] != "neutral":
        insights["key_insights"].append(f"Overall sentiment is {insights['sentiment']}")
    
    # Add topic-specific insights
    for topic, data in dynamic_topics.items():
        if data['confidence'] > 0.6:
            insights["key_insights"].append(f"Strong focus on {topic} (confidence: {data['confidence']:.1f})")
    
    return insights

def generate_follow_up_prompts(user_question: str, analysis_context: str, detected_topics: dict) -> list:
    """
    Generate contextual follow-up prompts based on the user's question and analysis context.
    """
    follow_ups = []
    question_lower = user_question.lower()
    
    # Sentiment-related follow-ups
    if any(word in question_lower for word in ['sentiment', 'positive', 'negative', 'mood', 'emotion', 'mindset']):
        follow_ups.extend([
            "How has your emotional state evolved over time across different topics?",
            "What patterns do you see in your most positive vs challenging conversations?",
            "How does your positive mindset influence your learning and growth patterns?",
            "Would you like to explore the connection between your emotional state and productivity?"
        ])
    
    # Programming-related follow-ups
    if any(word in question_lower for word in ['programming', 'code', 'technical', 'development']) or 'programming' in detected_topics:
        follow_ups.extend([
            "How has your programming confidence evolved over time?",
            "What connections do you see between your programming skills and other life areas?",
            "How do your programming discussions reflect your problem-solving approach?",
            "Would you like to analyze your learning progression in specific technologies?"
        ])
    
    # Spiritual/personal growth follow-ups
    if any(word in question_lower for word in ['spiritual', 'growth', 'development', 'personal', 'mindset']) or 'spirituality' in detected_topics:
        follow_ups.extend([
            "How do your different interests contribute to your personal growth?",
            "What patterns do you see in your self-reflection and learning journey?",
            "How has your perspective on life evolved through your conversations?",
            "Would you like to explore the balance between different aspects of your life?"
        ])
    
    # Relationship follow-ups
    if any(word in question_lower for word in ['relationship', 'social', 'connection', 'people']) or 'relationships' in detected_topics:
        follow_ups.extend([
            "How do your relationship discussions reflect your communication style?",
            "What patterns do you see in your social interactions and connections?",
            "How do your relationships influence your other areas of interest?",
            "Would you like to explore your approach to conflict resolution and understanding?"
        ])
    
    # Health/wellness follow-ups
    if any(word in question_lower for word in ['health', 'wellness', 'fitness', 'wellbeing']) or 'health' in detected_topics:
        follow_ups.extend([
            "How do your health discussions connect to your overall lifestyle patterns?",
            "What does your approach to wellness tell you about your priorities?",
            "How has your understanding of health and wellbeing evolved?",
            "Would you like to explore the connection between physical and mental wellbeing?"
        ])
    
    # Business/career follow-ups
    if any(word in question_lower for word in ['business', 'career', 'work', 'professional']) or 'business' in detected_topics:
        follow_ups.extend([
            "How do your business interests align with your personal values?",
            "What patterns do you see in your professional development?",
            "How has your approach to work and career evolved over time?",
            "Would you like to explore the balance between professional and personal growth?"
        ])
    
    # Creativity follow-ups
    if any(word in question_lower for word in ['creative', 'art', 'creativity', 'expression']) or 'creativity' in detected_topics:
        follow_ups.extend([
            "How does your creativity influence your other areas of interest?",
            "What patterns do you see in your creative expression and inspiration?",
            "How has your creative process evolved through your conversations?",
            "Would you like to explore the connection between creativity and problem-solving?"
        ])
    
    # Cross-topic connection follow-ups
    if len(detected_topics) > 2:
        follow_ups.extend([
            "How do your different interests connect and influence each other?",
            "What patterns do you see across your various areas of discussion?",
            "How does your diverse range of interests contribute to your overall growth?",
            "Would you like to explore how your different passions complement each other?"
        ])
    
    # General growth and pattern follow-ups
    follow_ups.extend([
        "What trends do you notice in your conversation topics over time?",
        "How has your approach to learning and exploration evolved?",
        "What does your conversation history reveal about your core values?",
        "Would you like to explore specific breakthroughs or turning points in your journey?"
    ])
    
    # Remove duplicates and limit to 4-6 most relevant
    unique_follow_ups = list(dict.fromkeys(follow_ups))  # Preserve order while removing duplicates
    return unique_follow_ups[:6]

def generate_ai_response_with_gpt(user_message: str, conversations: List[Conversation], focus_conversation: Optional[Conversation] = None) -> str:
    """
    Generate an AI response using ChatGPT API with caching and optimization.
    """
    if not openai_client:
        return "OpenAI API is not configured. Please set your OPENAI_API_KEY environment variable."
    
    try:
        # Check cache first
        conversations_hash = get_conversations_hash(conversations)
        cache_key = get_cache_key(user_message, conversations_hash)
        cached_response = get_cached_response(cache_key)
        
        if cached_response:
            print(f"[CACHE] Cache hit for: {user_message[:50]}...")
            return cached_response
        
        print(f"[CACHE] Cache miss, calling API for: {user_message[:50]}...")
        
        # Prepare context from conversations
        context_data = prepare_conversation_context(conversations, focus_conversation)
        
        # Create a comprehensive prompt
        system_prompt = """You are an AI assistant that provides personalized analysis of ChatGPT conversation history. You adapt to whatever topics each user actually discusses - whether that's programming, spirituality, relationships, health, business, creativity, travel, politics, science, or any other topics.

You have access to dynamic topic analysis that identifies what each user actually talks about, including:
- Dynamically detected topics based on their actual conversation content
- Topic confidence scores and conversation counts
- Sentiment analysis and emotional patterns
- Programming languages and technologies (when relevant)
- Recent conversation trends and patterns

Your role is to:
1. Provide insights based on the user's ACTUAL conversation topics (not assumptions)
2. Reference the specific topics they discuss and their confidence levels
3. Offer personalized observations about their unique conversation patterns
4. Connect insights across different topics when relevant
5. Adapt your analysis to whatever life areas they focus on
6. Provide holistic insights that reflect their individual interests and growth journey

Be conversational, insightful, and specific. Reference the dynamic topic data provided and offer meaningful observations about their personal conversation patterns, whatever topics they discuss."""

        user_prompt = f"""
User Question: {user_message}

Conversation Context:
{context_data}

Please provide a comprehensive, insightful response that addresses the user's question using the conversation data provided. Be specific, reference patterns you see, and offer meaningful insights about their personal growth journey across all life areas - programming, spirituality, relationships, health, business, personal development, and any other topics they discuss.
"""

        # Call ChatGPT API with optimized parameters
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1200,  # Reduced from 1500
            temperature=0.7,
            presence_penalty=0.1,  # Reduce repetition
            frequency_penalty=0.1   # Reduce repetition
        )
        
        ai_response = response.choices[0].message.content or ""
        
        # Generate follow-up prompts
        all_dynamic_topics = {}
        for conv in conversations:
            insights = analyze_conversation_content(conv.content)
            for topic, data in insights.get('dynamic_topics', {}).items():
                if topic not in all_dynamic_topics:
                    all_dynamic_topics[topic] = data
        
        follow_up_prompts = generate_follow_up_prompts(user_message, context_data, all_dynamic_topics)
        
        # Add follow-up prompts to the response
        if follow_up_prompts:
            ai_response += "\n\n[INSIGHT] **Follow-up Questions You Might Find Interesting:**\n"
            for i, prompt in enumerate(follow_up_prompts, 1):
                ai_response += f"{i}. {prompt}\n"
        
        # Cache the response
        save_cached_response(cache_key, ai_response)
        
        return ai_response
        
    except Exception as e:
        return f"Error generating AI response: {str(e)}"

def prepare_conversation_context(conversations: List[Conversation], focus_conversation: Optional[Conversation] = None) -> str:
    """
    Prepare optimized context data for ChatGPT analysis using smart sampling.
    """
    if focus_conversation:
        # Focus on specific conversation
        insights = analyze_conversation_content(focus_conversation.content)
        return f"""
FOCUSED CONVERSATION ANALYSIS:
Title: {focus_conversation.title or 'Untitled'}
Date: {focus_conversation.created_at.isoformat() if focus_conversation.created_at else 'Unknown'}

Content Analysis:
- Word Count: {insights['word_count']}
- Detected Topics: {', '.join(insights.get('topics', []))}
- Dynamic Topic Scores: {', '.join([f"{topic} ({data['confidence']:.1f})" for topic, data in insights.get('dynamic_topics', {}).items()])}
- Programming Languages: {', '.join(insights.get('programming_languages', []))}
- Technologies: {', '.join(insights.get('technologies', []))}
- Concepts: {', '.join(insights.get('concepts', []))}
- Sentiment: {insights['sentiment']}
- Key Insights: {'; '.join(insights['key_insights'])}

Conversation Content (first 1500 characters):
{focus_conversation.content[:1500]}{'...' if len(focus_conversation.content) > 1500 else ''}
"""
    else:
        # Smart sampling strategy to preserve historical context
        total_conversations = len(conversations)
        
        # Strategy: Sample across time periods to preserve historical patterns
        if total_conversations <= 100:
            # For smaller datasets, use all conversations
            sampled_conversations = conversations
            sample_strategy = "all conversations"
        else:
            # For larger datasets, use stratified sampling
            sampled_conversations = smart_sample_conversations(conversations)
            sample_strategy = "stratified sampling"
        
        all_dynamic_topics = {}
        topic_conversations = {}
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        
        # Collect all dynamic topics and categorize conversations
        for conv in sampled_conversations:
            insights = analyze_conversation_content(conv.content)
            sentiment_counts[insights["sentiment"]] += 1
            
            # Aggregate dynamic topics
            for topic, data in insights.get('dynamic_topics', {}).items():
                if topic not in all_dynamic_topics:
                    all_dynamic_topics[topic] = {
                        'total_score': 0,
                        'conversation_count': 0,
                        'avg_confidence': 0,
                        'conversations': []
                    }
                
                all_dynamic_topics[topic]['total_score'] += data['score']
                all_dynamic_topics[topic]['conversation_count'] += 1
                all_dynamic_topics[topic]['conversations'].append((conv, insights))
            
            # Categorize by primary topic
            if insights.get('topics'):
                primary_topic = insights['topics'][0]  # Highest scoring topic
                if primary_topic not in topic_conversations:
                    topic_conversations[primary_topic] = []
                topic_conversations[primary_topic].append((conv, insights))
        
        # Calculate average confidence for each topic
        for topic, data in all_dynamic_topics.items():
            data['avg_confidence'] = data['total_score'] / (data['conversation_count'] * 5.0)  # Normalize
        
        # Sort topics by conversation count and confidence
        sorted_topics = sorted(all_dynamic_topics.items(), 
                             key=lambda x: (x[1]['conversation_count'], x[1]['avg_confidence']), 
                             reverse=True)
        
        # Build optimized context string
        context_parts = [f"OVERALL CONVERSATION ANALYTICS:\nTotal Conversations: {total_conversations} (analyzed: {len(sampled_conversations)} using {sample_strategy})\n"]
        
        # Dynamic topic breakdown (limit to top 6)
        context_parts.append("DYNAMIC TOPIC ANALYSIS:")
        for topic, data in sorted_topics[:6]:  # Reduced from 8 to 6
            context_parts.append(f"- {topic.title()}: {data['conversation_count']} conversations (avg confidence: {data['avg_confidence']:.2f})")
        
        # Programming analysis (if relevant)
        if 'programming' in all_dynamic_topics:
            programming_convos = all_dynamic_topics['programming']['conversations']
            all_languages = []
            all_technologies = []
            all_concepts = []
            
            for _, insights in programming_convos:
                all_languages.extend(insights.get('programming_languages', []))
                all_technologies.extend(insights.get('technologies', []))
                all_concepts.extend(insights.get('concepts', []))
            
            from collections import Counter
            lang_counts = Counter(all_languages)
            tech_counts = Counter(all_technologies)
            concept_counts = Counter(all_concepts)
            
            top_languages = [lang for lang, _ in lang_counts.most_common(3)]  # Reduced from 5 to 3
            top_technologies = [tech for tech, _ in tech_counts.most_common(3)]  # Reduced from 5 to 3
            top_concepts = [concept for concept, _ in concept_counts.most_common(3)]  # Reduced from 5 to 3
            
            context_parts.append(f"\nPROGRAMMING ANALYSIS:")
            context_parts.append(f"- Top Languages: {', '.join(top_languages) if top_languages else 'Various'}")
            context_parts.append(f"- Top Technologies: {', '.join(top_technologies) if top_technologies else 'Various'}")
            context_parts.append(f"- Key Concepts: {', '.join(top_concepts) if top_concepts else 'Various'}")
        
        # Sentiment distribution
        context_parts.append(f"\nSENTIMENT DISTRIBUTION:")
        context_parts.append(f"- Positive: {sentiment_counts['positive']} conversations")
        context_parts.append(f"- Neutral: {sentiment_counts['neutral']} conversations")
        context_parts.append(f"- Negative: {sentiment_counts['negative']} conversations")
        
        # Recent conversations by topic (limit to top 4 topics, 1 conversation each)
        context_parts.append(f"\nRECENT CONVERSATIONS BY TOPIC (last 1 each):")
        for topic, convos in list(topic_conversations.items())[:4]:  # Reduced from 6 to 4
            recent_convos = convos[-1:]  # Reduced from 2 to 1
            context_parts.append(f"{topic.title()}:")
            for conv, insights in recent_convos:
                context_parts.append(f"  - {conv.title or 'Untitled'} ({insights['sentiment']} sentiment)")
        
        return '\n'.join(context_parts)

def smart_sample_conversations(conversations: List[Conversation]) -> List[Conversation]:
    """
    Smart sampling strategy that preserves historical context and important patterns.
    """
    total_conversations = len(conversations)
    target_sample_size = 100  # Increased from 50 to preserve more context
    
    if total_conversations <= target_sample_size:
        return conversations
    
    # Strategy: Stratified sampling across time periods
    # 1. Always include recent conversations (last 30%)
    # 2. Sample from middle period (30-70%)
    # 3. Sample from early period (first 30%)
    # 4. Include high-value conversations (long, diverse topics)
    
    recent_count = int(total_conversations * 0.3)  # Last 30%
    early_count = int(total_conversations * 0.3)   # First 30%
    middle_count = total_conversations - recent_count - early_count
    
    # Get recent conversations (always include)
    recent_conversations = conversations[-recent_count:]
    
    # Get early conversations (always include some for historical context)
    early_conversations = conversations[:early_count]
    
    # Sample from middle period
    middle_conversations = conversations[early_count:-recent_count]
    middle_sample_size = target_sample_size - recent_count - min(early_count, 20)  # Keep some early ones
    
    # Smart sampling from middle period
    if len(middle_conversations) > middle_sample_size:
        # Sample based on conversation length and topic diversity
        middle_conversations = sample_by_value(middle_conversations, middle_sample_size)
    
    # Combine all samples
    sampled = early_conversations[:20] + middle_conversations + recent_conversations
    
    # Ensure we don't exceed target size
    if len(sampled) > target_sample_size:
        # Prioritize recent and high-value conversations
        sampled = sampled[-target_sample_size:]
    
    return sampled

def sample_by_value(conversations: List[Conversation], target_size: int) -> List[Conversation]:
    """
    Sample conversations based on their value (length, topic diversity, etc.).
    """
    if len(conversations) <= target_size:
        return conversations
    
    # Score conversations based on value indicators
    scored_conversations = []
    for conv in conversations:
        score = 0
        
        # Length score (longer conversations often have more insights)
        length_score = min(len(conv.content) / 1000, 5)  # Cap at 5 points
        score += length_score
        
        # Topic diversity score
        insights = analyze_conversation_content(conv.content)
        topic_diversity = len(insights.get('topics', []))
        score += topic_diversity * 2
        
        # Sentiment score (include both positive and negative for balance)
        if insights['sentiment'] != 'neutral':
            score += 1
        
        scored_conversations.append((conv, score))
    
    # Sort by score and take top conversations
    scored_conversations.sort(key=lambda x: x[1], reverse=True)
    selected = [conv for conv, _ in scored_conversations[:target_size]]
    
    # Also include some random samples to maintain diversity
    if len(conversations) > target_size * 2:
        remaining = [conv for conv in conversations if conv not in selected]
        random_sample_size = min(10, len(remaining))
        import random
        random_samples = random.sample(remaining, random_sample_size)
        selected.extend(random_samples)
    
    return selected

def generate_ai_response(user_message: str, conversations: List[Conversation], focus_conversation: Optional[Conversation] = None) -> str:
    """
    Enhanced AI response generation with ChatGPT API integration.
    """
    # Try to use ChatGPT API first
    if openai_client:
        return generate_ai_response_with_gpt(user_message, conversations, focus_conversation)
    
    # Fallback to the existing logic if API is not available
    return generate_ai_response_fallback(user_message, conversations, focus_conversation)

def generate_ai_response_fallback(user_message: str, conversations: List[Conversation], focus_conversation: Optional[Conversation] = None) -> str:
    """
    Fallback AI response generation without ChatGPT API.
    """
    # Original implementation logic here...
    message_lower = user_message.lower()
    
    if focus_conversation:
        # Focus on specific conversation
        insights = analyze_conversation_content(focus_conversation.content)
        
        if 'summary' in message_lower or 'overview' in message_lower:
            return f"Here's a summary of your conversation '{focus_conversation.title or 'Untitled'}':\n\n" \
                   f"• Word count: {insights['word_count']}\n" \
                   f"• Topics: {', '.join(insights['topics']) if insights['topics'] else 'Various'}\n" \
                   f"• Sentiment: {insights['sentiment'].title()}\n" \
                   f"• Key insights: {'; '.join(insights['key_insights'])}"
        
        elif 'topic' in message_lower:
            return f"The main topics in this conversation are: {', '.join(insights['topics']) if insights['topics'] else 'Various topics covered'}"
        
        elif 'sentiment' in message_lower or 'mood' in message_lower:
            return f"The overall sentiment of this conversation is {insights['sentiment']}."
        
        else:
            return f"I've analyzed your conversation '{focus_conversation.title or 'Untitled'}'. " \
                   f"It contains {insights['word_count']} words and covers topics like {', '.join(insights['topics']) if insights['topics'] else 'various subjects'}. " \
                   f"What specific aspect would you like to know more about?"
    
    else:
        # Analyze all conversations
        total_conversations = len(conversations)
        total_words = sum(len(conv.content.split()) for conv in conversations)
        all_topics = set()
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        programming_conversations = []
        spiritual_conversations = []
        positive_conversations = []
        
        for conv in conversations:
            insights = analyze_conversation_content(conv.content)
            all_topics.update(insights["topics"])
            sentiment_counts[insights["sentiment"]] += 1
            
            # Categorize conversations
            if 'Programming' in insights["topics"]:
                programming_conversations.append((conv, insights))
            if any(word in conv.content.lower() for word in ['spiritual', 'philosophy', 'belief', 'faith', 'meditation', 'mindfulness']):
                spiritual_conversations.append((conv, insights))
            if insights["sentiment"] == "positive":
                positive_conversations.append((conv, insights))
        
        # Handle specific queries
        if 'programming' in message_lower or 'code' in message_lower:
            if programming_conversations:
                total_prog_words = sum(insights['word_count'] for _, insights in programming_conversations)
                avg_prog_sentiment = sum(1 for _, insights in programming_conversations if insights['sentiment'] == 'positive') / len(programming_conversations)
                
                # Analyze programming languages and technologies
                all_languages = []
                all_technologies = []
                all_concepts = []
                difficulty_levels = []
                
                for _, insights in programming_conversations:
                    all_languages.extend(insights.get('programming_languages', []))
                    all_technologies.extend(insights.get('technologies', []))
                    all_concepts.extend(insights.get('concepts', []))
                    difficulty_levels.append(insights.get('difficulty_level', 'intermediate'))
                
                # Count frequencies
                from collections import Counter
                lang_counts = Counter(all_languages)
                tech_counts = Counter(all_technologies)
                concept_counts = Counter(all_concepts)
                difficulty_counts = Counter(difficulty_levels)
                
                # Get top items
                top_languages = [lang for lang, _ in lang_counts.most_common(5)]
                top_technologies = [tech for tech, _ in tech_counts.most_common(5)]
                top_concepts = [concept for concept, _ in concept_counts.most_common(5)]
                dominant_difficulty = difficulty_counts.most_common(1)[0][0] if difficulty_counts else 'intermediate'
                
                response = f"I found {len(programming_conversations)} programming-related conversations in your data:\n\n" \
                          f"• Total programming conversations: {len(programming_conversations)}\n" \
                          f"• Total words in programming chats: {total_prog_words:,}\n" \
                          f"• Average sentiment: {'Positive' if avg_prog_sentiment > 0.5 else 'Neutral' if avg_prog_sentiment > 0.3 else 'Negative'}\n" \
                          f"• Most discussed programming languages: {', '.join(top_languages) if top_languages else 'Various'}\n" \
                          f"• Top technologies: {', '.join(top_technologies) if top_technologies else 'Various'}\n" \
                          f"• Key concepts: {', '.join(top_concepts) if top_concepts else 'Various'}\n" \
                          f"• Overall difficulty level: {dominant_difficulty.title()}"
                
                # Add learning insights
                if dominant_difficulty == 'beginner':
                    response += "\n\n[LEARNING] Learning Pattern: You seem to be focusing on foundational concepts and getting started with programming."
                elif dominant_difficulty == 'advanced':
                    response += "\n\n[ADVANCED] Advanced Topics: You're diving deep into complex programming concepts and advanced techniques."
                else:
                    response += "\n\n[BALANCED] Balanced Approach: You're covering a mix of beginner and advanced programming topics."
                
                return response
            else:
                return "I don't see any programming-related conversations in your data. Your conversations seem to focus on other topics."
        
        elif 'spiritual' in message_lower or 'philosophy' in message_lower:
            if spiritual_conversations:
                return f"I found {len(spiritual_conversations)} conversations that touch on spiritual or philosophical topics:\n\n" \
                       f"• Total spiritual conversations: {len(spiritual_conversations)}\n" \
                       f"• Common themes: mindfulness, personal growth, life purpose, meditation\n" \
                       f"• Sentiment: Mostly positive and reflective\n" \
                       f"• Key insights: You seem to be exploring personal development and inner growth"
            else:
                return "I don't see many explicitly spiritual or philosophical conversations in your data. Your conversations seem to focus more on practical topics like education, business, and relationships."
        
        elif 'positive' in message_lower or 'happy' in message_lower:
            if positive_conversations:
                return f"I found {len(positive_conversations)} conversations with positive sentiment:\n\n" \
                       f"• Total positive conversations: {len(positive_conversations)}\n" \
                       f"• Percentage of total: {len(positive_conversations)/total_conversations*100:.1f}%\n" \
                       f"• Common topics in positive chats: {', '.join(set().union(*[insights['topics'] for _, insights in positive_conversations[:5]]))}\n" \
                       f"• Average word count in positive conversations: {sum(insights['word_count'] for _, insights in positive_conversations)//len(positive_conversations)}"
            else:
                return "I don't see many conversations with strongly positive sentiment. Most of your conversations appear to be neutral in tone."
        
        elif 'summary' in message_lower or 'overview' in message_lower:
            dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0]
            return f"Here's an overview of your {total_conversations} conversations:\n\n" \
                   f"• Total conversations: {total_conversations}\n" \
                   f"• Total words: {total_words:,}\n" \
                   f"• Average words per conversation: {total_words//total_conversations if total_conversations > 0 else 0}\n" \
                   f"• Main topics: {', '.join(all_topics) if all_topics else 'Various'}\n" \
                   f"• Sentiment breakdown: {sentiment_counts['positive']} positive, {sentiment_counts['negative']} negative, {sentiment_counts['neutral']} neutral\n" \
                   f"• Overall tone: {dominant_sentiment.title()}"
        
        elif 'topic' in message_lower:
            return f"Across all your conversations, the main topics are: {', '.join(all_topics) if all_topics else 'Various topics covered'}"
        
        elif 'pattern' in message_lower or 'trend' in message_lower:
            dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0]
            return f"I notice some patterns in your conversations:\n\n" \
                   f"• You've discussed {len(all_topics)} different topics\n" \
                   f"• Most conversations have a {dominant_sentiment} tone\n" \
                   f"• Average conversation length: {total_words // total_conversations if total_conversations > 0 else 0} words\n" \
                   f"• Most active topics: {', '.join(list(all_topics)[:3]) if all_topics else 'Various'}"
        
        else:
            return f"I can help you analyze your {total_conversations} conversations! " \
                   f"You can ask me about:\n" \
                   f"• Summaries and overviews\n" \
                   f"• Topics and themes\n" \
                   f"• Sentiment analysis\n" \
                   f"• Patterns and trends\n" \
                   f"• Specific conversation details (mention the conversation ID)\n\n" \
                   f"Try asking: 'Give me a summary of my conversations' or 'What are the main topics I discuss?'"

@router.post("/send")
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Send a message to the AI assistant and get a response.
    """
    # Get user's conversations
    conversations = db.query(Conversation).filter(Conversation.user_id == current_user.id).all()
    
    if not conversations:
        raise HTTPException(
            status_code=404,
            detail="No conversations found. Please upload some ChatGPT conversations first."
        )
    
    # Find specific conversation if requested
    focus_conversation = None
    if request.conversation_id:
        focus_conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not focus_conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
    
    # Get or create session for storing interactions
    session = get_or_create_session(db, current_user.id)
    
    # Create context fusion engine
    context_engine = ContextFusionEngine(db)
    
    # Generate holistic prompt with context fusion
    context_data = context_engine.create_holistic_prompt(
        user_id=current_user.id,
        current_question=request.message,
        include_historical=True,
        include_recent=True
    )
    
    # Generate AI response with status updates
    try:
        ai_response = generate_ai_response_with_status(request.message, conversations, focus_conversation)
        
        # Store the interaction
        context_used = []
        if focus_conversation:
            context_used.append(f"conversation_{focus_conversation.id}")
        
        metadata = {
            "topics": ai_response.get('topics', []),
            "sentiment": ai_response.get('sentiment', 'neutral'),
            "word_count": len(request.message.split())
        }
        
        store_interaction(
            db=db,
            session_id=session.id,
            user_question=request.message,
            ai_response=ai_response['message'],
            context_used=context_used,
            metadata=metadata
        )
        
        return ChatResponse(
            message=ai_response['message'],
            conversation_id=request.conversation_id,
            timestamp=datetime.utcnow(),
            processing_status=ai_response.get('status', 'completed'),
            processing_stage=ai_response.get('stage', 'response_generated')
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )

@router.post("/send-stream")
async def send_message_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Send a message to the AI assistant and get streaming status updates.
    """
    async def generate_status_updates():
        try:
            # Get user's conversations
            conversations = db.query(Conversation).filter(Conversation.user_id == current_user.id).all()
            
            if not conversations:
                yield f"data: {json.dumps({'error': 'No conversations found. Please upload some ChatGPT conversations first.'})}\n\n"
                return
            
            # Find specific conversation if requested
            focus_conversation = None
            if request.conversation_id:
                focus_conversation = db.query(Conversation).filter(
                    Conversation.id == request.conversation_id,
                    Conversation.user_id == current_user.id
                ).first()
                
                if not focus_conversation:
                    yield f"data: {json.dumps({'error': 'Conversation not found'})}\n\n"
                    return
            
            # Get or create session for storing interactions
            session = get_or_create_session(db, current_user.id)
            
            # Stage 1: Checking cache
            yield f"data: {json.dumps({'stage': 'cache_check', 'status': 'Checking for cached response...', 'icon': '🔍'})}\n\n"
            await asyncio.sleep(0.5)
            
            # Stage 2: Analyzing conversations
            yield f"data: {json.dumps({'stage': 'analysis', 'status': 'Analyzing your conversations...', 'icon': '📊'})}\n\n"
            await asyncio.sleep(1)
            
            # Stage 3: Preparing context
            yield f"data: {json.dumps({'stage': 'context', 'status': 'Preparing conversation context...', 'icon': '🧠'})}\n\n"
            await asyncio.sleep(0.8)
            
            # Stage 4: Contacting OpenAI
            yield f"data: {json.dumps({'stage': 'openai', 'status': 'Contacting OpenAI API...', 'icon': '🤖'})}\n\n"
            await asyncio.sleep(1.2)
            
            # Stage 5: Generating response
            yield f"data: {json.dumps({'stage': 'generation', 'status': 'Crafting your personalized response...', 'icon': '✨'})}\n\n"
            await asyncio.sleep(1.5)
            
            # Stage 6: Processing and formatting
            yield f"data: {json.dumps({'stage': 'formatting', 'status': 'Adding insights and follow-up questions...', 'icon': '💡'})}\n\n"
            await asyncio.sleep(0.8)
            
            # Yield a status before calling OpenAI (blocking call)
            yield f"data: {json.dumps({'stage': 'openai_wait', 'status': 'Waiting for OpenAI API response...', 'icon': '🤖'})}\n\n"
            
            # Generate the actual response (blocking)
            ai_response = generate_ai_response_with_status(request.message, conversations, focus_conversation)
            
            # Store the interaction
            context_used = []
            if focus_conversation:
                context_used.append(f"conversation_{focus_conversation.id}")
            
            metadata = {
                "topics": ai_response.get('topics', []),
                "sentiment": ai_response.get('sentiment', 'neutral'),
                "word_count": len(request.message.split())
            }
            
            print(f"🔍 Chat API: Storing interaction for session {session.id}")
            print(f"🔍 Chat API: User question: {request.message[:50]}...")
            print(f"🔍 Chat API: AI response length: {len(ai_response['message'])}")
            
            store_interaction(
                db=db,
                session_id=session.id,
                user_question=request.message,
                ai_response=ai_response['message'],
                context_used=context_used,
                metadata=metadata
            )
            
            print(f"🔍 Chat API: Interaction stored successfully")
            
            # Final response
            yield f"data: {json.dumps({'stage': 'complete', 'status': 'Response ready!', 'message': ai_response['message'], 'icon': '✅'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Error generating response: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        generate_status_updates(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

def generate_ai_response_with_status(user_message: str, conversations: List[Conversation], focus_conversation: Optional[Conversation] = None) -> Dict[str, Any]:
    """
    Generate an AI response with status information.
    """
    if not openai_client:
        return {
            'message': "OpenAI API is not configured. Please set your OPENAI_API_KEY environment variable.",
            'status': 'error',
            'stage': 'api_error'
        }
    
    try:
        # Check cache first
        conversations_hash = get_conversations_hash(conversations)
        cache_key = get_cache_key(user_message, conversations_hash)
        cached_response = get_cached_response(cache_key)
        
        if cached_response:
            return {
                'message': cached_response,
                'status': 'completed',
                'stage': 'cache_hit'
            }
        
        # Prepare context from conversations
        context_data = prepare_conversation_context(conversations, focus_conversation)
        
        # Create a comprehensive prompt
        system_prompt = """You are an AI assistant that provides personalized analysis of ChatGPT conversation history. You adapt to whatever topics each user actually discusses - whether that's programming, spirituality, relationships, health, business, creativity, travel, politics, science, or any other topics.

You have access to dynamic topic analysis that identifies what each user actually talks about, including:
- Dynamically detected topics based on their actual conversation content
- Topic confidence scores and conversation counts
- Sentiment analysis and emotional patterns
- Programming languages and technologies (when relevant)
- Recent conversation trends and patterns

Your role is to:
1. Provide insights based on the user's ACTUAL conversation topics (not assumptions)
2. Reference the specific topics they discuss and their confidence levels
3. Offer personalized observations about their unique conversation patterns
4. Connect insights across different topics when relevant
5. Adapt your analysis to whatever life areas they focus on
6. Provide holistic insights that reflect their individual interests and growth journey

Be conversational, insightful, and specific. Reference the dynamic topic data provided and offer meaningful observations about their personal conversation patterns, whatever topics they discuss."""

        user_prompt = f"""
User Question: {user_message}

Conversation Context:
{context_data}

Please provide a comprehensive, insightful response that addresses the user's question using the conversation data provided. Be specific, reference patterns you see, and offer meaningful insights about their personal growth journey across all life areas - programming, spirituality, relationships, health, business, personal development, and any other topics they discuss.
"""

        # Call ChatGPT API with optimized parameters
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1200,  # Reduced from 1500
            temperature=0.7,
            presence_penalty=0.1,  # Reduce repetition
            frequency_penalty=0.1   # Reduce repetition
        )
        
        ai_response = response.choices[0].message.content or ""
        
        # Generate follow-up prompts
        all_dynamic_topics = {}
        for conv in conversations:
            insights = analyze_conversation_content(conv.content)
            for topic, data in insights.get('dynamic_topics', {}).items():
                if topic not in all_dynamic_topics:
                    all_dynamic_topics[topic] = data
        
        follow_up_prompts = generate_follow_up_prompts(user_message, context_data, all_dynamic_topics)
        
        # Add follow-up prompts to the response
        if follow_up_prompts:
            ai_response += "\n\n[INSIGHT] **Follow-up Questions You Might Find Interesting:**\n"
            for i, prompt in enumerate(follow_up_prompts, 1):
                ai_response += f"{i}. {prompt}\n"
        
        # Cache the response
        save_cached_response(cache_key, ai_response)
        
        return {
            'message': ai_response,
            'status': 'completed',
            'stage': 'response_generated'
        }
        
    except Exception as e:
        return {
            'message': f"Error generating AI response: {str(e)}",
            'status': 'error',
            'stage': 'generation_error'
        }

@router.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get all conversations for the current user with basic analytics.
    """
    conversations = db.query(Conversation).filter(Conversation.user_id == current_user.id).all()
    
    conversation_list = []
    for conv in conversations:
        insights = analyze_conversation_content(conv.content)
        conversation_list.append({
            "id": conv.id,
            "title": conv.title or "Untitled",
            "content_preview": conv.content[:200] + "..." if len(conv.content) > 200 else conv.content,
            "word_count": insights["word_count"],
            "topics": insights["topics"],
            "sentiment": insights["sentiment"],
            "created_at": conv.created_at.isoformat()
        })
    
    return {
        "conversations": conversation_list,
        "total_count": len(conversations),
        "total_words": sum(conv["word_count"] for conv in conversation_list)
    }

@router.get("/conversations/{conversation_id}")
async def get_conversation_details(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get detailed analysis of a specific conversation.
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    insights = analyze_conversation_content(conversation.content)
    
    return {
        "id": conversation.id,
        "title": conversation.title or "Untitled",
        "content": conversation.content,
        "insights": insights,
        "created_at": conversation.created_at.isoformat()
    } 

@router.get("/programming-analytics")
async def get_programming_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get detailed analytics about programming conversations.
    """
    # Get user's conversations
    conversations = db.query(Conversation).filter(Conversation.user_id == current_user.id).all()
    
    if not conversations:
        raise HTTPException(
            status_code=404,
            detail="No conversations found. Please upload some ChatGPT conversations first."
        )
    
    # Analyze all conversations
    programming_conversations = []
    all_languages = []
    all_technologies = []
    all_concepts = []
    difficulty_levels = []
    sentiment_by_language = {}
    monthly_activity = {}
    
    for conv in conversations:
        insights = analyze_conversation_content(conv.content)
        
        if 'Programming' in insights["topics"]:
            programming_conversations.append((conv, insights))
            
            # Collect data for analysis
            languages = insights.get('programming_languages', [])
            technologies = insights.get('technologies', [])
            concepts = insights.get('concepts', [])
            difficulty = insights.get('difficulty_level', 'intermediate')
            
            all_languages.extend(languages)
            all_technologies.extend(technologies)
            all_concepts.extend(concepts)
            difficulty_levels.append(difficulty)
            
            # Track sentiment by language
            for lang in languages:
                if lang not in sentiment_by_language:
                    sentiment_by_language[lang] = {'positive': 0, 'negative': 0, 'neutral': 0}
                sentiment_by_language[lang][insights['sentiment']] += 1
            
            # Track monthly activity
            month_key = conv.created_at.strftime('%Y-%m') if conv.created_at else 'Unknown'
            if month_key not in monthly_activity:
                monthly_activity[month_key] = 0
            monthly_activity[month_key] += 1
    
    if not programming_conversations:
        raise HTTPException(
            status_code=404,
            detail="No programming-related conversations found in your data."
        )
    
    # Calculate statistics
    from collections import Counter
    
    total_prog_words = sum(insights['word_count'] for _, insights in programming_conversations)
    avg_prog_sentiment = sum(1 for _, insights in programming_conversations if insights['sentiment'] == 'positive') / len(programming_conversations)
    
    lang_counts = Counter(all_languages)
    tech_counts = Counter(all_technologies)
    concept_counts = Counter(all_concepts)
    difficulty_counts = Counter(difficulty_levels)
    
    # Get top items
    top_languages = [{'language': lang, 'count': count} for lang, count in lang_counts.most_common(10)]
    top_technologies = [{'technology': tech, 'count': count} for tech, count in tech_counts.most_common(10)]
    top_concepts = [{'concept': concept, 'count': count} for concept, count in concept_counts.most_common(10)]
    
    # Calculate learning progression
    sorted_conversations = sorted(programming_conversations, key=lambda x: x[0].created_at if x[0].created_at else datetime.min)
    early_conversations = sorted_conversations[:len(sorted_conversations)//3]
    recent_conversations = sorted_conversations[-len(sorted_conversations)//3:]
    
    early_difficulty = Counter([insights.get('difficulty_level', 'intermediate') for _, insights in early_conversations])
    recent_difficulty = Counter([insights.get('difficulty_level', 'intermediate') for _, insights in recent_conversations])
    
    # Sentiment analysis by language
    language_sentiment = {}
    for lang, sentiments in sentiment_by_language.items():
        total = sum(sentiments.values())
        if total > 0:
            language_sentiment[lang] = {
                'positive_pct': (sentiments['positive'] / total) * 100,
                'negative_pct': (sentiments['negative'] / total) * 100,
                'neutral_pct': (sentiments['neutral'] / total) * 100,
                'total_conversations': total
            }
    
    # Monthly activity trend
    monthly_trend = sorted(monthly_activity.items())
    
    return {
        "summary": {
            "total_programming_conversations": len(programming_conversations),
            "total_words": total_prog_words,
            "average_sentiment": "Positive" if avg_prog_sentiment > 0.5 else "Neutral" if avg_prog_sentiment > 0.3 else "Negative",
            "sentiment_score": avg_prog_sentiment,
            "date_range": {
                "earliest": min(conv.created_at for conv, _ in programming_conversations if conv.created_at).isoformat() if any(conv.created_at for conv, _ in programming_conversations) else None,
                "latest": max(conv.created_at for conv, _ in programming_conversations if conv.created_at).isoformat() if any(conv.created_at for conv, _ in programming_conversations) else None
            }
        },
        "languages": {
            "top_languages": top_languages,
            "total_unique_languages": len(lang_counts),
            "sentiment_by_language": language_sentiment
        },
        "technologies": {
            "top_technologies": top_technologies,
            "total_unique_technologies": len(tech_counts)
        },
        "concepts": {
            "top_concepts": top_concepts,
            "total_unique_concepts": len(concept_counts)
        },
        "difficulty_analysis": {
            "current_distribution": dict(difficulty_counts),
            "learning_progression": {
                "early_period": dict(early_difficulty),
                "recent_period": dict(recent_difficulty)
            }
        },
        "activity_trends": {
            "monthly_activity": monthly_trend,
            "most_active_month": max(monthly_activity.items(), key=lambda x: x[1])[0] if monthly_activity else None
        },
        "insights": {
            "primary_focus": top_languages[0]['language'] if top_languages else "Various",
            "technology_stack": [tech['technology'] for tech in top_technologies[:3]],
            "key_learning_areas": [concept['concept'] for concept in top_concepts[:3]],
            "learning_pattern": "Beginner-focused" if difficulty_counts.get('beginner', 0) > difficulty_counts.get('advanced', 0) else "Advanced-focused" if difficulty_counts.get('advanced', 0) > difficulty_counts.get('beginner', 0) else "Balanced"
        }
    } 