# RoboView GitHub Copilot Skills

This directory contains specialized skills for GitHub Copilot to assist with RoboView development. Each skill provides domain-specific guidance for different aspects of the project.

## Available Skills

| Skill | Description | Applies To |
|-------|-------------|------------|
| [`roboview-backend`](./roboview-backend/SKILL.md) | Python backend development patterns | `packages/roboview/**/*.py` |
| [`roboview-extension`](./roboview-extension/SKILL.md) | VS Code extension development | `vscode-integration/src/**/*.ts` |
| [`roboview-webview`](./roboview-webview/SKILL.md) | React webview UI development | `vscode-integration/webview-ui/src/**/*.{tsx,ts}` |
| [`robot-framework`](./robot-framework/SKILL.md) | Robot Framework test development | `**/*.{robot,resource}` |
| [`api-development`](./api-development/SKILL.md) | FastAPI endpoint patterns | `packages/roboview/roboview/api/**/*.py` |
| [`report-generation`](./report-generation/SKILL.md) | Report feature development | `**/report*.py`, `**/exporters/**/*.py` |
| [`tdd`](./tdd/SKILL.md) | Test-driven development | All surfaces |
| [`diagnose`](./diagnose/SKILL.md) | Bug diagnosis methodology | All surfaces |
| [`improve-architecture`](./improve-architecture/SKILL.md) | Architectural improvements | All surfaces |
| [`cross-surface-changes`](./cross-surface-changes/SKILL.md) | Multi-surface coordination | Cross-boundary changes |
| [`code-review`](./code-review/SKILL.md) | Code review practices | All surfaces |

## How Skills Work

Skills are automatically loaded by GitHub Copilot based on:

1. **File Pattern Matching**: Skills with `applyTo` patterns activate when working on matching files
2. **Explicit Invocation**: Skills can be referenced directly in prompts
3. **Agent Recommendations**: Skills are assigned to agents in `AGENTS.md`

## Skill Structure

Each skill follows this format:

```markdown
---
name: skill-name
description: Brief description of the skill's purpose and when to use it.
applyTo: "optional/glob/pattern/**/*.py"
---

# Skill Name

[Detailed guidance, patterns, and examples]
```

## Creating New Skills

1. Create a new directory under `.github/skills/`
2. Add a `SKILL.md` file with YAML frontmatter
3. Include comprehensive guidance for the domain
4. Reference the skill in `AGENTS.md` if applicable
5. Update the main `copilot-instructions.md` skill table

## Related Files

- [`/AGENTS.md`](../../AGENTS.md) — Agent definitions with skill assignments
- [`/CONTEXT.md`](../../CONTEXT.md) — Domain vocabulary and concepts
- [`copilot-instructions.md`](../instructions/copilot-instructions.md) — Main project guidance
