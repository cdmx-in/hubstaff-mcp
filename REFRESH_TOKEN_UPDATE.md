# Hubstaff MCP Token Refresh Implementation

## Summary

Updated the Hubstaff MCP server to use the personal access token as a refresh token to obtain access tokens for API calls, as per the Hubstaff API authentication requirements.

## Changes Made

### 1. Client Authentication (`src/hubstaff_mcp/client.py`)
- **Changed initialization**: Now accepts `refresh_token` instead of `access_token`
- **Added `_refresh_access_token()` method**: Implements the token refresh flow using:
  - POST request to `https://account.hubstaff.com/access_tokens`
  - Form data with `grant_type=refresh_token` and `refresh_token=<personal_token>`
  - Content-Type: `application/x-www-form-urlencoded`
- **Added `_ensure_access_token()` method**: Ensures a valid access token is available
- **Updated `_make_request()` method**: 
  - Automatically gets access token before each request
  - Handles 401 errors by refreshing the token and retrying
  - Includes retry logic to prevent infinite loops

### 2. Environment Variables (`example.env`)
- **Changed**: `HUBSTAFF_ACCESS_TOKEN` → `HUBSTAFF_REFRESH_TOKEN`
- **Updated documentation**: Clarified that the personal token is used as a refresh token

### 3. Server Configuration (`src/hubstaff_mcp/server.py`)
- **Updated error message**: Now references `HUBSTAFF_REFRESH_TOKEN` in configuration errors

### 4. Documentation (`README.md`)
- **Updated configuration section**: Now uses `HUBSTAFF_REFRESH_TOKEN`
- **Added explanation**: Clarified the refresh token approach for better security
- **Updated all examples**: Claude Desktop configuration examples now use the correct environment variable

### 5. Tests (`tests/`)
- **Updated test fixtures**: Now use `HUBSTAFF_REFRESH_TOKEN` environment variable
- **Added new tests**: 
  - `test_refresh_access_token()`: Tests the token refresh functionality
  - `test_ensure_access_token()`: Tests automatic token acquisition
- **Fixed async mocking**: Properly handle async httpx calls in tests

### 6. Test Script (`test_connection_refresh.py`)
- **Created new test script**: Comprehensive testing of the token refresh flow
- **Includes error handling**: Provides troubleshooting guidance for common issues

## API Flow

1. **Initialization**: Client is initialized with personal access token as refresh token
2. **First API Call**: 
   - `_ensure_access_token()` is called
   - `_refresh_access_token()` makes POST request to get access token
   - Access token is cached for subsequent requests
3. **Subsequent API Calls**: Use cached access token
4. **Token Expiry**: When a 401 error occurs, automatically refresh token and retry

## Authentication Endpoint Details

```http
POST https://account.hubstaff.com/access_tokens
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&refresh_token=<personal_access_token>
```

**Response:**
```json
{
  "access_token": "temporary_access_token_here",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

## Benefits

1. **Enhanced Security**: Personal tokens are used only for authentication, not direct API access
2. **Automatic Token Management**: No manual token refresh required
3. **Error Recovery**: Automatic retry on token expiration
4. **Backward Compatibility**: Maintains the same MCP server interface

## Testing

All existing functionality remains the same from the MCP perspective. The token refresh happens transparently in the background.

To test with a real token:
1. Set `HUBSTAFF_REFRESH_TOKEN=<your_personal_token>`
2. Run `./test_connection_refresh.py`
3. Or use the MCP server directly with Claude Desktop

## Migration Guide

For existing users:
1. Change environment variable from `HUBSTAFF_ACCESS_TOKEN` to `HUBSTAFF_REFRESH_TOKEN`
2. Update your `.env` file or system environment variables
3. Update Claude Desktop configuration to use `HUBSTAFF_REFRESH_TOKEN`
4. The personal access token value remains the same - only the variable name changes
