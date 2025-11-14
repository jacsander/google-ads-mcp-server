# Copyright 2025 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""HTTP server wrapper for MCP server to support Cloud Run deployment."""

import os
import json
import logging
import asyncio
from typing import AsyncIterator, Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import StreamingResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from ads_mcp.coordinator import mcp

# Import tools to register them
from ads_mcp.tools import search, core  # noqa: F401

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def normalize_tool_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize tool schema to ensure Copilot Studio compatibility.
    
    Fixes common issues:
    - Converts array types to single type (uses string for union types)
    - Ensures all required fields are present
    """
    if not isinstance(schema, dict):
        return schema
    
    normalized = schema.copy()
    
    # Fix properties if they exist
    if "properties" in normalized and isinstance(normalized["properties"], dict):
        for prop_name, prop_schema in normalized["properties"].items():
            if isinstance(prop_schema, dict):
                # Fix array types (e.g., ["integer", "string"] -> "string")
                if "type" in prop_schema and isinstance(prop_schema["type"], list):
                    # Use string type for union types (more flexible)
                    prop_schema = prop_schema.copy()
                    prop_schema["type"] = "string"
                    if "description" not in prop_schema:
                        prop_schema["description"] = f"Accepts string or number (will be converted)"
                    normalized["properties"][prop_name] = prop_schema
    
    return normalized

app = FastAPI(title="Google Ads MCP Server")

# Add CORS middleware for browser-based clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {"status": "healthy", "service": "google-ads-mcp"}


@app.get("/sse")
async def sse_endpoint(request: Request):
    """Server-Sent Events endpoint for MCP protocol.
    
    Note: SSE for MCP requires bidirectional communication which is complex.
    For now, this endpoint redirects to POST /messages for actual requests.
    """
    # For SSE, we'll send a simple connection message
    # Actual requests should use POST /messages
    async def event_stream() -> AsyncIterator[str]:
        """Stream MCP messages as SSE events."""
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connection', 'status': 'connected', 'note': 'Use POST /messages for requests'})}\n\n"
            
            # Keep connection alive
            while True:
                await asyncio.sleep(30)
                yield f": keepalive\n\n"
                
        except asyncio.CancelledError:
            logger.info("SSE connection closed")
        except Exception as e:
            logger.error(f"SSE error: {e}", exc_info=True)
            error_result = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            yield f"data: {json.dumps(error_result)}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


async def handle_mcp_request(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle MCP protocol requests and return JSON-RPC responses.
    
    This is a shared handler for both / and /messages endpoints.
    Returns None for notifications (which don't require responses).
    """
    method = body.get("method")
    params = body.get("params", {})
    request_id = body.get("id")
    
    logger.info(f"Handling MCP request: method={method}, id={request_id}")
    
    # Handle notifications (they don't have an id and don't return responses)
    if method and method.startswith("notifications/"):
        logger.info(f"Received notification: {method}, no response needed")
        return None  # Notifications don't return responses in JSON-RPC 2.0
    
    # Handle initialize
    if method == "initialize":
        logger.info(f"Initialize request received. Params: {params}")
        # Enhanced capabilities to explicitly indicate tool support
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    },
                    "resources": {
                        "subscribe": False,
                        "listChanged": False
                    },
                    "prompts": {},
                    "sampling": {}
                },
                "serverInfo": {
                    "name": "google-ads-mcp",
                    "version": "0.0.1"
                }
            }
        }
        logger.info(f"Sending initialize response: {json.dumps(response, indent=2)}")
        return response
    
    # Handle tools/list
    elif method == "tools/list":
        tools = []
        try:
            # Use FastMCP's list_tools method if available
            if hasattr(mcp, 'list_tools'):
                mcp_tools_result = mcp.list_tools()
                # Check if it's a coroutine (async method)
                if asyncio.iscoroutine(mcp_tools_result):
                    mcp_tools = await mcp_tools_result
                else:
                    mcp_tools = mcp_tools_result
                for tool in mcp_tools:
                    # MCPTool objects have name, description, and inputSchema attributes
                    input_schema = getattr(tool, 'inputSchema', {})
                    # Normalize schema for Copilot Studio compatibility
                    input_schema = normalize_tool_schema(input_schema)
                    tool_dict = {
                        "name": getattr(tool, 'name', str(tool)),
                        "description": getattr(tool, 'description', ''),
                        "inputSchema": input_schema
                    }
                    tools.append(tool_dict)
                    logger.debug(f"Found tool: {tool_dict['name']}")
            # Fallback: try accessing tools directly
            elif hasattr(mcp, '_tools') and mcp._tools:
                for tool_name, tool_info in mcp._tools.items():
                    input_schema = tool_info.get("inputSchema", {})
                    # Normalize schema for Copilot Studio compatibility
                    input_schema = normalize_tool_schema(input_schema)
                    tools.append({
                        "name": tool_name,
                        "description": tool_info.get("description", ""),
                        "inputSchema": input_schema
                    })
            
            # If still no tools, use fallback definitions
            if not tools:
                logger.warning("No tools found via FastMCP, using fallback definitions")
                tools = [
                    {
                        "name": "search",
                        "description": "Retrieves information about the Google Ads account using GAQL queries",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "customer_id": {"type": "string"},
                                "resource": {"type": "string"},
                                "fields": {"type": "array", "items": {"type": "string"}},
                                "conditions": {"type": "array", "items": {"type": "string"}},
                                "orderings": {"type": "array", "items": {"type": "string"}},
                                "limit": {"type": "string", "description": "Limit as string (will be converted to integer)"}
                            },
                            "required": ["customer_id", "fields", "resource"]
                        }
                    },
                    {
                        "name": "list_accessible_customers",
                        "description": "Returns ids of customers directly accessible by the user authenticating the call",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
        except Exception as e:
            logger.error(f"Error getting tools: {e}", exc_info=True)
            # Use fallback tools on error
            tools = [
                {
                    "name": "search",
                    "description": "Retrieves information about the Google Ads account using GAQL queries",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "customer_id": {"type": "string"},
                            "resource": {"type": "string"},
                            "fields": {"type": "array", "items": {"type": "string"}},
                            "conditions": {"type": "array", "items": {"type": "string"}},
                            "orderings": {"type": "array", "items": {"type": "string"}},
                            "limit": {"type": "string", "description": "Limit as string (will be converted to integer)"}
                        },
                        "required": ["customer_id", "fields", "resource"]
                    }
                },
                {
                    "name": "list_accessible_customers",
                    "description": "Returns ids of customers directly accessible by the user authenticating the call",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        
        logger.info(f"Returning {len(tools)} tools")
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools}
        }
        logger.info(f"Tools list response: {json.dumps(response, indent=2)[:500]}...")  # Log first 500 chars
        return response
    
    # Handle tools/call
    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        
        logger.info(f"Calling tool: {tool_name} with args: {json.dumps(tool_args, indent=2)}")
        
        try:
            # Use FastMCP's call_tool method if available
            if hasattr(mcp, 'call_tool'):
                call_result = mcp.call_tool(tool_name, tool_args)
                # Check if it's a coroutine (async method)
                if asyncio.iscoroutine(call_result):
                    result = await call_result
                else:
                    result = call_result
                # call_tool returns either Sequence[ContentBlock] or dict[str, Any]
                # If it's already a dict with content, use it directly
                if isinstance(result, dict) and "content" in result:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
                # Otherwise, wrap it in content format
                elif isinstance(result, (list, tuple)):
                    # If it's a sequence of ContentBlock objects, convert them
                    content = []
                    for item in result:
                        if hasattr(item, 'text'):
                            content.append({"type": "text", "text": item.text})
                        elif isinstance(item, dict):
                            content.append(item)
                        else:
                            content.append({"type": "text", "text": str(item)})
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {"content": content}
                    }
                else:
                    # Convert to text content
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, indent=2) if not isinstance(result, str) else result
                                }
                            ]
                        }
                    }
            else:
                # Fallback: call the tool function directly
                if tool_name == "search":
                    from ads_mcp.tools.search import search
                    result = search(**tool_args)
                elif tool_name == "list_accessible_customers":
                    from ads_mcp.tools.core import list_accessible_customers
                    result = list_accessible_customers()
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error calling tool {tool_name}: {error_msg}", exc_info=True)
            
            # Provide more helpful error messages for common issues
            if "NOT_ADS_USER" in error_msg or "not associated with any Ads accounts" in error_msg:
                error_msg = (
                    "The Google account used for OAuth authentication is not associated with any Google Ads accounts. "
                    "Please ensure the Google account that generated the OAuth refresh token has access to at least one Google Ads account. "
                    "You may need to: 1) Use a different Google account that has Google Ads access, "
                    "2) Add the current account to a Google Ads account, or 3) Generate a new OAuth refresh token with an account that has Ads access."
                )
            elif "UNAUTHENTICATED" in error_msg and "OAuth" in error_msg:
                error_msg = (
                    "OAuth authentication failed. Please verify that the OAuth credentials (GOOGLE_ADS_CLIENT_ID, "
                    "GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN) are correct and the refresh token is still valid. "
                    f"Original error: {error_msg}"
                )
            elif "Fields parameter is required" in error_msg or "cannot be empty" in error_msg:
                error_msg = f"{error_msg} The 'fields' parameter must contain at least one field name (e.g., ['metrics.cost_micros', 'segments.date'])."
            elif "Customer ID must be numeric" in error_msg:
                error_msg = f"{error_msg} Please remove hyphens and use only numbers (e.g., '7011849472' instead of '701-184-9472')."
            elif "INVALID_ARGUMENT" in error_msg or "unexpected input" in error_msg:
                error_msg = f"Invalid query format: {error_msg}. Please check that all fields, conditions, and resource names are valid Google Ads API fields."
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Error executing tool {tool_name}: {error_msg}",
                    "data": {
                        "tool": tool_name,
                        "arguments": tool_args
                    }
                }
            }
    
    # Handle resources/list
    elif method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"resources": []}
        }
    
    # Unknown method
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }


@app.post("/")
async def root_handler(request: Request):
    """Root POST handler for Copilot Studio requests."""
    try:
        # Read and parse the request body once
        body = await request.json()
        logger.info(f"Root POST request received. Body keys: {list(body.keys())}, method: {body.get('method')}, id: {body.get('id')}")
        logger.debug(f"Request body: {json.dumps(body, indent=2)}")
        response = await handle_mcp_request(body)
        # Notifications return None and shouldn't send a response
        if response is None:
            # 204 No Content - must have no body and no Content-Length header
            logger.info("Sending 204 No Content response for notification")
            return Response(status_code=204)
        logger.info(f"Sending JSON response. Response keys: {list(response.keys()) if isinstance(response, dict) else 'not a dict'}")
        return JSONResponse(response)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": "Parse error"
            }
        }, status_code=400)
    except Exception as e:
        logger.error(f"Error handling root request: {e}", exc_info=True)
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Full traceback: {error_trace}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id") if isinstance(body, dict) else None,
            "error": {
                "code": -32603,
                "message": f"Internal server error: {str(e)}",
                "data": {
                    "error_type": type(e).__name__,
                    "error_details": str(e)
                }
            }
        }, status_code=500)


@app.post("/messages")
async def handle_messages(request: Request):
    """Handle MCP messages via HTTP POST.
    
    This endpoint accepts MCP protocol messages and returns responses.
    This is an alternative to SSE for MCP communication.
    """
    try:
        body = await request.json()
        response = await handle_mcp_request(body)
        # Notifications return None and shouldn't send a response
        if response is None:
            # 204 No Content - must have no body and no Content-Length header
            return Response(status_code=204, headers={"Content-Length": "0"})
        return JSONResponse(response)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": "Parse error"
            }
        }, status_code=400)
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }, status_code=500)


def run_http_server(host: str = "0.0.0.0", port: int = 8080):
    """Run the HTTP server."""
    import uvicorn
    
    port = int(os.environ.get("PORT", port))
    logger.info(f"Starting HTTP server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_http_server()

