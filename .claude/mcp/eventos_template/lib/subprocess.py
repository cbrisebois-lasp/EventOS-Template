"""Universal subprocess wrapper. All subprocess calls in the server funnel through here."""

import subprocess

from .paths import COMPOSE_ENV


def run_subprocess(cmd, timeout=120, env=None):
    """Run a command and return (output, returncode).

    Handles capture, timeout, and missing executable errors.
    """
    if env is None:
        env = COMPOSE_ENV
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, env=env
        )
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
        return output.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout}s", 1
    except FileNotFoundError:
        return "Docker not found. Is Docker installed and in PATH?", 1
