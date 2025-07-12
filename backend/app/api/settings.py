from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime
import json
import os
from ..database import get_sync_db
from ..models import User
from ..auth import get_current_user
import openai

router = APIRouter(prefix="/settings", tags=["settings"])

class SettingsRequest(BaseModel):
    openai_api_key: str
    model: str = "gpt-4"
    max_tokens: int = 1500
    temperature: float = 0.7

class TestApiKeyRequest(BaseModel):
    api_key: str

class SettingsResponse(BaseModel):
    openai_api_key: str = ""
    model: str = "gpt-4"
    max_tokens: int = 1500
    temperature: float = 0.7

@router.get("/", response_model=SettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get current settings for the user.
    """
    try:
        # Load settings from config file
        config_file = "config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            return SettingsResponse(
                openai_api_key=config.get('openai_api_key', ''),
                model=config.get('model', 'gpt-4'),
                max_tokens=config.get('max_tokens', 1500),
                temperature=config.get('temperature', 0.7)
            )
        else:
            return SettingsResponse()
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading settings: {str(e)}"
        )

@router.post("/")
async def save_settings(
    request: SettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Save settings for the user.
    """
    try:
        # Validate API key format
        if request.openai_api_key and not request.openai_api_key.startswith('sk-'):
            raise HTTPException(
                status_code=400,
                detail="Invalid API key format. Should start with 'sk-'"
            )
        
        # Save to config file
        config_data = {
            "openai_api_key": request.openai_api_key,
            "model": request.model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        with open("config.json", 'w') as f:
            json.dump(config_data, f, indent=4)
        
        # Set environment variable for current session
        if request.openai_api_key:
            os.environ['OPENAI_API_KEY'] = request.openai_api_key
        
        return {"message": "Settings saved successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving settings: {str(e)}"
        )

@router.post("/test-api-key")
async def test_api_key(
    request: TestApiKeyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Test if the provided API key is valid.
    """
    try:
        # Validate API key format
        if not request.api_key.startswith('sk-'):
            raise HTTPException(
                status_code=400,
                detail="Invalid API key format. Should start with 'sk-'"
            )
        
        # Test the API key
        try:
            client = openai.OpenAI(api_key=request.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            return {"message": "API key is valid and working!"}
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"API key test failed: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error testing API key: {str(e)}"
        ) 