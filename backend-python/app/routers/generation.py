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


@router.post("/generate/motivational_post", response_model=MotivationalPostResponse, status_code=200)
async def generate_motivational_post(request: GenerateTopicRequest):
    """
    Generate a motivational post with quote and image.
    
    Generates a unique motivational quote and a styled background image,
    uploads to S3, and returns the record.
    """
    try:
        # Generate quote using caption_generator
        caption_result = await tool_registry.execute_tool(
            "caption_generator",
            {"topic": request.topic, "tone": "motivational", "include_emojis": True}
        )
        quote_text = caption_result["result"]["caption"]
        
        # Generate image using image_generator
        image_result = await tool_registry.execute_tool(
            "image_generator",
            {"topic": request.topic, "style": "motivational and inspiring"}
        )
        image_url = image_result["result"]["image_url"]
        
        post_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        
        return MotivationalPostResponse(
            id=post_id,
            topic=request.topic,
            quote_text=quote_text,
            image_url=image_url,
            created_at=created_at.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/generate/blog_post", response_model=BlogPostResponse, status_code=200)
async def generate_blog_post(request: GenerateTopicRequest):
    """
    Generate a blog post with document and cover image.
    
    Generates a full blog post (Word DOCX) with RAG-enhanced content 
    and a cover image, uploads to S3.
    """
    try:
        # Generate blog content using blog_generator
        blog_result = await tool_registry.execute_tool(
            "blog_generator",
            {"topic": request.topic}
        )
        docx_url = blog_result["result"]["docx_url"]
        
        # Generate cover image using image_generator
        image_result = await tool_registry.execute_tool(
            "image_generator",
            {"topic": request.topic, "style": "blog cover, professional"}
        )
        cover_url = image_result["result"]["image_url"]
        
        post_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        
        return BlogPostResponse(
            id=post_id,
            topic=request.topic,
            docx_url=docx_url,
            cover_url=cover_url,
            created_at=created_at.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


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
