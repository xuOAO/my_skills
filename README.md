# my_skills

Personal Codex skills that can be synced across machines.

## Skills

- `generate-repo-learning-docs`: Generate beginner-friendly repository learning documentation from a module dependency DAG.

## Install On Another Server

Clone this repository, then install a skill globally:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R generate-repo-learning-docs "${CODEX_HOME:-$HOME/.codex}/skills/"
```

For repo-local usage, copy the skill into the target repository:

```bash
mkdir -p .agents/skills
cp -R /path/to/my_skills/generate-repo-learning-docs .agents/skills/
```
