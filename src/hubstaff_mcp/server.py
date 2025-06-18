"""Main MCP server implementation for Hubstaff integration."""

import asyncio
import os
import sys
from datetime import datetime, date
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from .client import HubstaffClient, HubstaffAPIError

# Load environment variables from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


# Initialize FastMCP server
mcp = FastMCP("hubstaff")

# Initialize Hubstaff client (will be re-initialized in main() with proper error handling)
hubstaff_client = None


def format_time_entry(entry: Dict[str, Any]) -> str:
    """Format a time entry for display."""
    tracked_hours = entry.get("tracked", 0) / 3600 if entry.get("tracked") else 0
    return f"""
Time Entry ID: {entry.get('id')}
User ID: {entry.get('user_id')}
Project ID: {entry.get('project_id')}
Task ID: {entry.get('task_id', 'N/A')}
Start Time: {entry.get('starts_at')}
End Time: {entry.get('stops_at', 'Still running')}
Tracked Time: {tracked_hours:.2f} hours
Keyboard Activity: {entry.get('keyboard', 0)}%
Mouse Activity: {entry.get('mouse', 0)}%
Overall Activity: {entry.get('overall', 0)}%
Paid: {'Yes' if entry.get('paid') else 'No'}
"""


def format_project(project: Dict[str, Any]) -> str:
    """Format a project for display."""
    return f"""
Project ID: {project.get('id')}
Name: {project.get('name')}
Description: {project.get('description', 'No description')}
Status: {project.get('status', 'Unknown')}
Created: {project.get('created_at', 'Unknown')}
"""


def parse_date_string(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD format.")


@mcp.tool()
async def get_time_entries(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user_ids: Optional[str] = None,
    project_ids: Optional[str] = None,
    organization_id: Optional[int] = None
) -> str:
    """Get time entries with optional filtering.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        user_ids: Comma-separated list of user IDs
        project_ids: Comma-separated list of project IDs
        organization_id: Organization ID to filter by
    """
    try:
        # Parse dates
        start_date_obj = parse_date_string(start_date) if start_date else None
        end_date_obj = parse_date_string(end_date) if end_date else None
        
        # Parse user and project IDs
        user_id_list = [int(x.strip()) for x in user_ids.split(",")] if user_ids else None
        project_id_list = [int(x.strip()) for x in project_ids.split(",")] if project_ids else None
        
        entries = await hubstaff_client.get_time_entries(
            start_date=start_date_obj,
            end_date=end_date_obj,
            user_ids=user_id_list,
            project_ids=project_id_list,
            organization_id=organization_id
        )
        
        if not entries:
            return "No time entries found for the specified criteria."
        
        formatted_entries = [format_time_entry(entry) for entry in entries]
        return "Time Entries:\n" + "\n---\n".join(formatted_entries)
        
    except Exception as e:
        return f"Error retrieving time entries: {str(e)}"


@mcp.tool()
async def create_time_entry(
    project_id: int,
    starts_at: str,
    stops_at: Optional[str] = None,
    task_id: Optional[int] = None
) -> str:
    """Create a new time entry.
    
    Args:
        project_id: ID of the project
        starts_at: Start time in ISO format (YYYY-MM-DDTHH:MM:SS)
        stops_at: End time in ISO format (optional, for running entries)
        task_id: Task ID (optional)
    """
    try:
        time_entry_data = {
            "project_id": project_id,
            "starts_at": starts_at,
        }
        
        if stops_at:
            time_entry_data["stops_at"] = stops_at
        if task_id:
            time_entry_data["task_id"] = task_id
            
        entry = await hubstaff_client.create_time_entry(time_entry_data)
        return f"Time entry created successfully:\n{format_time_entry(entry)}"
        
    except Exception as e:
        return f"Error creating time entry: {str(e)}"


@mcp.tool()
async def update_time_entry(
    entry_id: int,
    stops_at: Optional[str] = None,
    task_id: Optional[int] = None
) -> str:
    """Update an existing time entry.
    
    Args:
        entry_id: ID of the time entry to update
        stops_at: New end time in ISO format
        task_id: New task ID
    """
    try:
        updates = {}
        if stops_at:
            updates["stops_at"] = stops_at
        if task_id:
            updates["task_id"] = task_id
            
        if not updates:
            return "No updates provided."
            
        entry = await hubstaff_client.update_time_entry(entry_id, updates)
        return f"Time entry updated successfully:\n{format_time_entry(entry)}"
        
    except Exception as e:
        return f"Error updating time entry: {str(e)}"


@mcp.tool()
async def delete_time_entry(entry_id: int) -> str:
    """Delete a time entry.
    
    Args:
        entry_id: ID of the time entry to delete
    """
    try:
        await hubstaff_client.delete_time_entry(entry_id)
        return f"Time entry {entry_id} deleted successfully."
        
    except Exception as e:
        return f"Error deleting time entry: {str(e)}"


@mcp.tool()
async def get_projects(organization_id: Optional[int] = None) -> str:
    """Get list of projects.
    
    Args:
        organization_id: Organization ID to filter by (optional)
    """
    try:
        projects = await hubstaff_client.get_projects(organization_id=organization_id)
        
        if not projects:
            return "No projects found."
        
        formatted_projects = [format_project(project) for project in projects]
        return "Projects:\n" + "\n---\n".join(formatted_projects)
        
    except Exception as e:
        return f"Error retrieving projects: {str(e)}"


@mcp.tool()
async def get_project_details(project_id: int) -> str:
    """Get detailed information about a specific project.
    
    Args:
        project_id: ID of the project
    """
    try:
        project = await hubstaff_client.get_project(project_id)
        return f"Project Details:\n{format_project(project)}"
        
    except Exception as e:
        return f"Error retrieving project details: {str(e)}"


@mcp.tool()
async def get_tasks(project_id: int) -> str:
    """Get tasks for a specific project.
    
    Args:
        project_id: ID of the project
    """
    try:
        tasks = await hubstaff_client.get_tasks(project_id)
        
        if not tasks:
            return f"No tasks found for project {project_id}."
        
        formatted_tasks = []
        for task in tasks:
            formatted_task = f"""
Task ID: {task.get('id')}
Summary: {task.get('summary')}
Details: {task.get('details', 'No details')}
Project ID: {task.get('project_id')}
Assignee ID: {task.get('assignee_id', 'Unassigned')}
Status: {task.get('status', 'Unknown')}
"""
            formatted_tasks.append(formatted_task)
        
        return f"Tasks for Project {project_id}:\n" + "\n---\n".join(formatted_tasks)
        
    except Exception as e:
        return f"Error retrieving tasks: {str(e)}"


@mcp.tool()
async def create_task(
    project_id: int,
    summary: str,
    details: Optional[str] = None,
    assignee_id: Optional[int] = None
) -> str:
    """Create a new task.
    
    Args:
        project_id: ID of the project
        summary: Task summary/title
        details: Task details/description (optional)
        assignee_id: ID of the user to assign the task to (optional)
    """
    try:
        task_data = {
            "project_id": project_id,
            "summary": summary,
        }
        
        if details:
            task_data["details"] = details
        if assignee_id:
            task_data["assignee_id"] = assignee_id
            
        task = await hubstaff_client.create_task(task_data)
        return f"Task created successfully:\nTask ID: {task.get('id')}\nSummary: {task.get('summary')}"
        
    except Exception as e:
        return f"Error creating task: {str(e)}"


@mcp.tool()
async def get_current_user() -> str:
    """Get information about the current user."""
    try:
        user = await hubstaff_client.get_current_user()
        return f"""
Current User:
ID: {user.get('id')}
Name: {user.get('name')}
Email: {user.get('email')}
Time Zone: {user.get('time_zone', 'Not specified')}
Created: {user.get('created_at', 'Unknown')}
"""
        
    except Exception as e:
        return f"Error retrieving current user: {str(e)}"


@mcp.tool()
async def get_users(organization_id: Optional[int] = None) -> str:
    """Get organization users.
    
    Args:
        organization_id: Organization ID (optional)
    """
    try:
        users = await hubstaff_client.get_users(organization_id=organization_id)
        
        if not users:
            return "No users found."
        
        formatted_users = []
        for user in users:
            formatted_user = f"""
User ID: {user.get('id')}
Name: {user.get('name')}
Email: {user.get('email')}
Time Zone: {user.get('time_zone', 'Not specified')}
"""
            formatted_users.append(formatted_user)
        
        return "Users:\n" + "\n---\n".join(formatted_users)
        
    except Exception as e:
        return f"Error retrieving users: {str(e)}"


@mcp.tool()
async def get_organizations() -> str:
    """Get user organizations."""
    try:
        orgs = await hubstaff_client.get_organizations()
        
        if not orgs:
            return "No organizations found."
        
        formatted_orgs = []
        for org in orgs:
            formatted_org = f"""
Organization ID: {org.get('id')}
Name: {org.get('name')}
"""
            formatted_orgs.append(formatted_org)
        
        return "Organizations:\n" + "\n---\n".join(formatted_orgs)
        
    except Exception as e:
        return f"Error retrieving organizations: {str(e)}"


@mcp.tool()
async def get_teams(organization_id: int) -> str:
    """Get teams for an organization.
    
    Args:
        organization_id: Organization ID
    """
    try:
        teams = await hubstaff_client.get_teams(organization_id)
        
        if not teams:
            return f"No teams found for organization {organization_id}."
        
        formatted_teams = []
        for team in teams:
            formatted_team = f"""
Team ID: {team.get('id')}
Name: {team.get('name')}
"""
            formatted_teams.append(formatted_team)
        
        return f"Teams for Organization {organization_id}:\n" + "\n---\n".join(formatted_teams)
        
    except Exception as e:
        return f"Error retrieving teams: {str(e)}"


@mcp.tool()
async def get_activities(
    start_date: str,
    end_date: str,
    user_ids: Optional[str] = None,
    organization_id: Optional[int] = None
) -> str:
    """Get user activities for a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        user_ids: Comma-separated list of user IDs (optional)
        organization_id: Organization ID (optional)
    """
    try:
        start_date_obj = parse_date_string(start_date)
        end_date_obj = parse_date_string(end_date)
        user_id_list = [int(x.strip()) for x in user_ids.split(",")] if user_ids else None
        
        activities = await hubstaff_client.get_activities(
            start_date=start_date_obj,
            end_date=end_date_obj,
            user_ids=user_id_list,
            organization_id=organization_id
        )
        
        if not activities:
            return "No activities found for the specified criteria."
        
        formatted_activities = []
        for activity in activities:
            formatted_activity = f"""
Activity ID: {activity.get('id')}
User ID: {activity.get('user_id')}
Time Slot: {activity.get('time_slot')}
Keyboard: {activity.get('keyboard', 0)}%
Mouse: {activity.get('mouse', 0)}%
Overall: {activity.get('overall', 0)}%
"""
            formatted_activities.append(formatted_activity)
        
        return "Activities:\n" + "\n---\n".join(formatted_activities)
        
    except Exception as e:
        return f"Error retrieving activities: {str(e)}"


@mcp.tool()
async def get_screenshots(
    start_date: str,
    end_date: str,
    user_ids: Optional[str] = None,
    organization_id: Optional[int] = None
) -> str:
    """Get screenshots for a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        user_ids: Comma-separated list of user IDs (optional)
        organization_id: Organization ID (optional)
    """
    try:
        start_date_obj = parse_date_string(start_date)
        end_date_obj = parse_date_string(end_date)
        user_id_list = [int(x.strip()) for x in user_ids.split(",")] if user_ids else None
        
        screenshots = await hubstaff_client.get_screenshots(
            start_date=start_date_obj,
            end_date=end_date_obj,
            user_ids=user_id_list,
            organization_id=organization_id
        )
        
        if not screenshots:
            return "No screenshots found for the specified criteria."
        
        formatted_screenshots = []
        for screenshot in screenshots:
            formatted_screenshot = f"""
Screenshot ID: {screenshot.get('id')}
User ID: {screenshot.get('user_id')}
Time Slot: {screenshot.get('time_slot')}
URL: {screenshot.get('url')}
"""
            formatted_screenshots.append(formatted_screenshot)
        
        return "Screenshots:\n" + "\n---\n".join(formatted_screenshots)
        
    except Exception as e:
        return f"Error retrieving screenshots: {str(e)}"


@mcp.tool()
async def get_timesheets(
    start_date: str,
    end_date: str,
    user_ids: Optional[str] = None,
    project_ids: Optional[str] = None,
    organization_id: Optional[int] = None
) -> str:
    """Generate timesheets for a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        user_ids: Comma-separated list of user IDs (optional)
        project_ids: Comma-separated list of project IDs (optional)
        organization_id: Organization ID (optional)
    """
    try:
        start_date_obj = parse_date_string(start_date)
        end_date_obj = parse_date_string(end_date)
        user_id_list = [int(x.strip()) for x in user_ids.split(",")] if user_ids else None
        project_id_list = [int(x.strip()) for x in project_ids.split(",")] if project_ids else None
        
        timesheets = await hubstaff_client.get_timesheets(
            start_date=start_date_obj,
            end_date=end_date_obj,
            user_ids=user_id_list,
            project_ids=project_id_list,
            organization_id=organization_id
        )
        
        if not timesheets:
            return "No timesheet data found for the specified criteria."
        
        formatted_timesheets = []
        for timesheet in timesheets:
            total_hours = timesheet.get("tracked", 0) / 3600 if timesheet.get("tracked") else 0
            formatted_timesheet = f"""
User ID: {timesheet.get('user_id')}
Project ID: {timesheet.get('project_id')}
Date: {timesheet.get('date')}
Total Hours: {total_hours:.2f}
Tracked Time: {timesheet.get('tracked', 0)} seconds
"""
            formatted_timesheets.append(formatted_timesheet)
        
        return "Timesheets:\n" + "\n---\n".join(formatted_timesheets)
        
    except Exception as e:
        return f"Error generating timesheets: {str(e)}"


def main():
    """Main entry point for the MCP server."""
    try:
        # Initialize Hubstaff client here to catch configuration errors early
        global hubstaff_client
        hubstaff_client = HubstaffClient()
        mcp.run(transport="stdio")
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        print("Please set your HUBSTAFF_REFRESH_TOKEN environment variable or create a .env file", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
