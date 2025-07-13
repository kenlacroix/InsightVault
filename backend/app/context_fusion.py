"""
Context Fusion Engine for InsightVault Phase 2.
Merges historical ChatGPT conversations with recent user interactions
to create holistic AI prompts that consider both data sources.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import Conversation, UserSession, UserInteraction
import json

class ContextFusionEngine:
    """
    Engine that fuses historical conversations and recent interactions
    into a single, comprehensive context for AI analysis.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.max_historical_context = 5000  # characters
        self.max_recent_context = 2000      # characters
        self.max_total_context = 8000       # characters
    
    def get_historical_context(self, user_id: int, limit_conversations: int = 15) -> Dict[str, Any]:
        """
        Get relevant historical conversations for context.
        """
        # Import here to avoid circular import
        from .api.chat import analyze_conversation_content
        # Get recent conversations
        conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.created_at.desc()).limit(limit_conversations).all()
        
        if not conversations:
            return {
                "conversations": [],
                "summary": "No historical conversations found.",
                "total_conversations": 0,
                "topics": [],
                "sentiment_summary": "neutral"
            }
        
        # Analyze conversations for context
        conversation_data = []
        all_topics = set()
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        
        for conv in conversations:
            # Analyze conversation content
            insights = analyze_conversation_content(conv.content)
            
            conversation_data.append({
                "id": conv.id,
                "title": conv.title or "Untitled",
                "content_preview": conv.content[:300] + "..." if len(conv.content) > 300 else conv.content,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "topics": insights.get("topics", []),
                "sentiment": insights.get("sentiment", "neutral"),
                "word_count": insights.get("word_count", 0),
                "key_insights": insights.get("key_insights", [])
            })
            
            # Collect topics and sentiment
            all_topics.update(insights.get("topics", []))
            sentiment = insights.get("sentiment", "neutral")
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1
        
        # Determine overall sentiment
        total_conversations = len(conversations)
        if sentiment_counts["positive"] > sentiment_counts["negative"]:
            overall_sentiment = "positive"
        elif sentiment_counts["negative"] > sentiment_counts["positive"]:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        return {
            "conversations": conversation_data,
            "summary": f"Found {total_conversations} historical conversations covering {len(all_topics)} topics.",
            "total_conversations": total_conversations,
            "topics": list(all_topics),
            "sentiment_summary": overall_sentiment,
            "sentiment_breakdown": sentiment_counts
        }
    
    def get_recent_interactions_context(self, user_id: int, limit_interactions: int = 5) -> Dict[str, Any]:
        """
        Get recent user interactions for context.
        """
        # Get current active session
        current_session = self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.session_end.is_(None)
        ).first()
        
        if not current_session:
            return {
                "interactions": [],
                "summary": "No active session found.",
                "total_interactions": 0,
                "session_info": None
            }
        
        # Get recent interactions
        interactions = self.db.query(UserInteraction).filter(
            UserInteraction.session_id == current_session.id
        ).order_by(UserInteraction.created_at.desc()).limit(limit_interactions).all()
        
        if not interactions:
            return {
                "interactions": [],
                "summary": "No recent interactions found.",
                "total_interactions": 0,
                "session_info": {
                    "id": current_session.id,
                    "started": current_session.session_start.isoformat() if current_session.session_start else None
                }
            }
        
        # Process interactions
        interaction_data = []
        for interaction in interactions:
            interaction_data.append({
                "id": interaction.id,
                "question": interaction.user_question,
                "answer": interaction.ai_response,
                "created_at": interaction.created_at.isoformat() if interaction.created_at else None,
                "context_used": interaction.context_used or [],
                "metadata": interaction.interaction_metadata or {}
            })
        
        return {
            "interactions": interaction_data,
            "summary": f"Found {len(interactions)} recent interactions in current session.",
            "total_interactions": len(interactions),
            "session_info": {
                "id": current_session.id,
                "started": current_session.session_start.isoformat() if current_session.session_start else None,
                "context_summary": current_session.context_summary
            }
        }
    
    def create_holistic_prompt(self, user_id: int, current_question: str, 
                             include_historical: bool = True, 
                             include_recent: bool = True) -> Dict[str, Any]:
        """
        Create a holistic prompt that combines historical and recent context.
        """
        context_data = {
            "historical": None,
            "recent": None,
            "combined_summary": "",
            "prompt": "",
            "context_breakdown": {}
        }
        
        # Get historical context
        if include_historical:
            context_data["historical"] = self.get_historical_context(user_id)
        
        # Get recent interactions context
        if include_recent:
            context_data["recent"] = self.get_recent_interactions_context(user_id)
        
        # Create combined summary
        summary_parts = []
        
        if context_data["historical"]:
            hist = context_data["historical"]
            summary_parts.append(f"Historical: {hist['total_conversations']} conversations, {len(hist['topics'])} topics, {hist['sentiment_summary']} sentiment")
        
        if context_data["recent"]:
            recent = context_data["recent"]
            summary_parts.append(f"Recent: {recent['total_interactions']} interactions in current session")
        
        context_data["combined_summary"] = " | ".join(summary_parts) if summary_parts else "No context available"
        
        # Generate the holistic prompt
        prompt = self._generate_holistic_prompt(current_question, context_data)
        context_data["prompt"] = prompt
        
        # Add context breakdown for frontend
        context_data["context_breakdown"] = {
            "historical_conversations": context_data["historical"]["total_conversations"] if context_data["historical"] else 0,
            "recent_interactions": context_data["recent"]["total_interactions"] if context_data["recent"] else 0,
            "historical_topics": context_data["historical"]["topics"] if context_data["historical"] else [],
            "session_active": context_data["recent"]["session_info"] is not None if context_data["recent"] else False
        }
        
        return context_data
    
    def _generate_holistic_prompt(self, current_question: str, context_data: Dict[str, Any]) -> str:
        """
        Generate the actual prompt text combining all context.
        """
        prompt_parts = []
        
        # System instruction
        prompt_parts.append("You are a personal growth AI assistant with access to both historical ChatGPT conversations and recent user interactions. Consider both data sources to provide comprehensive, contextual insights.")
        
        # Historical context
        if context_data["historical"]:
            hist = context_data["historical"]
            prompt_parts.append(f"""
HISTORICAL CONVERSATIONS ({hist['total_conversations']} conversations):
{hist['summary']}
Topics covered: {', '.join(hist['topics'][:10])}
Overall sentiment: {hist['sentiment_summary']}

Recent conversations:
""")
            
            # Add recent conversation previews
            for conv in hist['conversations'][:3]:
                prompt_parts.append(f"- {conv['title']}: {conv['content_preview']}")
        
        # Recent interactions context
        if context_data["recent"]:
            recent = context_data["recent"]
            prompt_parts.append(f"""
RECENT INTERACTIONS ({recent['total_interactions']} in current session):
{recent['summary']}
""")
            
            # Add recent interaction previews
            for interaction in recent['interactions'][:3]:
                prompt_parts.append(f"Q: {interaction['question'][:100]}...")
                prompt_parts.append(f"A: {interaction['answer'][:100]}...")
        
        # Current question
        prompt_parts.append(f"""
CURRENT QUESTION: {current_question}

INSTRUCTIONS:
- Consider both historical patterns and recent user interactions
- Reference specific conversations and previous insights when relevant
- Build upon previous discussions and insights
- Identify patterns across time (historical + recent)
- Provide holistic analysis that connects past and present

RESPONSE FORMAT:
- Direct answer to current question
- Connections to historical patterns
- References to previous interactions
- New insights combining both contexts
- Suggested follow-up questions
""")
        
        return "\n".join(prompt_parts)
    
    def get_context_for_frontend(self, user_id: int) -> Dict[str, Any]:
        """
        Get context data formatted for frontend display.
        """
        historical = self.get_historical_context(user_id, limit_conversations=10)
        recent = self.get_recent_interactions_context(user_id, limit_interactions=3)
        
        return {
            "historical_context": {
                "conversations": historical["conversations"][:5],  # Limit for UI
                "total_count": historical["total_conversations"],
                "topics": historical["topics"][:8],  # Top 8 topics
                "sentiment": historical["sentiment_summary"]
            },
            "recent_context": {
                "interactions": recent["interactions"][:3],  # Limit for UI
                "total_count": recent["total_interactions"],
                "session_active": recent["session_info"] is not None,
                "session_info": recent["session_info"]
            },
            "combined_summary": f"{historical['total_conversations']} historical conversations, {recent['total_interactions']} recent interactions"
        } 