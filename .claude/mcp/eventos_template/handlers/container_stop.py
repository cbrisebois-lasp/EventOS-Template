"""Handler for the container_stop tool."""

from ..helpers.container import is_container_running, stop_container
from .formatting import format_failure


def handle_container_stop(args):
    running = is_container_running()
    if not running.success:
        return format_failure("container_stop", running)

    result = stop_container()
    if not result.success:
        return format_failure("container_stop", running, result)

    return result.result
