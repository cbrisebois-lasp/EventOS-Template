#!/usr/bin/env python3
"""
MCP server for EventOS-Template projects.
Provides container management and test running tools.
Communicates via JSON-RPC over stdio. Zero external dependencies.
"""

import json
import subprocess
import sys
import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..", "..")

COMPOSE_FILE = os.path.join(PROJECT_ROOT, "docker", "docker-compose.yaml")
COMPOSE_CMD = ["docker", "compose", "-f", COMPOSE_FILE]
CONTAINER_SERVICE = "eventos-app"
CONTAINER_USER = "user"
PROJECT_DIR = os.environ.get("PROJECT_DIR", os.path.basename(os.path.realpath(PROJECT_ROOT)))
COMPOSE_ENV = {**os.environ, "PROJECT_DIR": PROJECT_DIR}
CONTAINER_WORKDIR = f"/home/user/{PROJECT_DIR}"

# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------
TOOLS = [
    # --- Container ---
    {
        "name": "container_start",
        "description": "Start the EventOS-Template Docker container. Creates it if it doesn't exist.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "container_stop",
        "description": "Stop the running EventOS-Template Docker container.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "container_status",
        "description": "Check the status of the EventOS-Template Docker container (running, stopped, or not created).",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "container_build",
        "description": "Rebuild the Docker image from the Dockerfile.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "container_remove",
        "description": "Remove the Docker container, network, and volumes. This is destructive.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "container_exec",
        "description": "Execute a shell command inside the running container as the 'user' user.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute inside the container."
                },
                "workdir": {
                    "type": "string",
                    "description": "Working directory inside the container (default: /home/user/project)."
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 120)."
                }
            },
            "required": ["command"]
        }
    },
    # --- Build ---
    {
        "name": "build_app",
        "description": "Build the application inside the Docker container.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "build_clean",
        "description": "Remove application and test build directories inside the Docker container.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    # --- Tests ---
    {
        "name": "run_tests",
        "description": "Build and run tests inside the Docker container. Can run all tests, filter by module, or run a single test target.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "module": {
                    "type": "string",
                    "description": "Filter tests by module name. Omit to run all tests."
                },
                "target": {
                    "type": "string",
                    "description": "Run a single test target by name. Overrides module filter if both provided."
                }
            }
        }
    },
    {
        "name": "list_tests",
        "description": "List all available test targets.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "run_coverage",
        "description": "Build and run tests with coverage instrumentation, then generate an LCOV HTML report.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "module": {
                    "type": "string",
                    "description": "Filter coverage to a specific module. Omit for full coverage."
                }
            }
        }
    },
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_compose(args, timeout=120):
    """Run a docker compose command and return stdout+stderr."""
    full_cmd = COMPOSE_CMD + args
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout, env=COMPOSE_ENV)
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
        return output.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout}s", 1
    except FileNotFoundError:
        return "Docker not found. Is Docker installed and in PATH?", 1


def exec_in_container(cmd, workdir=CONTAINER_WORKDIR, timeout=120):
    """Run a command inside the Docker container and return stdout+stderr."""
    if not container_is_running():
        return "Container is not running. Start it with container_start.", 1

    full_cmd = COMPOSE_CMD + [
        "exec", "-T", "-u", CONTAINER_USER,
        "-w", workdir,
        CONTAINER_SERVICE, "sh", "-c", cmd
    ]
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout, env=COMPOSE_ENV)
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
        return output.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout}s: {cmd}", 1
    except FileNotFoundError:
        return "Docker not found. Is Docker installed and in PATH?", 1


def container_is_running():
    """Check if the container is up."""
    output, rc = run_compose(["ps", "-q", CONTAINER_SERVICE], timeout=10)
    return rc == 0 and bool(output.strip())


# ---------------------------------------------------------------------------
# Simple tool dispatch
# ---------------------------------------------------------------------------

SIMPLE_TOOLS = {
    "container_start": {
        "helper": "compose",
        "args": ["up", "-d", "--build"],
        "timeout": 300,
        "success": "Container started successfully.",
        "failure": "Failed to start container",
    },
    "container_build": {
        "helper": "compose",
        "args": ["build"],
        "timeout": 600,
        "success": "Image built successfully.",
        "failure": "Build failed",
    },
    "container_remove": {
        "helper": "compose",
        "args": ["down", "-t", "30", "-v"],
        "timeout": 60,
        "success": "Container, network, and volumes removed.",
        "failure": "Failed to remove",
    },
    "build_app": {
        "helper": "exec",
        "cmd": "make build",
        "timeout": 300,
    },
    "build_clean": {
        "helper": "exec",
        "cmd": "make clean",
        "timeout": 60,
    },
}


def handle_simple_tool(tool_name, args):
    """Generic handler for tools that are a single helper call + formatting."""
    config = SIMPLE_TOOLS[tool_name]
    if config["helper"] == "compose":
        output, rc = run_compose(config["args"], timeout=config["timeout"])
        if rc == 0:
            return f"{config['success']}\n\n{output}"
        return f"{config['failure']} (exit code {rc})\n\n{output}"
    else:
        output, rc = exec_in_container(config["cmd"], timeout=config["timeout"])
        status = "OK" if rc == 0 else "FAILED"
        return f"[{status}] exit code {rc}\n\n{output}"


# ---------------------------------------------------------------------------
# Custom handlers
# ---------------------------------------------------------------------------

def handle_container_stop(args):
    if not container_is_running():
        return "Container is not running."
    output, rc = run_compose(["stop"], timeout=60)
    if rc == 0:
        return f"Container stopped.\n\n{output}"
    return f"Failed to stop container (exit code {rc})\n\n{output}"


def handle_container_status(args):
    output, rc = run_compose(["ps", "--format", "json"], timeout=10)
    if rc != 0:
        output, rc = run_compose(["ps"], timeout=10)
        if rc != 0:
            return f"Failed to get status (exit code {rc})\n\n{output}"
        return output

    if not output.strip():
        return "Container is not created. Run container_start to create it."

    try:
        containers = json.loads(output)
        if isinstance(containers, dict):
            containers = [containers]
        for c in containers:
            name = c.get("Name", c.get("Service", "unknown"))
            state = c.get("State", "unknown")
            status = c.get("Status", "")
            return f"Container: {name}\nState: {state}\nStatus: {status}"
    except json.JSONDecodeError:
        return output


def handle_container_exec(args):
    command = args.get("command")
    if not command:
        return "Error: 'command' parameter is required."

    workdir = args.get("workdir", CONTAINER_WORKDIR)
    timeout = args.get("timeout", 120)

    output, rc = exec_in_container(command, workdir=workdir, timeout=timeout)
    status = "OK" if rc == 0 else "FAILED"
    return f"[{status}] exit code {rc}\n\n{output}"


def handle_run_tests(args):
    target = args.get("target")
    module = args.get("module")

    if target:
        cmd = f"cd test && make build && cd build && ctest -R {target} --output-on-failure"
    elif module:
        cmd = f"cd test && MODULE_FILTER={module} make test"
    else:
        cmd = "make test"

    output, rc = exec_in_container(cmd, timeout=300)
    status = "PASSED" if rc == 0 else "FAILED"
    return f"Test run {status} (exit code {rc})\n\n{output}"


def handle_list_tests(args):
    cmd = "cd test && make build > /dev/null 2>&1 && cd build && ctest -N"
    output, rc = exec_in_container(cmd, timeout=120)
    if rc != 0:
        return f"Failed to list tests (exit code {rc})\n\n{output}"
    return output


def handle_run_coverage(args):
    module = args.get("module")
    if module:
        cmd = f"cd test && MODULE_FILTER={module} make coverage"
    else:
        cmd = "cd test && make coverage"

    output, rc = exec_in_container(cmd, timeout=300)
    status = "PASSED" if rc == 0 else "FAILED"
    return f"Coverage run {status} (exit code {rc})\n\n{output}\n\nReport: test/build/coverage_report/index.html"


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

HANDLERS = {
    **{name: lambda args, n=name: handle_simple_tool(n, args) for name in SIMPLE_TOOLS},
    "container_stop": handle_container_stop,
    "container_status": handle_container_status,
    "container_exec": handle_container_exec,
    "run_tests": handle_run_tests,
    "list_tests": handle_list_tests,
    "run_coverage": handle_run_coverage,
}


# ---------------------------------------------------------------------------
# JSON-RPC transport
# ---------------------------------------------------------------------------

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
                "serverInfo": {"name": "eventos-template", "version": "1.0.0"}
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


if __name__ == "__main__":
    main()
