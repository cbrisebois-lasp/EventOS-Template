"""Centralized path and environment constants for the MCP server."""

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.join(SCRIPT_DIR, "..")
MCP_DIR = os.path.join(PACKAGE_DIR, "..")
PROJECT_ROOT = os.path.realpath(os.path.join(MCP_DIR, "..", ".."))

COMPOSE_FILE = os.path.join(PROJECT_ROOT, "docker", "docker-compose.yaml")
COMPOSE_CMD = ["docker", "compose", "-f", COMPOSE_FILE]
CONTAINER_SERVICE = "eventos-app"
CONTAINER_USER = "user"
PROJECT_DIR = os.environ.get(
    "PROJECT_DIR", os.path.basename(PROJECT_ROOT)
)
COMPOSE_ENV = {**os.environ, "PROJECT_DIR": PROJECT_DIR}
CONTAINER_WORKDIR = f"/home/user/{PROJECT_DIR}"
