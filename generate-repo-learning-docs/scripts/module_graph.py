#!/usr/bin/env python3
"""Build a candidate module dependency graph from static imports.

Edges are emitted as "module -> dependency", meaning A depends on B.
The output is intentionally a draft for review, not a complete architecture model.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from collections import defaultdict, deque
from pathlib import Path


IGNORE_DIRS = {
    ".git",
    ".agents",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    "node_modules",
    "dist",
    "build",
    "target",
    "coverage",
    ".next",
    ".nuxt",
}

TEST_PARTS = {"test", "tests", "__tests__", "spec"}
PY_SUFFIXES = {".py"}
JS_SUFFIXES = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
IMPORT_RE = re.compile(
    r"""(?:import\s+(?:[^'"]+\s+from\s+)?|export\s+[^'"]+\s+from\s+|require\()\s*['"]([^'"]+)['"]"""
)


def is_test_path(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    return bool(parts & TEST_PARTS) or path.name.startswith("test_") or path.name.endswith("_test.py")


def iter_source_files(root: Path, module_root: Path, include_tests: bool) -> list[Path]:
    files: list[Path] = []
    for path in module_root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in IGNORE_DIRS for part in rel.parts):
            continue
        if not include_tests and is_test_path(rel):
            continue
        if path.suffix in PY_SUFFIXES or path.suffix in JS_SUFFIXES:
            files.append(path)
    return sorted(files)


def module_for_path(module_root: Path, path: Path) -> str | None:
    rel = path.relative_to(module_root)
    if not rel.parts:
        return None
    if len(rel.parts) == 1:
        return rel.stem
    return rel.parts[0]


def discover_modules(module_root: Path, files: list[Path]) -> set[str]:
    modules = set()
    for file_path in files:
        module = module_for_path(module_root, file_path)
        if module:
            modules.add(module)
    return modules


def py_imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return set()
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def js_imports(path: Path) -> set[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return set()
    imports: set[str] = set()
    for match in IMPORT_RE.finditer(text):
        spec = match.group(1)
        if spec.startswith("."):
            continue
        imports.add(spec.split("/")[0] if not spec.startswith("@") else "/".join(spec.split("/")[:2]))
    return imports


def dependency_module(imported: str, modules: set[str], package_name: str | None) -> str | None:
    parts = imported.split(".")
    if package_name and parts and parts[0] == package_name:
        if len(parts) > 1 and parts[1] in modules:
            return parts[1]
        return None
    if parts and parts[0] in modules:
        return parts[0]
    return None


def build_graph(root: Path, module_root: Path, package_name: str | None, include_tests: bool) -> dict[str, object]:
    files = iter_source_files(root, module_root, include_tests)
    modules = discover_modules(module_root, files)
    edges: set[tuple[str, str]] = set()
    evidence: dict[str, list[str]] = defaultdict(list)

    for file_path in files:
        src = module_for_path(module_root, file_path)
        if not src:
            continue
        imports = py_imports(file_path) if file_path.suffix in PY_SUFFIXES else js_imports(file_path)
        for imported in imports:
            dst = dependency_module(imported, modules, package_name)
            if dst and dst != src:
                edges.add((src, dst))
                evidence[f"{src}->{dst}"].append(str(file_path.relative_to(root)))

    return {
        "edge_direction": "A -> B means module A depends on module B",
        "module_root": str(module_root.relative_to(root)) if module_root != root else ".",
        "modules": sorted(modules),
        "edges": [{"from": src, "to": dst, "evidence": evidence[f"{src}->{dst}"][:5]} for src, dst in sorted(edges)],
        "reverse_topological_order": reverse_topological_order(modules, edges),
        "cycles": cycle_nodes(modules, edges),
    }


def reverse_topological_order(modules: set[str], edges: set[tuple[str, str]]) -> list[str] | None:
    outgoing = defaultdict(set)
    incoming_count = {module: 0 for module in modules}
    for src, dst in edges:
        outgoing[src].add(dst)
        incoming_count[dst] += 1

    queue = deque(sorted(module for module, count in incoming_count.items() if count == 0))
    topo: list[str] = []
    while queue:
        module = queue.popleft()
        topo.append(module)
        for dst in sorted(outgoing[module]):
            incoming_count[dst] -= 1
            if incoming_count[dst] == 0:
                queue.append(dst)

    if len(topo) != len(modules):
        return None
    return list(reversed(topo))


def cycle_nodes(modules: set[str], edges: set[tuple[str, str]]) -> list[str]:
    order = reverse_topological_order(modules, edges)
    if order is not None:
        return []
    outgoing = defaultdict(set)
    incoming_count = {module: 0 for module in modules}
    for src, dst in edges:
        outgoing[src].add(dst)
        incoming_count[dst] += 1
    queue = deque(module for module, count in incoming_count.items() if count == 0)
    removed = set(queue)
    while queue:
        module = queue.popleft()
        for dst in outgoing[module]:
            incoming_count[dst] -= 1
            if incoming_count[dst] == 0:
                removed.add(dst)
                queue.append(dst)
    return sorted(modules - removed)


def print_mermaid(graph: dict[str, object]) -> None:
    print("graph TD")
    for module in graph["modules"]:
        print(f'    {safe_id(module)}["{module}"]')
    for edge in graph["edges"]:
        print(f"    {safe_id(edge['from'])} --> {safe_id(edge['to'])}")


def safe_id(name: str) -> str:
    return "m_" + re.sub(r"[^A-Za-z0-9_]", "_", name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_root", type=Path)
    parser.add_argument("--format", choices=["text", "json", "mermaid"], default="text")
    parser.add_argument("--include-tests", action="store_true")
    parser.add_argument("--module-root", type=Path, help="Subdirectory whose direct children are treated as modules.")
    parser.add_argument("--package-name", help="Import package prefix for module-root, such as picotron.")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    module_root = (root / args.module_root).resolve() if args.module_root else root
    if not module_root.exists() or not module_root.is_dir():
        parser.error(f"module root does not exist or is not a directory: {module_root}")
    graph = build_graph(root, module_root, args.package_name, args.include_tests)

    if args.format == "json":
        print(json.dumps(graph, indent=2, sort_keys=True))
    elif args.format == "mermaid":
        print_mermaid(graph)
    else:
        print(graph["edge_direction"])
        print(f"Module root: {graph['module_root']}")
        print("\nModules:")
        for module in graph["modules"]:
            print(f"- {module}")
        print("\nEdges:")
        for edge in graph["edges"]:
            evidence = ", ".join(edge["evidence"])
            print(f"- {edge['from']} -> {edge['to']} ({evidence})")
        print("\nReverse topological order:")
        order = graph["reverse_topological_order"]
        if order is None:
            print("- unavailable because cycles were detected")
        else:
            for module in order:
                print(f"- {module}")
        if graph["cycles"]:
            print("\nCycle candidates:")
            for module in graph["cycles"]:
                print(f"- {module}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
