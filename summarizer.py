"""
Conversation Summarizer for InsightVault
Uses OpenAI GPT-4 to generate summaries and tags for conversations
"""

import json
import os
import pickle
from datetime import datetime
from typing import List, Dict, Any, Optional
from openai import OpenAI
from chat_parser import Conversation, ChatParser


class ConversationSummarizer:
    """Handles summarization and tagging of conversations using GPT-4"""
    
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
    
    def _get_cache_path(self, conversation_id: str, cache_type: str) -> str:
        """Get cache file path for a conversation"""
        return os.path.join(self.cache_dir, f"{conversation_id}_{cache_type}.pkl")
    
    def _load_from_cache(self, conversation_id: str, cache_type: str) -> Optional[Dict[str, Any]]:
        """Load cached result if it exists"""
        cache_path = self._get_cache_path(conversation_id, cache_type)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading cache for {conversation_id}: {e}")
        return None
    
    def _save_to_cache(self, conversation_id: str, cache_type: str, data: Dict[str, Any]):
        """Save result to cache"""
        cache_path = self._get_cache_path(conversation_id, cache_type)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Error saving cache for {conversation_id}: {e}")
    
    def summarize_conversation(self, conversation: Conversation, force_refresh: bool = False) -> bool:
        """
        Generate summary and tags for a conversation
        Returns True if successful, False otherwise
        """
        # Check cache first
        if not force_refresh:
            cached = self._load_from_cache(conversation.id, 'summary')
            if cached:
                conversation.summary = cached['summary']
                conversation.tags = cached['tags']
                conversation.auto_title = cached['auto_title']
                return True
        
        try:
            # Prepare the conversation text
            conv_text = conversation.get_full_text()
            
            # If conversation is too long, truncate or use user messages only
            if len(conv_text) > 8000:  # Rough token limit
                conv_text = conversation.get_user_messages_only()
                if len(conv_text) > 6000:
                    conv_text = conv_text[:6000] + "... [truncated]"
            
            # Create the prompt
            prompt = self._create_summary_prompt(conv_text, conversation.title)
            
            # Call GPT-4
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing personal conversations for insights about growth, healing, and self-reflection."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.get('max_tokens', 1500),
                temperature=self.config.get('temperature', 0.7)
            )
            
            # Parse the response
            result = self._parse_summary_response(response.choices[0].message.content)
            
            # Update conversation object
            conversation.summary = result['summary']
            conversation.tags = result['tags']
            conversation.auto_title = result['auto_title']
            
            # Cache the result
            cache_data = {
                'summary': result['summary'],
                'tags': result['tags'],
                'auto_title': result['auto_title'],
                'generated_at': datetime.now().isoformat()
            }
            self._save_to_cache(conversation.id, 'summary', cache_data)
            
            return True
            
        except Exception as e:
            print(f"Error summarizing conversation {conversation.id}: {e}")
            return False
    
    def _create_summary_prompt(self, conversation_text: str, original_title: str) -> str:
        """Create the prompt for GPT-4 summarization"""
        return f"""
Please analyze this personal conversation and provide:

1. **AUTO_TITLE**: A clear, descriptive title (5-8 words) that captures the main theme
2. **SUMMARY**: A concise 2-5 sentence summary of the key topics and insights
3. **TAGS**: 3-7 relevant tags for categorization (focus on themes like spirituality, healing, relationships, personal growth, emotions, etc.)

**Original Title**: {original_title}

**Conversation**:
{conversation_text}

**Instructions**:
- Focus on personal growth, emotional patterns, spiritual insights, and healing themes
- Tags should be single words or short phrases, lowercase, separated by commas
- Summary should highlight the person's main concerns, insights, or growth areas
- Be empathetic and insightful in your analysis

**Format your response exactly like this**:
AUTO_TITLE: [your title here]
SUMMARY: [your summary here]
TAGS: [tag1, tag2, tag3, etc.]
"""
    
    def _parse_summary_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the GPT-4 response into structured data"""
        result = {
            'auto_title': '',
            'summary': '',
            'tags': []
        }
        
        lines = response_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('AUTO_TITLE:'):
                result['auto_title'] = line.replace('AUTO_TITLE:', '').strip()
            elif line.startswith('SUMMARY:'):
                result['summary'] = line.replace('SUMMARY:', '').strip()
            elif line.startswith('TAGS:'):
                tags_text = line.replace('TAGS:', '').strip()
                # Split by comma and clean up
                tags = [tag.strip().lower() for tag in tags_text.split(',')]
                result['tags'] = [tag for tag in tags if tag]  # Remove empty tags
        
        # Fallback if parsing fails
        if not result['auto_title']:
            result['auto_title'] = 'Personal Conversation'
        if not result['summary']:
            result['summary'] = 'A personal conversation covering various topics.'
        if not result['tags']:
            result['tags'] = ['personal', 'conversation']
        
        return result
    
    def summarize_all_conversations(self, conversations: List[Conversation], 
                                  force_refresh: bool = False) -> Dict[str, bool]:
        """
        Summarize all conversations
        Returns dict with conversation_id -> success status
        """
        results = {}
        
        for i, conv in enumerate(conversations):
            print(f"Processing conversation {i+1}/{len(conversations)}: {conv.title}")
            
            success = self.summarize_conversation(conv, force_refresh)
            results[conv.id] = success
            
            if success:
                print(f"  ✓ Generated: {conv.auto_title}")
                print(f"  ✓ Tags: {', '.join(conv.tags)}")
            else:
                print(f"  ✗ Failed to process")
        
        return results
    
    def get_all_tags(self, conversations: List[Conversation]) -> Dict[str, int]:
        """Get all unique tags with their frequency counts"""
        tag_counts = {}
        
        for conv in conversations:
            for tag in conv.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by frequency
        return dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))
    
    def export_summaries(self, conversations: List[Conversation], 
                        output_path: str = 'output/summaries.md') -> bool:
        """Export all summaries to a Markdown file"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# InsightVault - Conversation Summaries\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"Total Conversations: {len(conversations)}\n\n")
                
                # Tag summary
                tag_counts = self.get_all_tags(conversations)
                f.write("## Most Common Tags\n\n")
                for tag, count in list(tag_counts.items())[:15]:  # Top 15 tags
                    f.write(f"- **{tag}** ({count})\n")
                f.write("\n---\n\n")
                
                # Individual conversations
                for conv in sorted(conversations, key=lambda c: c.create_date, reverse=True):
                    f.write(f"## {conv.auto_title or conv.title}\n\n")
                    f.write(f"**Original Title:** {conv.title}\n\n")
                    f.write(f"**Date:** {conv.create_date.strftime('%Y-%m-%d')}\n\n")
                    f.write(f"**Tags:** {', '.join(conv.tags)}\n\n")
                    f.write(f"**Summary:** {conv.summary}\n\n")
                    f.write("---\n\n")
            
            print(f"Summaries exported to {output_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting summaries: {e}")
            return False


if __name__ == "__main__":
    # Test the summarizer
    parser = ChatParser()
    if parser.load_conversations('data/sample_conversations.json'):
        summarizer = ConversationSummarizer()
        results = summarizer.summarize_all_conversations(parser.conversations)
        
        print(f"\nSummarization Results:")
        for conv_id, success in results.items():
            status = "✓" if success else "✗"
            print(f"{status} {conv_id}")
        
        # Export summaries
        summarizer.export_summaries(parser.conversations)