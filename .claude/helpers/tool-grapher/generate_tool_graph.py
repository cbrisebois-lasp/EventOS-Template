#!/usr/bin/env python3
"""
Parse the MCP server source and generate a DOT graph of tool-to-helper
call relationships, including helper-to-helper chains and serial call order.
Optionally render to SVG via Graphviz.

Usage:
    python3 generate_tool_graph.py              # print DOT to stdout
    python3 generate_tool_graph.py -o graph.svg # render SVG (requires graphviz)
    python3 generate_tool_graph.py -o graph.dot # write DOT file
"""

import ast
import argparse
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MCP_SERVER = os.path.join(SCRIPT_DIR, "..", "..", "mcp", "eventos-template.py")

# Helpers defined in the MCP server that we want to track
KNOWN_HELPERS = {
    "run_compose",
    "exec_in_container",
    "container_is_running",
}

# Maps SIMPLE_TOOLS "helper" field values to the helper function they call
HELPER_FIELD_MAP = {
    "compose": "run_compose",
    "exec": "exec_in_container",
}


def _find_ordered_calls(node, targets):
    """Walk a function body in source order and return an ordered list of calls to targets."""
    calls = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func = child.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name and name in targets:
                calls.append((child.lineno, name))
    calls.sort(key=lambda x: x[0])
    # Deduplicate consecutive same-name calls (keep order, remove repeats)
    seen = set()
    ordered = []
    for _, name in calls:
        if name not in seen:
            seen.add(name)
            ordered.append(name)
    return ordered


def parse_simple_tools(tree):
    """Parse SIMPLE_TOOLS dict and return {tool_name: helper_function_name}."""
    simple = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "SIMPLE_TOOLS":
                    if isinstance(node.value, ast.Dict):
                        for key, value in zip(node.value.keys, node.value.values):
                            if not isinstance(key, ast.Constant) or not isinstance(value, ast.Dict):
                                continue
                            tool_name = key.value
                            for k, v in zip(value.keys, value.values):
                                if isinstance(k, ast.Constant) and k.value == "helper" and isinstance(v, ast.Constant):
                                    helper_fn = HELPER_FIELD_MAP.get(v.value)
                                    if helper_fn:
                                        simple[tool_name] = helper_fn
    return simple


def parse_call_graph(source_path):
    """Parse the MCP server and return tool and helper call graphs.

    Returns:
        tool_calls: {tool_name: [(order, helper_name), ...]}
        helper_calls: {helper_name: [(order, helper_name), ...]}
    """
    with open(source_path) as f:
        tree = ast.parse(f.read())

    # Collect tool -> handler mapping from the HANDLERS dict
    tool_to_handler = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "HANDLERS":
                    if isinstance(node.value, ast.Dict):
                        for key, value in zip(node.value.keys, node.value.values):
                            if isinstance(key, ast.Constant) and isinstance(value, ast.Name):
                                tool_to_handler[key.value] = value.id

    # Parse SIMPLE_TOOLS for config-driven tools
    simple_tools = parse_simple_tools(tree)

    # For each handler function, find ordered helper calls
    tool_calls = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in tool_to_handler.values():
            tool_name = next(t for t, h in tool_to_handler.items() if h == node.name)
            ordered = _find_ordered_calls(node, KNOWN_HELPERS)
            tool_calls[tool_name] = [(i + 1, name) for i, name in enumerate(ordered)]

    # Add simple tools — each calls handle_simple_tool which delegates to the configured helper
    for tool_name, helper_fn in simple_tools.items():
        tool_calls[tool_name] = [(1, helper_fn)]

    # For each helper function, find ordered calls to other helpers
    helper_calls = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in KNOWN_HELPERS:
            ordered = _find_ordered_calls(node, KNOWN_HELPERS - {node.name})
            if ordered:
                helper_calls[node.name] = [(i + 1, name) for i, name in enumerate(ordered)]

    return tool_calls, helper_calls


def generate_dot(tool_calls, helper_calls):
    """Generate DOT source from the call graphs."""
    lines = [
        'digraph tool_hierarchy {',
        '    rankdir=LR;',
        '    node [fontname="Helvetica" fontsize=11];',
        '    edge [color="#666666"];',
        '',
        '    // Tool nodes (entry points)',
        '    subgraph cluster_tools {',
        '        label="MCP Tools";',
        '        style=dashed;',
        '        color="#888888";',
        '        node [shape=box style=filled fillcolor="#4A90D9" fontcolor=white];',
    ]
    for tool in sorted(tool_calls.keys()):
        lines.append(f'        "{tool}";')
    lines.append('    }')
    lines.append('')

    lines.append('    // Helper nodes')
    lines.append('    subgraph cluster_helpers {')
    lines.append('        label="Helpers";')
    lines.append('        style=dashed;')
    lines.append('        color="#888888";')
    lines.append('        node [shape=ellipse style=filled fillcolor="#50C878" fontcolor=white];')
    all_helpers = set()
    for calls in tool_calls.values():
        all_helpers.update(name for _, name in calls)
    for calls in helper_calls.values():
        all_helpers.update(name for _, name in calls)
    all_helpers.discard("handle_simple_tool")
    for helper in sorted(all_helpers):
        lines.append(f'        "{helper}";')
    lines.append('    }')
    lines.append('')

    lines.append('    // Tool -> Helper edges (numbered for serial order)')
    for tool, calls in sorted(tool_calls.items()):
        for order, helper in calls:
            if helper == "handle_simple_tool":
                continue
            label = f' [label="{order}"]' if len(calls) > 1 else ''
            lines.append(f'    "{tool}" -> "{helper}"{label};')

    lines.append('')
    lines.append('    // Helper -> Helper edges (dashed, numbered for serial order)')
    for helper, calls in sorted(helper_calls.items()):
        for order, target in calls:
            label = f' label="{order}"' if len(calls) > 1 else ''
            lines.append(f'    "{helper}" -> "{target}" [style=dashed{" " + label if label else ""}];')

    lines.append('}')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate MCP tool hierarchy graph")
    parser.add_argument("-o", "--output", help="Output file (.svg, .png, .pdf, or .dot)")
    parser.add_argument("-s", "--source", default=MCP_SERVER, help="MCP server source file")
    args = parser.parse_args()

    tool_calls, helper_calls = parse_call_graph(args.source)
    dot_source = generate_dot(tool_calls, helper_calls)

    if not args.output:
        print(dot_source)
        return

    if args.output.endswith(".dot"):
        with open(args.output, "w") as f:
            f.write(dot_source)
        print(f"DOT written to {args.output}")
        return

    ext = os.path.splitext(args.output)[1].lstrip(".")
    if ext not in ("svg", "png", "pdf"):
        print(f"Unsupported format: {ext}. Use .svg, .png, .pdf, or .dot", file=sys.stderr)
        sys.exit(1)

    try:
        result = subprocess.run(
            ["dot", f"-T{ext}", "-o", args.output],
            input=dot_source, text=True, capture_output=True
        )
        if result.returncode != 0:
            print(f"Graphviz error:\n{result.stderr}", file=sys.stderr)
            sys.exit(1)
        print(f"{ext.upper()} written to {args.output}")
    except FileNotFoundError:
        print("Graphviz 'dot' not found. Install graphviz or use -o graph.dot for raw DOT output.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
