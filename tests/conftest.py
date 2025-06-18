"""Test configuration for hubstaff-mcp."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from hubstaff_mcp.client import HubstaffClient


@pytest.fixture
def mock_hubstaff_client():
    """Create a mock Hubstaff client for testing."""
    with patch.dict("os.environ", {"HUBSTAFF_REFRESH_TOKEN": "test_refresh_token"}):
        client = HubstaffClient()
        return client


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
