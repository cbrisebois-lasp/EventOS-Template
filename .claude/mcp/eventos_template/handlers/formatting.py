"""Failure log formatter for handler responses."""


def format_failure(tool_name, *helper_results):
    """Compose helper logs into a readable diagnostic string.

    Args:
        tool_name: The name of the tool that failed.
        *helper_results: HelperResult objects from each helper called,
                         in the order they were called.
    """
    total = len(helper_results)
    failed_index = next(
        (i for i, r in enumerate(helper_results) if not r.success),
        total - 1,
    )

    lines = [f"{tool_name} failed at helper {failed_index + 1}/{total}"]
    lines.append("")

    for i, result in enumerate(helper_results):
        status = "FAILED" if not result.success else "ok"
        lines.append(f"--- Helper {i + 1}/{total} ({status}) ---")
        for entry in result.log:
            lines.append(f"  [{entry.step}] {entry.detail}")
        if not result.success and result.result:
            lines.append(f"  {result.result}")
        lines.append("")

    return "\n".join(lines).rstrip()
