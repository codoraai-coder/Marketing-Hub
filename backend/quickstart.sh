#!/bin/bash

# Quick Start Guide for MCP Hub Backend

echo "🎯 MCP Hub Backend - Quick Start"
echo "=================================="
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 20+"
    exit 1
fi

echo "✅ Node.js $(node --version)"
echo "✅ npm $(npm --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

echo ""
echo "🐘 Database Setup:"
echo "Run these commands to start PostgreSQL and Redis:"
echo ""
echo "  docker run --name mcp-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=mcp_hub -p 5432:5432 -d postgres:15"
echo "  docker run --name mcp-redis -p 6379:6379 -d redis:7"
echo ""
echo "Or run: ./setup.sh"
echo ""

echo "⚙️  Environment Setup:"
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env with your AWS credentials"
else
    echo "✅ .env already exists"
fi

echo ""
echo "🚀 To start the backend:"
echo "  npm run start:dev"
echo ""
echo "📖 Documentation:"
echo "  - README.md - Getting started"
echo "  - ARCHITECTURE.md - System design"
echo ""
echo "🎯 MCP is ready for setup!"
