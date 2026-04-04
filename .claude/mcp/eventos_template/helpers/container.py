"""Container helpers."""

from ..lib.paths import COMPOSE_CMD, CONTAINER_SERVICE
from ..lib.result import HelperResult
from ..lib.subprocess import run_subprocess


def is_container_running():
    """Check if the container is running."""
    r = HelperResult(success=False)
    r.add_step("check", "Checking if container is running")
    cmd = COMPOSE_CMD + ["ps", "-q", CONTAINER_SERVICE]
    output, rc = run_subprocess(cmd, timeout=10)
    is_running = rc == 0 and bool(output.strip())
    r.success = is_running
    if is_running:
        r.add_step("result", "Container is running")
    else:
        r.result = "Container is not running. Start it with container_start."
        r.add_step("result", "Container is not running")
    return r


def start_container():
    """Start the container, building the image if needed."""
    r = HelperResult(success=False)
    r.add_step("compose", "Running docker compose up -d --build")
    cmd = COMPOSE_CMD + ["up", "-d", "--build"]
    output, rc = run_subprocess(cmd, timeout=300)
    r.success = rc == 0
    r.result = output
    r.add_step("result", "Container started" if rc == 0 else f"exit code {rc}")
    return r


def stop_container():
    """Stop the container."""
    r = HelperResult(success=False)
    r.add_step("compose", "Running docker compose stop")
    cmd = COMPOSE_CMD + ["stop"]
    output, rc = run_subprocess(cmd, timeout=60)
    r.success = rc == 0
    r.result = output
    r.add_step("result", "Container stopped" if rc == 0 else f"exit code {rc}")
    return r


def build_image():
    """Rebuild the Docker image."""
    r = HelperResult(success=False)
    r.add_step("compose", "Running docker compose build")
    cmd = COMPOSE_CMD + ["build"]
    output, rc = run_subprocess(cmd, timeout=600)
    r.success = rc == 0
    r.result = output
    r.add_step("result", "Image built" if rc == 0 else f"exit code {rc}")
    return r


def remove_container():
    """Remove the container, network, and volumes."""
    r = HelperResult(success=False)
    r.add_step("compose", "Running docker compose down -v")
    cmd = COMPOSE_CMD + ["down", "-t", "30", "-v"]
    output, rc = run_subprocess(cmd, timeout=60)
    r.success = rc == 0
    r.result = output
    r.add_step("result", "Container removed" if rc == 0 else f"exit code {rc}")
    return r
