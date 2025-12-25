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


# Table names (for Supabase queries)
USERS_TABLE = "users"
WORKSPACES_TABLE = "workspaces"
CONTENTS_TABLE = "contents"
WORKFLOWS_TABLE = "workflows"
JOBS_TABLE = "jobs"
SOCIAL_ACCOUNTS_TABLE = "social_accounts"
ANALYTICS_TABLE = "analytics"
