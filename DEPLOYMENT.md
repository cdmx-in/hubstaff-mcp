# Deployment Guide for Hubstaff MCP Server

This guide covers building, testing, and publishing the Hubstaff MCP Server package.

## Prerequisites

- Python 3.10 or higher
- `uv` package manager installed
- PyPI account (for publishing)
- Hubstaff account with API access

## Building the Package

### 1. Clean and Build

```bash
# Clean previous builds
rm -rf dist/ build/

# Install/update dependencies
uv sync

# Build the package
uv build
```

### 2. Verify Build

```bash
# Check built files
ls -la dist/

# Test local installation
uv pip install dist/hubstaff_mcp-*.whl

# Test the command
hubstaff-mcp --help  # Should show usage or start the server
```

## Testing

### 1. Local Testing

```bash
# Set environment variable
export HUBSTAFF_ACCESS_TOKEN="your_test_token"

# Test connection
uv run python test_connection.py

# Test MCP server (will wait for stdio input)
uv run hubstaff-mcp
```

### 2. Integration Testing with Claude Desktop

1. Copy the example config:
   ```bash
   cp claude_desktop_config.example.json ~/.config/claude_desktop_config.json
   ```

2. Update the config with your actual paths and token

3. Restart Claude Desktop and test MCP integration

## Publishing to PyPI

### 1. Prepare for Publishing

Update `pyproject.toml` with your information:

```toml
[project]
name = "hubstaff-mcp"
version = "0.1.0"  # Increment for new releases
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
```

### 2. Set Up PyPI Authentication

```bash
# Option 1: Using API token (recommended)
export UV_PUBLISH_TOKEN="your_pypi_api_token"

# Option 2: Interactive login
# uv will prompt for credentials during publish
```

### 3. Publish

```bash
# Using the publish script (recommended)
./publish.sh

# Or manually
uv publish

# For test PyPI (optional)
uv publish --publish-url https://test.pypi.org/legacy/
```

## Post-Publishing

### 1. Verify Publication

```bash
# Check on PyPI
# https://pypi.org/project/hubstaff-mcp/

# Test installation from PyPI
pip install hubstaff-mcp

# Or with uv
uv add hubstaff-mcp
```

### 2. Update Documentation

- Update README with installation instructions
- Tag the release in Git
- Create release notes

## Distribution Options

### Option 1: PyPI Installation (Recommended for end users)

```bash
pip install hubstaff-mcp
```

Claude Desktop config:
```json
{
  "mcpServers": {
    "hubstaff": {
      "command": "hubstaff-mcp",
      "env": {
        "HUBSTAFF_ACCESS_TOKEN": "your_token"
      }
    }
  }
}
```

### Option 2: UV Direct Run (Recommended for development)

```bash
uv add hubstaff-mcp
```

Claude Desktop config:
```json
{
  "mcpServers": {
    "hubstaff": {
      "command": "uv",
      "args": ["run", "hubstaff-mcp"],
      "env": {
        "HUBSTAFF_ACCESS_TOKEN": "your_token"
      }
    }
  }
}
```

### Option 3: Development Setup

```bash
git clone <repository>
cd hubstaff-mcp
uv sync
```

Claude Desktop config:
```json
{
  "mcpServers": {
    "hubstaff": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/hubstaff-mcp",
        "run",
        "hubstaff-mcp"
      ],
      "env": {
        "HUBSTAFF_ACCESS_TOKEN": "your_token"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure all dependencies are installed
2. **Token errors**: Verify HUBSTAFF_ACCESS_TOKEN is set correctly
3. **Permission errors**: Check file permissions and paths
4. **Network errors**: Verify internet connection and Hubstaff API access

### Getting Help

- Check the README.md for basic usage
- Review the example configurations
- Test with `python test_connection.py`
- Check Hubstaff API documentation for token setup

## Version Management

When releasing new versions:

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md (if exists)
3. Test thoroughly
4. Build and publish
5. Tag the release in Git
6. Update documentation
