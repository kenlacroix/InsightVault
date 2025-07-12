from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import json
import os
from ..database import get_sync_db
from ..models import User, Conversation
from ..auth import get_current_user
import openai

# Initialize OpenAI client
openai_client = None
try:
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        openai_client = openai.OpenAI(api_key=api_key)
except Exception as e:
    print(f"OpenAI client initialization failed: {e}")

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

def analyze_conversation_content(content: str) -> dict:
    """
    Analyze conversation content and extract insights.
    This is a simplified version - you can enhance this with more sophisticated analysis.
    """
    insights = {
        "word_count": len(content.split()),
        "character_count": len(content),
        "sentences": len([s for s in content.split('.') if s.strip()]),
        "topics": [],
        "sentiment": "neutral",
        "key_insights": [],
        "programming_languages": [],
        "technologies": [],
        "concepts": [],
        "difficulty_level": "intermediate"
    }
    
    # Simple topic detection
    topics = []
    content_lower = content.lower()
    
    # Programming-specific analysis
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
    
    if any(word in content_lower for word in ['code', 'programming', 'python', 'javascript']):
        topics.append('Programming')
    if any(word in content_lower for word in ['business', 'startup', 'entrepreneur']):
        topics.append('Business')
    if any(word in content_lower for word in ['health', 'fitness', 'exercise']):
        topics.append('Health & Fitness')
    if any(word in content_lower for word in ['learning', 'education', 'study']):
        topics.append('Education')
    if any(word in content_lower for word in ['relationship', 'family', 'friend']):
        topics.append('Relationships')
    if any(word in content_lower for word in ['goal', 'plan', 'future']):
        topics.append('Planning & Goals')
    
    insights["topics"] = topics
    
    # Determine difficulty level based on content
    beginner_keywords = ['beginner', 'basic', 'simple', 'tutorial', 'learn', 'getting started']
    advanced_keywords = ['advanced', 'complex', 'optimization', 'architecture', 'design patterns', 'algorithms']
    
    beginner_count = sum(1 for word in beginner_keywords if word in content_lower)
    advanced_count = sum(1 for word in advanced_keywords if word in content_lower)
    
    if advanced_count > beginner_count:
        insights["difficulty_level"] = "advanced"
    elif beginner_count > advanced_count:
        insights["difficulty_level"] = "beginner"
    
    # Simple sentiment analysis
    positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'happy', 'love', 'enjoy', 'solved', 'working', 'success']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry', 'frustrated', 'error', 'bug', 'broken', 'stuck']
    
    positive_count = sum(1 for word in positive_words if word in content_lower)
    negative_count = sum(1 for word in negative_words if word in content_lower)
    
    if positive_count > negative_count:
        insights["sentiment"] = "positive"
    elif negative_count > positive_count:
        insights["sentiment"] = "negative"
    
    # Key insights
    if insights["word_count"] > 500:
        insights["key_insights"].append("This is a substantial conversation with detailed content")
    if len(topics) > 2:
        insights["key_insights"].append("Covers multiple topics")
    if insights["sentiment"] != "neutral":
        insights["key_insights"].append(f"Overall sentiment is {insights['sentiment']}")
    if programming_languages:
        insights["key_insights"].append(f"Discusses {', '.join(programming_languages)} programming")
    if technologies:
        insights["key_insights"].append(f"Covers {', '.join(technologies)} technologies")
    
    return insights

def generate_ai_response_with_gpt(user_message: str, conversations: List[Conversation], focus_conversation: Optional[Conversation] = None) -> str:
    """
    Generate an AI response using ChatGPT API with rich context from conversations.
    """
    if not openai_client:
        return "OpenAI API is not configured. Please set your OPENAI_API_KEY environment variable."
    
    try:
        # Prepare context from conversations
        context_data = prepare_conversation_context(conversations, focus_conversation)
        
        # Create a comprehensive prompt
        system_prompt = """You are an AI assistant that helps users analyze their ChatGPT conversation history. You have access to detailed analytics about their conversations including:

- Programming languages and technologies discussed
- Sentiment analysis and emotional patterns
- Learning progression and difficulty levels
- Monthly activity trends
- Key insights and patterns

Your role is to:
1. Provide insightful analysis based on the conversation data
2. Identify patterns and trends in their learning journey
3. Offer personalized recommendations and observations
4. Answer specific questions about their programming conversations
5. Help them understand their growth and development

Be conversational, insightful, and specific. Reference the data provided and offer meaningful observations."""

        user_prompt = f"""
User Question: {user_message}

Conversation Context:
{context_data}

Please provide a comprehensive, insightful response that addresses the user's question using the conversation data provided. Be specific, reference patterns you see, and offer meaningful insights about their programming journey.
"""

        # Call ChatGPT API
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating AI response: {str(e)}"

def prepare_conversation_context(conversations: List[Conversation], focus_conversation: Optional[Conversation] = None) -> str:
    """
    Prepare rich context data for ChatGPT analysis.
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
- Programming Languages: {', '.join(insights.get('programming_languages', []))}
- Technologies: {', '.join(insights.get('technologies', []))}
- Concepts: {', '.join(insights.get('concepts', []))}
- Difficulty Level: {insights.get('difficulty_level', 'intermediate')}
- Sentiment: {insights['sentiment']}
- Key Insights: {'; '.join(insights['key_insights'])}

Conversation Content (first 2000 characters):
{focus_conversation.content[:2000]}{'...' if len(focus_conversation.content) > 2000 else ''}
"""
    else:
        # Analyze all conversations
        total_conversations = len(conversations)
        programming_conversations = []
        all_languages = []
        all_technologies = []
        all_concepts = []
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        
        for conv in conversations:
            insights = analyze_conversation_content(conv.content)
            sentiment_counts[insights["sentiment"]] += 1
            
            if 'Programming' in insights["topics"]:
                programming_conversations.append((conv, insights))
                all_languages.extend(insights.get('programming_languages', []))
                all_technologies.extend(insights.get('technologies', []))
                all_concepts.extend(insights.get('concepts', []))
        
        # Calculate statistics
        from collections import Counter
        lang_counts = Counter(all_languages)
        tech_counts = Counter(all_technologies)
        concept_counts = Counter(all_concepts)
        
        top_languages = [lang for lang, _ in lang_counts.most_common(5)]
        top_technologies = [tech for tech, _ in tech_counts.most_common(5)]
        top_concepts = [concept for concept, _ in concept_counts.most_common(5)]
        
        return f"""
OVERALL CONVERSATION ANALYTICS:
Total Conversations: {total_conversations}
Programming Conversations: {len(programming_conversations)}

Programming Analysis:
- Top Languages: {', '.join(top_languages) if top_languages else 'Various'}
- Top Technologies: {', '.join(top_technologies) if top_technologies else 'Various'}
- Key Concepts: {', '.join(top_concepts) if top_concepts else 'Various'}

Sentiment Distribution:
- Positive: {sentiment_counts['positive']} conversations
- Neutral: {sentiment_counts['neutral']} conversations  
- Negative: {sentiment_counts['negative']} conversations

Recent Programming Conversations (last 5):
{chr(10).join([f"- {conv.title or 'Untitled'} ({insights.get('difficulty_level', 'intermediate')} level, {insights['sentiment']} sentiment)" for conv, insights in programming_conversations[-5:]])}
"""

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
                    response += "\n\n📚 Learning Pattern: You seem to be focusing on foundational concepts and getting started with programming."
                elif dominant_difficulty == 'advanced':
                    response += "\n\n🚀 Advanced Topics: You're diving deep into complex programming concepts and advanced techniques."
                else:
                    response += "\n\n⚖️ Balanced Approach: You're covering a mix of beginner and advanced programming topics."
                
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
    
    # Generate AI response
    try:
        ai_response = generate_ai_response(request.message, conversations, focus_conversation)
        
        return ChatResponse(
            message=ai_response,
            conversation_id=request.conversation_id,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )

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