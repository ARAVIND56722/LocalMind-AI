from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.db.session import get_db
from app.models.entities import Session, Message, Artifact
from app.schemas.schemas import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionListItem,
    MessageResponse
)

router = APIRouter(prefix="/sessions", tags=["Sessions"])

def build_session_response(s: Session, messages: List[Message] = None) -> SessionResponse:
    msg_list = []
    if messages:
        for m in messages:
            msg_list.append(MessageResponse(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                sources=m.sources or [],
                artifact_id=m.artifact_id,
                execution_metadata=m.execution_metadata or {},
                created_at=m.created_at
            ))
    return SessionResponse(
        id=s.id,
        title=s.title,
        created_at=s.created_at,
        updated_at=s.updated_at,
        metadata_=s.metadata_ or {},
        messages=msg_list
    )

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(session_in: SessionCreate, db: AsyncSession = Depends(get_db)):
    db_session = Session(
        title=session_in.title or "New Research Session",
        metadata_=session_in.metadata
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return build_session_response(db_session, [])

@router.get("", response_model=List[SessionListItem])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    stmt = select(Session).order_by(desc(Session.updated_at))
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    
    items = []
    for s in sessions:
        items.append(SessionListItem(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=0
        ))
    return items

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Session).where(Session.id == session_id)
    result = await db.execute(stmt)
    db_session = result.scalar_one_or_none()
    
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    msg_stmt = select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
    msg_result = await db.execute(msg_stmt)
    messages = msg_result.scalars().all()
    
    return build_session_response(db_session, messages)

@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, update_in: SessionUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Session).where(Session.id == session_id)
    result = await db.execute(stmt)
    db_session = result.scalar_one_or_none()
    
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if update_in.title is not None:
        db_session.title = update_in.title
    if update_in.metadata is not None:
        db_session.metadata_ = update_in.metadata
        
    await db.commit()
    await db.refresh(db_session)
    return build_session_response(db_session, [])

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Session).where(Session.id == session_id)
    result = await db.execute(stmt)
    db_session = result.scalar_one_or_none()
    
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    await db.delete(db_session)
    await db.commit()
    return None
