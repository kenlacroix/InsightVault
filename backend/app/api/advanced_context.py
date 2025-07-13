"""
Advanced Context Intelligence API endpoints for InsightVault Phase 3.
Provides endpoints for sophisticated topic detection, dynamic context selection,
and machine learning capabilities with full user control and transparency.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..database import get_sync_db
from ..models import User
from ..advanced_context_intelligence import AdvancedContextIntelligenceEngine
from ..auth import get_current_user

router = APIRouter(prefix="/advanced-context", tags=["advanced-context"])

# Pydantic models for request/response
class UseCaseDetectionRequest(BaseModel):
    question: str
    user_id: Optional[int] = None

class UseCaseDetectionResponse(BaseModel):
    use_case: str
    confidence: float
    alternative_use_cases: List[Dict[str, Any]]
    reasoning: str

class GrowthPatternRequest(BaseModel):
    user_id: int
    force_refresh: bool = False

class GrowthPatternResponse(BaseModel):
    patterns: List[Dict[str, Any]]
    total_patterns: int
    last_updated: datetime
    summary: str

class ContextSelectionRequest(BaseModel):
    question: str
    use_case: Optional[str] = None
    include_historical: bool = True
    include_recent: bool = True
    include_insights: bool = True
    max_context_length: Optional[int] = None

class ContextSelectionResponse(BaseModel):
    selected_context: Dict[str, Any]
    use_case_detected: str
    context_breakdown: Dict[str, Any]
    transparency_info: Dict[str, Any]
    user_controls: Dict[str, Any]

class TopicEmbeddingRequest(BaseModel):
    conversation_id: int

class TopicEmbeddingResponse(BaseModel):
    topics: List[Dict[str, Any]]
    total_topics: int
    processing_time: float

class ConversationClusterRequest(BaseModel):
    user_id: int
    cluster_type: Optional[str] = None

class ConversationClusterResponse(BaseModel):
    clusters: List[Dict[str, Any]]
    total_clusters: int
    clustering_method: str
    metadata: Dict[str, Any]

class UseCaseProfileRequest(BaseModel):
    use_case_name: str
    context_preferences: Dict[str, Any]
    topic_weights: Dict[str, float]
    is_active: bool = True

class UseCaseProfileResponse(BaseModel):
    profile_id: int
    use_case_name: str
    created_at: datetime
    last_used: Optional[datetime]
    is_active: bool

@router.post("/detect-use-case", response_model=UseCaseDetectionResponse)
async def detect_use_case(
    request: UseCaseDetectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Detect the most likely use case for a given question using advanced ML.
    """
    try:
        engine = AdvancedContextIntelligenceEngine(db)
        user_id = request.user_id or current_user.id
        
        # Detect use case
        use_case = engine.detect_use_case(request.question, user_id)
        
        # Calculate confidence and alternatives
        confidence = 0.8  # Default confidence
        alternatives = []
        
        # Get alternative use cases
        for alt_use_case, profile in engine.use_case_profiles.items():
            if alt_use_case != use_case:
                score = 0
                for keyword in profile['keywords']:
                    if keyword in request.question.lower():
                        score += 1
                alt_score = score / len(profile['keywords'])
                if alt_score > 0.1:  # Only include if reasonably relevant
                    alternatives.append({
                        'use_case': alt_use_case,
                        'confidence': alt_score,
                        'keywords_matched': [k for k in profile['keywords'] if k in request.question.lower()]
                    })
        
        # Sort alternatives by confidence
        alternatives.sort(key=lambda x: x['confidence'], reverse=True)
        
        return UseCaseDetectionResponse(
            use_case=use_case,
            confidence=confidence,
            alternative_use_cases=alternatives[:3],  # Top 3 alternatives
            reasoning=f"Detected '{use_case}' based on keyword analysis and user patterns"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error detecting use case: {str(e)}"
        )

@router.post("/detect-growth-patterns", response_model=GrowthPatternResponse)
async def detect_growth_patterns(
    request: GrowthPatternRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Detect growth patterns, milestones, and breakthroughs in user's conversations.
    Can be run in background for large datasets.
    """
    try:
        engine = AdvancedContextIntelligenceEngine(db)
        user_id = request.user_id or current_user.id
        
        if request.force_refresh:
            # Run in background for large datasets
            background_tasks.add_task(engine.detect_growth_patterns, user_id)
            return GrowthPatternResponse(
                patterns=[],
                total_patterns=0,
                last_updated=datetime.utcnow(),
                summary="Pattern detection started in background"
            )
        
        # Run synchronously for immediate results
        patterns = engine.detect_growth_patterns(user_id)
        
        # Get summary statistics
        pattern_types = [p['type'] for p in patterns]
        type_counts = {}
        for p_type in pattern_types:
            type_counts[p_type] = type_counts.get(p_type, 0) + 1
        
        summary = f"Detected {len(patterns)} patterns: " + ", ".join([
            f"{count} {p_type}" for p_type, count in type_counts.items()
        ])
        
        return GrowthPatternResponse(
            patterns=patterns,
            total_patterns=len(patterns),
            last_updated=datetime.utcnow(),
            summary=summary
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error detecting growth patterns: {str(e)}"
        )

@router.post("/select-intelligent-context", response_model=ContextSelectionResponse)
async def select_intelligent_context(
    request: ContextSelectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Intelligently select the most relevant context for a given question.
    Provides full transparency and user control.
    """
    try:
        engine = AdvancedContextIntelligenceEngine(db)
        
        # Override max context length if specified
        if request.max_context_length:
            engine.max_context_length = request.max_context_length
        
        # Select intelligent context
        selected_context = engine.select_intelligent_context(
            user_id=current_user.id,
            current_question=request.question,
            use_case=request.use_case
        )
        
        # Prepare transparency information
        transparency_info = {
            "selection_method": selected_context.get('selection_method', 'intelligent'),
            "use_case_detected": selected_context.get('use_case', {}).get('name', 'unknown'),
            "context_sources": {
                "historical_conversations": len(selected_context.get('historical_context', [])),
                "recent_interactions": len(selected_context.get('recent_context', [])),
                "growth_insights": len(selected_context.get('growth_insights', []))
            },
            "relevance_scoring": "ML-based similarity and keyword matching",
            "context_length": selected_context.get('total_length', 0),
            "max_allowed_length": engine.max_context_length
        }
        
        # Prepare user controls
        user_controls = {
            "can_adjust_context_length": True,
            "can_override_use_case": True,
            "can_filter_context_types": True,
            "can_provide_feedback": True,
            "available_use_cases": list(engine.use_case_profiles.keys())
        }
        
        return ContextSelectionResponse(
            selected_context=selected_context,
            use_case_detected=selected_context.get('use_case', {}).get('name', 'personal_growth'),
            context_breakdown=selected_context.get('context_summary', ''),
            transparency_info=transparency_info,
            user_controls=user_controls
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error selecting intelligent context: {str(e)}"
        )

@router.post("/generate-topic-embeddings", response_model=TopicEmbeddingResponse)
async def generate_topic_embeddings(
    request: TopicEmbeddingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Generate topic embeddings for a conversation using advanced NLP.
    """
    try:
        import time
        start_time = time.time()
        
        engine = AdvancedContextIntelligenceEngine(db)
        
        # Verify user owns the conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found or access denied"
            )
        
        # Generate topic embeddings
        topics = engine.generate_topic_embeddings(request.conversation_id)
        
        processing_time = time.time() - start_time
        
        return TopicEmbeddingResponse(
            topics=topics,
            total_topics=len(topics),
            processing_time=processing_time
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating topic embeddings: {str(e)}"
        )

@router.post("/create-conversation-clusters", response_model=ConversationClusterResponse)
async def create_conversation_clusters(
    request: ConversationClusterRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Create conversation clusters using advanced clustering algorithms.
    """
    try:
        engine = AdvancedContextIntelligenceEngine(db)
        user_id = request.user_id or current_user.id
        
        # Run clustering in background for better performance
        background_tasks.add_task(engine.create_conversation_clusters, user_id)
        
        # Get existing clusters for immediate response
        existing_clusters = db.query(ConversationCluster).filter(
            ConversationCluster.user_id == user_id
        ).all()
        
        cluster_data = []
        for cluster in existing_clusters:
            member_count = db.query(ConversationClusterMembership).filter(
                ConversationClusterMembership.cluster_id == cluster.id
            ).count()
            
            cluster_data.append({
                'id': cluster.id,
                'name': cluster.cluster_name,
                'type': cluster.cluster_type,
                'description': cluster.description,
                'member_count': member_count,
                'created_at': cluster.created_at.isoformat(),
                'last_updated': cluster.last_updated.isoformat()
            })
        
        return ConversationClusterResponse(
            clusters=cluster_data,
            total_clusters=len(cluster_data),
            clustering_method="DBSCAN + K-means hybrid",
            metadata={
                "ml_available": engine.ml_available,
                "clustering_in_progress": True,
                "estimated_completion": "2-5 minutes"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating conversation clusters: {str(e)}"
        )

@router.get("/clusters/{user_id}")
async def get_conversation_clusters(
    user_id: int,
    cluster_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get conversation clusters for a user, optionally filtered by type.
    """
    try:
        # Verify user access
        if user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        
        query = db.query(ConversationCluster).filter(
            ConversationCluster.user_id == user_id
        )
        
        if cluster_type:
            query = query.filter(ConversationCluster.cluster_type == cluster_type)
        
        clusters = query.all()
        
        cluster_data = []
        for cluster in clusters:
            # Get cluster members
            memberships = db.query(ConversationClusterMembership).filter(
                ConversationClusterMembership.cluster_id == cluster.id
            ).all()
            
            member_conversations = []
            for membership in memberships:
                conversation = db.query(Conversation).filter(
                    Conversation.id == membership.conversation_id
                ).first()
                
                if conversation:
                    member_conversations.append({
                        'id': conversation.id,
                        'title': conversation.title,
                        'membership_score': membership.membership_score,
                        'created_at': conversation.created_at.isoformat()
                    })
            
            cluster_data.append({
                'id': cluster.id,
                'name': cluster.cluster_name,
                'type': cluster.cluster_type,
                'description': cluster.description,
                'member_count': len(member_conversations),
                'members': member_conversations,
                'metadata': cluster.cluster_metadata,
                'created_at': cluster.created_at.isoformat(),
                'last_updated': cluster.last_updated.isoformat()
            })
        
        return {
            "success": True,
            "data": cluster_data,
            "total_clusters": len(cluster_data),
            "filtered_by_type": cluster_type is not None
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving conversation clusters: {str(e)}"
        )

@router.post("/use-case-profiles", response_model=UseCaseProfileResponse)
async def create_use_case_profile(
    request: UseCaseProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Create or update a use case profile for personalized context selection.
    """
    try:
        from ..models import UseCaseProfile
        
        # Check if profile already exists
        existing_profile = db.query(UseCaseProfile).filter(
            UseCaseProfile.user_id == current_user.id,
            UseCaseProfile.use_case_name == request.use_case_name
        ).first()
        
        if existing_profile:
            # Update existing profile
            existing_profile.context_preferences = request.context_preferences
            existing_profile.topic_weights = request.topic_weights
            existing_profile.is_active = request.is_active
            profile = existing_profile
        else:
            # Create new profile
            profile = UseCaseProfile(
                user_id=current_user.id,
                use_case_name=request.use_case_name,
                context_preferences=request.context_preferences,
                topic_weights=request.topic_weights,
                is_active=request.is_active
            )
            db.add(profile)
        
        db.commit()
        db.refresh(profile)
        
        return UseCaseProfileResponse(
            profile_id=profile.id,
            use_case_name=profile.use_case_name,
            created_at=profile.created_at,
            last_used=profile.last_used,
            is_active=profile.is_active
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating use case profile: {str(e)}"
        )

@router.get("/use-case-profiles")
async def get_use_case_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get all use case profiles for the current user.
    """
    try:
        from ..models import UseCaseProfile
        
        profiles = db.query(UseCaseProfile).filter(
            UseCaseProfile.user_id == current_user.id
        ).all()
        
        profile_data = []
        for profile in profiles:
            profile_data.append({
                'id': profile.id,
                'use_case_name': profile.use_case_name,
                'context_preferences': profile.context_preferences,
                'topic_weights': profile.topic_weights,
                'is_active': profile.is_active,
                'created_at': profile.created_at.isoformat(),
                'last_used': profile.last_used.isoformat() if profile.last_used else None
            })
        
        return {
            "success": True,
            "data": profile_data,
            "total_profiles": len(profile_data)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving use case profiles: {str(e)}"
        )

@router.get("/growth-insights")
async def get_growth_insights(
    insight_type: Optional[str] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get growth insights for the current user, optionally filtered by type.
    """
    try:
        from ..models import GrowthInsight
        
        query = db.query(GrowthInsight).filter(
            GrowthInsight.user_id == current_user.id,
            GrowthInsight.is_active == True
        )
        
        if insight_type:
            query = query.filter(GrowthInsight.insight_type == insight_type)
        
        insights = query.order_by(GrowthInsight.detected_at.desc()).limit(limit).all()
        
        insight_data = []
        for insight in insights:
            insight_data.append({
                'id': insight.id,
                'type': insight.insight_type,
                'content': insight.content,
                'confidence_score': insight.confidence_score,
                'detected_at': insight.detected_at.isoformat(),
                'related_conversations': insight.related_conversations,
                'related_interactions': insight.related_interactions,
                'metadata': insight.insight_metadata
            })
        
        return {
            "success": True,
            "data": insight_data,
            "total_insights": len(insight_data),
            "filtered_by_type": insight_type is not None
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving growth insights: {str(e)}"
        )

@router.get("/context-transparency")
async def get_context_transparency(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get transparency information about how context is selected and used.
    """
    try:
        from ..models import ContextSelectionLog
        
        # Get recent context selection logs
        recent_logs = db.query(ContextSelectionLog).filter(
            ContextSelectionLog.user_id == current_user.id
        ).order_by(ContextSelectionLog.created_at.desc()).limit(10).all()
        
        log_data = []
        for log in recent_logs:
            log_data.append({
                'id': log.id,
                'selection_method': log.selection_method,
                'selected_context': log.selected_context,
                'relevance_scores': log.relevance_scores,
                'user_feedback': log.user_feedback,
                'created_at': log.created_at.isoformat()
            })
        
        # Get system statistics
        total_conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).count()
        
        total_interactions = db.query(UserInteraction).join(UserSession).filter(
            UserSession.user_id == current_user.id
        ).count()
        
        total_insights = db.query(GrowthInsight).filter(
            GrowthInsight.user_id == current_user.id,
            GrowthInsight.is_active == True
        ).count()
        
        return {
            "success": True,
            "data": {
                "recent_selections": log_data,
                "system_statistics": {
                    "total_conversations": total_conversations,
                    "total_interactions": total_interactions,
                    "total_growth_insights": total_insights
                },
                "transparency_features": {
                    "context_selection_logging": True,
                    "user_feedback_collection": True,
                    "selection_method_disclosure": True,
                    "relevance_score_visibility": True
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving context transparency: {str(e)}"
        )

@router.post("/context-feedback")
async def provide_context_feedback(
    interaction_id: int,
    feedback: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Provide feedback on context selection to improve future selections.
    """
    try:
        from ..models import ContextSelectionLog, UserInteraction
        
        # Verify the interaction belongs to the user
        interaction = db.query(UserInteraction).join(UserSession).filter(
            UserInteraction.id == interaction_id,
            UserSession.user_id == current_user.id
        ).first()
        
        if not interaction:
            raise HTTPException(
                status_code=404,
                detail="Interaction not found or access denied"
            )
        
        # Update the context selection log with feedback
        log = db.query(ContextSelectionLog).filter(
            ContextSelectionLog.interaction_id == interaction_id
        ).first()
        
        if log:
            log.user_feedback = feedback
            db.commit()
        
        return {
            "success": True,
            "message": "Feedback recorded successfully",
            "feedback_id": log.id if log else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error recording context feedback: {str(e)}"
        ) 