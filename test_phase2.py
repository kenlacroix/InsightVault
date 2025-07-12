"""
Comprehensive Test Suite for InsightVault AI Assistant Phase 2
Tests LLM integration, advanced query parsing, predictive analytics, and performance optimization.
"""

import unittest
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import traceback

# Import Phase 2 components
try:
    from llm_integration import LLMIntegration, GeneratedInsight, QueryContext
    from advanced_query_parser import AdvancedQueryParser, ComplexQueryIntent, TemporalRange, Comparison
    from predictive_analytics import PredictiveAnalytics, TrendAnalysis, GrowthPrediction, PredictedBreakthrough
    from user_profile_manager import UserProfileManager, UserProfile, UserFeedback
    from performance_optimizer import PerformanceOptimizer, ResponseCache, DatabaseManager, BackgroundProcessor
    from database_manager import DatabaseManager as DBManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all Phase 2 components are available")
    sys.exit(1)


class TestLLMIntegration(unittest.TestCase):
    """Test LLM integration functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock API key for testing
        self.api_key = "test_api_key_12345"
        self.llm = LLMIntegration(api_key=self.api_key, model="gpt-3.5-turbo")
        
        # Sample conversation data
        self.sample_conversations = [
            Mock(
                id="conv_1",
                title="Test Conversation 1",
                create_date=datetime.now() - timedelta(days=30),
                get_full_text=lambda: "This is a test conversation about relationships and boundaries.",
                messages=[Mock(role="user", content="How do I set better boundaries?")]
            ),
            Mock(
                id="conv_2", 
                title="Test Conversation 2",
                create_date=datetime.now() - timedelta(days=15),
                get_full_text=lambda: "This is another conversation about productivity and learning.",
                messages=[Mock(role="user", content="How can I improve my productivity?")]
            )
        ]
        
        # Sample analytics data
        self.sample_analytics = Mock(
            date_range=(datetime.now() - timedelta(days=30), datetime.now()),
            top_tags=[("relationships", 5), ("productivity", 3), ("learning", 2)],
            sentiment_trends={"2024-01": {"avg_sentiment": 0.3}},
            growth_metrics={"learning": 0.4, "relationships": 0.2},
            breakthrough_moments=[
                {"title": "Boundary Setting", "summary": "Learned about personal boundaries"}
            ]
        )
    
    @patch('openai.OpenAI')
    def test_llm_initialization(self, mock_openai):
        """Test LLM integration initialization"""
        llm = LLMIntegration(api_key="test_key")
        self.assertEqual(llm.api_key, "test_key")
        self.assertEqual(llm.model, "gpt-4")
        self.assertEqual(llm.max_tokens, 2000)
        self.assertEqual(llm.temperature, 0.7)
    
    def test_llm_initialization_no_api_key(self):
        """Test LLM initialization without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                LLMIntegration()
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        # type: ignore - Mock objects used for testing
        cache_key = self.llm._generate_cache_key("test query", self.sample_conversations, self.sample_analytics)
        self.assertIsInstance(cache_key, str)
        self.assertEqual(len(cache_key), 32)  # MD5 hash length
    
    def test_response_validation(self):
        """Test response validation"""
        valid_response = """
        💡 Holistic Insight: Your Learning Journey
        
        📊 Summary: You have shown consistent growth in your learning approach.
        
        🔍 Key Learnings:
        • You demonstrate reflective thinking
        • You actively seek improvement
        
        📈 Evolution Timeline:
        • Early Period: Initial exploration
        • Recent Period: Applied learning
        
        ⚡ Breakthrough Moments:
        • Conversation 1: "Key realization about learning"
        
        🎯 Next Steps:
        • Continue your learning journey
        • Apply insights to daily life
        
        🔮 Predictive Insights:
        • Continued growth expected
        
        Confidence: 85% | Personalization: Medium
        """
        
        self.assertTrue(self.llm.validate_response(valid_response))
        
        invalid_response = "This is not a properly formatted response"
        self.assertFalse(self.llm.validate_response(invalid_response))
    
    def test_fallback_to_template(self):
        """Test fallback to template system"""
        # type: ignore - Mock objects used for testing
        insight = self.llm._fallback_to_template("test query", self.sample_conversations, self.sample_analytics)
        
        self.assertIsInstance(insight, GeneratedInsight)
        self.assertEqual(insight.model_used, "template-fallback")
        self.assertGreater(len(insight.key_learnings), 0)
        self.assertGreater(len(insight.next_steps), 0)
    
    def test_usage_stats(self):
        """Test usage statistics tracking"""
        stats = self.llm.get_usage_stats()
        
        self.assertIn('request_count', stats)
        self.assertIn('total_tokens', stats)
        self.assertIn('total_cost', stats)
        self.assertIn('cache_hits', stats)
        self.assertIn('model_used', stats)
    
    def test_reset_usage_stats(self):
        """Test usage statistics reset"""
        self.llm.request_count = 10
        self.llm.total_tokens = 1000
        self.llm.total_cost = 0.05
        
        self.llm.reset_usage_stats()
        
        self.assertEqual(self.llm.request_count, 0)
        self.assertEqual(self.llm.total_tokens, 0)
        self.assertEqual(self.llm.total_cost, 0.0)


class TestAdvancedQueryParser(unittest.TestCase):
    """Test advanced query parsing functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.parser = AdvancedQueryParser()
    
    def test_parse_complex_query_simple(self):
        """Test parsing simple query"""
        query = "What have I learned about relationships?"
        intent = self.parser.parse_complex_query(query)
        
        self.assertIsInstance(intent, ComplexQueryIntent)
        self.assertEqual(intent.primary_topic, "relationships")
        self.assertEqual(intent.query_type, "analysis")
        self.assertEqual(intent.complexity_level, 1)
    
    def test_parse_complex_query_comparison(self):
        """Test parsing comparison query"""
        query = "How has my understanding of productivity evolved compared to my relationship insights?"
        intent = self.parser.parse_complex_query(query)
        
        self.assertIsInstance(intent, ComplexQueryIntent)
        self.assertEqual(intent.primary_topic, "productivity")
        self.assertIn("relationships", intent.secondary_topics)
        self.assertEqual(intent.query_type, "comparison")
        self.assertGreater(len(intent.comparisons), 0)
        self.assertGreater(intent.complexity_level, 1)
    
    def test_parse_complex_query_temporal(self):
        """Test parsing query with temporal constraints"""
        query = "What patterns do you see in my emotional responses to stress over the past year?"
        intent = self.parser.parse_complex_query(query)
        
        self.assertIsInstance(intent, ComplexQueryIntent)
        self.assertIsNotNone(intent.temporal_range)
        if intent.temporal_range is not None:
            self.assertEqual(intent.temporal_range.relative_period, "last_year")
    
    def test_extract_temporal_range(self):
        """Test temporal range extraction"""
        # Test relative periods
        query = "My learning over the past 3 months"
        temporal_range = self.parser.extract_temporal_range(query)
        
        self.assertIsInstance(temporal_range, TemporalRange)
        if temporal_range is not None:
            self.assertEqual(temporal_range.relative_period, "past_3_months")
            self.assertIsNotNone(temporal_range.start_date)
            self.assertIsNotNone(temporal_range.end_date)
        
        # Test specific dates
        query = "My conversations from January 2024 to March 2024"
        temporal_range = self.parser.extract_temporal_range(query)
        
        self.assertIsInstance(temporal_range, TemporalRange)
        if temporal_range is not None:
            self.assertGreater(len(temporal_range.specific_dates), 0)
    
    def test_detect_comparative_elements(self):
        """Test comparative elements detection"""
        query = "Compare my learning patterns in relationships vs. career development"
        comparisons = self.parser.detect_comparative_elements(query)
        
        self.assertIsInstance(comparisons, list)
        self.assertGreater(len(comparisons), 0)
        
        comparison = comparisons[0]
        self.assertIsInstance(comparison, Comparison)
        self.assertIn("relationships", comparison.primary_subject.lower())
        self.assertIn("career", comparison.secondary_subject.lower())
    
    def test_suggest_related_queries(self):
        """Test related query suggestions"""
        query = "What have I learned about productivity?"
        suggestions = self.parser.suggest_related_queries(query)
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        self.assertLessEqual(len(suggestions), 5)
        
        # Check that suggestions are relevant
        for suggestion in suggestions:
            self.assertIsInstance(suggestion, str)
            self.assertGreater(len(suggestion), 10)
    
    def test_get_query_statistics(self):
        """Test query statistics generation"""
        query = "How has my understanding of productivity evolved compared to my relationship insights over the past year?"
        stats = self.parser.get_query_statistics(query)
        
        self.assertIsInstance(stats, dict)
        self.assertIn('word_count', stats)
        self.assertIn('complexity_level', stats)
        self.assertIn('query_type', stats)
        self.assertIn('topics_count', stats)
        self.assertIn('comparisons_count', stats)
        self.assertIn('has_temporal_constraints', stats)
        self.assertIn('requires_context', stats)
        
        self.assertGreater(stats['complexity_level'], 1)
        self.assertTrue(stats['has_temporal_constraints'])
        self.assertGreater(stats['comparisons_count'], 0)


class TestPredictiveAnalytics(unittest.TestCase):
    """Test predictive analytics functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.analytics = PredictiveAnalytics()
        
        # Sample conversations for testing
        self.sample_conversations = [
            Mock(
                create_date=datetime.now() - timedelta(days=30),
                get_full_text=lambda: "This is a conversation about learning and growth.",
                messages=[Mock(role="user", content="How can I improve my learning?")]
            ),
            Mock(
                create_date=datetime.now() - timedelta(days=20),
                get_full_text=lambda: "Another conversation about relationships and boundaries.",
                messages=[Mock(role="user", content="How do I set better boundaries?")]
            ),
            Mock(
                create_date=datetime.now() - timedelta(days=10),
                get_full_text=lambda: "A conversation about productivity and time management.",
                messages=[Mock(role="user", content="How can I be more productive?")]
            )
        ]
        
        # Sample historical data
        self.sample_historical_data = {
            'conversations': self.sample_conversations,
            'growth_metrics': {
                'learning': 0.3,
                'relationships': 0.2,
                'productivity': 0.1
            },
            'sentiment_trends': {
                '2024-01': {'avg_sentiment': 0.2},
                '2024-02': {'avg_sentiment': 0.4}
            },
            'engagement_stats': {
                'conversation_frequency': 8
            },
            'top_tags': [('relationships', 10), ('learning', 8), ('productivity', 5)],
            'breakthrough_moments': [
                {'title': 'Learning Breakthrough', 'summary': 'Key insight about learning'}
            ]
        }
    
    def test_analyze_trends(self):
        """Test trend analysis"""
        trend_analysis = self.analytics.analyze_trends(self.sample_conversations)
        
        self.assertIsInstance(trend_analysis, TrendAnalysis)
        self.assertIn(trend_analysis.trend_direction, ['increasing', 'decreasing', 'stable', 'fluctuating'])
        self.assertGreaterEqual(trend_analysis.trend_strength, 0.0)
        self.assertLessEqual(trend_analysis.trend_strength, 1.0)
        self.assertGreaterEqual(trend_analysis.trend_confidence, 0.0)
        self.assertLessEqual(trend_analysis.trend_confidence, 1.0)
        self.assertIsInstance(trend_analysis.key_periods, list)
        self.assertIsInstance(trend_analysis.seasonal_patterns, list)
        self.assertIsInstance(trend_analysis.acceleration_points, list)
        self.assertIsInstance(trend_analysis.plateau_periods, list)
    
    def test_predict_growth_trajectory(self):
        """Test growth trajectory prediction"""
        growth_prediction = self.analytics.predict_growth_trajectory(self.sample_historical_data)
        
        self.assertIsInstance(growth_prediction, GrowthPrediction)
        self.assertIn(growth_prediction.predicted_trajectory, 
                     ['accelerating', 'steady', 'plateauing', 'declining'])
        self.assertGreaterEqual(growth_prediction.confidence_score, 0.0)
        self.assertLessEqual(growth_prediction.confidence_score, 1.0)
        self.assertIn(growth_prediction.time_horizon, ['short_term', 'medium_term', 'long_term'])
        self.assertIsInstance(growth_prediction.key_milestones, list)
        self.assertIsInstance(growth_prediction.potential_obstacles, list)
        self.assertIsInstance(growth_prediction.recommended_focus_areas, list)
        self.assertGreaterEqual(growth_prediction.growth_rate_estimate, 0.0)
    
    def test_identify_potential_breakthroughs(self):
        """Test breakthrough identification"""
        patterns = {
            'top_tags': [('relationships', 10), ('learning', 8), ('productivity', 5)],
            'aha_moments': 3,
            'pattern_recognition': 2,
            'paradigm_shifts': 1
        }
        
        breakthroughs = self.analytics.identify_potential_breakthroughs(patterns)
        
        self.assertIsInstance(breakthroughs, list)
        self.assertLessEqual(len(breakthroughs), 5)
        
        for breakthrough in breakthroughs:
            self.assertIsInstance(breakthrough, PredictedBreakthrough)
            self.assertIsInstance(breakthrough.topic, str)
            self.assertGreaterEqual(breakthrough.likelihood, 0.0)
            self.assertLessEqual(breakthrough.likelihood, 1.0)
            self.assertIsInstance(breakthrough.estimated_timing, datetime)
            self.assertIsInstance(breakthrough.trigger_factors, list)
            self.assertGreaterEqual(breakthrough.impact_score, 0.0)
            self.assertLessEqual(breakthrough.impact_score, 1.0)
            self.assertIsInstance(breakthrough.preparation_actions, list)
    
    def test_detect_risks_opportunities(self):
        """Test risk and opportunity detection"""
        analysis = {
            'growth_metrics': {'learning': 0.3, 'relationships': -0.1},
            'sentiment_trends': {'2024-01': {'avg_sentiment': 0.2}},
            'engagement_stats': {'conversation_frequency': 5}
        }
        
        risk_opportunity = self.analytics.detect_risks_opportunities(analysis)
        
        self.assertIsInstance(risk_opportunity, type(risk_opportunity))
        self.assertIsInstance(risk_opportunity.risks, list)
        self.assertIsInstance(risk_opportunity.opportunities, list)
        self.assertIsInstance(risk_opportunity.risk_mitigation_strategies, list)
        self.assertIsInstance(risk_opportunity.opportunity_leverage_strategies, list)
        self.assertIn(risk_opportunity.overall_risk_level, ['low', 'medium', 'high'])
        self.assertIn(risk_opportunity.overall_opportunity_level, ['low', 'medium', 'high'])
    
    def test_insufficient_data_handling(self):
        """Test handling of insufficient data"""
        # Test with empty conversations
        trend_analysis = self.analytics.analyze_trends([])
        self.assertEqual(trend_analysis.trend_direction, 'stable')
        self.assertEqual(trend_analysis.trend_strength, 0.0)
        self.assertEqual(trend_analysis.trend_confidence, 0.3)
        
        # Test with insufficient historical data
        growth_prediction = self.analytics.predict_growth_trajectory({})
        self.assertEqual(growth_prediction.predicted_trajectory, 'steady')
        self.assertEqual(growth_prediction.confidence_score, 0.3)
        self.assertEqual(growth_prediction.time_horizon, 'short_term')


class TestUserProfileManager(unittest.TestCase):
    """Test user profile management functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Use temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.profile_manager = UserProfileManager(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test environment"""
        os.unlink(self.temp_db.name)
    
    def test_create_user_profile(self):
        """Test user profile creation"""
        user_id = "test_user_123"
        initial_preferences = {
            'focus_areas': ['relationships', 'productivity'],
            'learning_goals': ['self_awareness']
        }
        
        profile = self.profile_manager.create_user_profile(user_id, initial_preferences)
        
        self.assertIsInstance(profile, UserProfile)
        if profile is not None:
            self.assertEqual(profile.user_id, user_id)
            self.assertIn('relationships', profile.focus_areas)
            self.assertIn('productivity', profile.focus_areas)
            self.assertIn('self_awareness', profile.learning_goals)
            self.assertIsInstance(profile.created_at, datetime)
            self.assertIsInstance(profile.last_updated, datetime)
    
    def test_get_user_profile(self):
        """Test user profile retrieval"""
        user_id = "test_user_456"
        profile = self.profile_manager.create_user_profile(user_id)
        
        retrieved_profile = self.profile_manager.get_user_profile(user_id)
        
        self.assertIsInstance(retrieved_profile, UserProfile)
        self.assertEqual(retrieved_profile.user_id, user_id)
        self.assertEqual(retrieved_profile.focus_areas, profile.focus_areas)
        self.assertEqual(retrieved_profile.learning_goals, profile.learning_goals)
    
    def test_update_preferences(self):
        """Test preference updates"""
        user_id = "test_user_789"
        self.profile_manager.create_user_profile(user_id)
        
        new_preferences = {
            'insight_depth': 'comprehensive',
            'response_style': 'formal'
        }
        
        self.profile_manager.update_preferences(user_id, new_preferences)
        
        profile = self.profile_manager.get_user_profile(user_id)
        self.assertEqual(profile.preferences['insight_depth'], 'comprehensive')
        self.assertEqual(profile.preferences['response_style'], 'formal')
    
    def test_collect_feedback(self):
        """Test feedback collection"""
        user_id = "test_user_feedback"
        self.profile_manager.create_user_profile(user_id)
        
        query = "What have I learned about relationships?"
        response = "Your relationships have evolved significantly..."
        rating = 4
        feedback_text = "Great insight!"
        
        self.profile_manager.collect_feedback(user_id, query, response, rating, feedback_text)
        
        profile = self.profile_manager.get_user_profile(user_id)
        self.assertGreater(len(profile.feedback_history), 0)
        
        feedback = profile.feedback_history[0]
        self.assertEqual(feedback['query'], query)
        self.assertEqual(feedback['response'], response)
        self.assertEqual(feedback['rating'], rating)
        self.assertEqual(feedback['feedback_text'], feedback_text)
    
    def test_record_interaction(self):
        """Test interaction recording"""
        user_id = "test_user_interaction"
        self.profile_manager.create_user_profile(user_id)
        
        query = "How has my learning evolved?"
        response = "Your learning patterns show..."
        
        self.profile_manager.record_interaction(user_id, query, response)
        
        profile = self.profile_manager.get_user_profile(user_id)
        self.assertGreater(len(profile.interaction_history), 0)
        
        interaction = profile.interaction_history[0]
        self.assertEqual(interaction['query'], query)
        self.assertEqual(interaction['response'], response)
    
    def test_get_user_statistics(self):
        """Test user statistics generation"""
        user_id = "test_user_stats"
        self.profile_manager.create_user_profile(user_id)
        
        # Add some interactions and feedback
        self.profile_manager.record_interaction(user_id, "Test query", "Test response")
        self.profile_manager.collect_feedback(user_id, "Test query", "Test response", 4)
        
        stats = self.profile_manager.get_user_statistics(user_id)
        
        self.assertIsInstance(stats, dict)
        self.assertIn('interaction_count', stats)
        self.assertIn('average_rating', stats)
        self.assertIn('common_queries', stats)
        self.assertIn('last_activity', stats)
        self.assertIn('engagement_level', stats)
        
        self.assertGreater(stats['interaction_count'], 0)
        self.assertIsInstance(stats['average_rating'], (int, float, type(None)))
    
    def test_get_recommendations(self):
        """Test recommendation generation"""
        user_id = "test_user_recs"
        self.profile_manager.create_user_profile(user_id, {
            'focus_areas': ['relationships', 'productivity'],
            'learning_goals': ['self_awareness']
        })
        
        recommendations = self.profile_manager.get_recommendations(user_id)
        
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)
        
        for recommendation in recommendations:
            self.assertIsInstance(recommendation, str)
            self.assertGreater(len(recommendation), 10)
    
    def test_personalize_insight(self):
        """Test insight personalization"""
        user_id = "test_user_personalize"
        profile = self.profile_manager.create_user_profile(user_id, {
            'focus_areas': ['relationships'],
            'learning_goals': ['self_awareness']
        })
        
        # Create mock insight
        insight = Mock()
        insight.key_learnings = ["Learning 1", "Learning 2", "Learning 3"]
        insight.next_steps = ["Step 1", "Step 2", "Step 3"]
        insight.summary = "This is a test summary."
        insight.confidence_score = 0.8
        
        personalized_insight = self.profile_manager.personalize_insight(insight, profile)
        
        self.assertIsNotNone(personalized_insight)
        # Check that personalization occurred
        self.assertGreater(len(personalized_insight.next_steps), 3)


class TestPerformanceOptimizer(unittest.TestCase):
    """Test performance optimization functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Use temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.optimizer = PerformanceOptimizer(self.temp_db.name, cache_size_mb=10, max_workers=2)
    
    def tearDown(self):
        """Clean up test environment"""
        try:
            self.optimizer.shutdown()
            # Force close any remaining database connections
            import gc
            gc.collect()
            # Wait a moment for connections to close
            import time
            time.sleep(0.1)
        except Exception:
            pass
        
        try:
            if hasattr(self, 'temp_db') and os.path.exists(self.temp_db.name):
                os.unlink(self.temp_db.name)
        except PermissionError:
            # File might still be locked, that's okay for tests
            pass
    
    def test_response_cache(self):
        """Test response caching functionality"""
        cache = ResponseCache(max_size_mb=1, max_entries=10)
        
        # Test cache set/get
        test_data = {"query": "test", "response": "test response"}
        cache.set("test_key", test_data)
        
        cached_data = cache.get("test_key")
        self.assertEqual(cached_data, test_data)
        
        # Test cache miss
        missing_data = cache.get("nonexistent_key")
        self.assertIsNone(missing_data)
        
        # Test cache stats
        stats = cache.get_stats()
        self.assertIn('hit_count', stats)
        self.assertIn('miss_count', stats)
        self.assertIn('hit_rate', stats)
        self.assertIn('current_size_mb', stats)
        self.assertIn('entry_count', stats)
        
        self.assertEqual(stats['hit_count'], 1)
        self.assertEqual(stats['miss_count'], 1)
        self.assertEqual(stats['hit_rate'], 0.5)
    
    def test_database_manager(self):
        """Test database manager functionality"""
        db_manager = DatabaseManager(self.temp_db.name)
        
        # Test query execution
        results = db_manager.execute_query("SELECT 1 as test")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['test'], 1)
        
        # Test database stats
        stats = db_manager.get_stats()
        self.assertIn('query_count', stats)
        self.assertIn('slow_queries', stats)
        self.assertIn('cache_hits', stats)
        self.assertIn('cache_hit_rate', stats)
        
        self.assertGreater(stats['query_count'], 0)
    
    def test_background_processor(self):
        """Test background processing functionality"""
        processor = BackgroundProcessor(max_workers=2)
        
        # Test task submission and execution
        def test_task():
            return "Task completed"
        
        task_id = processor.submit_task("test_task", test_task)
        self.assertIsInstance(task_id, str)
        
        # Test task result retrieval
        result = processor.get_task_result(task_id, timeout=5)
        self.assertEqual(result, "Task completed")
        
        # Test task with error
        def error_task():
            raise ValueError("Test error")
        
        error_task_id = processor.submit_task("error_task", error_task)
        error_result = processor.get_task_result(error_task_id, timeout=5)
        self.assertIn('error', error_result)
        
        processor.shutdown()
    
    def test_performance_optimizer_integration(self):
        """Test performance optimizer integration"""
        # Test caching
        test_data = {"query": "test", "response": "test response"}
        query_hash = "test_hash_123"
        
        self.optimizer.cache_response(query_hash, test_data)
        cached_data = self.optimizer.get_cached_response(query_hash)
        self.assertEqual(cached_data, test_data)
        
        # Test performance metrics
        metrics = self.optimizer.get_performance_metrics()
        self.assertIsInstance(metrics, type(metrics))
        self.assertIn('response_time_ms', metrics.__dict__)
        self.assertIn('cache_hit_rate', metrics.__dict__)
        self.assertIn('memory_usage_mb', metrics.__dict__)
        self.assertIn('cpu_usage_percent', metrics.__dict__)
        
        # Test performance summary
        summary = self.optimizer.get_performance_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn('average_response_time_ms', summary)
        self.assertIn('average_cache_hit_rate', summary)
        self.assertIn('cache_stats', summary)
        self.assertIn('database_stats', summary)
    
    def test_memory_optimization(self):
        """Test memory optimization functionality"""
        # Add some data to cache
        for i in range(100):
            self.optimizer.cache_response(f"key_{i}", {"data": "x" * 1000})
        
        # Test memory optimization
        self.optimizer.optimize_memory_usage()
        
        # Verify optimization occurred
        cache_stats = self.optimizer.cache.get_stats()
        self.assertLessEqual(cache_stats['entry_count'], 100)


class TestDatabaseManager(unittest.TestCase):
    """Test database manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_manager = DBManager(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test environment"""
        os.unlink(self.temp_db.name)
    
    def test_save_and_get_conversation(self):
        """Test conversation save and retrieve"""
        conversation_data = {
            'id': 'test_conv_1',
            'title': 'Test Conversation',
            'create_date': datetime.now().isoformat(),
            'update_date': datetime.now().isoformat(),
            'message_count': 2,
            'total_length': 100,
            'tags': ['test', 'sample'],
            'sentiment_score': 0.5,
            'topics': ['testing', 'development'],
            'messages': [
                {
                    'role': 'user',
                    'content': 'Hello, this is a test message',
                    'timestamp': datetime.now().isoformat(),
                    'sentiment_score': 0.3,
                    'topics': ['greeting']
                },
                {
                    'role': 'assistant',
                    'content': 'Hello! How can I help you today?',
                    'timestamp': datetime.now().isoformat(),
                    'sentiment_score': 0.7,
                    'topics': ['greeting', 'help']
                }
            ]
        }
        
        # Save conversation
        success = self.db_manager.save_conversation(conversation_data)
        self.assertTrue(success)
        
        # Retrieve conversation
        retrieved = self.db_manager.get_conversation('test_conv_1')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['id'], 'test_conv_1')
        self.assertEqual(retrieved['title'], 'Test Conversation')
        self.assertEqual(len(retrieved['messages']), 2)
    
    def test_analytics_cache(self):
        """Test analytics cache functionality"""
        cache_data = {'test': 'data', 'timestamp': datetime.now().isoformat()}
        
        # Save cache
        success = self.db_manager.save_analytics_cache('test_key', cache_data)
        self.assertTrue(success)
        
        # Retrieve cache
        cached = self.db_manager.get_analytics_cache('test_key')
        self.assertIsNotNone(cached)
        self.assertEqual(cached['test'], 'data')
    
    def test_user_insights(self):
        """Test user insights functionality"""
        user_id = "test_user"
        query = "What have I learned?"
        response = "You have learned many things..."
        
        # Save insight
        success = self.db_manager.save_user_insight(
            user_id, query, response, 0.8, "high", "gpt-4", 100, 0.02
        )
        self.assertTrue(success)
        
        # Get insights
        insights = self.db_manager.get_user_insights(user_id)
        self.assertGreater(len(insights), 0)
        
        insight = insights[0]
        self.assertEqual(insight['query'], query)
        self.assertEqual(insight['response'], response)
        self.assertEqual(insight['confidence_score'], 0.8)
        self.assertEqual(insight['personalization_level'], "high")
    
    def test_conversation_embeddings(self):
        """Test conversation embeddings functionality"""
        conversation_id = "test_conv_embeddings"
        embeddings = [0.1, 0.2, 0.3, 0.4, 0.5] * 300  # 1500 dimensions
        
        # Save embeddings
        success = self.db_manager.save_conversation_embeddings(conversation_id, embeddings)
        self.assertTrue(success)
        
        # Retrieve embeddings
        retrieved_embeddings = self.db_manager.get_conversation_embeddings(conversation_id)
        self.assertIsNotNone(retrieved_embeddings)
        self.assertEqual(len(retrieved_embeddings), len(embeddings))
    
    def test_growth_patterns(self):
        """Test growth patterns functionality"""
        user_id = "test_user_patterns"
        pattern_type = "learning_acceleration"
        pattern_data = {"trend": "increasing", "confidence": 0.8}
        
        # Save pattern
        success = self.db_manager.save_growth_pattern(user_id, pattern_type, pattern_data, 0.8)
        self.assertTrue(success)
        
        # Get patterns
        patterns = self.db_manager.get_growth_patterns(user_id)
        self.assertGreater(len(patterns), 0)
        
        pattern = patterns[0]
        self.assertEqual(pattern['pattern_type'], pattern_type)
        self.assertEqual(pattern['pattern_data'], pattern_data)
        self.assertEqual(pattern['confidence_score'], 0.8)
    
    def test_cleanup_expired_cache(self):
        """Test expired cache cleanup"""
        # Add some cache entries
        self.db_manager.save_analytics_cache('key1', {'data': 'test1'}, ttl_hours=0)
        self.db_manager.save_analytics_cache('key2', {'data': 'test2'}, ttl_hours=24)
        
        # Cleanup expired entries
        deleted_count = self.db_manager.cleanup_expired_cache()
        self.assertGreaterEqual(deleted_count, 1)
    
    def test_database_stats(self):
        """Test database statistics"""
        stats = self.db_manager.get_database_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('conversations_count', stats)
        self.assertIn('messages_count', stats)
        self.assertIn('analytics_cache_count', stats)
        self.assertIn('user_insights_count', stats)
        self.assertIn('conversation_embeddings_count', stats)
        self.assertIn('growth_patterns_count', stats)
        self.assertIn('database_size_bytes', stats)


class TestIntegration(unittest.TestCase):
    """Integration tests for Phase 2 components"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary files
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Initialize components
        self.llm = LLMIntegration(api_key="test_key", model="gpt-3.5-turbo")
        self.query_parser = AdvancedQueryParser()
        self.analytics = PredictiveAnalytics()
        self.profile_manager = UserProfileManager(self.temp_db.name)
        self.optimizer = PerformanceOptimizer(self.temp_db.name)
        self.db_manager = DBManager(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test environment"""
        self.optimizer.shutdown()
        os.unlink(self.temp_db.name)
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # 1. Create user profile
        user_id = "integration_test_user"
        profile = self.profile_manager.create_user_profile(user_id, {
            'focus_areas': ['relationships', 'learning'],
            'learning_goals': ['self_awareness']
        })
        
        # 2. Parse complex query
        query = "How has my understanding of relationships evolved compared to my learning patterns over the past year?"
        intent = self.query_parser.parse_complex_query(query)
        
        self.assertIsInstance(intent, ComplexQueryIntent)
        self.assertEqual(intent.primary_topic, "relationships")
        self.assertIn("learning", intent.secondary_topics)
        self.assertIsNotNone(intent.temporal_range)
        self.assertGreater(len(intent.comparisons), 0)
        
        # 3. Record interaction
        self.profile_manager.record_interaction(user_id, query, "Test response")
        
        # 4. Get user statistics
        stats = self.profile_manager.get_user_statistics(user_id)
        self.assertGreater(stats['interaction_count'], 0)
        
        # 5. Test caching
        query_hash = "test_hash_123"
        test_data = {"query": query, "response": "Test response"}
        self.optimizer.cache_response(query_hash, test_data)
        
        cached_data = self.optimizer.get_cached_response(query_hash)
        self.assertEqual(cached_data, test_data)
        
        # 6. Test database operations
        conversation_data = {
            'id': 'integration_conv_1',
            'title': 'Integration Test Conversation',
            'create_date': datetime.now().isoformat(),
            'update_date': datetime.now().isoformat(),
            'message_count': 1,
            'total_length': 50,
            'tags': ['test'],
            'sentiment_score': 0.5,
            'topics': ['testing'],
            'messages': []
        }
        
        success = self.db_manager.save_conversation(conversation_data)
        self.assertTrue(success)
        
        retrieved = self.db_manager.get_conversation('integration_conv_1')
        self.assertIsNotNone(retrieved)
        
        # 7. Test analytics
        sample_conversations = [
            Mock(
                create_date=datetime.now() - timedelta(days=30),
                get_full_text=lambda: "Test conversation",
                messages=[Mock(role="user", content="Test")]
            )
        ]
        
        trend_analysis = self.analytics.analyze_trends(sample_conversations)
        self.assertIsInstance(trend_analysis, TrendAnalysis)
        
        # 8. Test performance metrics
        metrics = self.optimizer.get_performance_metrics()
        self.assertIsInstance(metrics, type(metrics))
        
        summary = self.optimizer.get_performance_summary()
        self.assertIsInstance(summary, dict)


def run_all_tests():
    """Run all Phase 2 tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestLLMIntegration,
        TestAdvancedQueryParser,
        TestPredictiveAnalytics,
        TestUserProfileManager,
        TestPerformanceOptimizer,
        TestDatabaseManager,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"PHASE 2 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1) 