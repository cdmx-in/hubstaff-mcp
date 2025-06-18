#!/usr/bin/env bash
# Publish script for hubstaff-mcp package

set -e

echo "🚀 Publishing Hubstaff MCP Server to PyPI..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Run this script from the project root."
    exit 1
fi

# Check if dist directory exists and has files
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    echo "📦 Building distribution packages..."
    uv build
fi

echo "📋 Built packages:"
ls -la dist/

echo ""
echo "⚠️  IMPORTANT: Before publishing, make sure you have:"
echo "1. Updated the version in pyproject.toml"
echo "2. Updated your name and email in pyproject.toml"
echo "3. Set up your PyPI account and API token"
echo "4. Tested the package locally"
echo ""

read -p "🤔 Do you want to publish to PyPI? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Cancelled. You can publish later with: uv publish"
    exit 0
fi

# Publish to PyPI
echo "🚀 Publishing to PyPI..."
if command -v uv &> /dev/null; then
    uv publish
else
    echo "❌ uv not found. Please install uv first."
    exit 1
fi

echo "✅ Published successfully!"
echo ""
echo "🎉 Your package is now available on PyPI!"
echo "📦 Install with: pip install hubstaff-mcp"
echo "🔗 Or with uv: uv add hubstaff-mcp"
