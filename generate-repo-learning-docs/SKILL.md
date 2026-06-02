---
name: generate-repo-learning-docs
description: Generate beginner-friendly repository learning documentation from a module dependency DAG. Use when Codex is asked to help beginners learn a repo, create a repo study guide, produce module-by-module documentation, map module dependencies, derive a reading order, or build onboarding docs grounded in an existing codebase.
---

# Generate Repo Learning Docs

## Overview

Create a repository learning package for beginners by first understanding the project, then documenting modules in dependency order, and finally assembling a guided learning document. Favor code-grounded explanations over broad summaries.

## Core Workflow

1. Inspect the repository purpose and evidence:
   - Read top-level docs, manifests, tests, examples, config files, and likely entrypoints.
   - State what the repo appears to do and cite concrete paths.
   - Distinguish repo facts from inferences.
2. Identify modules:
   - Use the repo's natural boundaries: packages, top-level source directories, services, apps, libraries, plugins, or domain folders.
   - Keep module granularity learnable. Avoid treating every file as a module unless the repo is very small.
   - Exclude generated, vendored, cache, build, and dependency directories.
3. Build a module dependency graph:
   - Use `A --> B` to mean "module A depends on module B".
   - Prefer dependencies proven by imports, manifests, configs, entrypoint calls, tests, or documented runtime relationships.
   - Mark inferred edges explicitly.
   - Collapse cycles into strongly connected components instead of pretending the graph is a pure DAG.
4. Choose documentation order:
   - If edges use `A --> B` for "A depends on B", use reverse topological order so dependencies are documented before dependents.
   - If a cycle exists, document the whole strongly connected component together or pick the least surprising internal order and note the cycle.
5. Create module docs in order:
   - For each module, read its files plus docs for modules it depends on.
   - Each module doc must include these section concepts, translated naturally into the user's requested language: module responsibility, prerequisite concepts, runtime position, where to start reading, core objects/APIs, and key flow.
   - Add optional sections only when they materially improve learning, such as common questions, input/output contracts, communication semantics, tensor shapes, configuration, examples, tests, or verification.
   - Keep each module doc short enough to be useful. Link to deeper files instead of dumping everything.
6. Create the final teaching document:
   - Reference the module docs rather than duplicating all details.
   - Include the project purpose, module DAG, reading order, starting module, key module entrypoints, common workflows, exercises, and caveats.
   - Use the user's requested language; otherwise match the user's language.
7. Validate:
   - Check that file links, commands, diagrams, and module names match the repo.
   - Run lightweight scripts or tests only when practical and relevant.
   - Mention unverified commands or environment-sensitive steps clearly.

## DAG Helper

The bundled helper script can produce a candidate graph. Resolve relative paths from this skill directory when the skill is installed globally, or from `.agents/skills/generate-repo-learning-docs/` when the skill is checked into a target repo.

```bash
python scripts/module_graph.py <repo-root>
```

When the skill is checked into a target repo under `.agents/skills/`, the same helper is usually run as:

```bash
python .agents/skills/generate-repo-learning-docs/scripts/module_graph.py <repo-root>
```

Use the script output as a candidate graph, not as final truth. Static import detection misses dynamic imports, runtime wiring, dependency injection, configuration-only edges, and cross-language relationships. Review and edit the graph before using it in documentation.

Useful options:

```bash
python scripts/module_graph.py <repo-root> --format mermaid
python scripts/module_graph.py <repo-root> --format json
python scripts/module_graph.py <repo-root> --include-tests
python scripts/module_graph.py <repo-root> --module-root picotron --package-name picotron
```

## Output Layout

When the user asks to create files, prefer:

```text
docs/learning/
├── README.md
└── modules/
    ├── <module-name>.md
    └── ...
```

If the repo has no `docs/` directory and adding one would be surprising, use `LEARNING_GUIDE.md` at the root and include module sections inline.

Use `references/templates.md` for default outlines.

## Quality Bar

- Cite concrete repository paths for every major claim.
- Explain why a beginner should read modules in the chosen order.
- Keep diagrams small enough to teach. Split large graphs by subsystem.
- Prefer entrypoints and tests as anchors because they show how code is actually used.
- In module docs, make prerequisites specific. Prefer concrete APIs, algorithms, framework concepts, or domain terms over broad topics, and explain why each prerequisite matters in one short phrase.
- Core objects/APIs should be easy to scan, usually as a small table with object, location, and role.
- Optional sections must explain a real boundary, runtime behavior, verification path, or beginner confusion. Do not add sections just to make every module look symmetrical.
- Surface ambiguity: cycles, inferred edges, missing docs, generated code, private services, credentials, platform assumptions, or commands that cannot be run locally.
- Do not create a directory listing disguised as a guide. Explain relationships and learning sequence.

## Notes On The Proposed Workflow

The workflow is sound with two clarifications:

- "Reverse topological order" only has a stable meaning after defining edge direction. This skill standardizes on `dependent --> dependency`.
- Real repos often contain cycles. Treat the graph as a DAG of strongly connected components when necessary.
