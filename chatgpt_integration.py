"""
ChatGPT Integration for InsightVault
Provides AI-powered conversation analysis and intelligent responses
"""

import json
import os
import openai
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from chat_parser import Conversation


@dataclass
class ChatGPTConfig:
    """Configuration for ChatGPT integration"""
    api_key: str
    model: str = "gpt-4"
    max_tokens: int = 1500
    temperature: float = 0.7
    system_prompt: str = ""


class ChatGPTIntegration:
    """Main ChatGPT integration class"""
    
    def __init__(self, config: ChatGPTConfig):
        self.config = config
        self.client = openai.OpenAI(api_key=config.api_key)
        
        # Default system prompts
        self.default_system_prompt = """You are an AI personal growth coach and conversation analyst. You help users understand their personal development journey by analyzing their ChatGPT conversation history.

Your role is to:
1. Provide insightful analysis based on conversation patterns
2. Identify growth trends and emotional evolution
3. Offer personalized recommendations and observations
4. Answer specific questions about their development journey
5. Help them understand their progress and areas for growth

Be compassionate, insightful, and specific. Reference the conversation data provided and offer meaningful observations."""
    
    def analyze_conversations(self, conversations: List[Conversation], analysis_type: str = "general") -> Dict[str, Any]:
        """
        Analyze conversations and provide insights
        
        Args:
            conversations: List of conversations to analyze
            analysis_type: Type of analysis ("general", "emotional", "growth", "programming")
        
        Returns:
            Dictionary containing analysis results
        """
        if not conversations:
            return {"error": "No conversations provided"}
        
        try:
            # Prepare conversation context
            context = self._prepare_conversation_context(conversations, analysis_type)
            
            # Create analysis prompt based on type
            if analysis_type == "emotional":
                prompt = self._create_emotional_analysis_prompt(context)
            elif analysis_type == "growth":
                prompt = self._create_growth_analysis_prompt(context)
            elif analysis_type == "programming":
                prompt = self._create_programming_analysis_prompt(context)
            else:
                prompt = self._create_general_analysis_prompt(context)
            
            # Generate analysis
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self.config.system_prompt or self.default_system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            # Parse and structure the response
            analysis = self._parse_analysis_response(response.choices[0].message.content, analysis_type)
            
            return {
                "analysis_type": analysis_type,
                "conversations_analyzed": len(conversations),
                "analysis": analysis,
                "generated_at": datetime.now().isoformat(),
                "model_used": self.config.model
            }
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def generate_ai_response(self, user_message: str, conversations: List[Conversation], 
                           focus_conversation: Optional[Conversation] = None) -> str:
        """
        Generate an AI response based on user message and conversation context
        
        Args:
            user_message: The user's question or message
            conversations: List of conversations for context
            focus_conversation: Optional specific conversation to focus on
        
        Returns:
            AI-generated response
        """
        if not conversations:
            return "I don't have any conversation data to work with. Please load some conversations first."
        
        try:
            # Prepare rich context
            context = self._prepare_conversation_context(conversations, "general", focus_conversation)
            
            # Create the prompt
            prompt = f"""
User Question: {user_message}

Please analyze the following conversation data and provide a thoughtful, personalized response:

{context}

Your response should be:
- Insightful and specific to the user's question
- Based on patterns and trends in their conversations
- Helpful and actionable
- Conversational and engaging
"""
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self.config.system_prompt or self.default_system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I'm sorry, I encountered an error while processing your request: {str(e)}"
    
    def detect_programming_patterns(self, conversations: List[Conversation]) -> Dict[str, Any]:
        """
        Analyze conversations for programming-related patterns
        
        Returns:
            Dictionary with programming analysis
        """
        programming_conversations = []
        languages_detected = set()
        technologies_detected = set()
        concepts_detected = set()
        
        # Programming language keywords
        language_keywords = {
            'python': ['python', 'py', 'django', 'flask', 'pandas', 'numpy', 'matplotlib', 'scikit-learn'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue', 'angular', 'typescript', 'express'],
            'java': ['java', 'spring', 'android', 'kotlin', 'maven', 'gradle'],
            'c++': ['c++', 'cpp', 'c plus plus', 'stl', 'boost'],
            'c#': ['c#', 'csharp', '.net', 'asp.net', 'entity framework'],
            'go': ['go', 'golang', 'goroutine', 'channel'],
            'rust': ['rust', 'cargo', 'ownership', 'borrowing'],
            'php': ['php', 'laravel', 'wordpress', 'composer'],
            'ruby': ['ruby', 'rails', 'gem', 'bundler'],
            'swift': ['swift', 'ios', 'xcode', 'cocoa'],
            'sql': ['sql', 'mysql', 'postgresql', 'sqlite', 'mongodb', 'redis']
        }
        
        # Technology categories
        tech_categories = {
            'web_development': ['html', 'css', 'bootstrap', 'tailwind', 'responsive', 'frontend', 'backend', 'api'],
            'databases': ['database', 'sql', 'nosql', 'redis', 'elasticsearch', 'firebase', 'mongodb'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'microservices', 'serverless'],
            'ai_ml': ['machine learning', 'ai', 'neural network', 'tensorflow', 'pytorch', 'scikit-learn', 'nlp'],
            'mobile': ['mobile', 'ios', 'android', 'react native', 'flutter', 'xamarin'],
            'devops': ['ci/cd', 'jenkins', 'git', 'github', 'gitlab', 'deployment', 'kubernetes']
        }
        
        # Programming concepts
        programming_concepts = {
            'algorithms': ['algorithm', 'data structure', 'sorting', 'searching', 'complexity', 'big o'],
            'design_patterns': ['design pattern', 'singleton', 'factory', 'observer', 'mvc', 'mvvm'],
            'testing': ['test', 'unit test', 'integration test', 'tdd', 'bdd', 'jest', 'pytest'],
            'security': ['security', 'authentication', 'authorization', 'encryption', 'oauth', 'jwt'],
            'performance': ['performance', 'optimization', 'caching', 'scalability', 'load balancing'],
            'architecture': ['architecture', 'microservices', 'monolith', 'api', 'rest', 'graphql']
        }
        
        for conv in conversations:
            content = conv.get_full_text().lower()
            
            # Check for programming languages
            for lang, keywords in language_keywords.items():
                if any(keyword in content for keyword in keywords):
                    languages_detected.add(lang)
            
            # Check for technologies
            for tech, keywords in tech_categories.items():
                if any(keyword in content for keyword in keywords):
                    technologies_detected.add(tech)
            
            # Check for concepts
            for concept, keywords in programming_concepts.items():
                if any(keyword in content for keyword in keywords):
                    concepts_detected.add(concept)
            
            # If any programming content detected, add to programming conversations
            if languages_detected or technologies_detected or concepts_detected:
                programming_conversations.append(conv)
        
        return {
            "programming_conversations_count": len(programming_conversations),
            "total_conversations": len(conversations),
            "programming_percentage": (len(programming_conversations) / len(conversations)) * 100 if conversations else 0,
            "languages_detected": list(languages_detected),
            "technologies_detected": list(technologies_detected),
            "concepts_detected": list(concepts_detected),
            "programming_conversations": [
                {
                    "id": conv.id,
                    "title": conv.auto_title or conv.title,
                    "date": conv.create_date.isoformat(),
                    "summary": conv.summary
                }
                for conv in programming_conversations[:10]  # Limit to top 10
            ]
        }
    
    def _prepare_conversation_context(self, conversations: List[Conversation], 
                                    analysis_type: str = "general",
                                    focus_conversation: Optional[Conversation] = None) -> str:
        """Prepare conversation context for analysis"""
        if focus_conversation:
            conversations = [focus_conversation]
        
        context_parts = []
        
        # Add conversation summaries
        for i, conv in enumerate(conversations[:10]):  # Limit to 10 conversations
            date_str = conv.create_date.strftime('%Y-%m-%d')
            title = conv.auto_title or conv.title
            tags = ', '.join(conv.tags) if conv.tags else 'No tags'
            
            context_parts.append(f"""
Conversation {i+1} - {date_str}
Title: {title}
Tags: {tags}
Summary: {conv.summary or 'No summary available'}
""")
        
        # Add programming analysis if relevant
        if analysis_type == "programming":
            programming_analysis = self.detect_programming_patterns(conversations)
            context_parts.append(f"""
Programming Analysis:
- Languages: {', '.join(programming_analysis['languages_detected'])}
- Technologies: {', '.join(programming_analysis['technologies_detected'])}
- Concepts: {', '.join(programming_analysis['concepts_detected'])}
- Programming conversations: {programming_analysis['programming_conversations_count']} out of {programming_analysis['total_conversations']}
""")
        
        return '\n'.join(context_parts)
    
    def _create_general_analysis_prompt(self, context: str) -> str:
        """Create prompt for general conversation analysis"""
        return f"""
Please analyze the following conversations and provide insights about:

1. Overall themes and patterns
2. Personal growth and development
3. Emotional patterns and evolution
4. Key insights and observations
5. Areas for continued growth

Conversation Data:
{context}

Please provide a comprehensive analysis that helps the user understand their conversation patterns and personal development journey.
"""
    
    def _create_emotional_analysis_prompt(self, context: str) -> str:
        """Create prompt for emotional analysis"""
        return f"""
Please analyze the emotional patterns in these conversations:

1. Emotional themes and recurring feelings
2. Emotional evolution over time
3. Triggers and emotional responses
4. Coping mechanisms and strategies
5. Emotional growth and resilience

Conversation Data:
{context}

Focus on emotional patterns, sentiment changes, and emotional development.
"""
    
    def _create_growth_analysis_prompt(self, context: str) -> str:
        """Create prompt for growth analysis"""
        return f"""
Please analyze the personal growth and development patterns:

1. Areas of significant growth
2. Learning patterns and knowledge acquisition
3. Skill development and mastery
4. Goal achievement and progress
5. Challenges overcome and resilience built

Conversation Data:
{context}

Focus on personal development, learning, and growth patterns.
"""
    
    def _create_programming_analysis_prompt(self, context: str) -> str:
        """Create prompt for programming analysis"""
        return f"""
Please analyze the programming and technical learning patterns:

1. Programming languages and technologies discussed
2. Learning progression and skill development
3. Problem-solving approaches and strategies
4. Technical challenges and solutions
5. Career development and technical growth

Conversation Data:
{context}

Focus on technical learning, programming patterns, and skill development.
"""
    
    def _parse_analysis_response(self, response: str, analysis_type: str) -> Dict[str, Any]:
        """Parse the AI response into structured data"""
        # For now, return the raw response
        # In a more sophisticated implementation, you could parse structured JSON responses
        return {
            "raw_response": response,
            "analysis_type": analysis_type,
            "summary": response[:200] + "..." if len(response) > 200 else response
        }


def create_chatgpt_integration(config_file: str = "config.json") -> Optional[ChatGPTIntegration]:
    """Factory function to create ChatGPT integration from config file"""
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        if not config_data.get('openai_api_key') or config_data['openai_api_key'] == "your_openai_api_key_here":
            return None
        
        config = ChatGPTConfig(
            api_key=config_data['openai_api_key'],
            model=config_data.get('model', 'gpt-4'),
            max_tokens=config_data.get('max_tokens', 1500),
            temperature=config_data.get('temperature', 0.7)
        )
        
        return ChatGPTIntegration(config)
        
    except Exception as e:
        print(f"Error creating ChatGPT integration: {e}")
        return None 