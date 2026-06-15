# RoboView Agents

This file defines specialized AI agents for different aspects of RoboView development. Each agent has focused expertise and access to relevant skills.

## Agent Definitions

### Backend Agent

**Name**: `Backend`

**Description**: Expert in Python/FastAPI backend development for RoboView. Handles services, registries, API endpoints, schemas, and CLI development. Understands Robot Framework parsing and Robocop integration.

**Expertise**:
- FastAPI endpoint development
- Pydantic schema design
- Service layer patterns
- Registry data management
- Robot Framework file parsing
- Robocop linting integration
- Report generation

**Skills**:
- `roboview-backend`
- `api-development`
- `report-generation`
- `tdd`
- `diagnose`

**Use When**:
- Creating new API endpoints
- Implementing service methods
- Designing data models
- Debugging backend issues
- Adding CLI commands
- Working with Robot Framework parsers

---

### Extension Agent

**Name**: `Extension`

**Description**: Expert in VS Code extension development. Handles extension activation, commands, services, webview panel management, and backend communication.

**Expertise**:
- VS Code Extension API
- TypeScript patterns
- Backend HTTP communication
- Webview panel lifecycle
- Command registration
- Python environment detection

**Skills**:
- `roboview-extension`
- `cross-surface-changes`
- `diagnose`

**Use When**:
- Adding VS Code commands
- Managing backend connection
- Handling webview communication
- Extension lifecycle issues
- Python environment problems

---

### WebviewUI Agent

**Name**: `WebviewUI`

**Description**: Expert in React webview UI development. Handles dashboard components, data visualization, state management, and VS Code theme integration.

**Expertise**:
- React 19 patterns
- shadcn/ui components
- Recharts visualizations
- VS Code webview messaging
- Tailwind CSS styling
- Responsive layouts

**Skills**:
- `roboview-webview`
- `cross-surface-changes`
- `diagnose`

**Use When**:
- Building new UI components
- Creating data visualizations
- Implementing webview messaging
- Styling with VS Code themes
- Handling user interactions

---

### RobotFramework Agent

**Name**: `RobotFramework`

**Description**: Expert in Robot Framework test development. Creates and maintains test cases, keywords, and resource files. Understands BDD syntax and test organization.

**Expertise**:
- Robot Framework syntax
- Keyword design patterns
- Resource file organization
- BDD test writing
- Browser library usage
- Robocop compliance

**Skills**:
- `robot-framework`
- `tdd`

**Use When**:
- Writing new test cases
- Creating reusable keywords
- Organizing test resources
- Debugging test failures
- Improving test coverage

---

### Quality Agent

**Name**: `Quality`

**Description**: Expert in code quality, testing, and reviews. Handles test development, code review, and quality assurance across all surfaces.

**Expertise**:
- Test-driven development
- Code review practices
- Type checking (Pyright, TypeScript)
- Linting (ESLint, Robocop)
- Test coverage analysis
- Quality metrics

**Skills**:
- `tdd`
- `code-review`
- `diagnose`

**Use When**:
- Writing comprehensive tests
- Reviewing pull requests
- Improving code quality
- Setting up CI checks
- Analyzing test coverage

---

### Architecture Agent

**Name**: `Architecture`

**Description**: Expert in codebase architecture and design. Reviews structure, identifies refactoring opportunities, and ensures consistency across surfaces.

**Expertise**:
- Architectural patterns
- Module design (deep vs shallow)
- Cross-surface coordination
- Refactoring strategies
- Testability improvements
- Interface design

**Skills**:
- `improve-architecture`
- `cross-surface-changes`
- `code-review`

**Use When**:
- Reviewing codebase structure
- Planning major refactors
- Designing new features
- Improving testability
- Coordinating cross-surface changes

---

### FullStack Agent

**Name**: `FullStack`

**Description**: Generalist agent with knowledge of all surfaces. Handles features that span backend, extension, and webview. Coordinates cross-surface changes.

**Expertise**:
- All three surfaces (Python, TypeScript, React)
- End-to-end feature development
- API contract design
- Message protocol design
- Integration testing

**Skills**:
- `roboview-backend`
- `roboview-extension`
- `roboview-webview`
- `cross-surface-changes`
- `api-development`

**Use When**:
- Implementing end-to-end features
- Debugging cross-surface issues
- Designing new data flows
- Coordinating API changes

---

## Agent Selection Guide

| Task | Recommended Agent |
|------|------------------|
| New API endpoint | Backend |
| New service method | Backend |
| Schema design | Backend |
| VS Code command | Extension |
| Backend connection issues | Extension |
| New dashboard component | WebviewUI |
| Data visualization | WebviewUI |
| Robot Framework test | RobotFramework |
| Keyword library | RobotFramework |
| Write tests | Quality |
| Code review | Quality |
| Refactoring | Architecture |
| New end-to-end feature | FullStack |
| Cross-surface debugging | FullStack |

## Custom Agent Creation

To create a new specialized agent, add a section following this template:

```markdown
### [Agent Name] Agent

**Name**: `AgentName`

**Description**: Brief description of expertise and focus area.

**Expertise**:
- Specific skill 1
- Specific skill 2
- Specific skill 3

**Skills**:
- `skill-name-1`
- `skill-name-2`

**Use When**:
- Scenario 1
- Scenario 2
```
