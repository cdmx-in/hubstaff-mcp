#!/usr/bin/env python3
"""
Simple script to test the Hubstaff MCP server locally.
Run this to verify your setup is working.
"""

import asyncio
import os

# Load environment variables from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("ℹ️  python-dotenv not available, using system environment variables")

from hubstaff_mcp.client import HubstaffClient


async def main():
    """Test the Hubstaff client connection."""
    try:
        print("Testing Hubstaff MCP Server connection...")
        
        # Check if token is set
        token = os.getenv("HUBSTAFF_ACCESS_TOKEN")
        if not token:
            print("❌ HUBSTAFF_ACCESS_TOKEN environment variable not set")
            print("Please set your Hubstaff Personal Access Token:")
            print("export HUBSTAFF_ACCESS_TOKEN='your_token_here'")
            return
        
        # Initialize client
        client = HubstaffClient()
        print("✅ Client initialized successfully")
        
        # Test API connection
        user = await client.get_current_user()
        print(f"✅ API connection successful!")
        print(f"Connected as: {user.get('name', 'Unknown')} ({user.get('email', 'No email')})")
        
        # Get organizations
        orgs = await client.get_organizations()
        if orgs:
            print(f"✅ Found {len(orgs)} organization(s)")
            for org in orgs:
                print(f"   - {org.get('name')} (ID: {org.get('id')})")
        else:
            print("ℹ️  No organizations found")
        
        print("\n🎉 Setup is working correctly!")
        print("You can now use the MCP server with Claude Desktop or other MCP clients.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure your HUBSTAFF_ACCESS_TOKEN is valid")
        print("2. Check your internet connection")
        print("3. Verify your Hubstaff account has API access")


if __name__ == "__main__":
    asyncio.run(main())
