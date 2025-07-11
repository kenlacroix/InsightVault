"""
Insight Engine for InsightVault
Handles reflective questions and generates integrated insights using GPT-4
"""

import json
import os
import pickle
from datetime import datetime
from typing import List, Dict, Any, Optional
from openai import OpenAI
from chat_parser import Conversation


class InsightEngine:
    """Generates insights and reflections from conversations using GPT-4"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config = self._load_config(config_path)
        self.client = OpenAI(api_key=self.config['openai_api_key'])
        self.cache_dir = 'data/cache'
        self._ensure_cache_dir()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Config file {config_path} not found. "
                f"Please copy config.json.example to config.json and add your OpenAI API key."
            )
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def find_relevant_conversations(self, query: str, conversations: List[Conversation], 
                                  max_conversations: int = 10) -> List[Conversation]:
        """
        Find conversations most relevant to the reflective question
        Uses keyword matching and tag filtering
        """
        query_lower = query.lower()
        scored_conversations = []
        
        # Keywords that often indicate personal growth themes
        growth_keywords = [
            'spiritual', 'healing', 'trauma', 'relationship', 'emotion', 'growth',
            'therapy', 'self', 'identity', 'anxiety', 'depression', 'anger',
            'love', 'fear', 'healing', 'mindfulness', 'meditation', 'breakthrough',
            'pattern', 'habit', 'change', 'progress', 'journey', 'insight'
        ]
        
        for conv in conversations:
            score = 0
            
            # Score based on query keywords in content
            conv_text = conv.get_full_text().lower()
            query_words = query_lower.split()
            
            for word in query_words:
                if len(word) > 3:  # Ignore short words
                    score += conv_text.count(word) * 2
            
            # Score based on tags matching query
            for tag in conv.tags:
                for word in query_words:
                    if len(word) > 2 and word in tag.lower():  # Require minimum 3 chars for tag matching
                        score += 5
            
            # Score based on growth-related keywords
            for keyword in growth_keywords:
                if keyword in query_lower and keyword in conv_text:
                    score += 1
            
            # Score based on title/auto_title relevance
            title_text = (conv.title + ' ' + conv.auto_title).lower()
            for word in query_words:
                if len(word) > 2 and word in title_text:  # Require minimum 3 chars for title matching
                    score += 3
            
            if score > 0:
                scored_conversations.append((conv, score))
        
        # Sort by score and return top conversations
        scored_conversations.sort(key=lambda x: x[1], reverse=True)
        return [conv for conv, score in scored_conversations[:max_conversations]]
    
    def generate_insight(self, question: str, conversations: List[Conversation], 
                        use_cache: bool = True) -> Dict[str, Any]:
        """
        Generate an integrated reflection based on the question and relevant conversations
        """
        # Create cache key based on question and conversation IDs
        conv_ids = sorted([conv.id for conv in conversations])
        cache_key = f"insight_{hash(question + ''.join(conv_ids))}"
        
        # Check cache
        if use_cache:
            cached_result = self._load_insight_from_cache(cache_key)
            if cached_result:
                return cached_result
        
        try:
            # Find most relevant conversations
            relevant_convs = self.find_relevant_conversations(question, conversations)
            
            if not relevant_convs:
                return {
                    'question': question,
                    'insight': 'No relevant conversations found for this question.',
                    'quotes': [],
                    'themes': [],
                    'timeline_insights': [],
                    'conversations_analyzed': 0,
                    'generated_at': datetime.now().isoformat()
                }
            
            # Prepare conversation data for GPT
            conv_data = self._prepare_conversation_data(relevant_convs)
            
            # Create the insight prompt
            prompt = self._create_insight_prompt(question, conv_data)
            
            # Call GPT-4
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": self._get_insight_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.get('max_tokens', 2000),
                temperature=self.config.get('temperature', 0.7)
            )
            
            # Parse the response
            result = self._parse_insight_response(response.choices[0].message.content)
            
            # Add metadata
            result.update({
                'question': question,
                'conversations_analyzed': len(relevant_convs),
                'conversation_titles': [conv.auto_title or conv.title for conv in relevant_convs],
                'generated_at': datetime.now().isoformat()
            })
            
            # Cache the result
            if use_cache:
                self._save_insight_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            print(f"Error generating insight: {e}")
            return {
                'question': question,
                'insight': f'Error generating insight: {str(e)}',
                'quotes': [],
                'themes': [],
                'timeline_insights': [],
                'conversations_analyzed': 0,
                'generated_at': datetime.now().isoformat()
            }
    
    def _get_insight_system_prompt(self) -> str:
        """Get the system prompt for insight generation"""
        return """You are a compassionate AI therapist and personal growth coach. You help people reflect on their journey by analyzing their past conversations and generating deep insights about their personal development, healing, and spiritual growth.

Your role is to:
1. Identify patterns of growth, recurring themes, and emotional evolution
2. Extract meaningful quotes that show important moments or realizations
3. Provide timeline insights showing how perspectives have changed
4. Offer gentle, supportive observations about progress and areas for continued growth
5. Be empathetic, non-judgmental, and encouraging

Always maintain a warm, supportive tone while being insightful and specific."""
    
    def _prepare_conversation_data(self, conversations: List[Conversation]) -> str:
        """Prepare conversation data for the GPT prompt"""
        conv_texts = []
        
        for i, conv in enumerate(conversations):
            date_str = conv.create_date.strftime('%Y-%m-%d')
            conv_texts.append(f"""
CONVERSATION {i+1} - {date_str}
Title: {conv.auto_title or conv.title}
Tags: {', '.join(conv.tags)}
Summary: {conv.summary}

Content:
{conv.get_full_text()[:3000]}{'...' if len(conv.get_full_text()) > 3000 else ''}
""")
        
        return '\n\n' + '='*50 + '\n\n'.join(conv_texts)
    
    def _create_insight_prompt(self, question: str, conversation_data: str) -> str:
        """Create the prompt for insight generation"""
        return f"""
**REFLECTIVE QUESTION**: {question}

Please analyze the following conversations and provide a comprehensive reflection that addresses this question. Focus on patterns, growth, evolution of thinking, and meaningful insights.

{conversation_data}

**Please structure your response as follows:**

INSIGHT:
[Provide a thoughtful, multi-paragraph reflection that directly addresses the question. Include observations about growth patterns, recurring themes, and evolution over time. Be specific and reference the conversations.]

QUOTES:
[List 3-5 meaningful quotes from the conversations that support your insights. Format as "Quote text" - [Date]]

THEMES:
[List 4-6 key themes or patterns you identified, such as "Self-compassion development", "Relationship with anxiety", etc.]

TIMELINE_INSIGHTS:
[Describe 2-4 observations about how the person's perspective, understanding, or approach has evolved over time]

Remember to be compassionate, specific, and insightful. Focus on growth, healing, and positive development while acknowledging challenges and struggles as part of the journey.
"""
    
    def _parse_insight_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the GPT response into structured data"""
        result = {
            'insight': '',
            'quotes': [],
            'themes': [],
            'timeline_insights': []
        }
        
        # Split on section headers and process each section
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('INSIGHT:'):
                current_section = 'insight'
                content = line.replace('INSIGHT:', '').strip()
                if content:
                    result['insight'] = content
            elif line.startswith('QUOTES:'):
                current_section = 'quotes'
            elif line.startswith('THEMES:'):
                current_section = 'themes'  
            elif line.startswith('TIMELINE_INSIGHTS:'):
                current_section = 'timeline_insights'
            elif current_section and line:
                if current_section == 'insight':
                    if result['insight']:
                        result['insight'] += '\n' + line
                    else:
                        result['insight'] = line
                elif current_section == 'quotes':
                    # Parse quotes - handle different formats
                    if line.startswith('-') or line.startswith('•') or '"' in line:
                        clean_quote = line.lstrip('- •').strip()
                        if clean_quote:
                            result['quotes'].append(clean_quote)
                elif current_section == 'themes':
                    # Parse themes
                    if line.startswith('-') or line.startswith('•'):
                        clean_theme = line.lstrip('- •').strip()
                        if clean_theme:
                            result['themes'].append(clean_theme)
                    elif line and not line.startswith(('INSIGHT:', 'QUOTES:', 'TIMELINE_INSIGHTS:')):
                        # Handle themes without bullet points
                        result['themes'].append(line)
                elif current_section == 'timeline_insights':
                    # Parse timeline insights
                    if line.startswith('-') or line.startswith('•'):
                        clean_insight = line.lstrip('- •').strip()
                        if clean_insight:
                            result['timeline_insights'].append(clean_insight)
                    elif line and not line.startswith(('INSIGHT:', 'QUOTES:', 'THEMES:')):
                        # Handle timeline insights without bullet points
                        result['timeline_insights'].append(line)
        
        return result
    
    def _load_insight_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load cached insight if it exists"""
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                pass
        return None
    
    def _save_insight_to_cache(self, cache_key: str, data: Dict[str, Any]):
        """Save insight to cache"""
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Error saving insight cache: {e}")
    
    def export_insight(self, insight_data: Dict[str, Any], 
                      output_path: Optional[str] = None) -> str:
        """Export insight to a Markdown file"""
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"output/insight_{timestamp}.md"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# InsightVault - Personal Reflection\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Question:** {insight_data['question']}\n\n")
                f.write(f"**Conversations Analyzed:** {insight_data['conversations_analyzed']}\n\n")
                
                if insight_data.get('conversation_titles'):
                    f.write("**Source Conversations:**\n")
                    for title in insight_data['conversation_titles']:
                        f.write(f"- {title}\n")
                    f.write("\n")
                
                f.write("---\n\n")
                
                f.write("## Reflection\n\n")
                f.write(f"{insight_data['insight']}\n\n")
                
                if insight_data['themes']:
                    f.write("## Key Themes\n\n")
                    for theme in insight_data['themes']:
                        f.write(f"- {theme}\n")
                    f.write("\n")
                
                if insight_data['quotes']:
                    f.write("## Meaningful Quotes\n\n")
                    for quote in insight_data['quotes']:
                        f.write(f"> {quote}\n\n")
                
                if insight_data['timeline_insights']:
                    f.write("## Timeline Insights\n\n")
                    for insight in insight_data['timeline_insights']:
                        f.write(f"- {insight}\n")
                    f.write("\n")
            
            return output_path
            
        except Exception as e:
            print(f"Error exporting insight: {e}")
            return ""


# Predefined reflective questions for common themes
SAMPLE_QUESTIONS = [
    "How have I grown spiritually over time?",
    "What emotional patterns have I been working through?",
    "How has my relationship with anxiety/fear evolved?",
    "What breakthroughs have I had regarding childhood trauma?",
    "How has my sense of identity and self-worth changed?",
    "What have I learned about relationships and boundaries?",
    "How has my approach to healing and therapy evolved?",
    "What patterns do I see in my personal growth journey?",
    "How have my perspectives on love and self-compassion developed?",
    "What insights have I gained about my life purpose and direction?"
]


if __name__ == "__main__":
    # Test the insight engine
    from chat_parser import ChatParser
    
    parser = ChatParser()
    if parser.load_conversations('data/sample_conversations.json'):
        engine = InsightEngine()
        
        question = "How have I been working through anxiety and spiritual growth?"
        result = engine.generate_insight(question, parser.conversations)
        
        print(f"Question: {result['question']}")
        print(f"Conversations analyzed: {result['conversations_analyzed']}")
        print(f"\nInsight:\n{result['insight']}")
        
        if result['themes']:
            print(f"\nThemes: {', '.join(result['themes'])}")
        
        # Export the insight
        output_path = engine.export_insight(result)
        print(f"\nInsight exported to: {output_path}")