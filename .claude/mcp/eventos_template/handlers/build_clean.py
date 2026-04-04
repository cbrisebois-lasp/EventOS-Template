"""Handler for the build_clean tool."""

from ..helpers.container import is_container_running
from ..helpers.exec import execute_in_container
from .formatting import format_failure


def handle_build_clean(args):
    running = is_container_running()
    if not running.success:
        return format_failure("build_clean", running)

    result = execute_in_container("make clean", timeout=60)
    if not result.success:
        return format_failure("build_clean", running, result)

    return result.result
