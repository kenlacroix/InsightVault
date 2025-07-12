"""
Predictive Analytics Engine for InsightVault AI Assistant
Phase 2: Trend Analysis and Future Predictions

Provides advanced analytics for predicting growth trajectories,
identifying potential breakthrough moments, and detecting risks and opportunities.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import json
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')


@dataclass
class TrendAnalysis:
    """Analysis of trends over time"""
    trend_direction: str  # 'increasing', 'decreasing', 'stable', 'fluctuating'
    trend_strength: float  # 0.0 to 1.0
    trend_confidence: float  # 0.0 to 1.0
    key_periods: List[Dict[str, Any]]
    seasonal_patterns: List[Dict[str, Any]]
    acceleration_points: List[datetime]
    plateau_periods: List[Dict[str, Any]]


@dataclass
class GrowthPrediction:
    """Prediction of future growth patterns"""
    predicted_trajectory: str  # 'accelerating', 'steady', 'plateauing', 'declining'
    confidence_score: float  # 0.0 to 1.0
    time_horizon: str  # 'short_term', 'medium_term', 'long_term'
    key_milestones: List[Dict[str, Any]]
    potential_obstacles: List[str]
    recommended_focus_areas: List[str]
    growth_rate_estimate: float  # percentage per month


@dataclass
class PredictedBreakthrough:
    """Prediction of potential breakthrough moments"""
    topic: str
    likelihood: float  # 0.0 to 1.0
    estimated_timing: datetime
    trigger_factors: List[str]
    impact_score: float  # 0.0 to 1.0
    preparation_actions: List[str]


@dataclass
class RiskOpportunityAnalysis:
    """Analysis of risks and opportunities"""
    risks: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]
    risk_mitigation_strategies: List[str]
    opportunity_leverage_strategies: List[str]
    overall_risk_level: str  # 'low', 'medium', 'high'
    overall_opportunity_level: str  # 'low', 'medium', 'high'


class PredictiveAnalytics:
    """Predictive analytics engine for personal growth insights"""
    
    def __init__(self, min_data_points: int = 5):
        """
        Initialize predictive analytics engine
        
        Args:
            min_data_points: Minimum data points required for analysis
        """
        self.min_data_points = min_data_points
        self.scaler = StandardScaler()
        
        # Growth indicators and their weights
        self.growth_indicators = {
            'reflection_depth': 0.3,
            'goal_orientation': 0.25,
            'learning_patterns': 0.2,
            'emotional_awareness': 0.15,
            'action_taking': 0.1
        }
        
        # Breakthrough indicators
        self.breakthrough_indicators = [
            'aha_moments', 'pattern_recognition', 'paradigm_shifts',
            'emotional_breakthroughs', 'behavioral_changes'
        ]
    
    def analyze_trends(self, conversations: List[Any]) -> TrendAnalysis:
        """
        Analyze temporal patterns and trends in conversations
        
        Args:
            conversations: List of conversation objects with timestamps
            
        Returns:
            TrendAnalysis with trend information
        """
        if len(conversations) < self.min_data_points:
            return self._create_default_trend_analysis()
        
        # Convert conversations to time series data
        time_series_data = self._create_time_series(conversations)
        
        # Analyze trend direction and strength
        trend_direction, trend_strength = self._calculate_trend_direction(time_series_data)
        
        # Calculate trend confidence
        trend_confidence = self._calculate_trend_confidence(time_series_data)
        
        # Identify key periods
        key_periods = self._identify_key_periods(time_series_data)
        
        # Detect seasonal patterns
        seasonal_patterns = self._detect_seasonal_patterns(time_series_data)
        
        # Find acceleration points
        acceleration_points = self._find_acceleration_points(time_series_data)
        
        # Identify plateau periods
        plateau_periods = self._identify_plateau_periods(time_series_data)
        
        return TrendAnalysis(
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            trend_confidence=trend_confidence,
            key_periods=key_periods,
            seasonal_patterns=seasonal_patterns,
            acceleration_points=acceleration_points,
            plateau_periods=plateau_periods
        )
    
    def predict_growth_trajectory(self, historical_data: Dict[str, Any]) -> GrowthPrediction:
        """
        Predict future growth patterns based on historical data
        
        Args:
            historical_data: Dictionary containing historical analytics data
            
        Returns:
            GrowthPrediction with future trajectory information
        """
        if not historical_data or len(historical_data.get('conversations', [])) < self.min_data_points:
            return self._create_default_growth_prediction()
        
        # Extract growth metrics
        growth_metrics = historical_data.get('growth_metrics', {})
        sentiment_trends = historical_data.get('sentiment_trends', {})
        engagement_stats = historical_data.get('engagement_stats', {})
        
        # Calculate overall growth score
        growth_score = self._calculate_growth_score(growth_metrics, sentiment_trends, engagement_stats)
        
        # Predict trajectory
        predicted_trajectory = self._predict_trajectory(growth_score, historical_data)
        
        # Estimate confidence
        confidence_score = self._estimate_prediction_confidence(historical_data)
        
        # Determine time horizon
        time_horizon = self._determine_time_horizon(historical_data)
        
        # Generate key milestones
        key_milestones = self._generate_key_milestones(predicted_trajectory, growth_score)
        
        # Identify potential obstacles
        potential_obstacles = self._identify_potential_obstacles(historical_data)
        
        # Recommend focus areas
        recommended_focus_areas = self._recommend_focus_areas(historical_data, predicted_trajectory)
        
        # Estimate growth rate
        growth_rate_estimate = self._estimate_growth_rate(growth_score, predicted_trajectory)
        
        return GrowthPrediction(
            predicted_trajectory=predicted_trajectory,
            confidence_score=confidence_score,
            time_horizon=time_horizon,
            key_milestones=key_milestones,
            potential_obstacles=potential_obstacles,
            recommended_focus_areas=recommended_focus_areas,
            growth_rate_estimate=growth_rate_estimate
        )
    
    def identify_potential_breakthroughs(self, patterns: Dict[str, Any]) -> List[PredictedBreakthrough]:
        """
        Identify potential breakthrough moments based on patterns
        
        Args:
            patterns: Dictionary containing conversation patterns and analytics
            
        Returns:
            List of PredictedBreakthrough objects
        """
        potential_breakthroughs = []
        
        # Analyze conversation patterns for breakthrough indicators
        breakthrough_indicators = self._analyze_breakthrough_indicators(patterns)
        
        # Identify topics with high breakthrough potential
        high_potential_topics = self._identify_high_potential_topics(patterns)
        
        # Generate predictions for each high-potential topic
        for topic in high_potential_topics:
            breakthrough = self._predict_breakthrough_for_topic(topic, patterns, breakthrough_indicators)
            if breakthrough and breakthrough.likelihood > 0.3:  # Only include likely breakthroughs
                potential_breakthroughs.append(breakthrough)
        
        # Sort by likelihood and impact
        potential_breakthroughs.sort(key=lambda x: x.likelihood * x.impact_score, reverse=True)
        
        return potential_breakthroughs[:5]  # Return top 5 predictions
    
    def detect_risks_opportunities(self, analysis: Dict[str, Any]) -> RiskOpportunityAnalysis:
        """
        Detect risks and opportunities based on analysis
        
        Args:
            analysis: Dictionary containing comprehensive analysis data
            
        Returns:
            RiskOpportunityAnalysis with risks and opportunities
        """
        # Analyze risks
        risks = self._analyze_risks(analysis)
        
        # Analyze opportunities
        opportunities = self._analyze_opportunities(analysis)
        
        # Generate mitigation strategies
        risk_mitigation_strategies = self._generate_risk_mitigation_strategies(risks)
        
        # Generate leverage strategies
        opportunity_leverage_strategies = self._generate_opportunity_leverage_strategies(opportunities)
        
        # Calculate overall risk and opportunity levels
        overall_risk_level = self._calculate_overall_risk_level(risks)
        overall_opportunity_level = self._calculate_overall_opportunity_level(opportunities)
        
        return RiskOpportunityAnalysis(
            risks=risks,
            opportunities=opportunities,
            risk_mitigation_strategies=risk_mitigation_strategies,
            opportunity_leverage_strategies=opportunity_leverage_strategies,
            overall_risk_level=overall_risk_level,
            overall_opportunity_level=overall_opportunity_level
        )
    
    def _create_time_series(self, conversations: List[Any]) -> pd.DataFrame:
        """Create time series data from conversations"""
        data = []
        
        for conv in conversations:
            # Extract features for each conversation
            features = {
                'date': conv.create_date,
                'reflection_depth': self._calculate_reflection_depth(conv),
                'goal_orientation': self._calculate_goal_orientation(conv),
                'learning_patterns': self._calculate_learning_patterns(conv),
                'emotional_awareness': self._calculate_emotional_awareness(conv),
                'action_taking': self._calculate_action_taking(conv)
            }
            data.append(features)
        
        df = pd.DataFrame(data)
        df = df.sort_values('date')
        df = df.set_index('date')
        
        return df
    
    def _calculate_reflection_depth(self, conversation: Any) -> float:
        """Calculate reflection depth score for a conversation"""
        # Simple heuristic based on conversation length and content
        text_length = len(conversation.get_full_text())
        message_count = len(conversation.messages)
        
        # Normalize scores
        length_score = min(text_length / 1000, 1.0)  # Cap at 1000 characters
        message_score = min(message_count / 20, 1.0)  # Cap at 20 messages
        
        return (length_score + message_score) / 2
    
    def _calculate_goal_orientation(self, conversation: Any) -> float:
        """Calculate goal orientation score for a conversation"""
        text = conversation.get_full_text().lower()
        
        goal_keywords = ['goal', 'objective', 'target', 'aim', 'plan', 'strategy', 'achieve', 'accomplish']
        goal_count = sum(1 for keyword in goal_keywords if keyword in text)
        
        return min(goal_count / 5, 1.0)  # Normalize to 0-1
    
    def _calculate_learning_patterns(self, conversation: Any) -> float:
        """Calculate learning pattern score for a conversation"""
        text = conversation.get_full_text().lower()
        
        learning_keywords = ['learn', 'understand', 'realize', 'discover', 'figure out', 'insight', 'lesson']
        learning_count = sum(1 for keyword in learning_keywords if keyword in text)
        
        return min(learning_count / 5, 1.0)  # Normalize to 0-1
    
    def _calculate_emotional_awareness(self, conversation: Any) -> float:
        """Calculate emotional awareness score for a conversation"""
        text = conversation.get_full_text().lower()
        
        emotion_keywords = ['feel', 'emotion', 'mood', 'anxiety', 'stress', 'happy', 'sad', 'frustrated', 'excited']
        emotion_count = sum(1 for keyword in emotion_keywords if keyword in text)
        
        return min(emotion_count / 5, 1.0)  # Normalize to 0-1
    
    def _calculate_action_taking(self, conversation: Any) -> float:
        """Calculate action taking score for a conversation"""
        text = conversation.get_full_text().lower()
        
        action_keywords = ['do', 'action', 'implement', 'try', 'practice', 'start', 'begin', 'change']
        action_count = sum(1 for keyword in action_keywords if keyword in text)
        
        return min(action_count / 5, 1.0)  # Normalize to 0-1
    
    def _calculate_trend_direction(self, time_series: pd.DataFrame) -> Tuple[str, float]:
        """Calculate trend direction and strength"""
        if len(time_series) < 2:
            return 'stable', 0.0
        
        # Calculate overall growth score
        growth_scores = []
        for _, row in time_series.iterrows():
            score = sum(row[col] * weight for col, weight in self.growth_indicators.items())
            growth_scores.append(score)
        
        # Fit linear regression
        X = np.arange(len(growth_scores)).reshape(-1, 1)
        y = np.array(growth_scores)
        
        try:
            model = LinearRegression()
            model.fit(X, y)
            slope = model.coef_[0]
            
            # Determine direction
            if slope > 0.01:
                direction = 'increasing'
            elif slope < -0.01:
                direction = 'decreasing'
            else:
                direction = 'stable'
            
            # Calculate strength (normalized slope)
            strength = min(abs(slope) * 10, 1.0)
            
            return direction, strength
            
        except Exception:
            return 'stable', 0.0
    
    def _calculate_trend_confidence(self, time_series: pd.DataFrame) -> float:
        """Calculate confidence in trend analysis"""
        if len(time_series) < 3:
            return 0.3
        
        # Calculate R-squared for trend fit
        growth_scores = []
        for _, row in time_series.iterrows():
            score = sum(row[col] * weight for col, weight in self.growth_indicators.items())
            growth_scores.append(score)
        
        X = np.arange(len(growth_scores)).reshape(-1, 1)
        y = np.array(growth_scores)
        
        try:
            model = LinearRegression()
            model.fit(X, y)
            r_squared = model.score(X, y)
            return min(r_squared, 1.0)
        except Exception:
            return 0.5
    
    def _identify_key_periods(self, time_series: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify key periods in the time series"""
        key_periods = []
        
        if len(time_series) < 3:
            return key_periods
        
        # Find periods with high growth
        growth_scores = []
        for _, row in time_series.iterrows():
            score = sum(row[col] * weight for col, weight in self.growth_indicators.items())
            growth_scores.append(score)
        
        # Find peaks
        for i in range(1, len(growth_scores) - 1):
            if growth_scores[i] > growth_scores[i-1] and growth_scores[i] > growth_scores[i+1]:
                key_periods.append({
                    'type': 'peak',
                    'date': time_series.index[i],
                    'score': growth_scores[i],
                    'description': 'High growth period'
                })
        
        return key_periods[:3]  # Return top 3 key periods
    
    def _detect_seasonal_patterns(self, time_series: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect seasonal patterns in the data"""
        # Simple seasonal pattern detection
        patterns = []
        
        if len(time_series) < 12:  # Need at least 12 data points for seasonal analysis
            return patterns
        
        # Group by month and calculate average scores
        monthly_scores = defaultdict(list)
        for date, row in time_series.iterrows():
            month = date.month
            score = sum(row[col] * weight for col, weight in self.growth_indicators.items())
            monthly_scores[month].append(score)
        
        # Find months with consistently high/low scores
        for month, scores in monthly_scores.items():
            if len(scores) >= 2:
                avg_score = np.mean(scores)
                if avg_score > 0.7:
                    patterns.append({
                        'type': 'high_performance',
                        'month': month,
                        'average_score': avg_score,
                        'description': f'Consistently high performance in month {month}'
                    })
        
        return patterns
    
    def _find_acceleration_points(self, time_series: pd.DataFrame) -> List[datetime]:
        """Find points where growth accelerates"""
        acceleration_points = []
        
        if len(time_series) < 3:
            return acceleration_points
        
        growth_scores = []
        for _, row in time_series.iterrows():
            score = sum(row[col] * weight for col, weight in self.growth_indicators.items())
            growth_scores.append(score)
        
        # Find acceleration points (increasing rate of change)
        for i in range(2, len(growth_scores)):
            change1 = growth_scores[i-1] - growth_scores[i-2]
            change2 = growth_scores[i] - growth_scores[i-1]
            
            if change2 > change1 and change2 > 0.1:  # Significant acceleration
                acceleration_points.append(time_series.index[i])
        
        return acceleration_points
    
    def _identify_plateau_periods(self, time_series: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify periods where growth plateaus"""
        plateau_periods = []
        
        if len(time_series) < 3:
            return plateau_periods
        
        growth_scores = []
        for _, row in time_series.iterrows():
            score = sum(row[col] * weight for col, weight in self.growth_indicators.items())
            growth_scores.append(score)
        
        # Find plateau periods (little change over time)
        for i in range(2, len(growth_scores)):
            change = abs(growth_scores[i] - growth_scores[i-1])
            if change < 0.05:  # Small change indicates plateau
                plateau_periods.append({
                    'start_date': time_series.index[i-1],
                    'end_date': time_series.index[i],
                    'duration_days': (time_series.index[i] - time_series.index[i-1]).days,
                    'description': 'Growth plateau period'
                })
        
        return plateau_periods
    
    def _calculate_growth_score(self, growth_metrics: Dict, sentiment_trends: Dict, 
                               engagement_stats: Dict) -> float:
        """Calculate overall growth score from various metrics"""
        score = 0.0
        total_weight = 0.0
        
        # Growth metrics (40% weight)
        if growth_metrics:
            positive_metrics = sum(1 for v in growth_metrics.values() if v > 0)
            total_metrics = len(growth_metrics)
            if total_metrics > 0:
                score += 0.4 * (positive_metrics / total_metrics)
                total_weight += 0.4
        
        # Sentiment trends (30% weight)
        if sentiment_trends:
            positive_sentiment = sum(1 for v in sentiment_trends.values() 
                                   if isinstance(v, dict) and v.get('avg_sentiment', 0) > 0)
            total_periods = len(sentiment_trends)
            if total_periods > 0:
                score += 0.3 * (positive_sentiment / total_periods)
                total_weight += 0.3
        
        # Engagement stats (30% weight)
        if engagement_stats:
            # Simple engagement score based on conversation frequency
            conversation_frequency = engagement_stats.get('conversation_frequency', 0)
            score += 0.3 * min(conversation_frequency / 10, 1.0)  # Normalize to 0-1
            total_weight += 0.3
        
        return score / total_weight if total_weight > 0 else 0.5
    
    def _predict_trajectory(self, growth_score: float, historical_data: Dict) -> str:
        """Predict future growth trajectory"""
        if growth_score > 0.7:
            return 'accelerating'
        elif growth_score > 0.5:
            return 'steady'
        elif growth_score > 0.3:
            return 'plateauing'
        else:
            return 'declining'
    
    def _estimate_prediction_confidence(self, historical_data: Dict) -> float:
        """Estimate confidence in prediction"""
        # Base confidence on data quality and quantity
        conversations = historical_data.get('conversations', [])
        data_points = len(conversations)
        
        if data_points >= 20:
            return 0.9
        elif data_points >= 10:
            return 0.7
        elif data_points >= 5:
            return 0.5
        else:
            return 0.3
    
    def _determine_time_horizon(self, historical_data: Dict) -> str:
        """Determine appropriate time horizon for prediction"""
        conversations = historical_data.get('conversations', [])
        data_points = len(conversations)
        
        if data_points >= 15:
            return 'long_term'
        elif data_points >= 8:
            return 'medium_term'
        else:
            return 'short_term'
    
    def _generate_key_milestones(self, trajectory: str, growth_score: float) -> List[Dict[str, Any]]:
        """Generate key milestones based on predicted trajectory"""
        milestones = []
        
        if trajectory == 'accelerating':
            milestones = [
                {'timeline': '1 month', 'milestone': 'Significant breakthrough in primary focus area'},
                {'timeline': '3 months', 'milestone': 'Establishment of new growth habits'},
                {'timeline': '6 months', 'milestone': 'Major transformation in approach to personal development'}
            ]
        elif trajectory == 'steady':
            milestones = [
                {'timeline': '1 month', 'milestone': 'Consolidation of current learning'},
                {'timeline': '3 months', 'milestone': 'Application of insights to new areas'},
                {'timeline': '6 months', 'milestone': 'Integration of growth patterns'}
            ]
        else:
            milestones = [
                {'timeline': '1 month', 'milestone': 'Reassessment of current approach'},
                {'timeline': '3 months', 'milestone': 'Identification of new growth opportunities'},
                {'timeline': '6 months', 'milestone': 'Implementation of new strategies'}
            ]
        
        return milestones
    
    def _identify_potential_obstacles(self, historical_data: Dict) -> List[str]:
        """Identify potential obstacles to growth"""
        obstacles = []
        
        # Analyze patterns for potential obstacles
        if historical_data.get('growth_metrics', {}):
            negative_metrics = [k for k, v in historical_data['growth_metrics'].items() if v < 0]
            if negative_metrics:
                obstacles.append(f"Challenges in {', '.join(negative_metrics)}")
        
        # Add common obstacles based on data patterns
        obstacles.extend([
            "Potential burnout from high engagement",
            "Risk of plateauing without new challenges",
            "Need for balance between growth and rest"
        ])
        
        return obstacles[:3]  # Return top 3 obstacles
    
    def _recommend_focus_areas(self, historical_data: Dict, trajectory: str) -> List[str]:
        """Recommend focus areas based on trajectory"""
        focus_areas = []
        
        if trajectory == 'accelerating':
            focus_areas = [
                "Maintain momentum while avoiding burnout",
                "Deepen insights in current focus areas",
                "Share learnings with others"
            ]
        elif trajectory == 'steady':
            focus_areas = [
                "Explore new areas for growth",
                "Challenge current assumptions",
                "Seek feedback from trusted sources"
            ]
        else:
            focus_areas = [
                "Reassess current approach and goals",
                "Identify new sources of motivation",
                "Consider seeking external support or guidance"
            ]
        
        return focus_areas
    
    def _estimate_growth_rate(self, growth_score: float, trajectory: str) -> float:
        """Estimate monthly growth rate percentage"""
        base_rate = growth_score * 10  # Base rate 0-10%
        
        if trajectory == 'accelerating':
            return base_rate * 1.5
        elif trajectory == 'steady':
            return base_rate
        elif trajectory == 'plateauing':
            return base_rate * 0.5
        else:
            return base_rate * 0.2
    
    def _analyze_breakthrough_indicators(self, patterns: Dict) -> Dict[str, float]:
        """Analyze patterns for breakthrough indicators"""
        indicators = {}
        
        # Analyze conversation patterns for breakthrough indicators
        for indicator in self.breakthrough_indicators:
            # Simple heuristic scoring
            if indicator in patterns:
                indicators[indicator] = min(patterns[indicator] / 10, 1.0)
            else:
                indicators[indicator] = 0.0
        
        return indicators
    
    def _identify_high_potential_topics(self, patterns: Dict) -> List[str]:
        """Identify topics with high breakthrough potential"""
        high_potential_topics = []
        
        # Analyze top themes for breakthrough potential
        top_themes = patterns.get('top_tags', [])
        
        for theme, count in top_themes[:5]:  # Top 5 themes
            # Simple heuristic: themes with moderate to high frequency have breakthrough potential
            if 3 <= count <= 15:  # Sweet spot for breakthroughs
                high_potential_topics.append(theme)
        
        return high_potential_topics
    
    def _predict_breakthrough_for_topic(self, topic: str, patterns: Dict, 
                                      indicators: Dict) -> Optional[PredictedBreakthrough]:
        """Predict breakthrough for a specific topic"""
        
        # Calculate likelihood based on indicators
        likelihood = np.mean(list(indicators.values()))
        
        # Estimate timing (3-6 months from now)
        estimated_timing = datetime.now() + timedelta(days=90 + np.random.randint(0, 90))
        
        # Identify trigger factors
        trigger_factors = [
            "Continued reflection on this topic",
            "New experiences that challenge current understanding",
            "Integration of insights from other areas"
        ]
        
        # Calculate impact score
        impact_score = min(likelihood * 1.2, 1.0)
        
        # Generate preparation actions
        preparation_actions = [
            f"Continue exploring {topic} through conversations",
            f"Seek diverse perspectives on {topic}",
            f"Apply current insights about {topic} to daily life"
        ]
        
        return PredictedBreakthrough(
            topic=topic,
            likelihood=likelihood,
            estimated_timing=estimated_timing,
            trigger_factors=trigger_factors,
            impact_score=impact_score,
            preparation_actions=preparation_actions
        )
    
    def _analyze_risks(self, analysis: Dict) -> List[Dict[str, Any]]:
        """Analyze potential risks"""
        risks = []
        
        # Identify risks based on patterns
        if analysis.get('growth_metrics'):
            negative_growth = [k for k, v in analysis['growth_metrics'].items() if v < -0.2]
            if negative_growth:
                risks.append({
                    'type': 'growth_decline',
                    'description': f'Declining growth in {", ".join(negative_growth)}',
                    'severity': 'medium',
                    'probability': 0.6
                })
        
        # Add common risks
        risks.extend([
            {
                'type': 'burnout',
                'description': 'Risk of burnout from high engagement',
                'severity': 'high',
                'probability': 0.4
            },
            {
                'type': 'plateau',
                'description': 'Risk of growth plateauing',
                'severity': 'medium',
                'probability': 0.5
            }
        ])
        
        return risks
    
    def _analyze_opportunities(self, analysis: Dict) -> List[Dict[str, Any]]:
        """Analyze potential opportunities"""
        opportunities = []
        
        # Identify opportunities based on patterns
        if analysis.get('growth_metrics'):
            strong_growth = [k for k, v in analysis['growth_metrics'].items() if v > 0.3]
            if strong_growth:
                opportunities.append({
                    'type': 'growth_acceleration',
                    'description': f'Opportunity to accelerate growth in {", ".join(strong_growth)}',
                    'impact': 'high',
                    'probability': 0.7
                })
        
        # Add common opportunities
        opportunities.extend([
            {
                'type': 'knowledge_sharing',
                'description': 'Opportunity to share insights with others',
                'impact': 'medium',
                'probability': 0.8
            },
            {
                'type': 'new_areas',
                'description': 'Opportunity to explore new growth areas',
                'impact': 'high',
                'probability': 0.6
            }
        ])
        
        return opportunities
    
    def _generate_risk_mitigation_strategies(self, risks: List[Dict]) -> List[str]:
        """Generate strategies to mitigate risks"""
        strategies = []
        
        for risk in risks:
            if risk['type'] == 'burnout':
                strategies.append("Implement regular rest and recovery periods")
            elif risk['type'] == 'plateau':
                strategies.append("Seek new challenges and learning opportunities")
            elif risk['type'] == 'growth_decline':
                strategies.append("Reassess current approach and identify new strategies")
        
        return strategies
    
    def _generate_opportunity_leverage_strategies(self, opportunities: List[Dict]) -> List[str]:
        """Generate strategies to leverage opportunities"""
        strategies = []
        
        for opportunity in opportunities:
            if opportunity['type'] == 'growth_acceleration':
                strategies.append("Double down on successful growth areas")
            elif opportunity['type'] == 'knowledge_sharing':
                strategies.append("Document and share insights with others")
            elif opportunity['type'] == 'new_areas':
                strategies.append("Explore new domains for personal development")
        
        return strategies
    
    def _calculate_overall_risk_level(self, risks: List[Dict]) -> str:
        """Calculate overall risk level"""
        if not risks:
            return 'low'
        
        high_risk_count = sum(1 for risk in risks if risk['severity'] == 'high')
        total_risks = len(risks)
        
        if high_risk_count / total_risks > 0.5:
            return 'high'
        elif high_risk_count / total_risks > 0.2:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_overall_opportunity_level(self, opportunities: List[Dict]) -> str:
        """Calculate overall opportunity level"""
        if not opportunities:
            return 'low'
        
        high_impact_count = sum(1 for opp in opportunities if opp['impact'] == 'high')
        total_opportunities = len(opportunities)
        
        if high_impact_count / total_opportunities > 0.5:
            return 'high'
        elif high_impact_count / total_opportunities > 0.2:
            return 'medium'
        else:
            return 'low'
    
    def _create_default_trend_analysis(self) -> TrendAnalysis:
        """Create default trend analysis when insufficient data"""
        return TrendAnalysis(
            trend_direction='stable',
            trend_strength=0.0,
            trend_confidence=0.3,
            key_periods=[],
            seasonal_patterns=[],
            acceleration_points=[],
            plateau_periods=[]
        )
    
    def _create_default_growth_prediction(self) -> GrowthPrediction:
        """Create default growth prediction when insufficient data"""
        return GrowthPrediction(
            predicted_trajectory='steady',
            confidence_score=0.3,
            time_horizon='short_term',
            key_milestones=[],
            potential_obstacles=['Insufficient data for accurate prediction'],
            recommended_focus_areas=['Continue collecting data and insights'],
            growth_rate_estimate=2.0
        )


def main():
    """Test the predictive analytics engine"""
    analytics = PredictiveAnalytics()
    
    # Test with sample data
    sample_data = {
        'growth_metrics': {'learning': 0.3, 'relationships': 0.2, 'productivity': -0.1},
        'sentiment_trends': {'2024-01': {'avg_sentiment': 0.2}, '2024-02': {'avg_sentiment': 0.4}},
        'engagement_stats': {'conversation_frequency': 8},
        'top_tags': [('relationships', 10), ('learning', 8), ('productivity', 5)],
        'conversations': []  # Would contain actual conversation objects
    }
    
    # Test predictions
    growth_prediction = analytics.predict_growth_trajectory(sample_data)
    print(f"Predicted Trajectory: {growth_prediction.predicted_trajectory}")
    print(f"Confidence: {growth_prediction.confidence_score:.2f}")
    print(f"Growth Rate Estimate: {growth_prediction.growth_rate_estimate:.1f}% per month")
    
    # Test breakthrough predictions
    breakthroughs = analytics.identify_potential_breakthroughs(sample_data)
    print(f"\nPotential Breakthroughs: {len(breakthroughs)}")
    for breakthrough in breakthroughs:
        print(f"- {breakthrough.topic}: {breakthrough.likelihood:.2f} likelihood")


if __name__ == '__main__':
    main() 