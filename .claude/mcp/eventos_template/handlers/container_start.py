"""Handler for the container_start tool."""

from ..helpers.container import start_container
from .formatting import format_failure


def handle_container_start(args):
    result = start_container()
    if not result.success:
        return format_failure("container_start", result)
    return result.result
