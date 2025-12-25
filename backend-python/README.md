# FastAPI MCP Hub Backend

A FastAPI-based backend for the Marketing Content Platform (MCP) Hub.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
Copy `.env.example` to `.env` and update with your credentials.

3. Run the application:
```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --port 3000
```

## Project Structure

```
backend-python/
├── main.py              # Application entry point
├── app/
│   ├── __init__.py
│   ├── database.py      # Database configuration
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── routers/         # API route handlers
│   │   ├── workspace.py
│   │   ├── content.py
│   │   ├── workflow.py
│   │   └── job.py
│   └── services/        # Business logic services
│       └── s3_service.py
├── requirements.txt     # Python dependencies
└── .env                # Environment variables
```

## API Endpoints

- **Workspaces**: `/api/workspaces`
- **Content**: `/api/content`
- **Workflows**: `/api/workflows`
- **Jobs**: `/api/jobs`

## Features

- ✅ RESTful API with FastAPI
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ Supabase integration
- ✅ AWS S3 storage support
- ✅ Automatic API documentation (Swagger UI at `/docs`)
- ✅ Pydantic data validation
- ✅ CORS enabled
