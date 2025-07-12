"""
Advanced Query Parser for InsightVault AI Assistant
Phase 2: Complex Query Processing

Provides sophisticated parsing for complex, multi-part questions,
temporal range extraction, and comparative analysis capabilities.
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import spacy
from collections import defaultdict


@dataclass
class ComplexQueryIntent:
    """Parsed intent from complex query"""
    primary_topic: str
    secondary_topics: List[str]
    temporal_range: Optional['TemporalRange']
    comparisons: List['Comparison']
    cross_domain_relationships: List[str]
    query_type: str  # 'analysis', 'comparison', 'prediction', 'exploration'
    complexity_level: int  # 1-5 scale
    requires_context: bool


@dataclass
class TemporalRange:
    """Temporal constraints for query"""
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    relative_period: Optional[str]  # 'last_week', 'last_month', 'last_year', etc.
    specific_dates: List[datetime]
    time_granularity: str  # 'day', 'week', 'month', 'year'


@dataclass
class Comparison:
    """Comparative analysis request"""
    primary_subject: str
    secondary_subject: str
    comparison_type: str  # 'vs', 'compared_to', 'versus'
    metrics: List[str]  # what to compare
    context: str


class AdvancedQueryParser:
    """Advanced query parser for complex natural language questions"""
    
    def __init__(self):
        """Initialize the query parser"""
        # Load spaCy model for NLP processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback if spaCy model not available
            self.nlp = None
            print("Warning: spaCy model not available. Some features may be limited.")
        
        # Define patterns for different query types
        self.temporal_patterns = {
            'last_week': r'\b(?:in the )?last week\b',
            'last_month': r'\b(?:in the )?last month\b',
            'last_year': r'\b(?:in the )?last year\b',
            'past_3_months': r'\b(?:in the )?past 3 months?\b',
            'past_6_months': r'\b(?:in the )?past 6 months?\b',
            'this_year': r'\bthis year\b',
            'this_month': r'\bthis month\b',
            'recently': r'\brecently\b',
            'lately': r'\blately\b',
            'over_time': r'\bover time\b',
            'evolution': r'\bevolution\b',
            'progress': r'\bprogress\b'
        }
        
        self.comparison_patterns = {
            'vs': r'\b(?:vs|versus|compared to|in comparison to)\b',
            'versus': r'\bversus\b',
            'compared_to': r'\bcompared to\b',
            'in_comparison': r'\bin comparison to\b',
            'different_from': r'\bdifferent from\b',
            'similar_to': r'\bsimilar to\b'
        }
        
        self.query_type_patterns = {
            'analysis': r'\b(?:what|how|why|when|where)\b.*\b(?:learned|learned about|understood|realized|discovered)\b',
            'comparison': r'\b(?:compare|comparison|versus|vs|different|similar)\b',
            'prediction': r'\b(?:predict|future|will|going to|trend|trajectory)\b',
            'exploration': r'\b(?:explore|investigate|examine|look into|analyze)\b',
            'pattern': r'\b(?:pattern|trend|cycle|repetition|recurring)\b'
        }
        
        # Common topics and their synonyms
        self.topic_synonyms = {
            'relationships': ['relationships', 'relationship', 'friendships', 'romance', 'dating', 'partnership'],
            'boundaries': ['boundaries', 'boundary', 'limits', 'personal space', 'self-care'],
            'productivity': ['productivity', 'efficiency', 'work', 'time management', 'focus'],
            'learning': ['learning', 'education', 'knowledge', 'skills', 'growth'],
            'emotions': ['emotions', 'feelings', 'mood', 'emotional', 'mental health'],
            'career': ['career', 'job', 'work', 'professional', 'business'],
            'health': ['health', 'fitness', 'wellness', 'exercise', 'nutrition'],
            'creativity': ['creativity', 'creative', 'art', 'writing', 'expression'],
            'goals': ['goals', 'objectives', 'targets', 'aspirations', 'ambitions'],
            'communication': ['communication', 'speaking', 'listening', 'conversation', 'dialogue']
        }
    
    def parse_complex_query(self, query: str) -> ComplexQueryIntent:
        """
        Parse complex, multi-part query into structured intent
        
        Args:
            query: Natural language query from user
            
        Returns:
            ComplexQueryIntent with parsed components
        """
        query_lower = query.lower()
        
        # Extract primary and secondary topics
        primary_topic, secondary_topics = self._extract_topics(query_lower)
        
        # Extract temporal range
        temporal_range = self._extract_temporal_range(query_lower)
        
        # Extract comparisons
        comparisons = self._extract_comparisons(query_lower)
        
        # Identify cross-domain relationships
        cross_domain_relationships = self._identify_cross_domain_relationships(query_lower)
        
        # Determine query type
        query_type = self._determine_query_type(query_lower)
        
        # Calculate complexity level
        complexity_level = self._calculate_complexity(query_lower, comparisons, temporal_range)
        
        # Determine if context is required
        requires_context = self._requires_context(query_lower, query_type)
        
        return ComplexQueryIntent(
            primary_topic=primary_topic,
            secondary_topics=secondary_topics,
            temporal_range=temporal_range,
            comparisons=comparisons,
            cross_domain_relationships=cross_domain_relationships,
            query_type=query_type,
            complexity_level=complexity_level,
            requires_context=requires_context
        )
    
    def _extract_topics(self, query: str) -> Tuple[str, List[str]]:
        """Extract primary and secondary topics from query"""
        topics = []
        
        # Check for explicit topic mentions
        for topic, synonyms in self.topic_synonyms.items():
            for synonym in synonyms:
                if synonym in query:
                    topics.append(topic)
                    break
        
        # Use spaCy for additional topic extraction if available
        if self.nlp:
            doc = self.nlp(query)
            # Extract noun phrases and named entities
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower()
                if len(chunk_text) > 3 and chunk_text not in ['the', 'and', 'or', 'but']:
                    topics.append(chunk_text)
        
        # Remove duplicates and sort by frequency
        topic_counts = defaultdict(int)
        for topic in topics:
            topic_counts[topic] += 1
        
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_topics:
            primary_topic = sorted_topics[0][0]
            secondary_topics = [topic for topic, _ in sorted_topics[1:3]]  # Top 2 secondary topics
        else:
            primary_topic = "general"
            secondary_topics = []
        
        return primary_topic, secondary_topics
    
    def _extract_temporal_range(self, query: str) -> Optional[TemporalRange]:
        """Extract temporal constraints from query"""
        
        # Check for relative time periods
        relative_period = None
        for period, pattern in self.temporal_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                relative_period = period
                break
        
        # Check for specific dates
        date_patterns = [
            r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b',  # MM/DD/YYYY
            r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b',  # YYYY-MM-DD
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})\b'
        ]
        
        specific_dates = []
        for pattern in date_patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                try:
                    if '/' in match.group():
                        month, day, year = match.groups()
                        date = datetime(int(year), int(month), int(day))
                    elif '-' in match.group():
                        year, month, day = match.groups()
                        date = datetime(int(year), int(month), int(day))
                    else:
                        month_name, year = match.groups()
                        month_num = {
                            'january': 1, 'february': 2, 'march': 3, 'april': 4,
                            'may': 5, 'june': 6, 'july': 7, 'august': 8,
                            'september': 9, 'october': 10, 'november': 11, 'december': 12
                        }[month_name.lower()]
                        date = datetime(int(year), month_num, 1)
                    specific_dates.append(date)
                except ValueError:
                    continue
        
        # Determine time granularity
        time_granularity = 'month'  # default
        if 'day' in query or 'daily' in query:
            time_granularity = 'day'
        elif 'week' in query or 'weekly' in query:
            time_granularity = 'week'
        elif 'year' in query or 'yearly' in query:
            time_granularity = 'year'
        
        # Calculate start and end dates for relative periods
        start_date = None
        end_date = None
        
        if relative_period:
            end_date = datetime.now()
            if relative_period == 'last_week':
                start_date = end_date - timedelta(days=7)
            elif relative_period == 'last_month':
                start_date = end_date - timedelta(days=30)
            elif relative_period == 'last_year':
                start_date = end_date - timedelta(days=365)
            elif relative_period == 'past_3_months':
                start_date = end_date - timedelta(days=90)
            elif relative_period == 'past_6_months':
                start_date = end_date - timedelta(days=180)
            elif relative_period == 'this_year':
                start_date = datetime(end_date.year, 1, 1)
            elif relative_period == 'this_month':
                start_date = datetime(end_date.year, end_date.month, 1)
        
        if relative_period or specific_dates:
            return TemporalRange(
                start_date=start_date,
                end_date=end_date,
                relative_period=relative_period,
                specific_dates=specific_dates,
                time_granularity=time_granularity
            )
        
        return None
    
    def _extract_comparisons(self, query: str) -> List[Comparison]:
        """Extract comparative analysis requests from query"""
        comparisons = []
        
        # Find comparison patterns
        for comp_type, pattern in self.comparison_patterns.items():
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                # Extract text before and after comparison
                before_text = query[:match.start()].strip()
                after_text = query[match.end():].strip()
                
                # Extract subjects
                primary_subject = self._extract_subject(before_text)
                secondary_subject = self._extract_subject(after_text)
                
                if primary_subject and secondary_subject:
                    comparison = Comparison(
                        primary_subject=primary_subject,
                        secondary_subject=secondary_subject,
                        comparison_type=comp_type,
                        metrics=self._extract_comparison_metrics(query),
                        context=query
                    )
                    comparisons.append(comparison)
        
        return comparisons
    
    def _extract_subject(self, text: str) -> Optional[str]:
        """Extract subject from text fragment"""
        if not text:
            return None
        
        # Use spaCy for better subject extraction if available
        if self.nlp:
            doc = self.nlp(text)
            # Look for noun phrases or named entities
            for chunk in doc.noun_chunks:
                if len(chunk.text.strip()) > 2:
                    return chunk.text.strip()
        
        # Fallback: extract last meaningful phrase
        words = text.split()
        if len(words) >= 2:
            return ' '.join(words[-2:])
        elif len(words) == 1:
            return words[0]
        
        return None
    
    def _extract_comparison_metrics(self, query: str) -> List[str]:
        """Extract what metrics to compare"""
        metrics = []
        
        # Common comparison metrics
        metric_keywords = [
            'understanding', 'learning', 'growth', 'progress', 'development',
            'patterns', 'trends', 'insights', 'realizations', 'breakthroughs',
            'challenges', 'successes', 'failures', 'improvements'
        ]
        
        for metric in metric_keywords:
            if metric in query:
                metrics.append(metric)
        
        return metrics
    
    def _identify_cross_domain_relationships(self, query: str) -> List[str]:
        """Identify relationships between different life domains"""
        relationships = []
        
        # Check for cross-domain language
        cross_domain_indicators = [
            'impact on', 'influence on', 'affect', 'relate to', 'connect to',
            'spill over', 'carry over', 'transfer', 'apply to'
        ]
        
        for indicator in cross_domain_indicators:
            if indicator in query:
                relationships.append(indicator)
        
        return relationships
    
    def _determine_query_type(self, query: str) -> str:
        """Determine the type of query being asked"""
        
        for query_type, pattern in self.query_type_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                return query_type
        
        # Default to analysis if no specific type detected
        return 'analysis'
    
    def _calculate_complexity(self, query: str, comparisons: List[Comparison], 
                            temporal_range: Optional[TemporalRange]) -> int:
        """Calculate complexity level of query (1-5 scale)"""
        complexity = 1
        
        # Base complexity
        if len(query.split()) > 20:
            complexity += 1
        
        # Add complexity for comparisons
        if comparisons:
            complexity += 1
        
        # Add complexity for temporal constraints
        if temporal_range:
            complexity += 1
        
        # Add complexity for multiple topics
        if len(query.split()) > 30:
            complexity += 1
        
        # Add complexity for cross-domain relationships
        if 'impact' in query or 'influence' in query or 'relate' in query:
            complexity += 1
        
        return min(complexity, 5)
    
    def _requires_context(self, query: str, query_type: str) -> bool:
        """Determine if query requires additional context"""
        
        # Queries that typically need context
        context_indicators = [
            'compared to', 'versus', 'different from', 'similar to',
            'influence', 'impact', 'relate', 'connect', 'pattern',
            'trend', 'evolution', 'progress', 'development'
        ]
        
        for indicator in context_indicators:
            if indicator in query:
                return True
        
        # Complex query types need context
        if query_type in ['comparison', 'prediction']:
            return True
        
        return False
    
    def extract_temporal_range(self, query: str) -> Optional[TemporalRange]:
        """Extract temporal range from query (public interface)"""
        return self._extract_temporal_range(query.lower())
    
    def detect_comparative_elements(self, query: str) -> List[Comparison]:
        """Detect comparative elements in query (public interface)"""
        return self._extract_comparisons(query.lower())
    
    def suggest_related_queries(self, query: str) -> List[str]:
        """Generate related query suggestions"""
        suggestions = []
        
        # Parse the original query
        intent = self.parse_complex_query(query)
        
        # Generate suggestions based on query type
        if intent.query_type == 'analysis':
            suggestions.extend([
                f"How has my understanding of {intent.primary_topic} evolved over time?",
                f"What patterns do you see in my {intent.primary_topic} conversations?",
                f"When did I have breakthrough moments about {intent.primary_topic}?"
            ])
        
        elif intent.query_type == 'comparison':
            for comparison in intent.comparisons:
                suggestions.extend([
                    f"Compare my learning patterns in {comparison.primary_subject} vs {comparison.secondary_subject}",
                    f"How does my approach to {comparison.primary_subject} differ from {comparison.secondary_subject}?",
                    f"What insights can I apply from {comparison.primary_subject} to {comparison.secondary_subject}?"
                ])
        
        elif intent.query_type == 'prediction':
            suggestions.extend([
                f"Based on my {intent.primary_topic} patterns, what should I focus on next?",
                f"What potential breakthroughs might I have about {intent.primary_topic}?",
                f"How can I accelerate my growth in {intent.primary_topic}?"
            ])
        
        # Add general suggestions
        suggestions.extend([
            "What have I learned about my personal growth journey?",
            "How has my self-awareness evolved over time?",
            "What are my most significant breakthrough moments?",
            "What patterns do you see in my learning style?"
        ])
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def get_query_statistics(self, query: str) -> Dict[str, Any]:
        """Get detailed statistics about the query"""
        intent = self.parse_complex_query(query)
        
        return {
            'word_count': len(query.split()),
            'complexity_level': intent.complexity_level,
            'query_type': intent.query_type,
            'topics_count': 1 + len(intent.secondary_topics),
            'comparisons_count': len(intent.comparisons),
            'has_temporal_constraints': intent.temporal_range is not None,
            'requires_context': intent.requires_context,
            'cross_domain_relationships': len(intent.cross_domain_relationships)
        }


def main():
    """Test the advanced query parser"""
    parser = AdvancedQueryParser()
    
    # Test queries
    test_queries = [
        "What have I learned about my relationships and boundaries?",
        "How has my understanding of productivity evolved compared to my relationship insights?",
        "What patterns do you see in my emotional responses to stress over the past year?",
        "When did I have breakthrough moments about self-care, and what triggered them?",
        "Compare my learning patterns in relationships vs. career development"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        intent = parser.parse_complex_query(query)
        print(f"Primary Topic: {intent.primary_topic}")
        print(f"Secondary Topics: {intent.secondary_topics}")
        print(f"Query Type: {intent.query_type}")
        print(f"Complexity Level: {intent.complexity_level}")
        print(f"Comparisons: {len(intent.comparisons)}")
        print(f"Temporal Range: {intent.temporal_range is not None}")
        
        suggestions = parser.suggest_related_queries(query)
        print(f"Suggestions: {suggestions[:2]}")


if __name__ == '__main__':
    main() 