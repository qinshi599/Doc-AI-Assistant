#!/bin/bash

echo "🚀 ITDoc AI Assistant - Start"
echo "=================================="

# Check virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Activating virtual environment..."
    source venv/bin/activate
fi

# Check environment file
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    echo "Please copy env_example.txt to .env and configure your API keys"
    exit 1
fi

echo "✅ Environment check complete"

# Setup vector store if requested
if [ "$1" = "--setup" ]; then
    echo ""
    echo "🔄 Setting up vector store..."
    python3 scripts/setup_vectorstore.py
    if [ $? -ne 0 ]; then
        echo "❌ Vector store setup failed"
        exit 1
    fi
    echo "✅ Vector store setup complete"
fi

# Install Node.js dependencies if needed
if [ ! -d "backend/node_modules" ]; then
    echo ""
    echo "📦 Installing Node.js dependencies..."
    cd backend && npm install && cd ..
fi

# Start backend service
echo ""
echo "🚀 Starting API server..."
cd backend
npm run dev &
BACKEND_PID=$!
cd ..

# Wait for server startup
sleep 3

# Test server
echo ""
echo "🧪 Testing server..."
if curl -s http://localhost:3001/health > /dev/null; then
    echo "✅ Server started successfully!"
else
    echo "❌ Server startup failed"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 ITDoc AI Assistant is running!"
echo ""
echo "📍 Available endpoints:"
echo "  - Health: http://localhost:3001/health"  
echo "  - Q&A: http://localhost:3001/api/ask-langchain"
echo ""
echo "💡 Test command:"
echo '  curl -X POST http://localhost:3001/api/ask-langchain \'
echo '    -H "Content-Type: application/json" \'
echo '    -d '"'"'{"question": "How to troubleshoot Azure VM startup failures?"}'"'"
echo ""
echo "Press Ctrl+C to stop service"

# Wait for user to stop
trap 'echo ""; echo "🛑 Stopping service..."; kill $BACKEND_PID 2>/dev/null; exit 0' INT
wait
