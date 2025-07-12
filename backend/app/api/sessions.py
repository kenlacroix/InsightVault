from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..database import get_sync_db
from ..models import User, UserSession, UserInteraction
from ..auth import get_current_user

router = APIRouter(prefix="/sessions", tags=["sessions"])

class SessionCreate(BaseModel):
    context_summary: Optional[str] = None

class SessionResponse(BaseModel):
    id: int
    session_start: datetime
    session_end: Optional[datetime]
    context_summary: Optional[str]
    interaction_count: int

class InteractionResponse(BaseModel):
    id: int
    user_question: str
    ai_response: str
    context_used: Optional[List[str]]
    created_at: datetime
    interaction_metadata: Optional[dict]

class RecentInteractionsResponse(BaseModel):
    session: SessionResponse
    interactions: List[InteractionResponse]

@router.post("/start", response_model=SessionResponse)
async def start_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Start a new user session"""
    # End any existing active session
    active_session = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.session_end.is_(None)
    ).first()
    
    if active_session:
        active_session.session_end = datetime.utcnow()
        db.commit()
    
    # Create new session
    new_session = UserSession()
    new_session.user_id = current_user.id
    new_session.context_summary = session_data.context_summary
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return SessionResponse(
        id=new_session.id,
        session_start=new_session.session_start,
        session_end=new_session.session_end,
        context_summary=new_session.context_summary,
        interaction_count=0
    )

@router.post("/{session_id}/end")
async def end_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """End a user session"""
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.session_end = datetime.utcnow()
    db.commit()
    
    return {"message": "Session ended successfully"}

@router.get("/current", response_model=SessionResponse)
async def get_current_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Get the current active session for the user"""
    session = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.session_end.is_(None)
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="No active session found")
    
    interaction_count = db.query(UserInteraction).filter(
        UserInteraction.session_id == session.id
    ).count()
    
    return SessionResponse(
        id=session.id,
        session_start=session.session_start,
        session_end=session.session_end,
        context_summary=session.context_summary,
        interaction_count=interaction_count
    )

@router.get("/recent", response_model=List[RecentInteractionsResponse])
async def get_recent_interactions(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Get recent interactions from the current session"""
    # Get current session
    session = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.session_end.is_(None)
    ).first()
    
    if not session:
        return []
    
    # Get recent interactions
    interactions = db.query(UserInteraction).filter(
        UserInteraction.session_id == session.id
    ).order_by(UserInteraction.created_at.desc()).limit(limit).all()
    
    interaction_responses = [
        InteractionResponse(
            id=interaction.id,
            user_question=interaction.user_question,
            ai_response=interaction.ai_response,
            context_used=interaction.context_used,
            created_at=interaction.created_at,
            interaction_metadata=interaction.interaction_metadata
        )
        for interaction in interactions
    ]
    
    session_response = SessionResponse(
        id=session.id,
        session_start=session.session_start,
        session_end=session.session_end,
        context_summary=session.context_summary,
        interaction_count=len(interaction_responses)
    )
    
    return [RecentInteractionsResponse(
        session=session_response,
        interactions=interaction_responses
    )]

@router.get("/history", response_model=List[SessionResponse])
async def get_session_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Get session history for the user"""
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id
    ).order_by(UserSession.session_start.desc()).limit(limit).all()
    
    session_responses = []
    for session in sessions:
        interaction_count = db.query(UserInteraction).filter(
            UserInteraction.session_id == session.id
        ).count()
        
        session_responses.append(SessionResponse(
            id=session.id,
            session_start=session.session_start,
            session_end=session.session_end,
            context_summary=session.context_summary,
            interaction_count=interaction_count
        ))
    
    return session_responses

@router.get("/{session_id}/interactions", response_model=List[InteractionResponse])
async def get_session_interactions(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """Get all interactions for a specific session"""
    # Verify session belongs to user
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    interactions = db.query(UserInteraction).filter(
        UserInteraction.session_id == session_id
    ).order_by(UserInteraction.created_at.asc()).all()
    
    return [
        InteractionResponse(
            id=interaction.id,
            user_question=interaction.user_question,
            ai_response=interaction.ai_response,
            context_used=interaction.context_used,
            created_at=interaction.created_at,
            interaction_metadata=interaction.interaction_metadata
        )
        for interaction in interactions
    ] 