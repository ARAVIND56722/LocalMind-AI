from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.db.session import get_db
from app.models.entities import Session, Artifact
from app.schemas.schemas import ArtifactCreate, ArtifactResponse, Ship30Request
from app.services.skills.ship30 import ship30_skill

router = APIRouter(tags=["Skills & Artifacts"])

@router.post("/skills/ship30")
async def generate_ship30_essay(req: Ship30Request, db: AsyncSession = Depends(get_db)):
    # Verify session
    stmt = select(Session).where(Session.id == req.session_id)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    essay, citations, meta = await ship30_skill.generate_essay(
        topic=req.topic,
        user_instructions=req.instructions,
        target_words=req.target_word_count,
        provider_name=req.provider,
        model_name=req.model
    )

    # Persist as artifact
    db_artifact = Artifact(
        session_id=req.session_id,
        title=f"Ship 30 Essay: {req.topic[:50]}",
        artifact_type="markdown",
        content=essay,
        metadata_=meta
    )
    db.add(db_artifact)
    await db.commit()
    await db.refresh(db_artifact)

    return {
        "artifact_id": db_artifact.id,
        "title": db_artifact.title,
        "content": essay,
        "sources": citations,
        "metadata": meta
    }

@router.post("/artifacts", response_model=ArtifactResponse, status_code=status.HTTP_201_CREATED)
async def save_artifact(artifact_in: ArtifactCreate, db: AsyncSession = Depends(get_db)):
    # Verify session
    stmt = select(Session).where(Session.id == artifact_in.session_id)
    res = await db.execute(stmt)
    if not res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Session not found")

    db_artifact = Artifact(
        session_id=artifact_in.session_id,
        title=artifact_in.title,
        artifact_type=artifact_in.artifact_type,
        content=artifact_in.content,
        metadata_=artifact_in.metadata
    )
    db.add(db_artifact)
    await db.commit()
    await db.refresh(db_artifact)
    
    return ArtifactResponse(
        id=db_artifact.id,
        session_id=db_artifact.session_id,
        title=db_artifact.title,
        artifact_type=db_artifact.artifact_type,
        content=db_artifact.content,
        metadata=db_artifact.metadata_ or {},
        created_at=db_artifact.created_at,
        updated_at=db_artifact.updated_at
    )

@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Artifact).where(Artifact.id == artifact_id)
    res = await db.execute(stmt)
    art = res.scalar_one_or_none()
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found")

    return ArtifactResponse(
        id=art.id,
        session_id=art.session_id,
        title=art.title,
        artifact_type=art.artifact_type,
        content=art.content,
        metadata=art.metadata_ or {},
        created_at=art.created_at,
        updated_at=art.updated_at
    )

@router.get("/artifacts/session/{session_id}", response_model=List[ArtifactResponse])
async def list_session_artifacts(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Artifact).where(Artifact.session_id == session_id).order_by(desc(Artifact.created_at))
    res = await db.execute(stmt)
    arts = res.scalars().all()
    return [
        ArtifactResponse(
            id=a.id,
            session_id=a.session_id,
            title=a.title,
            artifact_type=a.artifact_type,
            content=a.content,
            metadata=a.metadata_ or {},
            created_at=a.created_at,
            updated_at=a.updated_at
        )
        for a in arts
    ]
