#!/bin/bash
# Run ENTROPY FastAPI server

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting ENTROPY API server...${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copy .env.example to .env and configure API keys."
    exit 1
fi

# Check if ANTHROPIC_API_KEY is set
if ! grep -q "ANTHROPIC_API_KEY=sk-" .env 2>/dev/null; then
    echo "⚠️  ANTHROPIC_API_KEY not configured in .env"
    echo "   Please add: ANTHROPIC_API_KEY=sk-ant-..."
    exit 1
fi

echo -e "${GREEN}✅ Environment configured${NC}"
echo ""
echo "Starting server at http://localhost:8000"
echo "  • Swagger UI: http://localhost:8000/docs"
echo "  • ReDoc:      http://localhost:8000/redoc"
echo "  • Health:     http://localhost:8000/health"
echo ""

# Run uvicorn
uvicorn entropy.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info
