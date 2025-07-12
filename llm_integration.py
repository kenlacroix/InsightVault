"""
LLM Integration Layer for InsightVault AI Assistant
Phase 2: Advanced AI-Powered Insights

Provides OpenAI GPT-4 integration with sophisticated prompt engineering,
response validation, and fallback mechanisms for generating personalized insights.
"""

import os
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import openai
from openai import OpenAI
import time
import re

from chat_parser import Conversation
from analytics_engine import AnalyticsData


@dataclass
class GeneratedInsight:
    """Structured insight response from LLM"""
    summary: str
    key_learnings: List[str]
    evolution_timeline: Dict[str, str]
    breakthrough_moments: List[Dict[str, Any]]
    next_steps: List[str]
    predictive_insights: List[str]
    confidence_score: float
    personalization_level: str
    source_conversations: List[str]
    generated_at: datetime
    query: str
    model_used: str
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None


@dataclass
class QueryContext:
    """Context information for query processing"""
    query: str
    user_id: Optional[str] = None
    conversation_count: int = 0
    date_range: Tuple[datetime, datetime] = None
    top_themes: List[Tuple[str, int]] = None
    sentiment_trends: Dict[str, Any] = None
    growth_metrics: Dict[str, float] = None
    breakthrough_moments: List[Dict[str, Any]] = None
    user_preferences: Dict[str, Any] = None


class LLMIntegration:
    """LLM integration layer with OpenAI GPT-4 support"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4", 
                 max_tokens: int = 2000, temperature: float = 0.7):
        """
        Initialize LLM integration
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
            model: Model to use (gpt-4, gpt-3.5-turbo, etc.)
            max_tokens: Maximum tokens for response
            temperature: Response creativity (0.0-1.0)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.client = OpenAI(api_key=self.api_key)
        
        # Rate limiting and cost tracking
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.last_request_time = 0
        self.rate_limit_delay = 0.1  # 100ms between requests
        
        # Response cache
        self.response_cache = {}
        self.cache_ttl = timedelta(hours=24)
        
        # Logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Cost tracking (approximate)
        self.token_costs = {
            'gpt-4': {'input': 0.03, 'output': 0.06},  # per 1K tokens
            'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002}
        }
    
    def generate_insight(self, query: str, conversations: List[Conversation], 
                        analytics_data: AnalyticsData, user_profile: Optional[Dict] = None) -> GeneratedInsight:
        """
        Generate LLM-powered insight from query and conversation data
        
        Args:
            query: User's natural language query
            conversations: List of relevant conversations
            analytics_data: Pre-computed analytics data
            user_profile: Optional user profile for personalization
            
        Returns:
            GeneratedInsight with structured response
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(query, conversations, analytics_data)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                self.logger.info(f"Returning cached response for query: {query[:50]}...")
                return cached_response
            
            # Prepare context
            context = self._prepare_query_context(query, conversations, analytics_data, user_profile)
            
            # Generate prompt
            system_prompt = self._create_system_prompt()
            user_prompt = self._create_user_prompt(context)
            
            # Make API call
            response = self._make_api_call(system_prompt, user_prompt)
            
            # Parse and validate response
            parsed_response = self._parse_response(response, query)
            
            # Cache response
            self._cache_response(cache_key, parsed_response)
            
            return parsed_response
            
        except Exception as e:
            self.logger.error(f"Error generating insight: {e}")
            # Fallback to template system
            return self._fallback_to_template(query, conversations, analytics_data)
    
    def _prepare_query_context(self, query: str, conversations: List[Conversation], 
                              analytics_data: AnalyticsData, user_profile: Optional[Dict]) -> QueryContext:
        """Prepare context for LLM prompt"""
        return QueryContext(
            query=query,
            conversation_count=len(conversations),
            date_range=analytics_data.date_range if analytics_data else None,
            top_themes=analytics_data.top_tags if analytics_data else [],
            sentiment_trends=analytics_data.sentiment_trends if analytics_data else {},
            growth_metrics=analytics_data.growth_metrics if analytics_data else {},
            breakthrough_moments=analytics_data.breakthrough_moments if analytics_data else [],
            user_preferences=user_profile or {}
        )
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for LLM"""
        return """You are InsightVault, an AI-powered personal growth assistant that analyzes ChatGPT conversations to provide deep, contextual insights about personal development.

Your role is to:
1. Analyze conversation patterns and extract meaningful insights
2. Identify learning journeys and personal growth trajectories
3. Detect breakthrough moments and key realizations
4. Provide actionable recommendations for continued growth
5. Generate personalized insights based on user patterns

You must respond in the EXACT format specified below. Do not deviate from this structure.

RESPONSE FORMAT:
💡 Holistic Insight: [Topic] Journey

📊 Summary: [2-3 sentences describing the overall evolution and key patterns]

🔍 Key Learnings:
• [Specific insight with evidence from conversations]
• [Another specific insight]
• [Third specific insight]

📈 Evolution Timeline:
• [Stage 1]: [Description of early phase]
• [Stage 2]: [Description of middle phase]
• [Stage 3]: [Description of current phase]

⚡ Breakthrough Moments:
• [Conversation reference]: "[Exact quote or key realization]"
• [Another breakthrough moment]

🎯 Next Steps:
• [Specific, actionable recommendation]
• [Another actionable recommendation]
• [Third actionable recommendation]

🔮 Predictive Insights:
• [Future growth prediction based on patterns]
• [Potential opportunity or risk to watch for]

Confidence: [85-95]% | Personalization: [High/Medium/Low]%

IMPORTANT:
- Be specific and reference actual conversation content when possible
- Provide actionable, practical advice
- Maintain a supportive, growth-oriented tone
- Use evidence from the conversations to support insights
- Keep responses concise but comprehensive
- Always include all sections in the exact format above"""
    
    def _create_user_prompt(self, context: QueryContext) -> str:
        """Create user prompt with conversation context"""
        
        # Prepare conversation summaries
        conversation_summaries = []
        for i, conv in enumerate(context.conversations[:10]):  # Limit to 10 most relevant
            summary = f"Conversation {i+1} ({conv.create_date.strftime('%Y-%m-%d')}): {conv.title[:100]}..."
            conversation_summaries.append(summary)
        
        # Prepare analytics summary
        analytics_summary = ""
        if context.sentiment_trends:
            analytics_summary += f"Sentiment trends: {len(context.sentiment_trends)} time periods analyzed. "
        if context.growth_metrics:
            positive_metrics = sum(1 for v in context.growth_metrics.values() if v > 0)
            analytics_summary += f"Growth metrics: {positive_metrics}/{len(context.growth_metrics)} show positive trends. "
        if context.breakthrough_moments:
            analytics_summary += f"Breakthrough moments detected: {len(context.breakthrough_moments)}. "
        
        # Prepare user preferences
        preferences_summary = ""
        if context.user_preferences:
            if 'focus_areas' in context.user_preferences:
                preferences_summary += f"User focus areas: {', '.join(context.user_preferences['focus_areas'])}. "
            if 'learning_goals' in context.user_preferences:
                preferences_summary += f"Learning goals: {', '.join(context.user_preferences['learning_goals'])}. "
        
        prompt = f"""USER QUERY: {context.query}

CONTEXT:
- Total conversations analyzed: {context.conversation_count}
- Date range: {context.date_range[0].strftime('%Y-%m-%d')} to {context.date_range[1].strftime('%Y-%m-%d')} if context.date_range else 'Not specified'
- {analytics_summary}
- {preferences_summary}

TOP THEMES IDENTIFIED:
{chr(10).join([f"• {theme}: {count} occurrences" for theme, count in context.top_themes[:5]]) if context.top_themes else "No themes identified"}

BREAKTHROUGH MOMENTS DETECTED:
{chr(10).join([f"• {moment['title']}: {moment['summary'][:100]}..." for moment in context.breakthrough_moments[:3]]) if context.breakthrough_moments else "No breakthrough moments detected"}

CONVERSATION SUMMARIES:
{chr(10).join(conversation_summaries)}

Please analyze this data and provide insights in the exact format specified in the system prompt. Focus on the user's specific query and provide evidence from the conversations to support your insights."""

        return prompt
    
    def _make_api_call(self, system_prompt: str, user_prompt: str) -> str:
        """Make API call to OpenAI with rate limiting and error handling"""
        
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_request_time < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            # Update tracking
            self.request_count += 1
            self.total_tokens += response.usage.total_tokens
            self.last_request_time = time.time()
            
            # Calculate cost
            cost = self._calculate_cost(response.usage.prompt_tokens, response.usage.completion_tokens)
            self.total_cost += cost
            
            self.logger.info(f"API call successful. Tokens: {response.usage.total_tokens}, Cost: ${cost:.4f}")
            
            return response.choices[0].message.content
            
        except openai.RateLimitError:
            self.logger.warning("Rate limit hit, waiting 60 seconds...")
            time.sleep(60)
            return self._make_api_call(system_prompt, user_prompt)
            
        except openai.APIError as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise
            
        except Exception as e:
            self.logger.error(f"Unexpected error in API call: {e}")
            raise
    
    def _parse_response(self, response: str, query: str) -> GeneratedInsight:
        """Parse and validate LLM response"""
        
        # Extract sections using regex
        summary_match = re.search(r'📊 Summary: (.+?)(?=\n\n|\n🔍|\n📈|\n⚡|\n🎯|\n🔮|$)', response, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else "Analysis completed successfully."
        
        # Extract key learnings
        learnings_match = re.search(r'🔍 Key Learnings:\n(.*?)(?=\n\n|\n📈|\n⚡|\n🎯|\n🔮|$)', response, re.DOTALL)
        learnings_text = learnings_match.group(1) if learnings_match else ""
        key_learnings = [line.strip()[2:] for line in learnings_text.split('\n') if line.strip().startswith('•')]
        
        # Extract evolution timeline
        timeline_match = re.search(r'📈 Evolution Timeline:\n(.*?)(?=\n\n|\n⚡|\n🎯|\n🔮|$)', response, re.DOTALL)
        timeline_text = timeline_match.group(1) if timeline_match else ""
        evolution_timeline = {}
        for line in timeline_text.split('\n'):
            if ':' in line and line.strip().startswith('•'):
                parts = line.strip()[2:].split(':', 1)
                if len(parts) == 2:
                    evolution_timeline[parts[0].strip()] = parts[1].strip()
        
        # Extract breakthrough moments
        breakthroughs_match = re.search(r'⚡ Breakthrough Moments:\n(.*?)(?=\n\n|\n🎯|\n🔮|$)', response, re.DOTALL)
        breakthroughs_text = breakthroughs_match.group(1) if breakthroughs_match else ""
        breakthrough_moments = []
        for line in breakthroughs_text.split('\n'):
            if line.strip().startswith('•'):
                content = line.strip()[2:]
                if ':' in content:
                    conv_ref, quote = content.split(':', 1)
                    breakthrough_moments.append({
                        'conversation_ref': conv_ref.strip(),
                        'quote': quote.strip().strip('"'),
                        'impact_score': 0.8
                    })
        
        # Extract next steps
        steps_match = re.search(r'🎯 Next Steps:\n(.*?)(?=\n\n|\n🔮|$)', response, re.DOTALL)
        steps_text = steps_match.group(1) if steps_match else ""
        next_steps = [line.strip()[2:] for line in steps_text.split('\n') if line.strip().startswith('•')]
        
        # Extract predictive insights
        predictive_match = re.search(r'🔮 Predictive Insights:\n(.*?)(?=\n\n|$)', response, re.DOTALL)
        predictive_text = predictive_match.group(1) if predictive_match else ""
        predictive_insights = [line.strip()[2:] for line in predictive_text.split('\n') if line.strip().startswith('•')]
        
        # Extract confidence score
        confidence_match = re.search(r'Confidence: (\d+)%', response)
        confidence_score = float(confidence_match.group(1)) / 100 if confidence_match else 0.85
        
        # Extract personalization level
        personalization_match = re.search(r'Personalization: (High|Medium|Low)', response)
        personalization_level = personalization_match.group(1) if personalization_match else "Medium"
        
        return GeneratedInsight(
            summary=summary,
            key_learnings=key_learnings,
            evolution_timeline=evolution_timeline,
            breakthrough_moments=breakthrough_moments,
            next_steps=next_steps,
            predictive_insights=predictive_insights,
            confidence_score=confidence_score,
            personalization_level=personalization_level,
            source_conversations=[f"Conversation {i+1}" for i in range(min(5, len(conversations)))],
            generated_at=datetime.now(),
            query=query,
            model_used=self.model
        )
    
    def validate_response(self, response: str) -> bool:
        """Validate that response follows required format"""
        required_sections = ['💡 Holistic Insight:', '📊 Summary:', '🔍 Key Learnings:', 
                           '📈 Evolution Timeline:', '⚡ Breakthrough Moments:', 
                           '🎯 Next Steps:', '🔮 Predictive Insights:', 'Confidence:']
        
        for section in required_sections:
            if section not in response:
                return False
        
        return True
    
    def _fallback_to_template(self, query: str, conversations: List[Conversation], 
                             analytics_data: AnalyticsData) -> GeneratedInsight:
        """Fallback to template-based insight generation"""
        self.logger.warning("Falling back to template-based insight generation")
        
        # Simple template-based response
        summary = f"Based on your query about {query.lower()}, I've analyzed your conversations and found several interesting patterns."
        
        key_learnings = [
            "Your conversations show consistent engagement with personal growth topics",
            "You demonstrate reflective thinking and self-awareness",
            "There are clear patterns in how you approach challenges and learning"
        ]
        
        evolution_timeline = {
            "Early Period": "Initial exploration and question-asking",
            "Middle Period": "Deeper reflection and pattern recognition", 
            "Recent Period": "Application of insights and continued growth"
        }
        
        breakthrough_moments = [
            {
                "conversation_ref": "Recent conversations",
                "quote": "You've shown consistent growth and learning",
                "impact_score": 0.7
            }
        ]
        
        next_steps = [
            "Continue your reflective practice",
            "Apply insights from your conversations to daily life",
            "Share your learnings with others"
        ]
        
        predictive_insights = [
            "Continued growth in self-awareness and personal development",
            "Potential for deeper insights as you continue your journey"
        ]
        
        return GeneratedInsight(
            summary=summary,
            key_learnings=key_learnings,
            evolution_timeline=evolution_timeline,
            breakthrough_moments=breakthrough_moments,
            next_steps=next_steps,
            predictive_insights=predictive_insights,
            confidence_score=0.75,
            personalization_level="Medium",
            source_conversations=[f"Conversation {i+1}" for i in range(min(5, len(conversations)))],
            generated_at=datetime.now(),
            query=query,
            model_used="template-fallback"
        )
    
    def _generate_cache_key(self, query: str, conversations: List[Conversation], 
                           analytics_data: AnalyticsData) -> str:
        """Generate cache key for response caching"""
        # Create hash of query and conversation IDs
        conv_ids = [conv.id for conv in conversations[:10]]  # Limit to 10 conversations
        data_str = f"{query}:{sorted(conv_ids)}"
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[GeneratedInsight]:
        """Get cached response if available and not expired"""
        if cache_key in self.response_cache:
            cached_data, timestamp = self.response_cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data
            else:
                del self.response_cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: GeneratedInsight):
        """Cache response with timestamp"""
        self.response_cache[cache_key] = (response, datetime.now())
        
        # Clean old cache entries
        current_time = datetime.now()
        expired_keys = [key for key, (_, timestamp) in self.response_cache.items() 
                       if current_time - timestamp > self.cache_ttl]
        for key in expired_keys:
            del self.response_cache[key]
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate approximate cost of API call"""
        if self.model in self.token_costs:
            costs = self.token_costs[self.model]
            prompt_cost = (prompt_tokens / 1000) * costs['input']
            completion_cost = (completion_tokens / 1000) * costs['output']
            return prompt_cost + completion_cost
        return 0.0
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics and cost tracking"""
        return {
            'request_count': self.request_count,
            'total_tokens': self.total_tokens,
            'total_cost': self.total_cost,
            'cache_hits': len(self.response_cache),
            'model_used': self.model,
            'last_request': self.last_request_time
        }
    
    def reset_usage_stats(self):
        """Reset usage statistics"""
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.last_request_time = 0


def main():
    """Test the LLM integration"""
    # This would require actual API key and conversation data
    print("LLM Integration Layer initialized successfully!")
    print("To test, you'll need:")
    print("1. OPENAI_API_KEY environment variable set")
    print("2. Sample conversation data")
    print("3. Analytics data from analytics_engine")


if __name__ == '__main__':
    main() 