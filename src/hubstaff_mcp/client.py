"""Hubstaff API client for MCP server."""

import asyncio
import os
from datetime import date, datetime
from typing import Any, Dict, List, Optional
import httpx


class HubstaffAPIError(Exception):
    """Exception raised for Hubstaff API errors."""
    pass


class HubstaffClient:
    """Hubstaff API client with OAuth token management."""
    
    def __init__(self):
        """Initialize the client with refresh token from environment."""
        self.refresh_token = os.getenv("HUBSTAFF_REFRESH_TOKEN")
        if not self.refresh_token:
            raise ValueError(
                "Hubstaff refresh token (personal token) is required. "
                "Set the HUBSTAFF_REFRESH_TOKEN environment variable."
            )
        
        self.base_url = "https://api.hubstaff.com/v2"
        self.auth_url = "https://account.hubstaff.com/access_tokens"
        self.access_token = None
        self.token_expires_at = None
    
    async def _refresh_access_token(self) -> str:
        """Refresh the access token using the refresh token."""
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token
                }
                
                response = await client.post(self.auth_url, data=data)
                await response.raise_for_status()

                # Get the JSON response
                token_data = await response.json()

                # Extract the access token
                return token_data["access_token"]
                
        except Exception as e:
            # Get error details if it's an HTTP error
            if hasattr(e, 'response'):
                error_text = f"HTTP {e.response.status_code}: {e.response.text}"
            else:
                error_text = str(e)
            raise HubstaffAPIError(f"Token refresh failed - {error_text}")
    
    async def _ensure_access_token(self) -> str:
        """Ensure we have a valid access token."""
        if not self.access_token:
            self.access_token = await self._refresh_access_token()
        return self.access_token
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an authenticated request to the Hubstaff API."""
        access_token = await self._ensure_access_token()
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=headers, json=data)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=headers, json=data)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Handle 401 Unauthorized - token might be expired
                if response.status_code == 401:
                    # Refresh token and retry once
                    self.access_token = await self._refresh_access_token()
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    
                    if method.upper() == "GET":
                        response = await client.get(url, headers=headers, params=params)
                    elif method.upper() == "POST":
                        response = await client.post(url, headers=headers, json=data)
                    elif method.upper() == "PUT":
                        response = await client.put(url, headers=headers, json=data)
                    elif method.upper() == "DELETE":
                        response = await client.delete(url, headers=headers)
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            # Get error details if it's an HTTP error
            if hasattr(e, 'response'):
                try:
                    error_data = e.response.json()
                    error_msg = f"HTTP {e.response.status_code}: {error_data}"
                except Exception:
                    error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            else:
                error_msg = f"Request failed: {str(e)}"
            raise HubstaffAPIError(error_msg)
    
    # API Methods
    
    async def get_current_user(self) -> Dict[str, Any]:
        """Get information about the current user."""
        response = await self._make_request("GET", "/users/me")
        return response.get("user", response)
    
    async def get_users(self, organization_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get organization users."""
        endpoint = "/users"
        params = {}
        if organization_id:
            params["organization_id"] = organization_id
        
        response = await self._make_request("GET", endpoint, params=params)
        return response.get("users", [])
    
    async def get_organizations(self) -> List[Dict[str, Any]]:
        """Get user organizations."""
        response = await self._make_request("GET", "/organizations")
        return response.get("organizations", [])
    
    async def get_projects(self, organization_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get list of projects."""
        endpoint = "/projects"
        params = {}
        if organization_id:
            params["organization_id"] = organization_id
        
        response = await self._make_request("GET", endpoint, params=params)
        return response.get("projects", [])
    
    async def get_project(self, project_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific project."""
        response = await self._make_request("GET", f"/projects/{project_id}")
        return response.get("project", response)
    
    async def get_tasks(self, project_id: int) -> List[Dict[str, Any]]:
        """Get tasks for a specific project."""
        response = await self._make_request("GET", f"/projects/{project_id}/tasks")
        return response.get("tasks", [])
    
    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task."""
        response = await self._make_request("POST", "/tasks", data=task_data)
        return response.get("task", response)
    
    async def get_teams(self, organization_id: int) -> List[Dict[str, Any]]:
        """Get teams for an organization."""
        response = await self._make_request("GET", f"/organizations/{organization_id}/teams")
        return response.get("teams", [])
    
    async def get_time_entries(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        user_ids: Optional[List[int]] = None,
        project_ids: Optional[List[int]] = None,
        organization_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get time entries with optional filtering."""
        params = {}
        
        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["end_date"] = end_date.strftime("%Y-%m-%d")
        if user_ids:
            params["user_ids"] = ",".join(map(str, user_ids))
        if project_ids:
            params["project_ids"] = ",".join(map(str, project_ids))
        if organization_id:
            params["organization_id"] = organization_id
        
        response = await self._make_request("GET", "/time_entries", params=params)
        return response.get("time_entries", [])
    
    async def create_time_entry(self, time_entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new time entry."""
        response = await self._make_request("POST", "/time_entries", data=time_entry_data)
        return response.get("time_entry", response)
    
    async def update_time_entry(self, entry_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing time entry."""
        response = await self._make_request("PUT", f"/time_entries/{entry_id}", data=updates)
        return response.get("time_entry", response)
    
    async def delete_time_entry(self, entry_id: int) -> None:
        """Delete a time entry."""
        await self._make_request("DELETE", f"/time_entries/{entry_id}")
    
    async def get_activities(
        self,
        start_date: date,
        end_date: date,
        user_ids: Optional[List[int]] = None,
        organization_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get user activities for a date range."""
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        if user_ids:
            params["user_ids"] = ",".join(map(str, user_ids))
        if organization_id:
            params["organization_id"] = organization_id
        
        response = await self._make_request("GET", "/activities", params=params)
        return response.get("activities", [])
    
    async def get_screenshots(
        self,
        start_date: date,
        end_date: date,
        user_ids: Optional[List[int]] = None,
        organization_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get screenshots for a date range."""
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        if user_ids:
            params["user_ids"] = ",".join(map(str, user_ids))
        if organization_id:
            params["organization_id"] = organization_id
        
        response = await self._make_request("GET", "/screenshots", params=params)
        return response.get("screenshots", [])
    
    async def get_timesheets(
        self,
        start_date: date,
        end_date: date,
        user_ids: Optional[List[int]] = None,
        project_ids: Optional[List[int]] = None,
        organization_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Generate timesheets for a date range."""
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        if user_ids:
            params["user_ids"] = ",".join(map(str, user_ids))
        if project_ids:
            params["project_ids"] = ",".join(map(str, project_ids))
        if organization_id:
            params["organization_id"] = organization_id
        
        response = await self._make_request("GET", "/timesheets", params=params)
        return response.get("timesheets", [])
