from fastapi import APIRouter, HTTPException
from app.schemas import (
    GenerateTopicRequest, MotivationalPostResponse, BlogPostResponse,
    CaptionRequest, CaptionResponse,
    HashtagRequest, HashtagResponse,
    ContentOptimizeRequest, ContentOptimizeResponse
)
from app.services.tool_registry import ToolRegistry
from datetime import datetime
import uuid

router = APIRouter()

# Initialize tool registry
tool_registry = ToolRegistry()


@router.post("/generate/caption", response_model=CaptionResponse, status_code=200)
async def generate_caption(request: CaptionRequest):
    """
    Generate a social media caption.
    
    Generates an engaging caption for the given topic and platform.
    """
    try:
        result = await tool_registry.execute_tool(
            "caption_generator",
            {
                "topic": request.topic,
                "platform": request.platform,
                "tone": request.tone,
                "include_emojis": request.include_emojis,
                "include_hashtags": request.include_hashtags
            }
        )
        
        return CaptionResponse(
            id=str(uuid.uuid4()),
            caption=result["result"]["caption"],
            platform=request.platform,
            tone=request.tone,
            created_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Caption generation failed: {str(e)}")


@router.post("/generate/hashtags", response_model=HashtagResponse, status_code=200)
async def generate_hashtags(request: HashtagRequest):
    """
    Generate relevant hashtags.
    
    Generates trending and relevant hashtags for the given topic.
    """
    try:
        result = await tool_registry.execute_tool(
            "hashtag_generator",
            {
                "topic": request.topic,
                "count": request.count,
                "platform": request.platform
            }
        )
        
        return HashtagResponse(
            id=str(uuid.uuid4()),
            hashtags=result["result"]["hashtags"],
            count=len(result["result"]["hashtags"]),
            platform=request.platform,
            created_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hashtag generation failed: {str(e)}")


@router.post("/generate/optimize", response_model=ContentOptimizeResponse, status_code=200)
async def optimize_content(request: ContentOptimizeRequest):
    """
    Optimize content for better engagement.
    
    Optimizes the given content based on goal, audience, and platform.
    """
    try:
        result = await tool_registry.execute_tool(
            "content_optimizer",
            {
                "content": request.content,
                "goal": request.goal,
                "audience": request.audience,
                "platform": request.platform
            }
        )
        
        return ContentOptimizeResponse(
            id=str(uuid.uuid4()),
            original=request.content,
            optimized=result["result"]["optimized"],
            goal=request.goal,
            platform=request.platform,
            created_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content optimization failed: {str(e)}")
