#!/bin/bash

# MCP Hub Backend Setup Script

echo "🚀 Setting up MCP Hub Backend..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "❌ Docker is not running. Please start Docker first."
  exit 1
fi

# Start PostgreSQL
echo "📦 Starting PostgreSQL..."
docker run --name mcp-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=mcp_hub \
  -p 5432:5432 \
  -d postgres:15 2>/dev/null || docker start mcp-postgres

# Start Redis
echo "📦 Starting Redis..."
docker run --name mcp-redis \
  -p 6379:6379 \
  -d redis:7 2>/dev/null || docker start mcp-redis

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
sleep 5

# Check if .env exists
if [ ! -f .env ]; then
  echo "📝 Creating .env file..."
  cp .env.example .env
  echo "⚠️  Please update .env with your AWS credentials"
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your AWS credentials"
echo "2. Run: npm run start:dev"
echo "3. Visit: http://localhost:3000"
