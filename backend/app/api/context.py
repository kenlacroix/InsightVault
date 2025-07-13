from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..database import get_sync_db
from ..models import User
from ..context_fusion import ContextFusionEngine
from ..auth import get_current_user

router = APIRouter(prefix="/context", tags=["context"])

@router.get("/fusion")
async def get_context_fusion_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get context fusion data for the current user.
    Returns historical conversations and recent interactions for frontend display.
    """
    try:
        context_engine = ContextFusionEngine(db)
        context_data = context_engine.get_context_for_frontend(current_user.id)
        
        return {
            "success": True,
            "data": context_data,
            "message": "Context fusion data retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving context fusion data: {str(e)}"
        )

@router.get("/summary")
async def get_context_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get a summary of available context for the current user.
    """
    try:
        context_engine = ContextFusionEngine(db)
        
        # Get historical context summary
        historical = context_engine.get_historical_context(current_user.id, limit_conversations=1)
        
        # Get recent interactions summary
        recent = context_engine.get_recent_interactions_context(current_user.id, limit_interactions=1)
        
        summary = {
            "historical_available": historical["total_conversations"] > 0,
            "historical_count": historical["total_conversations"],
            "historical_topics": len(historical["topics"]),
            "recent_available": recent["total_interactions"] > 0,
            "recent_count": recent["total_interactions"],
            "session_active": recent["session_info"] is not None,
            "combined_context": f"{historical['total_conversations']} historical, {recent['total_interactions']} recent"
        }
        
        return {
            "success": True,
            "data": summary,
            "message": "Context summary retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving context summary: {str(e)}"
        ) 