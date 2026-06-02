# Learning Documentation Templates

## Module Doc

Translate section headings naturally into the user's requested language. Do not use the literal English headings if the user asked for another language.

```markdown
# <Module Name>

## <Module Responsibility>

Explain what this module owns in the project. Cite the key paths.

## <Prerequisite Concepts>

List specific concepts, APIs, algorithms, or framework terms needed to read this module.
Each item should include a short reason.

## <Runtime Position>

Explain when this module appears in the main entrypoint, runtime lifecycle, request flow, training loop, build flow, or other dominant project flow.

## <Where To Start Reading>

- `<path>`: why this file is the best first read.
- `<path>`: what to inspect next.

## <Core Objects/APIs>

| Object | Location | Role |
| --- | --- | --- |
| `<name>` | `<path>` | Explain why it matters. |

## <Key Flow>

Explain the main control/data flow in 3-7 steps. Link to concrete files.

## <Common Questions>

Optional. Include only if there are real beginner confusions, surprising conventions, or recurring pitfalls.

## Optional Sections

Add other sections only when useful, such as dependency details, used-by relationships, input/output contracts, communication semantics, tensor shapes, configuration, examples, tests, or verification.
Do not add optional sections just to make every module look symmetrical.
```

Required module section concepts are: module responsibility, prerequisite concepts, runtime position, where to start reading, core objects/APIs, and key flow. Common questions and all other sections are optional. Translate these section concepts into the output language.

## Final Learning Guide

```markdown
# <Project Name> Learning Guide

## Who This Is For

State the assumed reader level and prerequisites.

## Project In One Page

Explain what the project does, who uses it, and what repo evidence supports that.

## Module Map

Include a concise table of modules and responsibilities.

## Dependency DAG

Use a Mermaid graph. State edge direction: `A --> B` means A depends on B.

## Recommended Reading Order

List modules in dependency-first order. Explain why this order helps.

## Start Here

Point to the best first module and the best first entrypoint file.

## Key Entrypoints

List commands, runtime entrypoints, API surfaces, tests, or examples beginners should inspect.

## Module Guides

Link to module docs or include concise summaries if writing a single-file guide.

## Common Change Recipes

Give small, realistic workflows grounded in existing code patterns.

## Practice Exercises

Give 3-6 exercises from easy to harder.

## Caveats And Open Questions

Mention inferred edges, cycles, environment constraints, missing docs, and commands not verified locally.
```
