---
name: diagnose
description: Disciplined diagnosis loop for hard bugs and performance regressions in RoboView. Use when debugging issues in the backend, extension, or webview. Follows reproduce → minimise → hypothesise → instrument → fix → regression-test methodology.
---

# Diagnose

A discipline for hard bugs in the RoboView codebase. Skip phases only when explicitly justified.

## Phase 1 — Build a Feedback Loop

**This is the skill.** Everything else is mechanical. If you have a fast, deterministic, agent-runnable pass/fail signal for the bug, you will find the cause.

### RoboView-Specific Feedback Loops

Choose the right loop based on where the bug lives:

#### Backend Bugs (Python)
1. **Failing pytest test** — Preferred for service/registry/API bugs
   ```bash
   pytest packages/roboview/tests/utest/services_tests/test_keyword_usage_service.py -k "test_specific_case" -v
   ```

2. **API endpoint test** — For HTTP-level issues
   ```bash
   # Start server
   uvicorn roboview.main:app --port 18123
   # Test endpoint
   curl http://127.0.0.1:18123/keyword-usage/keywords-wo-usages
   ```

3. **Parser test** — For Robot Framework parsing issues
   ```python
   # Create minimal .robot file, run parser directly
   from roboview.models.robot_parsing import CalledKeywordFinder
   finder = CalledKeywordFinder()
   # Test with specific input
   ```

#### Extension Bugs (TypeScript)
1. **Extension Host debugging** — Press F5 to launch Extension Development Host
2. **Output channel logs** — Check "RoboView" output channel for errors
3. **Developer Tools** — Ctrl+Shift+I in webview to see console errors

#### Webview Bugs (React)
1. **Vite dev server** — Run webview in isolation
   ```bash
   cd vscode-integration/webview-ui
   npm run dev
   ```
2. **React DevTools** — Inspect component state
3. **Network tab** — Verify message passing

### Iterate on the Loop

- Can I make it faster? (Use focused pytest `-k` filters, skip unrelated init)
- Can I make the signal sharper? (Assert on the specific symptom)
- Can I make it more deterministic? (Mock external dependencies)

## Phase 2 — Reproduce

Run the loop. Watch the bug appear.

Confirm:
- [ ] The loop produces the failure mode the **user** described
- [ ] The failure is reproducible across multiple runs
- [ ] You have captured the exact symptom (error message, wrong output)

Do not proceed until you reproduce the bug.

## Phase 3 — Hypothesise

Generate **3–5 ranked hypotheses** before testing any of them.

Each hypothesis must be **falsifiable**:

> Format: "If <X> is the cause, then <changing Y> will make the bug disappear / <changing Z> will make it worse."

### Common RoboView Bug Categories

**Backend:**
- Registry not populated correctly (initialization order)
- Schema validation failures (Pydantic)
- Robot Framework parsing edge cases
- Service method returning wrong data shape

**Extension:**
- Backend not starting (Python environment issue)
- Message passing failure (webview ↔ extension)
- Command registration timing

**Webview:**
- State not updating (missing useEffect dependency)
- Type mismatch in message handling
- VS Code theme variable not applied

## Phase 4 — Instrument

Each probe must map to a specific prediction from Phase 3. Change one variable at a time.

### RoboView Instrumentation Tools

**Python:**
```python
# Tag debug logs for easy cleanup
import logging
logger = logging.getLogger(__name__)
logger.debug("[DEBUG-abc123] Variable state: %s", var)
```

**TypeScript:**
```typescript
// Output channel logging
this.outputChannel.appendLine(`[DEBUG-abc123] State: ${JSON.stringify(state)}`);
```

**React:**
```tsx
// Temporary console logging
console.log('[DEBUG-abc123] Props:', props);
useEffect(() => {
    console.log('[DEBUG-abc123] Effect triggered');
}, [dependency]);
```

**Tag every debug log** with a unique prefix. Cleanup at the end becomes a single grep.

## Phase 5 — Fix + Regression Test

Write the regression test **before the fix** — but only if there is a correct seam.

### RoboView Test Seams

**Backend services** — Good seam:
```python
def test_get_keywords_without_usages_handles_edge_case(tmp_path):
    """Regression test for issue #XYZ."""
    # Arrange: Create minimal reproducing state
    registry = KeywordRegistry()
    # ... setup
    service = KeywordUsageService(registry, file_registry)
    
    # Act
    result = service.get_keywords_without_usages()
    
    # Assert: Verify fix
    assert len(result) == expected
```

**API endpoints** — Integration seam:
```python
def test_endpoint_handles_edge_case(client):
    """Regression test for API issue."""
    response = client.get("/keyword-usage/specific-endpoint")
    assert response.status_code == 200
    assert response.json()["expected_field"] == expected_value
```

## Phase 6 — Cleanup + Post-mortem

Required before declaring done:

- [ ] Original repro no longer reproduces
- [ ] Regression test passes (or absence of seam is documented)
- [ ] All `[DEBUG-...]` instrumentation removed
- [ ] Commit message states the hypothesis that turned out correct

**Then ask: what would have prevented this bug?**

If the answer involves:
- Missing test coverage → Add tests
- Unclear API contract → Update schema documentation
- Cross-surface integration issue → Add integration test
- Architecture problem → Note for future refactoring
