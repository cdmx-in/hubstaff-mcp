# Hubstaff MCP Server

A Model Context Protocol (MCP) server for Hubstaff API integration, enabling seamless time tracking, project management, and team collaboration through AI assistants.

## Features

- **Time Tracking**: Create, update, and retrieve time entries
- **Project Management**: List and manage projects, tasks, and teams  
- **User Management**: Get user information and organization details
- **Activity Monitoring**: Access screenshots, activities, and productivity data
- **Reporting**: Generate timesheets and activity reports

## Installation

### Using uv (recommended)

```bash
uv add hubstaff-mcp
```

### Using pip

```bash
pip install hubstaff-mcp
```

## Configuration

Before using the server, you need to obtain a Personal Access Token from Hubstaff:

1. Log in to your Hubstaff account
2. Go to Settings → Personal Access Tokens
3. Create a new token with the required permissions

### Environment Variables

Set the following environment variable:

```bash
export HUBSTAFF_REFRESH_TOKEN="your_personal_access_token_here"
```

Or create a `.env` file in your project root:

```
HUBSTAFF_REFRESH_TOKEN=your_personal_access_token_here
```

**Note**: The personal access token is used as a refresh token to obtain temporary access tokens for API calls. This approach provides better security by automatically handling token renewal.

## Usage

### Running the Server

```bash
hubstaff-mcp
```

Or using uv:

```bash
uv run hubstaff-mcp
```

### Configuration with Claude Desktop

Add the following to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

#### Option 1: Using the installed package (Recommended)

```json
{
  "mcpServers": {
    "hubstaff": {
      "command": "hubstaff-mcp",
      "env": {
        "HUBSTAFF_REFRESH_TOKEN": "your_personal_access_token_here"
      }
    }
  }
}
```

#### Option 2: Using uv with project directory

```json
{
  "mcpServers": {
    "hubstaff": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project",
        "run",
        "hubstaff-mcp"
      ],
      "env": {
        "HUBSTAFF_REFRESH_TOKEN": "your_personal_access_token_here"
      }
    }
  }
}
```

#### Option 3: Using uv run directly

```json
{
  "mcpServers": {
    "hubstaff": {
      "command": "uv",
      "args": ["run", "hubstaff-mcp"],
      "env": {
        "HUBSTAFF_REFRESH_TOKEN": "your_personal_access_token_here"
      }
    }
  }
}
```

## Available Tools

The server provides the following tools:

### Time Management
- `get_time_entries` - Retrieve time entries with filtering options
- `create_time_entry` - Create a new time entry
- `update_time_entry` - Update an existing time entry
- `delete_time_entry` - Delete a time entry

### Project & Task Management
- `get_projects` - List all projects
- `get_project_details` - Get detailed project information
- `get_tasks` - List tasks for a project
- `create_task` - Create a new task
- `update_task` - Update task details

### User & Organization
- `get_current_user` - Get current user information
- `get_users` - List organization users
- `get_organizations` - List user organizations
- `get_teams` - List organization teams

### Activity & Monitoring
- `get_activities` - Retrieve user activities
- `get_screenshots` - Get screenshots for time entries
- `get_timesheets` - Generate timesheets

## Example Queries

Once configured with Claude Desktop, you can ask:

- "Show me my time entries for this week"
- "Create a new task called 'Update documentation' in the Development project"
- "What projects am I currently working on?"
- "Get my team's activity summary for today"
- "Show me screenshots from my last work session"

## Development

### Setup

```bash
git clone https://github.com/yourusername/hubstaff-mcp
cd hubstaff-mcp
uv sync --dev
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black .
uv run ruff check .
```

## API Coverage

This MCP server covers the following Hubstaff API endpoints:

- Time Entries
- Projects & Tasks
- Users & Organizations
- Teams
- Activities & Screenshots
- Timesheets
- Notes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/hubstaff-mcp/issues
- Hubstaff API Documentation: https://developer.hubstaff.com/docs/hubstaff_v2
