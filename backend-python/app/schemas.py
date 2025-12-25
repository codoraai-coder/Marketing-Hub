from pydantic import BaseModel, UUID4, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    BLOG = "blog"
    IMAGE = "image"
    CAPTION = "caption"
    DOC = "doc"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    USED = "used"
    POSTED = "posted"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SocialPlatform(str, Enum):
    LINKEDIN = "linkedin"


# Workspace Schemas
class CreateWorkspaceDto(BaseModel):
    owner_user_id: UUID4
    name: str


class WorkspaceResponse(BaseModel):
    id: UUID4
    owner_user_id: UUID4
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# Content Schemas
class CreateContentDto(BaseModel):
    workspace_id: UUID4
    type: ContentType
    s3_url: Optional[str] = None
    text_data: Optional[str] = None
    status: Optional[ContentStatus] = ContentStatus.DRAFT


class UpdateContentStatusDto(BaseModel):
    status: ContentStatus


class ContentResponse(BaseModel):
    id: UUID4
    workspace_id: UUID4
    type: ContentType
    s3_url: Optional[str]
    text_data: Optional[str]
    status: ContentStatus
    created_at: datetime

    class Config:
        from_attributes = True


# Workflow Schemas
class WorkflowStepDto(BaseModel):
    tool: str
    input: Optional[Dict[str, Any]] = None


class CreateWorkflowDto(BaseModel):
    workspace_id: UUID4
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStepDto]


class WorkflowResponse(BaseModel):
    id: UUID4
    workspace_id: UUID4
    name: str
    description: Optional[str]
    steps: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# Job Schemas
class JobResponse(BaseModel):
    id: UUID4
    workflow_id: UUID4
    status: JobStatus
    logs: Optional[Dict[str, Any]]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
