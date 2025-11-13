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
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ads_mcp.coordinator import mcp

# Import tools to register them
from ads_mcp.tools import search, core  # noqa: F401

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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


async def handle_mcp_request(body: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP protocol requests and return JSON-RPC responses.
    
    This is a shared handler for both / and /messages endpoints.
    """
    method = body.get("method")
    params = body.get("params", {})
    request_id = body.get("id")
    
    logger.info(f"Handling MCP request: method={method}, id={request_id}")
    
    # Handle initialize
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "google-ads-mcp",
                    "version": "0.0.1"
                }
            }
        }
    
    # Handle tools/list
    elif method == "tools/list":
        tools = []
        try:
            # Use FastMCP's list_tools method if available
            if hasattr(mcp, 'list_tools'):
                mcp_tools = mcp.list_tools()
                for tool in mcp_tools:
                    # MCPTool objects have name, description, and inputSchema attributes
                    tool_dict = {
                        "name": getattr(tool, 'name', str(tool)),
                        "description": getattr(tool, 'description', ''),
                        "inputSchema": getattr(tool, 'inputSchema', {})
                    }
                    tools.append(tool_dict)
                    logger.debug(f"Found tool: {tool_dict['name']}")
            # Fallback: try accessing tools directly
            elif hasattr(mcp, '_tools') and mcp._tools:
                for tool_name, tool_info in mcp._tools.items():
                    tools.append({
                        "name": tool_name,
                        "description": tool_info.get("description", ""),
                        "inputSchema": tool_info.get("inputSchema", {})
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
                                "limit": {"type": ["integer", "string"]}
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
                            "limit": {"type": ["integer", "string"]}
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
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools}
        }
    
    # Handle tools/call
    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        
        logger.info(f"Calling tool: {tool_name} with args: {tool_args}")
        
        try:
            # Use FastMCP's call_tool method if available (it's synchronous)
            if hasattr(mcp, 'call_tool'):
                result = mcp.call_tool(tool_name, tool_args)
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
            logger.error(f"Error calling tool {tool_name}: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Error executing tool {tool_name}: {str(e)}"
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
        body = await request.json()
        response = await handle_mcp_request(body)
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
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": str(e)
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

