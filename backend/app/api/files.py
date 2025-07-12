from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os
import tempfile
from datetime import datetime
from ..database import get_sync_db
from ..models import User, UploadedFile, Conversation
from ..auth import get_current_user

router = APIRouter(prefix="/files", tags=["files"])

# Store temporary file chunks
temp_chunks = {}

def parse_chatgpt_export(file_content: str) -> List[dict]:
    """
    Parse ChatGPT export file content and extract conversations.
    Supports both JSON and text formats.
    """
    conversations = []
    
    try:
        # Try to parse as JSON first
        data = json.loads(file_content)
        
        # Handle different ChatGPT export formats
        if isinstance(data, list):
            # Direct conversation list
            conversations = data
        elif isinstance(data, dict):
            # Wrapped in an object
            if 'conversations' in data:
                conversations = data['conversations']
            elif 'data' in data:
                conversations = data['data']
            else:
                # Single conversation
                conversations = [data]
        
    except json.JSONDecodeError:
        # Try to parse as text format
        lines = file_content.split('\n')
        current_conversation = {"messages": []}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for conversation markers
            if line.startswith('=== Conversation') or line.startswith('---'):
                if current_conversation["messages"]:
                    conversations.append(current_conversation)
                current_conversation = {"messages": []}
            elif ':' in line:
                # Try to parse as "Role: Message" format
                parts = line.split(':', 1)
                if len(parts) == 2:
                    role, message = parts
                    current_conversation["messages"].append({
                        "role": role.strip().lower(),
                        "content": message.strip()
                    })
        
        # Add the last conversation
        if current_conversation["messages"]:
            conversations.append(current_conversation)
    
    return conversations

@router.post("/upload-chunk")
async def upload_chunk(
    chunk: UploadFile = File(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    filename: str = Form(...),
    upload_id: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Upload a chunk of a large file.
    """
    # Validate file type
    allowed_extensions = ['.json', '.txt', '.md']
    file_extension = os.path.splitext(filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Read chunk content
    try:
        chunk_content = await chunk.read()
        
        # Store chunk in temporary storage
        if upload_id not in temp_chunks:
            temp_chunks[upload_id] = {
                'chunks': {},
                'filename': filename,
                'user_id': current_user.id,
                'total_chunks': total_chunks
            }
        
        temp_chunks[upload_id]['chunks'][chunk_index] = chunk_content
        
        return {
            "message": f"Chunk {chunk_index + 1}/{total_chunks} uploaded successfully",
            "upload_id": upload_id,
            "chunk_index": chunk_index,
            "total_chunks": total_chunks
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading chunk: {str(e)}")

@router.post("/complete-upload")
async def complete_upload(
    upload_id: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Complete the chunked upload by combining all chunks and processing the file.
    """
    if upload_id not in temp_chunks:
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    upload_data = temp_chunks[upload_id]
    
    # Verify all chunks are present
    if len(upload_data['chunks']) != upload_data['total_chunks']:
        raise HTTPException(status_code=400, detail="Not all chunks received")
    
    # Combine chunks in order
    try:
        combined_content = b''
        for i in range(upload_data['total_chunks']):
            if i not in upload_data['chunks']:
                raise HTTPException(status_code=400, detail=f"Missing chunk {i}")
            combined_content += upload_data['chunks'][i]
        
        # Check total file size (100MB limit for chunked uploads)
        if len(combined_content) > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=400, 
                detail="File size too large. Maximum 100MB allowed for chunked uploads."
            )
        
        file_content = combined_content.decode('utf-8')
        
        # Parse conversations
        conversations_data = parse_chatgpt_export(file_content)
        
        if not conversations_data:
            raise HTTPException(status_code=400, detail="No conversations found in file")
        
        # Save uploaded file record
        uploaded_file = UploadedFile(
            filename=upload_data['filename'],
            user_id=current_user.id
        )
        db.add(uploaded_file)
        db.flush()  # Get the ID
        
        # Save conversations
        saved_conversations = []
        for conv_data in conversations_data:
            # Extract conversation title and content
            title = None
            content = ""
            
            if "title" in conv_data:
                title = conv_data["title"]
            elif "messages" in conv_data and conv_data["messages"]:
                # Use first message as title
                first_msg = conv_data["messages"][0]
                if isinstance(first_msg, dict) and "content" in first_msg:
                    title = first_msg["content"][:100] + "..." if len(first_msg["content"]) > 100 else first_msg["content"]
            
            # Convert conversation to string content
            if "messages" in conv_data:
                for msg in conv_data["messages"]:
                    if isinstance(msg, dict):
                        role = msg.get("role", "unknown")
                        msg_content = msg.get("content", "")
                        content += f"{role.upper()}: {msg_content}\n\n"
                    else:
                        content += f"{msg}\n\n"
            else:
                content = str(conv_data)
            
            conversation = Conversation(
                title=title,
                content=content,
                user_id=current_user.id,
                file_id=uploaded_file.id
            )
            db.add(conversation)
            saved_conversations.append(conversation)
        
        db.commit()
        
        # Clean up temporary chunks
        del temp_chunks[upload_id]
        
        return {
            "message": "File uploaded and processed successfully",
            "file_id": uploaded_file.id,
            "filename": uploaded_file.filename,
            "conversations_count": len(saved_conversations),
            "uploaded_at": uploaded_file.upload_time.isoformat()
        }
        
    except Exception as e:
        # Clean up on error
        if upload_id in temp_chunks:
            del temp_chunks[upload_id]
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Upload and process a ChatGPT export file (for smaller files).
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    allowed_extensions = ['.json', '.txt', '.md']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Read file content
    try:
        content = await file.read()
        
        # Check file size (50MB limit for single upload)
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=400, 
                detail="File size too large. Use chunked upload for files larger than 50MB."
            )
        
        file_content = content.decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    # Parse conversations
    try:
        conversations_data = parse_chatgpt_export(file_content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")
    
    if not conversations_data:
        raise HTTPException(status_code=400, detail="No conversations found in file")
    
    # Save uploaded file record
    uploaded_file = UploadedFile(
        filename=file.filename,
        user_id=current_user.id
    )
    db.add(uploaded_file)
    db.flush()  # Get the ID
    
    # Save conversations
    saved_conversations = []
    for conv_data in conversations_data:
        # Extract conversation title and content
        title = None
        content = ""
        
        if "title" in conv_data:
            title = conv_data["title"]
        elif "messages" in conv_data and conv_data["messages"]:
            # Use first message as title
            first_msg = conv_data["messages"][0]
            if isinstance(first_msg, dict) and "content" in first_msg:
                title = first_msg["content"][:100] + "..." if len(first_msg["content"]) > 100 else first_msg["content"]
        
        # Convert conversation to string content
        if "messages" in conv_data:
            for msg in conv_data["messages"]:
                if isinstance(msg, dict):
                    role = msg.get("role", "unknown")
                    msg_content = msg.get("content", "")
                    content += f"{role.upper()}: {msg_content}\n\n"
                else:
                    content += f"{msg}\n\n"
        else:
            content = str(conv_data)
        
        conversation = Conversation(
            title=title,
            content=content,
            user_id=current_user.id,
            file_id=uploaded_file.id
        )
        db.add(conversation)
        saved_conversations.append(conversation)
    
    db.commit()
    
    return {
        "message": "File uploaded successfully",
        "file_id": uploaded_file.id,
        "filename": uploaded_file.filename,
        "conversations_count": len(saved_conversations),
        "uploaded_at": uploaded_file.upload_time.isoformat()
    }

@router.get("/")
async def get_user_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get all files uploaded by the current user.
    """
    files = db.query(UploadedFile).filter(UploadedFile.user_id == current_user.id).all()
    
    return [
        {
            "id": file.id,
            "filename": file.filename,
            "upload_time": file.upload_time.isoformat(),
            "conversations_count": len(file.conversations)
        }
        for file in files
    ]

@router.get("/{file_id}")
async def get_file_details(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get details of a specific uploaded file.
    """
    file = db.query(UploadedFile).filter(
        UploadedFile.id == file_id,
        UploadedFile.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "id": file.id,
        "filename": file.filename,
        "upload_time": file.upload_time.isoformat(),
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "content_preview": conv.content[:200] + "..." if len(conv.content) > 200 else conv.content,
                "created_at": conv.created_at.isoformat()
            }
            for conv in file.conversations
        ]
    } 