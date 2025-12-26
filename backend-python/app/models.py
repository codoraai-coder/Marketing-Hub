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


# Table names (for Supabase queries)
USERS_TABLE = "users"
WORKSPACES_TABLE = "workspaces"
WORKFLOWS_TABLE = "workflows"
JOBS_TABLE = "jobs"
SOCIAL_ACCOUNTS_TABLE = "social_accounts"
ANALYTICS_TABLE = "analytics"
CONTENT_TABLE = "content"
