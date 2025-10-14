#!/bin/bash
# Run ENTROPY terminal chat interface

set -e

# Colors
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting ENTROPY terminal chat...${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copy .env.example to .env and configure API keys."
    exit 1
fi

# Run the chat
python -m entropy.cli.chat
