"""
AI Assistant Core for InsightVault
Phase 1: Natural Language Query Processing and Insight Generation

Provides the main AI assistant functionality:
- Natural language query processing
- Semantic search integration
- Insight generation with templates
- Conversation analysis and synthesis
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import re

from enhanced_chat_parser import EnhancedConversation, EnhancedChatParser
from ai_semantic_search import AISemanticSearch, SearchResult, QueryIntent


@dataclass
class InsightTemplate:
    """Template for generating structured insights"""
    summary_template: str
    key_learnings_template: str
    evolution_timeline_template: str
    breakthrough_moments_template: str
    next_steps_template: str
    confidence_calculation: str


@dataclass
class GeneratedInsight:
    """Represents a generated insight response"""
    summary: str
    key_learnings: List[str]
    evolution_timeline: Dict[str, str]
    breakthrough_moments: List[Dict[str, Any]]
    actionable_next_steps: List[str]
    confidence_score: float
    supporting_conversations: List[Dict[str, Any]]
    query_intent: QueryIntent
    generated_at: datetime = field(default_factory=datetime.now)


class AIAssistant:
    """Main AI assistant for personal growth analysis"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config = self._load_config(config_path)
        self.parser = EnhancedChatParser()
        self.semantic_search = AISemanticSearch()
        self.conversations: List[EnhancedConversation] = []
        
        # Initialize insight templates
        self.insight_templates = self._initialize_insight_templates()
        
        # Query processing patterns
        self.query_patterns = self._initialize_query_patterns()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Use default config
            return {
                'ai_assistant': {
                    'max_search_results': 15,
                    'min_confidence_score': 0.3,
                    'insight_depth': 'comprehensive',
                    'enable_breakthrough_detection': True,
                    'enable_timeline_analysis': True
                }
            }
    
    def _initialize_insight_templates(self) -> Dict[str, InsightTemplate]:
        """Initialize templates for different types of insights"""
        return {
            'learning': InsightTemplate(
                summary_template="Your understanding of {topic} has evolved significantly over {time_period}. {key_insight}",
                key_learnings_template="• {learning_point}",
                evolution_timeline_template="• {period}: {description}",
                breakthrough_moments_template="• Conversation #{conv_id}: \"{quote}\"",
                next_steps_template="• {action_item}",
                confidence_calculation="base_score * (1 + breakthrough_bonus + recency_bonus)"
            ),
            'relationships': InsightTemplate(
                summary_template="Your approach to {topic} has transformed from {old_pattern} to {new_pattern}. {key_insight}",
                key_learnings_template="• {learning_point}",
                evolution_timeline_template="• {period}: {description}",
                breakthrough_moments_template="• Conversation #{conv_id}: \"{quote}\"",
                next_steps_template="• {action_item}",
                confidence_calculation="base_score * (1 + emotional_intensity_bonus + pattern_consistency_bonus)"
            ),
            'goals': InsightTemplate(
                summary_template="Your goal-setting and achievement patterns show {pattern_description}. {key_insight}",
                key_learnings_template="• {learning_point}",
                evolution_timeline_template="• {period}: {description}",
                breakthrough_moments_template="• Conversation #{conv_id}: \"{quote}\"",
                next_steps_template="• {action_item}",
                confidence_calculation="base_score * (1 + progress_consistency_bonus + goal_clarity_bonus)"
            ),
            'emotions': InsightTemplate(
                summary_template="Your emotional awareness and regulation have {change_description}. {key_insight}",
                key_learnings_template="• {learning_point}",
                evolution_timeline_template="• {period}: {description}",
                breakthrough_moments_template="• Conversation #{conv_id}: \"{quote}\"",
                next_steps_template="• {action_item}",
                confidence_calculation="base_score * (1 + emotional_depth_bonus + self_awareness_bonus)"
            ),
            'general': InsightTemplate(
                summary_template="Your journey with {topic} reveals {pattern_description}. {key_insight}",
                key_learnings_template="• {learning_point}",
                evolution_timeline_template="• {period}: {description}",
                breakthrough_moments_template="• Conversation #{conv_id}: \"{quote}\"",
                next_steps_template="• {action_item}",
                confidence_calculation="base_score * (1 + relevance_bonus + data_quality_bonus)"
            )
        }
    
    def _initialize_query_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for query classification"""
        return {
            'learning': [
                r'what.*learn.*about',
                r'how.*understanding.*evolved',
                r'what.*discovered.*about',
                r'how.*knowledge.*grown',
                r'what.*realized.*about'
            ],
            'relationships': [
                r'relationship.*boundary',
                r'friendship.*pattern',
                r'how.*interact.*with',
                r'what.*learn.*relationship',
                r'communication.*style'
            ],
            'goals': [
                r'goal.*progress',
                r'what.*achieved',
                r'how.*planning.*evolved',
                r'what.*working.*toward',
                r'achievement.*pattern'
            ],
            'emotions': [
                r'emotional.*well.*being',
                r'how.*feel.*changed',
                r'mental.*health.*journey',
                r'emotional.*awareness',
                r'stress.*management'
            ]
        }
    
    def load_conversations(self, file_path: str) -> bool:
        """Load and process conversations for AI analysis"""
        try:
            success = self.parser.load_conversations(file_path)
            if success:
                self.conversations = self.parser.conversations
                
                # Index conversations for semantic search
                if self.conversations:
                    self.semantic_search.index_conversations(self.conversations)
                
                print(f"AI Assistant loaded {len(self.conversations)} conversations")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error loading conversations: {e}")
            return False
    
    def process_query(self, query: str) -> GeneratedInsight:
        """Process a natural language query and generate insights"""
        try:
            print(f"Processing query: {query}")
            
            # Parse query intent
            query_intent = self.semantic_search._parse_query_intent(query)
            
            # Perform semantic search
            search_results = self.semantic_search.search(
                query, 
                self.conversations, 
                limit=self.config.get('ai_assistant', {}).get('max_search_results', 15)
            )
            
            if not search_results:
                return self._generate_empty_insight(query_intent)
            
            # Analyze relevant conversations
            analysis_data = self._analyze_conversations(search_results, query_intent)
            
            # Generate structured insight
            insight = self._generate_structured_insight(query, query_intent, analysis_data, search_results)
            
            return insight
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return self._generate_error_insight(query)
    
    def _analyze_conversations(self, search_results: List[SearchResult], 
                             query_intent: QueryIntent) -> Dict[str, Any]:
        """Analyze relevant conversations for insight generation"""
        analysis = {
            'total_conversations': len(search_results),
            'date_range': self._get_date_range(search_results),
            'key_themes': self._extract_key_themes(search_results),
            'sentiment_trends': self._analyze_sentiment_trends(search_results),
            'breakthrough_moments': self._find_breakthrough_moments(search_results),
            'evolution_patterns': self._detect_evolution_patterns(search_results, query_intent),
            'common_patterns': self._identify_common_patterns(search_results),
            'actionable_insights': self._extract_actionable_insights(search_results)
        }
        
        return analysis
    
    def _get_date_range(self, search_results: List[SearchResult]) -> Dict[str, datetime]:
        """Get the date range of relevant conversations"""
        dates = [result.conversation.create_date for result in search_results]
        return {
            'earliest': min(dates) if dates else datetime.now(),
            'latest': max(dates) if dates else datetime.now()
        }
    
    def _extract_key_themes(self, search_results: List[SearchResult]) -> List[str]:
        """Extract key themes from relevant conversations"""
        all_themes = []
        for result in search_results:
            all_themes.extend(result.conversation.metadata.key_themes)
        
        # Count and return most common themes
        theme_counts = Counter(all_themes)
        return [theme for theme, count in theme_counts.most_common(5)]
    
    def _analyze_sentiment_trends(self, search_results: List[SearchResult]) -> Dict[str, Any]:
        """Analyze sentiment trends across conversations"""
        sentiments = [result.conversation.metadata.sentiment_trend for result in search_results]
        
        if not sentiments:
            return {'average': 0.0, 'trend': 'neutral'}
        
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        # Determine trend
        if avg_sentiment > 0.1:
            trend = 'positive'
        elif avg_sentiment < -0.1:
            trend = 'negative'
        else:
            trend = 'neutral'
        
        return {
            'average': avg_sentiment,
            'trend': trend,
            'conversation_count': len(sentiments)
        }
    
    def _find_breakthrough_moments(self, search_results: List[SearchResult]) -> List[Dict[str, Any]]:
        """Find breakthrough moments across conversations"""
        breakthroughs = []
        
        for result in search_results:
            conv = result.conversation
            for moment_idx in conv.metadata.breakthrough_moments:
                if moment_idx < len(conv.messages):
                    message = conv.messages[moment_idx]
                    breakthroughs.append({
                        'conversation_id': conv.id,
                        'conversation_title': conv.title,
                        'date': conv.create_date,
                        'message_index': moment_idx,
                        'content': message.content[:200] + '...' if len(message.content) > 200 else message.content,
                        'sentiment': message.metadata.sentiment_score,
                        'emotional_intensity': message.metadata.emotional_intensity
                    })
        
        # Sort by emotional intensity and recency
        breakthroughs.sort(key=lambda x: (x['emotional_intensity'], x['date']), reverse=True)
        return breakthroughs[:5]  # Return top 5 breakthroughs
    
    def _detect_evolution_patterns(self, search_results: List[SearchResult], 
                                 query_intent: QueryIntent) -> Dict[str, Any]:
        """Detect evolution patterns in conversations"""
        # Sort conversations by date
        sorted_results = sorted(search_results, key=lambda x: x.conversation.create_date)
        
        if len(sorted_results) < 2:
            return {'pattern': 'insufficient_data', 'stages': []}
        
        # Analyze temporal segments
        stages = []
        total_conversations = len(sorted_results)
        
        # Divide into 3-4 stages
        stage_size = max(1, total_conversations // 3)
        
        for i in range(0, total_conversations, stage_size):
            stage_results = sorted_results[i:i+stage_size]
            stage_sentiments = [r.conversation.metadata.sentiment_trend for r in stage_results]
            avg_sentiment = sum(stage_sentiments) / len(stage_sentiments) if stage_sentiments else 0.0
            
            # Extract key themes for this stage
            stage_themes = []
            for result in stage_results:
                stage_themes.extend(result.conversation.metadata.key_themes[:2])
            
            theme_counts = Counter(stage_themes)
            dominant_themes = [theme for theme, count in theme_counts.most_common(2)]
            
            stages.append({
                'stage_number': len(stages) + 1,
                'conversation_count': len(stage_results),
                'date_range': {
                    'start': stage_results[0].conversation.create_date,
                    'end': stage_results[-1].conversation.create_date
                },
                'avg_sentiment': avg_sentiment,
                'dominant_themes': dominant_themes,
                'description': self._generate_stage_description(dominant_themes, avg_sentiment, query_intent)
            })
        
        return {
            'pattern': 'evolutionary',
            'stages': stages,
            'total_stages': len(stages)
        }
    
    def _generate_stage_description(self, themes: List[str], sentiment: float, 
                                  query_intent: QueryIntent) -> str:
        """Generate description for an evolution stage"""
        if not themes:
            return "General exploration and reflection"
        
        theme_str = ' and '.join(themes)
        
        if sentiment > 0.2:
            mood = "positive growth"
        elif sentiment < -0.2:
            mood = "challenging period"
        else:
            mood = "balanced exploration"
        
        return f"Focus on {theme_str} with {mood}"
    
    def _identify_common_patterns(self, search_results: List[SearchResult]) -> List[str]:
        """Identify common patterns across conversations"""
        patterns = []
        
        # Analyze message patterns
        all_messages = []
        for result in search_results:
            all_messages.extend(result.conversation.messages)
        
        # Look for recurring themes in messages
        common_phrases = []
        for msg in all_messages:
            if msg.metadata.key_phrases:
                common_phrases.extend(msg.metadata.key_phrases)
        
        phrase_counts = Counter(common_phrases)
        top_phrases = [phrase for phrase, count in phrase_counts.most_common(3)]
        
        if top_phrases:
            patterns.append(f"Frequent expressions: {', '.join(top_phrases)}")
        
        # Analyze emotional patterns
        emotional_messages = [msg for msg in all_messages if msg.metadata.emotional_intensity > 0.5]
        if emotional_messages:
            patterns.append(f"High emotional engagement in {len(emotional_messages)} messages")
        
        # Analyze complexity patterns
        avg_complexity = sum(msg.metadata.complexity_score for msg in all_messages) / len(all_messages)
        if avg_complexity > 5.0:
            patterns.append("Consistent use of complex, reflective language")
        elif avg_complexity < 3.0:
            patterns.append("Preference for direct, simple communication")
        
        return patterns
    
    def _extract_actionable_insights(self, search_results: List[SearchResult]) -> List[str]:
        """Extract actionable insights from conversations"""
        insights = []
        
        # Look for action-oriented language
        action_keywords = ['should', 'need to', 'will', 'going to', 'plan to', 'try to', 'practice']
        
        for result in search_results:
            for msg in result.conversation.messages:
                if msg.role == 'user':  # Focus on user messages for actions
                    content_lower = msg.content.lower()
                    if any(keyword in content_lower for keyword in action_keywords):
                        # Extract the action-oriented sentence
                        sentences = msg.content.split('.')
                        for sentence in sentences:
                            if any(keyword in sentence.lower() for keyword in action_keywords):
                                insights.append(sentence.strip())
                                break
        
        # Remove duplicates and limit
        unique_insights = list(set(insights))
        return unique_insights[:5]  # Return top 5 actionable insights
    
    def _generate_structured_insight(self, query: str, query_intent: QueryIntent, 
                                   analysis_data: Dict[str, Any], 
                                   search_results: List[SearchResult]) -> GeneratedInsight:
        """Generate structured insight using templates"""
        
        # Select appropriate template
        template = self.insight_templates.get(query_intent.intent, self.insight_templates['general'])
        
        # Generate summary
        summary = self._generate_summary(query_intent, analysis_data, template)
        
        # Generate key learnings
        key_learnings = self._generate_key_learnings(analysis_data, template)
        
        # Generate evolution timeline
        evolution_timeline = self._generate_evolution_timeline(analysis_data, template)
        
        # Generate breakthrough moments
        breakthrough_moments = self._generate_breakthrough_moments(analysis_data, template)
        
        # Generate actionable next steps
        next_steps = self._generate_next_steps(analysis_data, template)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(search_results, analysis_data)
        
        # Prepare supporting conversations
        supporting_conversations = self._prepare_supporting_conversations(search_results)
        
        return GeneratedInsight(
            summary=summary,
            key_learnings=key_learnings,
            evolution_timeline=evolution_timeline,
            breakthrough_moments=breakthrough_moments,
            actionable_next_steps=next_steps,
            confidence_score=confidence_score,
            supporting_conversations=supporting_conversations,
            query_intent=query_intent
        )
    
    def _generate_summary(self, query_intent: QueryIntent, analysis_data: Dict[str, Any], 
                         template: InsightTemplate) -> str:
        """Generate insight summary"""
        date_range = analysis_data['date_range']
        time_period = self._calculate_time_period(date_range['earliest'], date_range['latest'])
        
        # Extract key insight from patterns
        key_insight = self._extract_key_insight(analysis_data)
        
        # Get topic from query intent
        topic = 'personal growth'
        if query_intent.entities:
            topic = ' and '.join(query_intent.entities)
        elif query_intent.intent != 'general':
            topic = query_intent.intent
        
        return template.summary_template.format(
            topic=topic,
            time_period=time_period,
            key_insight=key_insight
        )
    
    def _calculate_time_period(self, start_date: datetime, end_date: datetime) -> str:
        """Calculate human-readable time period"""
        days_diff = (end_date - start_date).days
        
        if days_diff < 30:
            return f"{days_diff} days"
        elif days_diff < 365:
            months = days_diff // 30
            return f"{months} months"
        else:
            years = days_diff // 365
            return f"{years} years"
    
    def _extract_key_insight(self, analysis_data: Dict[str, Any]) -> str:
        """Extract key insight from analysis data"""
        sentiment_trend = analysis_data['sentiment_trends']['trend']
        patterns = analysis_data['common_patterns']
        
        if sentiment_trend == 'positive':
            return "You've shown consistent positive growth and self-awareness."
        elif sentiment_trend == 'negative':
            return "You've been working through challenging periods with resilience."
        else:
            return "You've maintained a balanced approach to personal development."
    
    def _generate_key_learnings(self, analysis_data: Dict[str, Any], 
                               template: InsightTemplate) -> List[str]:
        """Generate key learnings from analysis"""
        learnings = []
        
        # Add theme-based learnings
        themes = analysis_data['key_themes']
        for theme in themes[:3]:
            learnings.append(f"You've developed deep insights about {theme}")
        
        # Add pattern-based learnings
        patterns = analysis_data['common_patterns']
        for pattern in patterns[:2]:
            learnings.append(pattern)
        
        # Add actionable insights
        actionable = analysis_data['actionable_insights']
        for insight in actionable[:2]:
            learnings.append(insight)
        
        return learnings[:5]  # Limit to 5 key learnings
    
    def _generate_evolution_timeline(self, analysis_data: Dict[str, Any], 
                                   template: InsightTemplate) -> Dict[str, str]:
        """Generate evolution timeline"""
        timeline = {}
        
        evolution = analysis_data['evolution_patterns']
        if evolution['pattern'] == 'evolutionary' and evolution['stages']:
            for stage in evolution['stages']:
                period_key = f"Stage {stage['stage_number']}"
                timeline[period_key] = stage['description']
        
        return timeline
    
    def _generate_breakthrough_moments(self, analysis_data: Dict[str, Any], 
                                     template: InsightTemplate) -> List[Dict[str, Any]]:
        """Generate breakthrough moments"""
        return analysis_data['breakthrough_moments'][:3]  # Return top 3
    
    def _generate_next_steps(self, analysis_data: Dict[str, Any], 
                           template: InsightTemplate) -> List[str]:
        """Generate actionable next steps"""
        steps = []
        
        # Add actionable insights as next steps
        actionable = analysis_data['actionable_insights']
        for insight in actionable[:3]:
            steps.append(insight)
        
        # Add general next steps based on patterns
        sentiment_trend = analysis_data['sentiment_trends']['trend']
        if sentiment_trend == 'positive':
            steps.append("Continue building on your current momentum and insights")
        elif sentiment_trend == 'negative':
            steps.append("Consider seeking additional support or resources for challenging areas")
        else:
            steps.append("Maintain your balanced approach while exploring new growth opportunities")
        
        return steps[:4]  # Limit to 4 next steps
    
    def _calculate_confidence_score(self, search_results: List[SearchResult], 
                                  analysis_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the insight"""
        base_score = 0.5
        
        # Factor 1: Number of relevant conversations
        conv_count = len(search_results)
        if conv_count >= 10:
            base_score += 0.2
        elif conv_count >= 5:
            base_score += 0.1
        
        # Factor 2: Quality of search results
        avg_similarity = sum(r.similarity_score for r in search_results) / len(search_results)
        base_score += avg_similarity * 0.2
        
        # Factor 3: Presence of breakthrough moments
        breakthrough_count = len(analysis_data['breakthrough_moments'])
        if breakthrough_count > 0:
            base_score += min(breakthrough_count * 0.05, 0.1)
        
        # Factor 4: Data consistency
        if analysis_data['evolution_patterns']['pattern'] == 'evolutionary':
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _prepare_supporting_conversations(self, search_results: List[SearchResult]) -> List[Dict[str, Any]]:
        """Prepare supporting conversation data"""
        supporting = []
        
        for result in search_results[:5]:  # Top 5 supporting conversations
            supporting.append({
                'id': result.conversation.id,
                'title': result.conversation.title,
                'date': result.conversation.create_date.isoformat(),
                'similarity_score': result.similarity_score,
                'key_themes': result.conversation.metadata.key_themes,
                'sentiment_trend': result.conversation.metadata.sentiment_trend
            })
        
        return supporting
    
    def _generate_empty_insight(self, query_intent: QueryIntent) -> GeneratedInsight:
        """Generate insight when no relevant conversations found"""
        return GeneratedInsight(
            summary="I couldn't find any conversations that directly address your question. This might be a new area for exploration.",
            key_learnings=["Consider starting conversations about this topic to build insights"],
            evolution_timeline={},
            breakthrough_moments=[],
            actionable_next_steps=[
                "Begin journaling or discussing this topic with ChatGPT",
                "Reflect on your current thoughts and feelings about this area",
                "Set specific goals for exploring this topic further"
            ],
            confidence_score=0.1,
            supporting_conversations=[],
            query_intent=query_intent
        )
    
    def _generate_error_insight(self, query: str) -> GeneratedInsight:
        """Generate insight when an error occurs"""
        return GeneratedInsight(
            summary="I encountered an error while processing your query. Please try rephrasing your question.",
            key_learnings=[],
            evolution_timeline={},
            breakthrough_moments=[],
            actionable_next_steps=[
                "Try rephrasing your question with different words",
                "Break down complex questions into simpler parts",
                "Check if your conversation data is properly loaded"
            ],
            confidence_score=0.0,
            supporting_conversations=[],
            query_intent=QueryIntent(intent='general', entities=[], time_context='all_time', 
                                   focus_areas=[], query_type='general')
        )
    
    def format_insight_response(self, insight: GeneratedInsight) -> str:
        """Format insight into a readable response"""
        response_parts = []
        
        # Header
        topic = ' and '.join(insight.query_intent.entities) if insight.query_intent.entities else insight.query_intent.intent
        response_parts.append(f"💡 Holistic Insight: Your {topic.title()} Journey")
        response_parts.append("")
        
        # Summary
        response_parts.append(f"📊 Summary: {insight.summary}")
        response_parts.append("")
        
        # Key Learnings
        if insight.key_learnings:
            response_parts.append("🔍 Key Learnings:")
            for learning in insight.key_learnings:
                response_parts.append(f"• {learning}")
            response_parts.append("")
        
        # Evolution Timeline
        if insight.evolution_timeline:
            response_parts.append("📈 Evolution Timeline:")
            for period, description in insight.evolution_timeline.items():
                response_parts.append(f"• {period}: {description}")
            response_parts.append("")
        
        # Breakthrough Moments
        if insight.breakthrough_moments:
            response_parts.append("⚡ Breakthrough Moments:")
            for moment in insight.breakthrough_moments:
                response_parts.append(f"• Conversation #{moment['conversation_id'][:8]}: \"{moment['content']}\"")
            response_parts.append("")
        
        # Next Steps
        if insight.actionable_next_steps:
            response_parts.append("🎯 Next Steps:")
            for step in insight.actionable_next_steps:
                response_parts.append(f"• {step}")
            response_parts.append("")
        
        # Confidence and metadata
        confidence_percentage = int(insight.confidence_score * 100)
        response_parts.append(f"Confidence: {confidence_percentage}%")
        
        return "\n".join(response_parts)


if __name__ == "__main__":
    # Test the AI assistant
    assistant = AIAssistant()
    
    print("AI Assistant initialized")
    print("Ready to process queries about your personal growth journey!")
    
    # Example usage (would need actual conversation data)
    # assistant.load_conversations('data/conversations.json')
    # insight = assistant.process_query("What have I learned about relationships and boundaries?")
    # print(assistant.format_insight_response(insight))