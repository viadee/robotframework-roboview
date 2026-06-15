# RoboView Domain Context

This document defines the domain vocabulary for RoboView. Use these terms consistently in code, documentation, and conversation.

## Core Domain Concepts

### Keyword

A named, reusable block of Robot Framework code. Keywords can be:

- **User-Defined Keyword**: A keyword defined in a `.robot` or `.resource` file within the project
- **External Keyword**: A keyword from an imported library (e.g., Browser, Collections) or resource
- **Builtin Keyword**: A keyword from Robot Framework's BuiltIn library

**Properties**:
- `keyword_name_with_prefix`: Full name including file prefix (e.g., `login.Enter Username`)
- `keyword_name_without_prefix`: Name without prefix (e.g., `Enter Username`)
- `source`: File path where the keyword is defined
- `code`: The implementation body
- `documentation`: The `[Documentation]` setting value
- `called_keywords`: Other keywords invoked by this keyword

### File

A Robot Framework source file. Types:

- **Test File** (`.robot`): Contains test cases, may contain keywords
- **Resource File** (`.resource`): Contains keywords and variables, no test cases

**Properties**:
- `initialized_keywords`: Keywords defined in this file
- `called_keywords`: Keywords used in this file
- `imported_files`: Resources and libraries imported

### Usage

How keywords are used across the codebase:

- **File Usages**: Count of keyword calls within a specific file
- **Total Usages**: Count of keyword calls across all files
- **Unused Keyword**: A keyword with zero usages
- **Reusage Rate**: Percentage of keywords used more than once

### Robocop

The linting tool for Robot Framework. Concepts:

- **Rule**: A specific check (e.g., "keyword should have documentation")
- **Message**: An instance of a rule violation in a specific file/line
- **Category**: Grouping of rules (Documentation, Naming, Length, etc.)
- **Severity**: Issue importance (ERROR, WARNING, INFO)

### Similarity

Comparison between keywords:

- **Cosine Similarity**: Token-based comparison score (0-100)
- **Duplicate Candidate**: Keywords with high similarity that may be redundant
- **Token**: A word or identifier extracted from keyword code

## Metric Definitions

### Documentation Coverage

`(keywords with [Documentation]) / (total user-defined keywords) × 100`

### Keyword Reusage Rate

`(keywords with > 1 usage) / (total user-defined keywords) × 100`

### Quality Score

Composite score based on:
- Documentation coverage (weight: 0.3)
- Reusage rate (weight: 0.3)
- Maintainability (1 - issues/lines ratio) (weight: 0.4)

## Surfaces

### Backend

The Python FastAPI server that:
- Parses Robot Framework files
- Computes metrics and analysis
- Exposes REST API endpoints
- Generates reports

### Extension

The VS Code extension that:
- Manages backend lifecycle (start/stop/restart)
- Handles user commands
- Bridges webview and backend communication
- Detects Python environment

### Webview

The React dashboard that:
- Displays KPIs and metrics
- Visualizes keyword usage
- Shows Robocop issues
- Enables file navigation

## Common Abbreviations

| Abbreviation | Full Term |
|--------------|-----------|
| RF | Robot Framework |
| KPI | Key Performance Indicator |
| DTO | Data Transfer Object |
| API | Application Programming Interface |
| UI | User Interface |

## File Naming Conventions

| Pattern | Purpose |
|---------|---------|
| `*.robot` | Test files |
| `*.resource` | Resource files |
| `sel*.resource` | Selector-only resource files |
| `*_test.py` | Python test files |
| `*.test.tsx` | React test files |
