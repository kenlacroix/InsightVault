"""
ChatGPT Conversation Parser for InsightVault
Handles loading and parsing conversations.json from OpenAI exports
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dateutil import parser as date_parser


class ChatMessage:
    """Represents a single message in a conversation"""
    
    def __init__(self, message_data: Dict[str, Any]):
        self.id = message_data.get('id', '')
        self.role = message_data.get('author', {}).get('role', 'unknown')
        self.create_time = message_data.get('create_time', 0)
        self.content = self._extract_content(message_data.get('content', {}))
    
    def _extract_content(self, content_data: Dict[str, Any]) -> str:
        """Extract text content from the content structure"""
        if content_data.get('content_type') == 'text':
            parts = content_data.get('parts', [])
            return ' '.join(str(part) for part in parts if part)
        return ''
    
    @property
    def timestamp(self) -> datetime:
        """Get datetime object from create_time"""
        return datetime.fromtimestamp(self.create_time)
    
    def __str__(self):
        return f"{self.role}: {self.content[:100]}..."


class Conversation:
    """Represents a complete conversation with metadata"""
    
    def __init__(self, conversation_data: Dict[str, Any]):
        self.id = conversation_data.get('id', '')
        self.title = conversation_data.get('title', 'Untitled')
        self.create_time = conversation_data.get('create_time', 0)
        self.update_time = conversation_data.get('update_time', 0)
        self.messages = self._parse_messages(conversation_data.get('mapping', {}))
        
        # Metadata that will be populated by summarizer
        self.summary = ''
        self.tags = []
        self.auto_title = ''
    
    def _parse_messages(self, mapping: Dict[str, Any]) -> List[ChatMessage]:
        """Parse messages from the mapping structure"""
        messages = []
        for message_id, message_wrapper in mapping.items():
            if 'message' in message_wrapper and message_wrapper['message']:
                message = ChatMessage(message_wrapper['message'])
                if message.content.strip():  # Only include messages with content
                    messages.append(message)
        
        # Sort by create_time
        messages.sort(key=lambda m: m.create_time)
        return messages
    
    @property
    def create_date(self) -> datetime:
        """Get datetime object from create_time"""
        return datetime.fromtimestamp(self.create_time)
    
    @property
    def update_date(self) -> datetime:
        """Get datetime object from update_time"""
        return datetime.fromtimestamp(self.update_time)
    
    def get_full_text(self) -> str:
        """Get the full conversation as a single string"""
        text_parts = []
        for message in self.messages:
            text_parts.append(f"{message.role.upper()}: {message.content}")
        return '\n\n'.join(text_parts)
    
    def get_user_messages_only(self) -> str:
        """Get only user messages as a single string"""
        user_messages = [msg.content for msg in self.messages if msg.role == 'user']
        return '\n\n'.join(user_messages)
    
    def __str__(self):
        return f"Conversation '{self.title}' ({len(self.messages)} messages)"


class ChatParser:
    """Main parser class for ChatGPT conversations"""
    
    def __init__(self):
        self.conversations: List[Conversation] = []
    
    def load_conversations(self, file_path: str) -> bool:
        """
        Load conversations from a JSON file
        Returns True if successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                print(f"Error: File {file_path} not found")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both list format and single conversation format
            if isinstance(data, list):
                conversations_data = data
            elif isinstance(data, dict) and 'conversations' in data:
                conversations_data = data['conversations']
            else:
                conversations_data = [data]  # Single conversation
            
            self.conversations = []
            for conv_data in conversations_data:
                conversation = Conversation(conv_data)
                if conversation.messages:  # Only add conversations with messages
                    self.conversations.append(conversation)
            
            print(f"Successfully loaded {len(self.conversations)} conversations")
            return True
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return False
        except Exception as e:
            print(f"Error loading conversations: {e}")
            return False
    
    def get_conversations_by_date_range(self, start_date: Optional[datetime] = None, 
                                      end_date: Optional[datetime] = None) -> List[Conversation]:
        """Get conversations within a date range"""
        filtered = self.conversations
        
        if start_date:
            filtered = [c for c in filtered if c.create_date >= start_date]
        
        if end_date:
            filtered = [c for c in filtered if c.create_date <= end_date]
        
        return filtered
    
    def search_conversations(self, query: str, search_content: bool = True, 
                           search_titles: bool = True, search_tags: bool = True) -> List[Conversation]:
        """Search conversations by keyword"""
        query_lower = query.lower()
        results = []
        
        for conv in self.conversations:
            match = False
            
            if search_titles and query_lower in conv.title.lower():
                match = True
            elif search_titles and query_lower in conv.auto_title.lower():
                match = True
            elif search_tags and any(query_lower in tag.lower() for tag in conv.tags):
                match = True
            elif search_content and query_lower in conv.get_full_text().lower():
                match = True
            
            if match:
                results.append(conv)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded conversations"""
        if not self.conversations:
            return {}
        
        total_messages = sum(len(conv.messages) for conv in self.conversations)
        total_chars = sum(len(conv.get_full_text()) for conv in self.conversations)
        
        dates = [conv.create_date for conv in self.conversations]
        earliest = min(dates)
        latest = max(dates)
        
        return {
            'total_conversations': len(self.conversations),
            'total_messages': total_messages,
            'total_characters': total_chars,
            'earliest_date': earliest,
            'latest_date': latest,
            'date_range_days': (latest - earliest).days
        }


if __name__ == "__main__":
    # Test the parser with sample data
    parser = ChatParser()
    if parser.load_conversations('data/sample_conversations.json'):
        print(f"Loaded {len(parser.conversations)} conversations")
        for conv in parser.conversations:
            print(f"- {conv}")
            print(f"  Created: {conv.create_date}")
            print(f"  Messages: {len(conv.messages)}")
            print()