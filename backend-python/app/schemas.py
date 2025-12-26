from pydantic import BaseModel, UUID4, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SocialPlatform(str, Enum):
    LINKEDIN = "linkedin"


class ContentType(str, Enum):
    BLOG_POST = "blog_post"
    IMAGE = "image"
    CAPTION = "caption"
    HASHTAGS = "hashtags"
    OPTIMIZED_CONTENT = "optimized_content"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    USED = "used"
    POSTED = "posted"


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


# Workflow Schemas
class WorkflowStepDto(BaseModel):
    """Schema for creating a workflow step"""
    order: int
    name: Optional[str] = None
    tool_name: str
    config: Optional[Dict[str, Any]] = None


class WorkflowStepResponse(BaseModel):
    """Schema for workflow step in responses"""
    id: str
    order: int
    name: Optional[str]
    tool_name: str
    config: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class CreateWorkflowDto(BaseModel):
    """Schema for creating a new workflow"""
    workspace_id: UUID4
    name: str
    description: Optional[str] = None
    target_platform: Optional[SocialPlatform] = None
    steps: List[WorkflowStepDto]


class UpdateWorkflowDto(BaseModel):
    """Schema for updating an existing workflow"""
    name: Optional[str] = None
    description: Optional[str] = None
    target_platform: Optional[SocialPlatform] = None
    steps: Optional[List[WorkflowStepDto]] = None


class WorkflowListResponse(BaseModel):
    """Schema for workflow in list view (summary without steps)"""
    id: UUID4
    name: str
    description: Optional[str]
    target_platform: Optional[str]
    last_run_at: Optional[datetime]
    last_run_status: Optional[JobStatus]
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowResponse(BaseModel):
    """Schema for detailed workflow view (includes steps)"""
    id: UUID4
    workspace_id: UUID4
    name: str
    description: Optional[str]
    target_platform: Optional[str]
    steps: List[WorkflowStepResponse]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Job Schemas
class RunWorkflowResponse(BaseModel):
    """Response when triggering workflow execution"""
    job_id: UUID4
    workflow_id: UUID4
    status: JobStatus
    started_at: datetime

    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    id: UUID4
    workflow_id: UUID4
    status: JobStatus
    logs: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: Optional[int] = None
    current_step: Optional[int] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


# Generation Endpoint Schemas
class GenerateTopicRequest(BaseModel):
    """Request schema for generation endpoints"""
    topic: str = Field(..., min_length=1, description="Topic for content generation")


class CaptionRequest(BaseModel):
    """Request schema for caption generation"""
    topic: str = Field(..., min_length=1, description="Topic for caption")
    platform: Optional[str] = Field(default="linkedin", description="Target platform")
    tone: Optional[str] = Field(default="professional", description="Tone of the caption")
    include_emojis: Optional[bool] = Field(default=True, description="Include emojis")
    include_hashtags: Optional[bool] = Field(default=True, description="Include hashtags")


class HashtagRequest(BaseModel):
    """Request schema for hashtag generation"""
    topic: str = Field(..., min_length=1, description="Topic for hashtags")
    count: Optional[int] = Field(default=5, description="Number of hashtags to generate")
    platform: Optional[str] = Field(default="linkedin", description="Target platform")


class ContentOptimizeRequest(BaseModel):
    """Request schema for content optimization"""
    content: str = Field(..., min_length=1, description="Content to optimize")
    goal: Optional[str] = Field(default="engagement", description="Optimization goal")
    audience: Optional[str] = Field(default="professionals", description="Target audience")
    platform: Optional[str] = Field(default="linkedin", description="Target platform")


class MotivationalPostResponse(BaseModel):
    """Response for motivational post generation"""
    id: str
    topic: str
    quote_text: str
    image_url: str
    created_at: str


class BlogPostResponse(BaseModel):
    """Response for blog post generation"""
    id: str
    topic: str
    docx_url: str
    cover_url: str
    created_at: str


class CaptionResponse(BaseModel):
    """Response for caption generation"""
    id: str
    caption: str
    platform: str
    tone: str
    created_at: str


class HashtagResponse(BaseModel):
    """Response for hashtag generation"""
    id: str
    hashtags: List[str]
    count: int
    platform: str
    created_at: str


class ContentOptimizeResponse(BaseModel):
    """Response for content optimization"""
    id: str
    original: str
    optimized: str
    goal: str
    platform: str
    created_at: str


# Content Schemas
class CreateContentDto(BaseModel):
    """Schema for creating new content"""
    workspace_id: UUID4
    job_id: UUID4
    workflow_step_id: str
    content_type: ContentType
    title: Optional[str] = None
    data: Dict[str, Any]
    status: Optional[ContentStatus] = ContentStatus.DRAFT


class UpdateContentDto(BaseModel):
    """Schema for updating content"""
    title: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    status: Optional[ContentStatus] = None


class ContentResponse(BaseModel):
    """Schema for content in responses"""
    id: UUID4
    workspace_id: UUID4
    job_id: UUID4
    workflow_step_id: str
    content_type: ContentType
    title: Optional[str]
    data: Dict[str, Any]
    status: ContentStatus
    created_at: datetime
    updated_at: Optional[datetime]
    approved_at: Optional[datetime]
    posted_at: Optional[datetime]

    class Config:
        from_attributes = True

