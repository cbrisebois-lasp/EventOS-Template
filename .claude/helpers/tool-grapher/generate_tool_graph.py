#!/usr/bin/env python3
"""
Parse the MCP server source and generate a DOT graph of tool-to-helper
call relationships. Optionally render to SVG via Graphviz.

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


def parse_call_graph(source_path):
    """Parse the MCP server and return {tool_name: [called_helpers]}."""
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

    # For each handler, find which helpers it calls, keyed by tool name
    tool_to_helpers = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in tool_to_handler.values():
            # Find the tool name for this handler
            tool_name = next(t for t, h in tool_to_handler.items() if h == node.name)
            called = set()
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    func = child.func
                    name = None
                    if isinstance(func, ast.Name):
                        name = func.id
                    elif isinstance(func, ast.Attribute):
                        name = func.attr
                    if name and name in KNOWN_HELPERS:
                        called.add(name)
            tool_to_helpers[tool_name] = sorted(called)

    return tool_to_helpers


def generate_dot(tool_to_helpers):
    """Generate DOT source from the call graph."""
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
    for tool in sorted(tool_to_helpers.keys()):
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
    for called in tool_to_helpers.values():
        all_helpers.update(called)
    for helper in sorted(all_helpers):
        lines.append(f'        "{helper}";')
    lines.append('    }')
    lines.append('')

    lines.append('    // Tool -> Helper edges')
    for tool, helpers in sorted(tool_to_helpers.items()):
        for helper in helpers:
            lines.append(f'    "{tool}" -> "{helper}";')

    lines.append('}')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate MCP tool hierarchy graph")
    parser.add_argument("-o", "--output", help="Output file (.svg, .png, .pdf, or .dot)")
    parser.add_argument("-s", "--source", default=MCP_SERVER, help="MCP server source file")
    args = parser.parse_args()

    tool_to_helpers = parse_call_graph(args.source)
    dot_source = generate_dot(tool_to_helpers)

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
