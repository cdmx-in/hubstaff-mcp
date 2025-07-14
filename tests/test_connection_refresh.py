#!/usr/bin/env python3
"""Test script to verify Hubstaff MCP connection with refresh token."""

import asyncio
import os
import sys
from pathlib import Path

import pytest

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from hubstaff_mcp.client import HubstaffClient, HubstaffAPIError


@pytest.mark.asyncio
async def test_connection():
    """Test the Hubstaff API connection."""
    try:
        # Load environment variables from .env file if present
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("dotenv not installed, relying on environment variables")
        
        # Check if refresh token is available
        refresh_token = os.getenv("HUBSTAFF_REFRESH_TOKEN")
        if not refresh_token:
            print("❌ HUBSTAFF_REFRESH_TOKEN environment variable not set")
            print("Please set your Hubstaff personal access token as HUBSTAFF_REFRESH_TOKEN")
            return False
        
        print("🔧 Initializing Hubstaff client...")
        client = HubstaffClient()
        
        print("🔑 Testing token refresh...")
        access_token = await client._refresh_access_token()
        print(f"✅ Successfully obtained access token: {access_token[:10]}...")
        
        print("👤 Testing API call - getting current user...")
        user = await client.get_current_user()
        print(f"✅ Current user: {user.get('name')} ({user.get('email')})")
        
        print("🏢 Testing API call - getting organizations...")
        organizations = await client.get_organizations()
        if organizations:
            for org in organizations:
                print(f"✅ Organization: {org.get('name')} (ID: {org.get('id')})")
        else:
            print("ℹ️  No organizations found")
        
        print("🎉 All tests passed! Hubstaff MCP connection is working correctly.")
        return True
        
    except HubstaffAPIError as e:
        print(f"❌ Hubstaff API Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def main():
    """Main function."""
    print("🚀 Testing Hubstaff MCP Connection...")
    print("=" * 50)
    
    success = await test_connection()
    
    print("=" * 50)
    if success:
        print("✅ Connection test completed successfully!")
        sys.exit(0)
    else:
        print("❌ Connection test failed!")
        print("\n📋 Troubleshooting steps:")
        print("1. Make sure you have a valid Hubstaff personal access token")
        print("2. Set the HUBSTAFF_REFRESH_TOKEN environment variable")
        print("3. Or create a .env file with HUBSTAFF_REFRESH_TOKEN=your_token")
        print("4. Ensure your token has the necessary permissions")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
