---
name: code-review
description: Systematic code review for RoboView contributions. Use when reviewing pull requests, checking code quality, or validating changes before merge. Covers style, testing, security, and cross-surface consistency.
---

# Code Review for RoboView

## Review Philosophy

Good code review catches issues early, shares knowledge, and maintains consistency. Focus on:

1. **Correctness** — Does it work? Does it handle edge cases?
2. **Maintainability** — Can others understand and modify it?
3. **Consistency** — Does it follow project patterns?
4. **Testing** — Is it adequately tested?
5. **Cross-Surface Impact** — Does it affect other surfaces correctly?

## Review Checklist by Surface

### Python Backend (`packages/roboview/`)

#### Code Quality
- [ ] Follows existing patterns (services, registries, schemas)
- [ ] Type hints on all public functions and methods
- [ ] Docstrings on all public functions with Args/Returns
- [ ] No unused imports or variables
- [ ] Exceptions are specific, not bare `except:`
- [ ] Logging uses structured format with appropriate levels

#### Testing
- [ ] New functionality has corresponding tests
- [ ] Tests use factory helpers, not hardcoded data
- [ ] Test names follow `test_<method>_<scenario>` pattern
- [ ] Edge cases are covered (empty inputs, None values)
- [ ] `pytest` passes locally

#### Type Safety
- [ ] `pyright` reports no errors on changed files
- [ ] Schema models use `Field()` with descriptions
- [ ] Optional fields explicitly typed as `X | None`

#### API Changes
- [ ] Response models defined in `schemas/dtos/`
- [ ] Error responses documented
- [ ] Endpoint has summary and description
- [ ] Breaking changes documented

### TypeScript Extension (`vscode-integration/src/`)

#### Code Quality
- [ ] Follows existing service patterns
- [ ] Proper error handling with user-friendly messages
- [ ] Disposables are cleaned up
- [ ] Output channel logging for debugging
- [ ] No `any` types without justification

#### Testing
- [ ] Critical paths have tests
- [ ] Mocks are minimal and focused
- [ ] `npm run check-types` passes
- [ ] `npm run lint` passes

#### VS Code API Usage
- [ ] Commands registered in `registerCommands()`
- [ ] Subscriptions added to `context.subscriptions`
- [ ] Configuration reads use proper defaults
- [ ] Webview messages are typed

### React Webview (`vscode-integration/webview-ui/`)

#### Code Quality
- [ ] Components follow existing patterns
- [ ] Props are typed with interfaces
- [ ] Hooks follow rules (dependencies, cleanup)
- [ ] No direct DOM manipulation
- [ ] Tailwind classes used consistently

#### State Management
- [ ] Local state for UI-only concerns
- [ ] Message passing for data from extension
- [ ] Memoization for expensive computations
- [ ] Loading states handled

#### Accessibility
- [ ] Interactive elements are keyboard accessible
- [ ] ARIA labels where needed
- [ ] Color contrast meets VS Code theme requirements

#### Performance
- [ ] Large lists use virtualization
- [ ] No unnecessary re-renders
- [ ] Images/assets are optimized

### Robot Framework Tests (`rf_usergrp_vtiger/`)

#### Code Quality
- [ ] Keywords have `[Documentation]`
- [ ] Variables use consistent naming (`${UPPER_CASE}` for constants)
- [ ] Resource imports are minimal and specific
- [ ] Selectors in separate `sel*.resource` files

#### Test Quality
- [ ] Tests are independent (can run in any order)
- [ ] Test names describe behavior, not implementation
- [ ] Appropriate tags for filtering
- [ ] Setup/teardown handle cleanup

## Review by Change Type

### New Feature

1. **Design Review**
   - Does the feature fit the existing architecture?
   - Are interfaces minimal and deep?
   - Is it in the right surface(s)?

2. **Implementation Review**
   - Follows established patterns?
   - Handles errors gracefully?
   - Has appropriate logging?

3. **Testing Review**
   - Unit tests for new logic
   - Integration tests if crossing surfaces
   - Manual testing instructions provided

4. **Documentation Review**
   - Code comments where non-obvious
   - README updates if needed
   - API documentation if applicable

### Bug Fix

1. **Root Cause**
   - Is the actual root cause addressed?
   - Could the fix cause regressions?

2. **Regression Test**
   - Is there a test that would have caught this?
   - Is there a test that prevents recurrence?

3. **Similar Issues**
   - Are there similar patterns elsewhere that need fixing?

### Refactoring

1. **Behavior Preservation**
   - Does existing functionality still work?
   - Are tests updated appropriately?

2. **Incremental Change**
   - Is the refactor scoped appropriately?
   - Can it be merged safely?

3. **Cross-Surface Impact**
   - Does this affect interfaces between surfaces?
   - Are dependent surfaces updated?

## Review Comments

### Good Comment Examples

```
# Specific and actionable
"This could return `None` if the registry is empty. Consider handling that case explicitly."

# Explains why
"The current pattern uses dependency injection here. Could we follow that instead of accessing `request.app.state` directly?"

# Offers alternative
"This nested loop is O(n²). For large registries, consider pre-building a lookup dict."

# Asks clarifying question
"I see this catches all exceptions. Is there a specific exception type we expect here?"
```

### Comment Levels

- **Blocker**: Must be fixed before merge
- **Suggestion**: Would improve code, author's discretion
- **Question**: Clarification needed, may not require change
- **Nit**: Minor style/preference, low priority

## Automated Checks

Ensure these pass before manual review:

```yaml
# Python
- pyright packages/roboview/
- pytest packages/roboview/tests/utest/ --tb=short
- deptry packages/roboview/

# TypeScript
- npm run check-types (in vscode-integration/)
- npm run lint (in vscode-integration/)

# Webview
- npm run typecheck (in webview-ui/)
- npm run build (in webview-ui/)
```

## Post-Review

After approval:

- [ ] Squash/rebase commits if needed
- [ ] Update PR description with final changes
- [ ] Merge when CI passes
- [ ] Delete feature branch
- [ ] Verify deployment/build succeeds
