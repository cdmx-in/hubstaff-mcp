"""Hubstaff API client for MCP server."""

import os
from typing import Any, Dict, List, Optional
from datetime import datetime, date
import httpx
from pydantic import BaseModel, Field
import asyncio


class HubstaffAPIError(Exception):
    """Custom exception for Hubstaff API errors."""
    pass


class TimeEntry(BaseModel):
    """Time entry model."""
    id: Optional[int] = None
    user_id: int
    project_id: int
    task_id: Optional[int] = None
    starts_at: datetime
    stops_at: Optional[datetime] = None
    tracked: Optional[int] = None  # seconds
    keyboard: Optional[int] = None
    mouse: Optional[int] = None
    overall: Optional[int] = None
    paid: Optional[bool] = None


class Project(BaseModel):
    """Project model."""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None


class Task(BaseModel):
    """Task model."""
    id: Optional[int] = None
    summary: str
    details: Optional[str] = None
    project_id: int
    assignee_id: Optional[int] = None
    status: Optional[str] = None


class User(BaseModel):
    """User model."""
    id: Optional[int] = None
    name: str
    email: str
    time_zone: Optional[str] = None
    created_at: Optional[datetime] = None


class HubstaffClient:
    """Hubstaff API client."""
    
    def __init__(self, refresh_token: Optional[str] = None):
        """Initialize the Hubstaff client.
        
        Args:
            refresh_token: Personal access token used as refresh token. If not provided, 
                          will look for HUBSTAFF_REFRESH_TOKEN environment variable.
        """
        self.refresh_token = refresh_token or os.getenv("HUBSTAFF_REFRESH_TOKEN")
        if not self.refresh_token:
            raise ValueError(
                "Hubstaff refresh token (personal token) is required. Set HUBSTAFF_REFRESH_TOKEN "
                "environment variable or pass it as a parameter."
            )
        
        self.access_token: Optional[str] = None
        self.base_url = "https://api.hubstaff.com/v2"
        self.auth_url = "https://account.hubstaff.com/access_tokens"
        
    async def _refresh_access_token(self) -> str:
        """Get access token using refresh token."""
        async with httpx.AsyncClient() as client:
            try:
                # Use form data as specified in the API documentation
                form_data = {
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token
                }
                
                response = await client.post(
                    self.auth_url,
                    data=form_data,
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                
                token_data = await response.json()
                access_token = token_data.get("access_token")
                
                if not access_token:
                    raise HubstaffAPIError("No access token received from refresh request")
                
                return access_token
                
            except httpx.HTTPStatusError as e:
                raise HubstaffAPIError(f"Token refresh failed - HTTP {e.response.status_code}: {e.response.text}")
            except Exception as e:
                raise HubstaffAPIError(f"Token refresh failed: {str(e)}")
    
    async def _ensure_access_token(self) -> str:
        """Ensure we have a valid access token."""
        if not self.access_token:
            self.access_token = await self._refresh_access_token()
        return self.access_token
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        retry_auth: bool = True
    ) -> Dict[str, Any]:
        """Make HTTP request to Hubstaff API."""
        await self._ensure_access_token()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # If we get 401 and haven't retried auth yet, try refreshing token
                if e.response.status_code == 401 and retry_auth:
                    try:
                        self.access_token = await self._refresh_access_token()
                        return await self._make_request(method, endpoint, params, data, retry_auth=False)
                    except Exception:
                        pass  # Fall through to original error
                        
                raise HubstaffAPIError(f"HTTP {e.response.status_code}: {e.response.text}")
            except Exception as e:
                raise HubstaffAPIError(f"Request failed: {str(e)}")
    
    # Time Entries
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
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
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
        return response.get("time_entry", {})
    
    async def update_time_entry(self, entry_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing time entry."""
        response = await self._make_request("PUT", f"/time_entries/{entry_id}", data=updates)
        return response.get("time_entry", {})
    
    async def delete_time_entry(self, entry_id: int) -> bool:
        """Delete a time entry."""
        await self._make_request("DELETE", f"/time_entries/{entry_id}")
        return True
    
    # Projects
    async def get_projects(self, organization_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get list of projects."""
        params = {}
        if organization_id:
            params["organization_id"] = organization_id
            
        response = await self._make_request("GET", "/projects", params=params)
        return response.get("projects", [])
    
    async def get_project(self, project_id: int) -> Dict[str, Any]:
        """Get project details."""
        response = await self._make_request("GET", f"/projects/{project_id}")
        return response.get("project", {})
    
    # Tasks
    async def get_tasks(self, project_id: int) -> List[Dict[str, Any]]:
        """Get tasks for a project."""
        params = {"project_id": project_id}
        response = await self._make_request("GET", "/tasks", params=params)
        return response.get("tasks", [])
    
    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task."""
        response = await self._make_request("POST", "/tasks", data=task_data)
        return response.get("task", {})
    
    async def update_task(self, task_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task."""
        response = await self._make_request("PUT", f"/tasks/{task_id}", data=updates)
        return response.get("task", {})
    
    # Users
    async def get_current_user(self) -> Dict[str, Any]:
        """Get current user information."""
        response = await self._make_request("GET", "/users/me")
        return response.get("user", {})
    
    async def get_users(self, organization_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get organization users."""
        params = {}
        if organization_id:
            params["organization_id"] = organization_id
            
        response = await self._make_request("GET", "/users", params=params)
        return response.get("users", [])
    
    # Organizations
    async def get_organizations(self) -> List[Dict[str, Any]]:
        """Get user organizations."""
        response = await self._make_request("GET", "/organizations")
        return response.get("organizations", [])
    
    # Teams
    async def get_teams(self, organization_id: int) -> List[Dict[str, Any]]:
        """Get teams for an organization."""
        params = {"organization_id": organization_id}
        response = await self._make_request("GET", "/teams", params=params)
        return response.get("teams", [])
    
    # Activities
    async def get_activities(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        user_ids: Optional[List[int]] = None,
        organization_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get user activities."""
        params = {}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        if user_ids:
            params["user_ids"] = ",".join(map(str, user_ids))
        if organization_id:
            params["organization_id"] = organization_id
            
        response = await self._make_request("GET", "/activities", params=params)
        return response.get("activities", [])
    
    # Screenshots
    async def get_screenshots(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        user_ids: Optional[List[int]] = None,
        organization_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get screenshots."""
        params = {}
        if start_date:
            params["time_slot[start]"] = start_date.isoformat()
        if end_date:
            params["time_slot[stop]"] = end_date.isoformat()
        if user_ids:
            params["user_ids"] = ",".join(map(str, user_ids))
        if organization_id:
            params["organization_id"] = organization_id
            
        response = await self._make_request("GET", "/screenshots", params=params)
        return response.get("screenshots", [])
    
    # Timesheets
    async def get_timesheets(
        self,
        start_date: date,
        end_date: date,
        user_ids: Optional[List[int]] = None,
        project_ids: Optional[List[int]] = None,
        organization_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Generate timesheets."""
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        if user_ids:
            params["user_ids"] = ",".join(map(str, user_ids))
        if project_ids:
            params["project_ids"] = ",".join(map(str, project_ids))
        if organization_id:
            params["organization_id"] = organization_id
            
        response = await self._make_request("GET", "/timesheets", params=params)
        return response.get("timesheets", [])
