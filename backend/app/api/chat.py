from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.db.session import get_db
from app.models.entities import Session, Message, Artifact
from app.schemas.schemas import ChatRequest, ChatResponse, ArtifactResponse
from app.services.agent.router import pi_agent

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def process_chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    # 1. Verify session exists
    stmt = select(Session).where(Session.id == req.session_id)
    res = await db.execute(stmt)
    db_session = res.scalar_one_or_none()
    if not db_session:
        raise HTTPException(status_code=404, detail=f"Session '{req.session_id}' not found")

    # 2. Persist user message
    user_msg = Message(
        session_id=req.session_id,
        role="user",
        content=req.message,
        sources=[]
    )
    db.add(user_msg)
    await db.flush()

    # 3. Retrieve prior session history for multi-turn conversational grounding
    hist_stmt = (
        select(Message)
        .where(Message.session_id == req.session_id)
        .order_by(Message.created_at)
    )
    hist_res = await db.execute(hist_stmt)
    history_records = hist_res.scalars().all()
    history = [{"role": m.role, "content": m.content} for m in history_records]

    # 4. Execute Pi Agent Router
    response_text, citations, artifact_dict, meta = await pi_agent.execute(
        session_id=req.session_id,
        message=req.message,
        history=history,
        workflow=req.workflow or "auto",
        provider_name=req.provider,
        model_name=req.model
    )

    # 5. Handle artifact persistence if generated
    saved_artifact = None
    if artifact_dict:
        saved_artifact = Artifact(
            session_id=req.session_id,
            title=artifact_dict["title"],
            artifact_type=artifact_dict["artifact_type"],
            content=artifact_dict["content"],
            metadata_=artifact_dict.get("metadata", {})
        )
        db.add(saved_artifact)
        await db.flush()

    # 6. Persist assistant message
    asst_msg = Message(
        session_id=req.session_id,
        role="assistant",
        content=response_text,
        sources=[c.model_dump() for c in citations],
        artifact_id=saved_artifact.id if saved_artifact else None,
        execution_metadata=meta
    )
    db.add(asst_msg)

    # Update session title if default
    if db_session.title in ["New Research Session", "New Editorial Session"]:
        db_session.title = req.message[:50].strip() + ("..." if len(req.message) > 50 else "")

    db_session.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(asst_msg)

    artifact_resp = None
    if saved_artifact:
        artifact_resp = ArtifactResponse(
            id=saved_artifact.id,
            session_id=saved_artifact.session_id,
            title=saved_artifact.title,
            artifact_type=saved_artifact.artifact_type,
            content=saved_artifact.content,
            metadata=saved_artifact.metadata_ or {},
            created_at=saved_artifact.created_at,
            updated_at=saved_artifact.updated_at
        )

    return ChatResponse(
        session_id=req.session_id,
        message_id=asst_msg.id,
        role="assistant",
        content=response_text,
        sources=citations,
        artifact=artifact_resp,
        execution_metadata=meta
    )
