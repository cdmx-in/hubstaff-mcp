#!/usr/bin/env bash
# Setup script for Hubstaff MCP Server

set -e

echo "🚀 Setting up Hubstaff MCP Server..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed successfully"
    echo "⚠️  Please restart your terminal and run this script again"
    exit 1
fi

echo "✅ uv found"

# Create virtual environment and install dependencies
echo "📦 Installing dependencies..."
uv sync

echo "🔑 Setting up environment..."
if [ ! -f ".env" ]; then
    cp example.env .env
    echo "✅ Created .env file from example.env"
    echo "⚠️  Please edit .env and add your Hubstaff Personal Access Token"
    echo "   You can get a token from: Hubstaff Settings → Personal Access Tokens"
else
    echo "ℹ️  .env file already exists"
fi

echo ""
echo "🎉 Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your HUBSTAFF_ACCESS_TOKEN"
echo "2. Test the connection: uv run python test_connection.py"
echo "3. Run the server: uv run hubstaff-mcp"
echo ""
echo "For Claude Desktop integration, add this to your config:"
echo '{
  "mcpServers": {
    "hubstaff": {
      "command": "uv",
      "args": [
        "--directory",
        "'$(pwd)'",
        "run",
        "hubstaff-mcp"
      ]
    }
  }
}'
