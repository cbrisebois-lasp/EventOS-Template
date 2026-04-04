"""MCP tool schema definitions."""

TOOLS = [
    {
        "name": "container_start",
        "description": "Start the EventOS-Template Docker container. Creates and builds the image if needed.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "container_stop",
        "description": "Stop the running EventOS-Template Docker container.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "container_build",
        "description": "Rebuild the Docker image from the Dockerfile.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "container_remove",
        "description": "Remove the Docker container, network, and volumes. This is destructive.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "build_app",
        "description": "Build the application inside the Docker container.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "build_clean",
        "description": "Remove application and test build directories inside the Docker container.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "run_tests",
        "description": "Build and run all tests inside the Docker container.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_tests",
        "description": "List all available test targets.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "run_coverage",
        "description": "Build and run tests with coverage instrumentation, then generate an LCOV HTML report.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]
