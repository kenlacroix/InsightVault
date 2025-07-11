"""
Analytics Engine for InsightVault
Provides advanced data analytics, emotional tracking, and trend analysis
"""

import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict
from dataclasses import dataclass
import pickle

# Optional imports for sentiment analysis
try:
    from textblob import TextBlob
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False

# Optional imports for advanced analytics
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

from chat_parser import Conversation


@dataclass
class AnalyticsData:
    """Container for analytics data"""
    conversation_count: int
    total_messages: int
    date_range: Tuple[datetime, datetime]
    top_tags: List[Tuple[str, int]]
    sentiment_trends: Optional[Dict[str, List[float]]]
    emotional_patterns: Dict[str, Any]
    growth_metrics: Dict[str, float]
    engagement_stats: Dict[str, Any]
    breakthrough_moments: List[Dict[str, Any]]  # New: breakthrough detection
    writing_style_evolution: Dict[str, Any]     # New: writing style analysis
    concept_relationships: Dict[str, Any]       # New: concept mapping
    goal_achievement: Dict[str, Any]            # New: goal tracking


class AnalyticsEngine:
    """Advanced analytics engine for conversation data analysis"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config = self._load_config(config_path)
        self.cache_dir = 'data/analytics_cache'
        self._ensure_cache_dir()
        
        # Set up visualization styles
        self._setup_visualization_styles()
        
        # Initialize emotional keywords for analysis
        self._initialize_emotional_keywords()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Use default config if file not found
            return {
                'analytics': {
                    'sentiment_analysis': True,
                    'emotional_tracking': True,
                    'cache_analytics': True,
                    'visualization_theme': 'insights'
                }
            }
    
    def _ensure_cache_dir(self):
        """Ensure analytics cache directory exists"""
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _setup_visualization_styles(self):
        """Set up consistent visualization styles"""
        # Set color palette for insights theme
        self.color_palette = [
            '#3498db',  # Blue
            '#e74c3c',  # Red  
            '#2ecc71',  # Green
            '#f39c12',  # Orange
            '#9b59b6',  # Purple
            '#1abc9c',  # Teal
            '#34495e',  # Dark gray
            '#e67e22'   # Dark orange
        ]
        
        # Configure matplotlib and seaborn
        plt.style.use('seaborn-v0_8')
        sns.set_palette(self.color_palette)
        
        # Configure plotly theme
        self.plotly_template = 'plotly_white'
    
    def _initialize_emotional_keywords(self):
        """Initialize emotional keyword dictionaries for analysis"""
        self.emotional_keywords = {
            'positive': [
                'happy', 'joy', 'grateful', 'love', 'peaceful', 'calm', 'excited',
                'accomplished', 'proud', 'confident', 'hopeful', 'optimistic',
                'content', 'satisfied', 'inspired', 'motivated', 'breakthrough',
                'progress', 'growth', 'healing', 'better', 'improving', 'success'
            ],
            'negative': [
                'sad', 'depressed', 'anxious', 'worried', 'stressed', 'angry',
                'frustrated', 'overwhelmed', 'disappointed', 'guilty', 'shame',
                'fear', 'panic', 'lonely', 'isolated', 'hopeless', 'stuck',
                'struggling', 'difficult', 'hard', 'painful', 'trauma', 'trigger'
            ],
            'neutral': [
                'thinking', 'considering', 'wondering', 'exploring', 'learning',
                'understanding', 'realizing', 'noticing', 'observing', 'reflecting'
            ]
        }
        
        # Initialize breakthrough keywords for detection
        self.breakthrough_keywords = [
            'breakthrough', 'epiphany', 'realization', 'aha moment', 'suddenly realized',
            'it clicked', 'everything changed', 'turning point', 'lightbulb moment',
            'finally understood', 'made sense', 'clear now', 'got it', 'figured out',
            'discovered', 'unlocked', 'opened up', 'transformed', 'shifted', 'changed'
        ]
        
        # Initialize writing style indicators
        self.writing_style_indicators = {
            'complexity': ['however', 'therefore', 'consequently', 'furthermore', 'moreover', 'nevertheless'],
            'emotional_depth': ['feel', 'emotion', 'heart', 'soul', 'deep', 'profound', 'intense'],
            'analytical': ['analyze', 'examine', 'consider', 'evaluate', 'assess', 'investigate'],
            'reflective': ['reflect', 'think about', 'consider', 'ponder', 'contemplate', 'meditate'],
            'concrete': ['specific', 'example', 'instance', 'case', 'situation', 'scenario'],
            'abstract': ['concept', 'idea', 'theory', 'principle', 'philosophy', 'understanding']
        }
        
        # Initialize goal-related keywords
        self.goal_keywords = [
            'goal', 'objective', 'target', 'aim', 'purpose', 'intention', 'plan',
            'achieve', 'accomplish', 'reach', 'attain', 'complete', 'finish',
            'success', 'milestone', 'progress', 'advancement', 'development',
            'improvement', 'growth', 'better', 'enhance', 'upgrade', 'evolve'
        ]
    
    def analyze_conversations(self, conversations: List[Conversation], 
                            use_cache: bool = True) -> AnalyticsData:
        """
        Perform comprehensive analytics on conversation data
        """
        # Create cache key
        conv_ids = sorted([conv.id for conv in conversations])
        cache_key = f"analytics_{hash(''.join(conv_ids))}"
        
        # Check cache
        if use_cache:
            cached_data = self._load_analytics_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        # Basic conversation statistics
        conversation_count = len(conversations)
        total_messages = sum(len(conv.messages) for conv in conversations)
        
        # Date range analysis
        dates = [conv.create_date for conv in conversations]
        date_range = (min(dates), max(dates)) if dates else (datetime.now(), datetime.now())
        
        # Tag frequency analysis
        all_tags = []
        for conv in conversations:
            all_tags.extend(conv.tags)
        top_tags = Counter(all_tags).most_common(20)
        
        # Sentiment and emotional analysis
        sentiment_trends = None
        emotional_patterns = {}
        
        if SENTIMENT_AVAILABLE and self.config.get('analytics', {}).get('sentiment_analysis', True):
            sentiment_trends = self._analyze_sentiment_trends(conversations)
            emotional_patterns = self._analyze_emotional_patterns(conversations)
        
        # Growth metrics calculation
        growth_metrics = self._calculate_growth_metrics(conversations)
        
        # Engagement statistics
        engagement_stats = self._calculate_engagement_stats(conversations)
        
        # Breakthrough detection
        breakthrough_moments = self._detect_breakthrough_moments(conversations)
        
        # Writing style analysis
        writing_style_evolution = self._analyze_writing_style_evolution(conversations)
        
        # Concept relationships
        concept_relationships = self._analyze_concept_relationships(conversations)
        
        # Goal achievement
        goal_achievement = self._analyze_goal_achievement(conversations)
        
        # Create analytics data object
        analytics_data = AnalyticsData(
            conversation_count=conversation_count,
            total_messages=total_messages,
            date_range=date_range,
            top_tags=top_tags,
            sentiment_trends=sentiment_trends,
            emotional_patterns=emotional_patterns,
            growth_metrics=growth_metrics,
            engagement_stats=engagement_stats,
            breakthrough_moments=breakthrough_moments,
            writing_style_evolution=writing_style_evolution,
            concept_relationships=concept_relationships,
            goal_achievement=goal_achievement
        )
        
        # Cache results
        if use_cache:
            self._save_analytics_to_cache(cache_key, analytics_data)
        
        return analytics_data
    
    def _analyze_sentiment_trends(self, conversations: List[Conversation]) -> Dict[str, List[float]]:
        """Analyze sentiment trends over time"""
        if not SENTIMENT_AVAILABLE:
            return {}
        
        # Group conversations by month
        monthly_sentiment = defaultdict(list)
        
        for conv in conversations:
            month_key = conv.create_date.strftime('%Y-%m')
            
            # Calculate sentiment for conversation
            full_text = conv.get_full_text()
            if full_text:
                blob = TextBlob(full_text)
                sentiment_score = blob.sentiment.polarity  # -1 to 1
                monthly_sentiment[month_key].append(sentiment_score)
        
        # Calculate average sentiment per month
        sentiment_trends = {}
        for month, scores in monthly_sentiment.items():
            sentiment_trends[month] = {
                'avg_sentiment': np.mean(scores),
                'sentiment_std': np.std(scores),
                'conversation_count': len(scores)
            }
        
        return sentiment_trends
    
    def _analyze_emotional_patterns(self, conversations: List[Conversation]) -> Dict[str, Any]:
        """Analyze emotional patterns in conversations"""
        emotional_counts = defaultdict(int)
        emotional_timeline = defaultdict(lambda: defaultdict(int))
        
        for conv in conversations:
            month_key = conv.create_date.strftime('%Y-%m')
            text = conv.get_full_text().lower()
            
            # Count emotional keywords
            for emotion_type, keywords in self.emotional_keywords.items():
                count = sum(text.count(keyword) for keyword in keywords)
                emotional_counts[emotion_type] += count
                emotional_timeline[month_key][emotion_type] += count
        
        return {
            'overall_emotional_distribution': dict(emotional_counts),
            'emotional_timeline': dict(emotional_timeline)
        }
    
    def _calculate_growth_metrics(self, conversations: List[Conversation]) -> Dict[str, float]:
        """Calculate personal growth metrics"""
        if len(conversations) < 2:
            return {}
        
        # Sort conversations by date
        sorted_convs = sorted(conversations, key=lambda x: x.create_date)
        
        # Split into early and recent periods
        mid_point = len(sorted_convs) // 2
        early_convs = sorted_convs[:mid_point]
        recent_convs = sorted_convs[mid_point:]
        
        # Calculate metrics for each period
        early_metrics = self._calculate_period_metrics(early_convs)
        recent_metrics = self._calculate_period_metrics(recent_convs)
        
        # Calculate growth rates
        growth_metrics = {}
        for metric in early_metrics:
            if early_metrics[metric] > 0:
                growth_rate = (recent_metrics[metric] - early_metrics[metric]) / early_metrics[metric]
                growth_metrics[f'{metric}_growth'] = growth_rate
        
        return growth_metrics
    
    def _calculate_period_metrics(self, conversations: List[Conversation]) -> Dict[str, float]:
        """Calculate metrics for a specific time period"""
        if not conversations:
            return defaultdict(float)
        
        total_text = ' '.join(conv.get_full_text().lower() for conv in conversations)
        
        # Self-awareness indicators
        self_awareness_keywords = [
            'realize', 'understand', 'notice', 'aware', 'insight', 'pattern',
            'recognize', 'learn', 'discover', 'reflection'
        ]
        
        # Progress indicators
        progress_keywords = [
            'better', 'improve', 'progress', 'growth', 'healing', 'overcome',
            'breakthrough', 'success', 'achievement', 'forward'
        ]
        
        # Calculate keyword density
        word_count = len(total_text.split())
        
        metrics = {
            'self_awareness_density': sum(total_text.count(kw) for kw in self_awareness_keywords) / max(word_count, 1),
            'progress_density': sum(total_text.count(kw) for kw in progress_keywords) / max(word_count, 1),
            'conversation_frequency': len(conversations),
            'avg_conversation_length': np.mean([len(conv.get_full_text()) for conv in conversations])
        }
        
        return metrics
    
    def _calculate_engagement_stats(self, conversations: List[Conversation]) -> Dict[str, Any]:
        """Calculate engagement and interaction statistics"""
        if not conversations:
            return {}
        
        # Message length statistics
        message_lengths = []
        for conv in conversations:
            for msg in conv.messages:
                if msg.content:
                    message_lengths.append(len(msg.content))
        
        # Conversation timing analysis
        conversation_gaps = []
        sorted_convs = sorted(conversations, key=lambda x: x.create_date)
        
        for i in range(1, len(sorted_convs)):
            gap = (sorted_convs[i].create_date - sorted_convs[i-1].create_date).days
            conversation_gaps.append(gap)
        
        return {
            'avg_message_length': np.mean(message_lengths) if message_lengths else 0,
            'message_length_std': np.std(message_lengths) if message_lengths else 0,
            'avg_conversation_gap_days': np.mean(conversation_gaps) if conversation_gaps else 0,
            'total_characters': sum(message_lengths),
            'most_active_month': self._find_most_active_month(conversations)
        }
    
    def _find_most_active_month(self, conversations: List[Conversation]) -> str:
        """Find the month with most conversation activity"""
        monthly_counts = defaultdict(int)
        for conv in conversations:
            month_key = conv.create_date.strftime('%Y-%m')
            monthly_counts[month_key] += 1
        
        if monthly_counts:
            return max(monthly_counts.items(), key=lambda x: x[1])[0]
        return ""
    
    def _detect_breakthrough_moments(self, conversations: List[Conversation]) -> List[Dict[str, Any]]:
        """Detect breakthrough moments in conversations"""
        breakthroughs = []
        
        for conv in conversations:
            text = conv.get_full_text().lower()
            breakthrough_score = 0
            detected_keywords = []
            
            # Check for breakthrough keywords
            for keyword in self.breakthrough_keywords:
                if keyword in text:
                    breakthrough_score += 1
                    detected_keywords.append(keyword)
            
            # Check for emotional intensity (high sentiment variance)
            if SENTIMENT_AVAILABLE:
                try:
                    blob = TextBlob(text)
                    sentiment_variance = abs(blob.sentiment.polarity)
                    if sentiment_variance > 0.3:  # High emotional content
                        breakthrough_score += 0.5
                except:
                    pass  # Skip sentiment analysis if it fails
            
            # Check for long, detailed responses (indicating deep reflection)
            if len(text) > 1000:  # Long conversation
                breakthrough_score += 0.5
            
            # If breakthrough detected
            if breakthrough_score >= 1.0:
                breakthroughs.append({
                    'conversation_id': conv.id,
                    'date': conv.create_date.isoformat(),
                    'title': conv.auto_title or conv.title,
                    'breakthrough_score': breakthrough_score,
                    'detected_keywords': detected_keywords,
                    'summary': conv.summary[:200] + '...' if len(conv.summary) > 200 else conv.summary
                })
        
        # Sort by breakthrough score and date
        breakthroughs.sort(key=lambda x: (x['breakthrough_score'], x['date']), reverse=True)
        return breakthroughs[:10]  # Return top 10 breakthroughs
    
    def _analyze_writing_style_evolution(self, conversations: List[Conversation]) -> Dict[str, Any]:
        """Analyze writing style evolution over time"""
        if len(conversations) < 3:
            return {}
        
        # Sort conversations by date
        sorted_convs = sorted(conversations, key=lambda x: x.create_date)
        
        # Split into time periods
        period_size = len(sorted_convs) // 3
        periods = {
            'early': sorted_convs[:period_size],
            'middle': sorted_convs[period_size:2*period_size],
            'recent': sorted_convs[2*period_size:]
        }
        
        style_evolution = {}
        
        for period_name, period_convs in periods.items():
            if not period_convs:
                continue
                
            period_text = ' '.join(conv.get_full_text().lower() for conv in period_convs)
            word_count = len(period_text.split())
            
            period_metrics = {}
            
            # Analyze each writing style dimension
            for style_type, keywords in self.writing_style_indicators.items():
                keyword_count = sum(period_text.count(kw) for kw in keywords)
                period_metrics[style_type] = keyword_count / max(word_count, 1)
            
            # Calculate average sentence length
            sentences = period_text.split('.')
            avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
            period_metrics['avg_sentence_length'] = avg_sentence_length
            
            # Calculate vocabulary diversity
            unique_words = len(set(period_text.split()))
            period_metrics['vocabulary_diversity'] = unique_words / max(word_count, 1)
            
            style_evolution[period_name] = period_metrics
        
        return style_evolution
    
    def _analyze_concept_relationships(self, conversations: List[Conversation]) -> Dict[str, Any]:
        """Analyze concept relationships and topic clustering"""
        if not conversations or not ML_AVAILABLE:
            return {}
        
        # Extract all text for analysis
        all_texts = [conv.get_full_text() for conv in conversations]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        
        try:
            # Fit and transform the texts
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Perform topic clustering
            n_clusters = min(5, len(conversations))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            
            # Analyze concept relationships
            concept_relationships = {
                'top_concepts': feature_names[:20].tolist(),
                'concept_clusters': {},
                'concept_cooccurrence': {}
            }
            
            # Group conversations by cluster
            for i in range(n_clusters):
                cluster_convs = [conv for j, conv in enumerate(conversations) if cluster_labels[j] == i]
                cluster_topics = [conv.auto_title or conv.title for conv in cluster_convs]
                concept_relationships['concept_clusters'][f'cluster_{i}'] = {
                    'topics': cluster_topics[:5],
                    'size': len(cluster_convs)
                }
            
            # Calculate concept co-occurrence
            for i, conv in enumerate(conversations):
                conv_vector = tfidf_matrix[i].toarray()[0]
                top_concepts = [feature_names[j] for j in np.argsort(conv_vector)[-5:]]
                
                for concept in top_concepts:
                    if concept not in concept_relationships['concept_cooccurrence']:
                        concept_relationships['concept_cooccurrence'][concept] = []
                    concept_relationships['concept_cooccurrence'][concept].append({
                        'conversation_id': conv.id,
                        'date': conv.create_date.isoformat(),
                        'title': conv.auto_title or conv.title
                    })
            
            return concept_relationships
            
        except Exception as e:
            print(f"Error in concept relationship analysis: {e}")
            return {}
    
    def _analyze_goal_achievement(self, conversations: List[Conversation]) -> Dict[str, Any]:
        """Analyze goal achievement patterns and progress tracking"""
        if not conversations:
            return {}
        
        # Sort conversations by date
        sorted_convs = sorted(conversations, key=lambda x: x.create_date)
        
        goal_mentions = []
        achievement_patterns = []
        
        for conv in sorted_convs:
            text = conv.get_full_text().lower()
            date = conv.create_date
            
            # Count goal-related keywords
            goal_count = sum(text.count(kw) for kw in self.goal_keywords)
            
            if goal_count > 0:
                goal_mentions.append({
                    'date': date.isoformat(),
                    'conversation_id': conv.id,
                    'title': conv.auto_title or conv.title,
                    'goal_mentions': goal_count,
                    'summary': conv.summary[:150] + '...' if len(conv.summary) > 150 else conv.summary
                })
            
            # Check for achievement indicators
            achievement_indicators = [
                'achieved', 'accomplished', 'completed', 'reached', 'attained',
                'success', 'milestone', 'breakthrough', 'progress', 'improvement'
            ]
            
            achievement_count = sum(text.count(indicator) for indicator in achievement_indicators)
            if achievement_count > 0:
                achievement_patterns.append({
                    'date': date.isoformat(),
                    'conversation_id': conv.id,
                    'title': conv.auto_title or conv.title,
                    'achievement_score': achievement_count,
                    'summary': conv.summary[:150] + '...' if len(conv.summary) > 150 else conv.summary
                })
        
        # Calculate goal achievement metrics
        total_goals = len(goal_mentions)
        total_achievements = len(achievement_patterns)
        achievement_rate = total_achievements / max(total_goals, 1)
        
        return {
            'goal_mentions': goal_mentions,
            'achievement_patterns': achievement_patterns,
            'total_goals_mentioned': total_goals,
            'total_achievements': total_achievements,
            'achievement_rate': achievement_rate,
            'goal_timeline': [gm['date'] for gm in goal_mentions],
            'achievement_timeline': [ap['date'] for ap in achievement_patterns]
        }
    
    def create_sentiment_timeline_chart(self, sentiment_trends: Dict[str, Any], 
                                      output_path: str = None) -> str:
        """Create an interactive sentiment timeline chart"""
        if not sentiment_trends:
            return ""
        
        # Prepare data
        months = sorted(sentiment_trends.keys())
        sentiments = [sentiment_trends[month]['avg_sentiment'] for month in months]
        conversation_counts = [sentiment_trends[month]['conversation_count'] for month in months]
        
        # Create plotly figure
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Sentiment Trend Over Time', 'Conversation Activity'),
            vertical_spacing=0.1
        )
        
        # Sentiment line chart
        fig.add_trace(
            go.Scatter(
                x=months,
                y=sentiments,
                mode='lines+markers',
                name='Average Sentiment',
                line=dict(color=self.color_palette[0], width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=1)
        
        # Conversation count bar chart
        fig.add_trace(
            go.Bar(
                x=months,
                y=conversation_counts,
                name='Conversations',
                marker_color=self.color_palette[1],
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            title='Emotional Journey Analytics',
            template=self.plotly_template,
            height=600,
            showlegend=False
        )
        
        fig.update_yaxes(title_text="Sentiment Score", row=1, col=1)
        fig.update_yaxes(title_text="Conversation Count", row=2, col=1)
        fig.update_xaxes(title_text="Month", row=2, col=1)
        
        # Save chart
        if not output_path:
            output_path = f"output/sentiment_timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        fig.write_html(output_path)
        
        return output_path
    
    def create_emotional_patterns_chart(self, emotional_patterns: Dict[str, Any],
                                      output_path: str = None) -> str:
        """Create emotional patterns visualization"""
        if not emotional_patterns:
            return ""
        
        # Create subplots
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Overall Emotional Distribution', 'Emotional Trends Over Time'),
            specs=[[{"type": "pie"}, {"type": "scatter"}]]
        )
        
        # Pie chart for overall distribution
        emotions = list(emotional_patterns['overall_emotional_distribution'].keys())
        values = list(emotional_patterns['overall_emotional_distribution'].values())
        
        fig.add_trace(
            go.Pie(
                labels=emotions,
                values=values,
                hole=0.3,
                marker_colors=self.color_palette[:len(emotions)]
            ),
            row=1, col=1
        )
        
        # Timeline chart for emotional trends
        timeline_data = emotional_patterns['emotional_timeline']
        months = sorted(timeline_data.keys())
        
        for i, emotion in enumerate(emotions):
            emotion_values = [timeline_data[month].get(emotion, 0) for month in months]
            fig.add_trace(
                go.Scatter(
                    x=months,
                    y=emotion_values,
                    mode='lines+markers',
                    name=emotion.title(),
                    line=dict(color=self.color_palette[i % len(self.color_palette)])
                ),
                row=1, col=2
            )
        
        # Update layout
        fig.update_layout(
            title='Emotional Patterns Analysis',
            template=self.plotly_template,
            height=500
        )
        
        # Save chart
        if not output_path:
            output_path = f"output/emotional_patterns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        fig.write_html(output_path)
        
        return output_path
    
    def create_growth_metrics_chart(self, growth_metrics: Dict[str, float],
                                   output_path: str = None) -> str:
        """Create growth metrics visualization"""
        if not growth_metrics:
            return ""
        
        # Prepare data
        metrics = list(growth_metrics.keys())
        values = list(growth_metrics.values())
        
        # Create color mapping (positive = green, negative = red)
        colors = [self.color_palette[2] if v >= 0 else self.color_palette[1] for v in values]
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=metrics,
                y=values,
                marker_color=colors,
                text=[f'{v:.1%}' for v in values],
                textposition='auto'
            )
        ])
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        # Update layout
        fig.update_layout(
            title='Personal Growth Metrics',
            xaxis_title='Growth Areas',
            yaxis_title='Growth Rate (%)',
            template=self.plotly_template,
            height=400
        )
        
        # Format y-axis as percentage
        fig.update_yaxes(tickformat='.0%')
        
        # Save chart
        if not output_path:
            output_path = f"output/growth_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        fig.write_html(output_path)
        
        return output_path
    
    def create_tag_analysis_chart(self, top_tags: List[Tuple[str, int]],
                                 output_path: str = None) -> str:
        """Create tag frequency analysis chart"""
        if not top_tags:
            return ""
        
        # Prepare data (top 15 tags)
        tags = [tag for tag, count in top_tags[:15]]
        counts = [count for tag, count in top_tags[:15]]
        
        # Create horizontal bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=counts,
                y=tags,
                orientation='h',
                marker_color=self.color_palette[0],
                text=counts,
                textposition='auto'
            )
        ])
        
        # Update layout
        fig.update_layout(
            title='Most Common Conversation Topics',
            xaxis_title='Frequency',
            yaxis_title='Topics/Tags',
            template=self.plotly_template,
            height=500
        )
        
        # Reverse y-axis to show highest values at top
        fig.update_yaxes(autorange="reversed")
        
        # Save chart
        if not output_path:
            output_path = f"output/tag_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.write_html(output_path)
        
        return output_path
    
    def create_comprehensive_dashboard(self, analytics_data: AnalyticsData,
                                     output_path: str = None) -> str:
        """Create a comprehensive analytics dashboard"""
        if not output_path:
            output_path = f"output/analytics_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Create individual charts
        chart_paths = []
        
        if analytics_data.sentiment_trends:
            sentiment_path = self.create_sentiment_timeline_chart(analytics_data.sentiment_trends)
            chart_paths.append(('sentiment', sentiment_path))
        
        if analytics_data.emotional_patterns:
            emotional_path = self.create_emotional_patterns_chart(analytics_data.emotional_patterns)
            chart_paths.append(('emotional', emotional_path))
        
        if analytics_data.growth_metrics:
            growth_path = self.create_growth_metrics_chart(analytics_data.growth_metrics)
            chart_paths.append(('growth', growth_path))
        
        if analytics_data.top_tags:
            tags_path = self.create_tag_analysis_chart(analytics_data.top_tags)
            chart_paths.append(('tags', tags_path))
        
        # Create comprehensive HTML dashboard
        html_content = self._create_dashboard_html(analytics_data, chart_paths)
        
        # Save dashboard
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _create_dashboard_html(self, analytics_data: AnalyticsData, 
                              chart_paths: List[Tuple[str, str]]) -> str:
        """Create HTML content for the comprehensive dashboard"""
        start_date = analytics_data.date_range[0].strftime('%B %Y')
        end_date = analytics_data.date_range[1].strftime('%B %Y')
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>InsightVault Analytics Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 20px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .chart-section {{
            margin: 40px 0;
            padding: 20px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
        }}
        .chart-title {{
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #2c3e50;
        }}
        iframe {{
            width: 100%;
            height: 600px;
            border: none;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 InsightVault Analytics Dashboard</h1>
            <p>Personal Growth Analytics • {start_date} to {end_date}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{analytics_data.conversation_count}</div>
                <div class="stat-label">Total Conversations</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{analytics_data.total_messages}</div>
                <div class="stat-label">Total Messages</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(analytics_data.top_tags)}</div>
                <div class="stat-label">Unique Topics</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{analytics_data.engagement_stats.get('total_characters', 0):,}</div>
                <div class="stat-label">Characters Written</div>
            </div>
        </div>
"""
        
        # Add charts
        for chart_type, chart_path in chart_paths:
            chart_name = {
                'sentiment': 'Emotional Journey Timeline',
                'emotional': 'Emotional Patterns Analysis', 
                'growth': 'Personal Growth Metrics',
                'tags': 'Conversation Topics Analysis'
            }.get(chart_type, 'Analytics Chart')
            
            html += f"""
        <div class="chart-section">
            <h2 class="chart-title">{chart_name}</h2>
            <iframe src="{os.path.basename(chart_path)}"></iframe>
        </div>
"""
        
        # Add insights summary
        html += f"""
        <div class="chart-section">
            <h2 class="chart-title">Key Insights Summary</h2>
            <div style="line-height: 1.8;">
"""
        
        if analytics_data.growth_metrics:
            html += "<h3>Growth Metrics:</h3><ul>"
            for metric, value in analytics_data.growth_metrics.items():
                direction = "↗️" if value > 0 else "↘️" if value < 0 else "➡️"
                html += f"<li>{direction} <strong>{metric.replace('_', ' ').title()}:</strong> {value:.1%}</li>"
            html += "</ul>"
        
        if analytics_data.top_tags:
            top_3_tags = analytics_data.top_tags[:3]
            html += f"<h3>Most Discussed Topics:</h3><ul>"
            for tag, count in top_3_tags:
                html += f"<li><strong>{tag.title()}:</strong> {count} conversations</li>"
            html += "</ul>"
        
        html += """
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e9ecef; color: #6c757d;">
            <p>Generated by InsightVault Analytics Engine • """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _load_analytics_from_cache(self, cache_key: str) -> Optional[AnalyticsData]:
        """Load cached analytics data"""
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                pass
        return None
    
    def _save_analytics_to_cache(self, cache_key: str, data: AnalyticsData):
        """Save analytics data to cache"""
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Error saving analytics cache: {e}")
    
    def export_analytics_data(self, analytics_data: AnalyticsData, 
                             output_path: str = None, format: str = 'csv') -> str:
        """Export analytics data in various formats"""
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"output/analytics_export_{timestamp}.{format}"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if format == 'csv':
            # Create CSV export
            export_data = {
                'metric': [],
                'value': [],
                'category': []
            }
            
            # Basic stats
            export_data['metric'].extend(['conversation_count', 'total_messages'])
            export_data['value'].extend([analytics_data.conversation_count, analytics_data.total_messages])
            export_data['category'].extend(['basic', 'basic'])
            
            # Tag data
            for tag, count in analytics_data.top_tags:
                export_data['metric'].append(f'tag_{tag}')
                export_data['value'].append(count)
                export_data['category'].append('tags')
            
            # Growth metrics
            for metric, value in analytics_data.growth_metrics.items():
                export_data['metric'].append(metric)
                export_data['value'].append(value)
                export_data['category'].append('growth')
            
            df = pd.DataFrame(export_data)
            df.to_csv(output_path, index=False)
            
        elif format == 'json':
            # Create JSON export
            export_dict = {
                'conversation_count': analytics_data.conversation_count,
                'total_messages': analytics_data.total_messages,
                'date_range': {
                    'start': analytics_data.date_range[0].isoformat(),
                    'end': analytics_data.date_range[1].isoformat()
                },
                'top_tags': analytics_data.top_tags,
                'growth_metrics': analytics_data.growth_metrics,
                'engagement_stats': analytics_data.engagement_stats,
                'exported_at': datetime.now().isoformat()
            }
            
            if analytics_data.sentiment_trends:
                export_dict['sentiment_trends'] = analytics_data.sentiment_trends
            
            if analytics_data.emotional_patterns:
                export_dict['emotional_patterns'] = analytics_data.emotional_patterns
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_dict, f, indent=2, ensure_ascii=False)
        
        return output_path


if __name__ == "__main__":
    # Test the analytics engine
    from chat_parser import ChatParser
    
    parser = ChatParser()
    if parser.load_conversations('data/sample_conversations.json'):
        analytics = AnalyticsEngine()
        
        # Analyze conversations
        analytics_data = analytics.analyze_conversations(parser.conversations)
        
        print(f"Analytics Summary:")
        print(f"- Conversations: {analytics_data.conversation_count}")
        print(f"- Messages: {analytics_data.total_messages}")
        print(f"- Top tags: {analytics_data.top_tags[:5]}")
        
        # Create dashboard
        dashboard_path = analytics.create_comprehensive_dashboard(analytics_data)
        print(f"\nDashboard created: {dashboard_path}")
        
        # Export data
        csv_path = analytics.export_analytics_data(analytics_data, format='csv')
        json_path = analytics.export_analytics_data(analytics_data, format='json')
        print(f"Data exported: {csv_path}, {json_path}")