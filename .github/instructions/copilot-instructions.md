---
description: "Primary guidance for RoboView development. Covers repo layout, cross-stack coordination, validation targets, and references specialized skills for domain-specific work."
name: "RoboView Project Guidance"
---

# RoboView Project Guidance

## Project Overview

RoboView is a VS Code extension for Robot Framework keyword analysis. It consists of three connected surfaces:

1. **Python Backend** (`packages/roboview/roboview/`) — FastAPI server on port 18123
2. **VS Code Extension** (`vscode-integration/src/`) — Extension host and commands
3. **React Webview** (`vscode-integration/webview-ui/src/`) — Dashboard UI

## Architecture Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│  VS Code Extension (TypeScript)                                  │
│  - Commands, Services, Webview Panel                            │
│  - Communicates with backend via HTTP (axios)                   │
│  - Communicates with webview via postMessage                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│  Python Backend (FastAPI)                                        │
│  - Services: KeywordUsageService, KeywordSimilarityService, etc │
│  - Registries: KeywordRegistry, FileRegistry, RobocopRegistry   │
│  - Parses Robot Framework files using robot.api.parsing         │
└─────────────────────────────────────────────────────────────────┘
```

## Core Development Rules

### Surface Ownership

- Keep changes inside the owning surface unless behavior crosses boundaries
- If you change backend schemas or endpoints, verify extension and webview callers still match
- When crossing surfaces, use the `cross-surface-changes` skill

### Validation Commands

**Python Backend:**
```bash
cd packages/roboview
pyright                              # Type checking
pytest tests/utest/ -v               # Unit tests
deptry .                             # Dependency checking
```

**VS Code Extension:**
```bash
cd vscode-integration
npm run check-types                  # TypeScript checking
npm run lint                         # ESLint
npm run compile                      # Build
```

**React Webview:**
```bash
cd vscode-integration/webview-ui
npm run typecheck                    # TypeScript checking
npm run build                        # Production build
```

### Code Patterns

**Backend Services:**
- Constructor takes registries via dependency injection
- Methods prefixed with `get_`, `_build_`, `_load_`, `_calculate_`
- Use Pydantic models for all data structures

**API Endpoints:**
- Access services via `request.app.state.service_name`
- Return DTO schemas (not domain models)
- Handle exceptions with HTTPException

**Extension Services:**
- Use EventEmitter for state changes
- Clean up disposables in `dispose()`
- Log to output channel for debugging

**Webview Components:**
- Use shadcn/ui components
- Message passing via `vscode.postMessage()`
- Handle loading and error states

## Available Skills

The following skills provide domain-specific guidance. Reference them for detailed patterns:

| Skill | Purpose | Applies To |
|-------|---------|------------|
| `roboview-backend` | Python backend development | `packages/roboview/**/*.py` |
| `roboview-extension` | VS Code extension development | `vscode-integration/src/**/*.ts` |
| `roboview-webview` | React webview UI development | `vscode-integration/webview-ui/src/**/*.{tsx,ts}` |
| `robot-framework` | Robot Framework tests | `**/*.{robot,resource}` |
| `api-development` | FastAPI endpoint patterns | `packages/roboview/roboview/api/**/*.py` |
| `report-generation` | Report feature development | `**/report*.py`, `**/exporters/**/*.py` |
| `tdd` | Test-driven development | All surfaces |
| `diagnose` | Bug diagnosis methodology | All surfaces |
| `improve-architecture` | Architectural improvements | All surfaces |
| `cross-surface-changes` | Multi-surface coordination | Cross-boundary changes |
| `code-review` | Code review practices | All surfaces |

## Available Agents

See `AGENTS.md` for specialized agents:

- **Backend** — Python/FastAPI expertise
- **Extension** — VS Code extension expertise
- **WebviewUI** — React webview expertise
- **RobotFramework** — RF test development
- **Quality** — Testing and code quality
- **Architecture** — Design and refactoring
- **FullStack** — End-to-end features

## Quick Reference

### Key Paths

| Component | Path |
|-----------|------|
| Backend services | `packages/roboview/roboview/services/` |
| Backend API | `packages/roboview/roboview/api/endpoints/` |
| Backend schemas | `packages/roboview/roboview/schemas/` |
| Extension entry | `vscode-integration/src/extension.ts` |
| Extension services | `vscode-integration/src/services/` |
| Webview pages | `vscode-integration/webview-ui/src/app/` |
| Webview components | `vscode-integration/webview-ui/src/components/` |
| RF tests | `rf_usergrp_vtiger/tests/` |
| RF resources | `rf_usergrp_vtiger/resources/` |

### Key Technologies

| Surface | Stack |
|---------|-------|
| Backend | Python 3.10+, FastAPI, Pydantic, Robot Framework, Robocop |
| Extension | TypeScript, VS Code API, Axios |
| Webview | React 19, Vite, Tailwind CSS, shadcn/ui, Recharts |
| Tests | pytest, Robot Framework |

### API Base URL

Backend server runs at `http://127.0.0.1:18123`

Key endpoints:
- `GET /system/health` — Health check
- `POST /system/initialize` — Initialize with project path
- `GET /overview/kpis` — Dashboard KPIs
- `GET /keyword-usage/*` — Keyword analysis endpoints
- `GET /robocop/*` — Robocop issue endpoints