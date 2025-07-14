#!/usr/bin/env python3
"""Test script to reproduce the MCP error."""

import asyncio
import os
import sys
from pathlib import Path

import pytest

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set up environment
os.environ['HUBSTAFF_REFRESH_TOKEN'] = 'test_token'

from hubstaff_mcp.server import mcp, get_users


@pytest.mark.asyncio
async def test_mcp_function():
    """Test the get_users function directly."""
    try:
        print("Testing get_users function...")
        result = await get_users()
        print("Result:", result)
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mcp_function())
