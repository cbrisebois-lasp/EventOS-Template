"""Handler for the container_build tool."""

from ..helpers.container import build_image
from .formatting import format_failure


def handle_container_build(args):
    result = build_image()
    if not result.success:
        return format_failure("container_build", result)
    return result.result
