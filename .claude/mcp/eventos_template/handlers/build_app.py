"""Handler for the build_app tool."""

from ..helpers.container import is_container_running
from ..helpers.exec import execute_in_container
from .formatting import format_failure


def handle_build_app(args):
    running = is_container_running()
    if not running.success:
        return format_failure("build_app", running)

    result = execute_in_container("make build", timeout=300)
    if not result.success:
        return format_failure("build_app", running, result)

    return result.result
