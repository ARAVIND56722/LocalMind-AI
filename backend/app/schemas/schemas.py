from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# --- Source Citation Schemas ---
class SourceCitation(BaseModel):
    id: str
    title: str
    guest: Optional[str] = None
    timestamp: Optional[str] = None
    speaker: Optional[str] = None
    url: Optional[str] = None
    quote: str
    score: Optional[float] = None

# --- Artifact Schemas ---
class ArtifactBase(BaseModel):
    title: str
    artifact_type: str = Field(..., description="'markdown', 'html', or 'ship30_essay'")
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ArtifactCreate(ArtifactBase):
    session_id: str

class ArtifactResponse(ArtifactBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    session_id: str
    created_at: datetime
    updated_at: datetime

# --- Message Schemas ---
class MessageBase(BaseModel):
    role: str
    content: str
    sources: List[SourceCitation] = Field(default_factory=list)
    artifact_id: Optional[str] = None
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)

class MessageCreate(BaseModel):
    content: str
    provider: Optional[str] = None
    model: Optional[str] = None

class MessageResponse(MessageBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    session_id: str
    created_at: datetime

# --- Session Schemas ---
class SessionCreate(BaseModel):
    title: Optional[str] = "New Research Session"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SessionUpdate(BaseModel):
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    messages: List[MessageResponse] = Field(default_factory=list)

class SessionListItem(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

# --- Chat & Skill Request Schemas ---
class ChatRequest(BaseModel):
    session_id: str
    message: str
    provider: Optional[str] = None
    model: Optional[str] = None
    workflow: Optional[str] = Field("auto", description="'auto', 'qa', 'ship30', 'artifact'")

class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    role: str = "assistant"
    content: str
    sources: List[SourceCitation] = Field(default_factory=list)
    artifact: Optional[ArtifactResponse] = None
    execution_metadata: Dict[str, Any] = Field(default_factory=dict)

class Ship30Request(BaseModel):
    session_id: str
    topic: str
    instructions: Optional[str] = None
    target_word_count: int = 1250
    provider: Optional[str] = None
    model: Optional[str] = None

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    available: bool
    is_default: bool = False
    details: Optional[str] = None

class ModelListResponse(BaseModel):
    active_provider: str
    active_model: str
    models: List[ModelInfo]
