"""
User Profile Manager for InsightVault AI Assistant
Phase 2: Personalization and User Preferences

Provides user profile management, preference tracking, and personalized
insight generation based on user history and preferences.
"""

import sqlite3
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from pathlib import Path


@dataclass
class UserProfile:
    """User profile with preferences and history"""
    user_id: str
    created_at: datetime
    last_updated: datetime
    preferences: Dict[str, Any]
    learning_goals: List[str]
    focus_areas: List[str]
    interaction_history: List[Dict[str, Any]]
    feedback_history: List[Dict[str, Any]]
    insight_preferences: Dict[str, Any]
    growth_patterns: Dict[str, Any]


@dataclass
class UserFeedback:
    """User feedback on insights"""
    user_id: str
    query: str
    response: str
    rating: int  # 1-5 scale
    feedback_text: Optional[str]
    timestamp: datetime
    insight_id: Optional[str] = None


class UserProfileManager:
    """Manages user profiles, preferences, and personalization"""
    
    def __init__(self, db_path: str = "data/user_profiles.db"):
        """
        Initialize user profile manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    preferences TEXT,
                    learning_goals TEXT,
                    focus_areas TEXT,
                    insight_preferences TEXT,
                    growth_patterns TEXT
                )
            ''')
            
            # Interaction history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interaction_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    query TEXT,
                    response TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            ''')
            
            # Feedback history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    query TEXT,
                    response TEXT,
                    rating INTEGER,
                    feedback_text TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    insight_id TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            ''')
            
            # User preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT,
                    preference_key TEXT,
                    preference_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, preference_key),
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            ''')
            
            conn.commit()
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Retrieve user profile and preferences
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            UserProfile object or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get main profile
            cursor.execute('''
                SELECT created_at, last_updated, preferences, learning_goals, 
                       focus_areas, insight_preferences, growth_patterns
                FROM user_profiles WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            created_at, last_updated, preferences_json, learning_goals_json, \
            focus_areas_json, insight_preferences_json, growth_patterns_json = row
            
            # Parse JSON fields
            preferences = json.loads(preferences_json) if preferences_json else {}
            learning_goals = json.loads(learning_goals_json) if learning_goals_json else []
            focus_areas = json.loads(focus_areas_json) if focus_areas_json else []
            insight_preferences = json.loads(insight_preferences_json) if insight_preferences_json else {}
            growth_patterns = json.loads(growth_patterns_json) if growth_patterns_json else {}
            
            # Get interaction history
            cursor.execute('''
                SELECT query, response, timestamp, session_id
                FROM interaction_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 50
            ''', (user_id,))
            
            interaction_history = []
            for row in cursor.fetchall():
                interaction_history.append({
                    'query': row[0],
                    'response': row[1],
                    'timestamp': datetime.fromisoformat(row[2]),
                    'session_id': row[3]
                })
            
            # Get feedback history
            cursor.execute('''
                SELECT query, response, rating, feedback_text, timestamp, insight_id
                FROM feedback_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 50
            ''', (user_id,))
            
            feedback_history = []
            for row in cursor.fetchall():
                feedback_history.append({
                    'query': row[0],
                    'response': row[1],
                    'rating': row[2],
                    'feedback_text': row[3],
                    'timestamp': datetime.fromisoformat(row[4]),
                    'insight_id': row[5]
                })
            
            return UserProfile(
                user_id=user_id,
                created_at=datetime.fromisoformat(created_at),
                last_updated=datetime.fromisoformat(last_updated),
                preferences=preferences,
                learning_goals=learning_goals,
                focus_areas=focus_areas,
                interaction_history=interaction_history,
                feedback_history=feedback_history,
                insight_preferences=insight_preferences,
                growth_patterns=growth_patterns
            )
    
    def create_user_profile(self, user_id: str, initial_preferences: Optional[Dict] = None) -> UserProfile:
        """
        Create a new user profile
        
        Args:
            user_id: Unique user identifier
            initial_preferences: Optional initial preferences
            
        Returns:
            Created UserProfile object
        """
        default_preferences = {
            'insight_depth': 'detailed',
            'response_style': 'conversational',
            'focus_areas': ['personal_growth', 'relationships', 'productivity'],
            'learning_goals': ['self_awareness', 'emotional_intelligence'],
            'notification_preferences': {'email': False, 'in_app': True},
            'privacy_level': 'standard'
        }
        
        if initial_preferences:
            default_preferences.update(initial_preferences)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_profiles 
                (user_id, preferences, learning_goals, focus_areas, insight_preferences)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                json.dumps(default_preferences),
                json.dumps(default_preferences.get('learning_goals', [])),
                json.dumps(default_preferences.get('focus_areas', [])),
                json.dumps({'response_format': 'structured', 'detail_level': 'medium'})
            ))
            
            conn.commit()
        
        return self.get_user_profile(user_id)
    
    def update_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """
        Update user preferences
        
        Args:
            user_id: Unique user identifier
            preferences: Dictionary of preferences to update
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current preferences
            cursor.execute('SELECT preferences FROM user_profiles WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                current_preferences = json.loads(row[0]) if row[0] else {}
                current_preferences.update(preferences)
                
                cursor.execute('''
                    UPDATE user_profiles 
                    SET preferences = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (json.dumps(current_preferences), user_id))
            else:
                # Create profile if it doesn't exist
                self.create_user_profile(user_id, preferences)
            
            conn.commit()
    
    def personalize_insight(self, insight: Any, user_profile: UserProfile) -> Any:
        """
        Personalize insight based on user profile
        
        Args:
            insight: GeneratedInsight object to personalize
            user_profile: UserProfile object
            
        Returns:
            Personalized insight
        """
        if not user_profile:
            return insight
        
        # Adjust detail level based on user preferences
        detail_level = user_profile.insight_preferences.get('detail_level', 'medium')
        if detail_level == 'basic':
            # Simplify the insight
            insight.key_learnings = insight.key_learnings[:2]  # Limit to 2 key learnings
            insight.next_steps = insight.next_steps[:2]  # Limit to 2 next steps
        elif detail_level == 'comprehensive':
            # Add more detail if available
            pass  # Keep all details
        
        # Adjust response style based on preferences
        response_style = user_profile.preferences.get('response_style', 'conversational')
        if response_style == 'formal':
            # Make language more formal
            insight.summary = self._make_formal(insight.summary)
        elif response_style == 'casual':
            # Make language more casual
            insight.summary = self._make_casual(insight.summary)
        
        # Focus on user's preferred areas
        focus_areas = user_profile.focus_areas
        if focus_areas:
            # Prioritize insights related to focus areas
            insight.key_learnings = self._prioritize_by_focus_areas(
                insight.key_learnings, focus_areas
            )
        
        # Add personalized recommendations based on learning goals
        learning_goals = user_profile.learning_goals
        if learning_goals:
            insight.next_steps = self._add_goal_aligned_steps(
                insight.next_steps, learning_goals
            )
        
        # Adjust confidence based on user's feedback history
        avg_rating = self._calculate_average_rating(user_profile.feedback_history)
        if avg_rating and avg_rating < 3.0:
            insight.confidence_score *= 0.9  # Reduce confidence if user gives low ratings
        
        return insight
    
    def collect_feedback(self, user_id: str, query: str, response: str, 
                        rating: int, feedback_text: Optional[str] = None, 
                        insight_id: Optional[str] = None):
        """
        Collect and store user feedback
        
        Args:
            user_id: Unique user identifier
            query: Original user query
            response: Generated response
            rating: User rating (1-5)
            feedback_text: Optional text feedback
            insight_id: Optional insight identifier
        """
        if not (1 <= rating <= 5):
            self.logger.warning(f"Invalid rating {rating} for user {user_id}")
            return
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO feedback_history 
                (user_id, query, response, rating, feedback_text, insight_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, query, response, rating, feedback_text, insight_id))
            
            conn.commit()
        
        # Update user preferences based on feedback
        self._update_preferences_from_feedback(user_id, rating, feedback_text)
    
    def record_interaction(self, user_id: str, query: str, response: str, 
                          session_id: Optional[str] = None):
        """
        Record user interaction for analysis
        
        Args:
            user_id: Unique user identifier
            query: User query
            response: Generated response
            session_id: Optional session identifier
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO interaction_history 
                (user_id, query, response, session_id)
                VALUES (?, ?, ?, ?)
            ''', (user_id, query, response, session_id))
            
            conn.commit()
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get user interaction statistics
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Dictionary with user statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get interaction count
            cursor.execute('SELECT COUNT(*) FROM interaction_history WHERE user_id = ?', (user_id,))
            interaction_count = cursor.fetchone()[0]
            
            # Get average rating
            cursor.execute('SELECT AVG(rating) FROM feedback_history WHERE user_id = ?', (user_id,))
            avg_rating = cursor.fetchone()[0]
            
            # Get most common query topics
            cursor.execute('''
                SELECT query, COUNT(*) as count 
                FROM interaction_history 
                WHERE user_id = ? 
                GROUP BY query 
                ORDER BY count DESC 
                LIMIT 5
            ''', (user_id,))
            
            common_queries = [{'query': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # Get recent activity
            cursor.execute('''
                SELECT timestamp 
                FROM interaction_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (user_id,))
            
            last_activity = cursor.fetchone()
            last_activity = datetime.fromisoformat(last_activity[0]) if last_activity else None
            
            return {
                'interaction_count': interaction_count,
                'average_rating': avg_rating,
                'common_queries': common_queries,
                'last_activity': last_activity,
                'engagement_level': self._calculate_engagement_level(interaction_count, avg_rating)
            }
    
    def get_recommendations(self, user_id: str) -> List[str]:
        """
        Get personalized recommendations for user
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            List of personalized recommendations
        """
        profile = self.get_user_profile(user_id)
        if not profile:
            return []
        
        recommendations = []
        
        # Analyze interaction patterns
        stats = self.get_user_statistics(user_id)
        
        # Low engagement recommendations
        if stats['interaction_count'] < 5:
            recommendations.extend([
                "Try asking about your learning patterns to get started",
                "Explore your conversation history for insights",
                "Ask about specific areas you want to improve"
            ])
        
        # Low rating recommendations
        if stats['average_rating'] and stats['average_rating'] < 3.0:
            recommendations.extend([
                "Try being more specific in your questions",
                "Ask about recent conversations for more relevant insights",
                "Provide feedback to help improve responses"
            ])
        
        # Focus area recommendations
        focus_areas = profile.focus_areas
        for area in focus_areas:
            recommendations.append(f"Ask about your progress in {area}")
        
        # Learning goal recommendations
        learning_goals = profile.learning_goals
        for goal in learning_goals:
            recommendations.append(f"Explore how you're developing {goal}")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _make_formal(self, text: str) -> str:
        """Make text more formal"""
        # Simple formalization rules
        replacements = {
            "you've": "you have",
            "you're": "you are",
            "don't": "do not",
            "can't": "cannot",
            "won't": "will not",
            "I've": "I have",
            "I'm": "I am"
        }
        
        for informal, formal in replacements.items():
            text = text.replace(informal, formal)
        
        return text
    
    def _make_casual(self, text: str) -> str:
        """Make text more casual"""
        # Simple casualization rules
        replacements = {
            "you have": "you've",
            "you are": "you're",
            "do not": "don't",
            "cannot": "can't",
            "will not": "won't",
            "I have": "I've",
            "I am": "I'm"
        }
        
        for formal, casual in replacements.items():
            text = text.replace(formal, casual)
        
        return text
    
    def _prioritize_by_focus_areas(self, key_learnings: List[str], 
                                  focus_areas: List[str]) -> List[str]:
        """Prioritize key learnings based on focus areas"""
        if not focus_areas:
            return key_learnings
        
        # Simple prioritization: move focus area related learnings to front
        prioritized = []
        others = []
        
        for learning in key_learnings:
            if any(area.lower() in learning.lower() for area in focus_areas):
                prioritized.append(learning)
            else:
                others.append(learning)
        
        return prioritized + others
    
    def _add_goal_aligned_steps(self, next_steps: List[str], 
                               learning_goals: List[str]) -> List[str]:
        """Add goal-aligned next steps"""
        if not learning_goals:
            return next_steps
        
        # Add goal-specific steps
        goal_steps = []
        for goal in learning_goals:
            if 'self_awareness' in goal:
                goal_steps.append("Practice daily self-reflection to deepen self-awareness")
            elif 'emotional_intelligence' in goal:
                goal_steps.append("Notice and name your emotions throughout the day")
            elif 'relationships' in goal:
                goal_steps.append("Apply insights about relationships in your daily interactions")
            elif 'productivity' in goal:
                goal_steps.append("Implement one productivity insight this week")
        
        return next_steps + goal_steps[:2]  # Add up to 2 goal-specific steps
    
    def _calculate_average_rating(self, feedback_history: List[Dict]) -> Optional[float]:
        """Calculate average rating from feedback history"""
        if not feedback_history:
            return None
        
        ratings = [feedback['rating'] for feedback in feedback_history]
        return sum(ratings) / len(ratings)
    
    def _update_preferences_from_feedback(self, user_id: str, rating: int, 
                                        feedback_text: Optional[str]):
        """Update user preferences based on feedback"""
        if rating <= 2 and feedback_text:
            # Low rating with feedback - might indicate preference mismatch
            feedback_lower = feedback_text.lower()
            
            if 'too detailed' in feedback_lower or 'too long' in feedback_lower:
                self.update_preferences(user_id, {'insight_depth': 'basic'})
            elif 'too simple' in feedback_lower or 'not enough detail' in feedback_lower:
                self.update_preferences(user_id, {'insight_depth': 'comprehensive'})
            elif 'too formal' in feedback_lower:
                self.update_preferences(user_id, {'response_style': 'casual'})
            elif 'too casual' in feedback_lower:
                self.update_preferences(user_id, {'response_style': 'formal'})
    
    def _calculate_engagement_level(self, interaction_count: int, 
                                  avg_rating: Optional[float]) -> str:
        """Calculate user engagement level"""
        if interaction_count >= 20 and avg_rating and avg_rating >= 4.0:
            return 'high'
        elif interaction_count >= 10 and avg_rating and avg_rating >= 3.0:
            return 'medium'
        else:
            return 'low'
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all user data for privacy compliance
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Dictionary containing all user data
        """
        profile = self.get_user_profile(user_id)
        if not profile:
            return {}
        
        return {
            'user_id': user_id,
            'profile': asdict(profile),
            'statistics': self.get_user_statistics(user_id),
            'recommendations': self.get_recommendations(user_id),
            'exported_at': datetime.now().isoformat()
        }
    
    def delete_user_data(self, user_id: str) -> bool:
        """
        Delete all user data for privacy compliance
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            True if deletion successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete all user data
                cursor.execute('DELETE FROM feedback_history WHERE user_id = ?', (user_id,))
                cursor.execute('DELETE FROM interaction_history WHERE user_id = ?', (user_id,))
                cursor.execute('DELETE FROM user_preferences WHERE user_id = ?', (user_id,))
                cursor.execute('DELETE FROM user_profiles WHERE user_id = ?', (user_id,))
                
                conn.commit()
            
            return True
        except Exception as e:
            self.logger.error(f"Error deleting user data for {user_id}: {e}")
            return False


def main():
    """Test the user profile manager"""
    manager = UserProfileManager("test_user_profiles.db")
    
    # Test user ID
    user_id = "test_user_123"
    
    # Create profile
    profile = manager.create_user_profile(user_id, {
        'focus_areas': ['relationships', 'productivity'],
        'learning_goals': ['self_awareness', 'emotional_intelligence']
    })
    
    print(f"Created profile for user: {profile.user_id}")
    print(f"Focus areas: {profile.focus_areas}")
    print(f"Learning goals: {profile.learning_goals}")
    
    # Record interaction
    manager.record_interaction(user_id, "What have I learned about relationships?", 
                              "Your relationships have evolved...")
    
    # Collect feedback
    manager.collect_feedback(user_id, "What have I learned about relationships?", 
                           "Your relationships have evolved...", 4, "Great insight!")
    
    # Get statistics
    stats = manager.get_user_statistics(user_id)
    print(f"User statistics: {stats}")
    
    # Get recommendations
    recommendations = manager.get_recommendations(user_id)
    print(f"Recommendations: {recommendations}")


if __name__ == '__main__':
    main() 