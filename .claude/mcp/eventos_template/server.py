"""JSON-RPC transport over stdio. Zero external dependencies."""

import json
import sys

from .tools import TOOLS
from .handlers import HANDLERS


def send(msg):
    """Write a JSON-RPC message to stdout."""
    raw = json.dumps(msg)
    sys.stdout.write(raw + "\n")
    sys.stdout.flush()


def handle_request(request):
    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params", {})

    if method == "initialize":
        send({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "eventos-template", "version": "2.0.0"}
            }
        })
    elif method == "notifications/initialized":
        pass
    elif method == "tools/list":
        send({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS}
        })
    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        handler = HANDLERS.get(tool_name)
        if handler:
            text = handler(tool_args)
            send({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": text}]
                }
            })
        else:
            send({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
            })
    else:
        if req_id is not None:
            send({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"}
            })


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            handle_request(request)
        except json.JSONDecodeError as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {e}"}
            }), flush=True)
