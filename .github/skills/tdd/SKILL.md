---
name: tdd
description: Test-driven development for RoboView. Use when building new features, fixing bugs, or adding tests. Follows red-green-refactor loop with vertical slices. Covers pytest patterns for backend and React testing for webview.
---

# Test-Driven Development for RoboView

## Philosophy

**Core principle**: Tests should verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't.

**Good tests** are integration-style: they exercise real code paths through public APIs. They describe _what_ the system does, not _how_ it does it.

**Bad tests** are coupled to implementation. They mock internal collaborators, test private methods, or verify through external means. The warning sign: your test breaks when you refactor, but behavior hasn't changed.

## Anti-Pattern: Horizontal Slices

**DO NOT write all tests first, then all implementation.**

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  RED→GREEN: test3→impl3
```

## Workflow

### 1. Planning

Before writing any code:

- [ ] Confirm with user what interface changes are needed
- [ ] Confirm with user which behaviors to test (prioritize)
- [ ] Identify opportunities for deep modules (small interface, deep implementation)
- [ ] List the behaviors to test (not implementation steps)
- [ ] Get user approval on the plan

### 2. Tracer Bullet

Write ONE test that confirms ONE thing about the system:

```
RED:   Write test for first behavior → test fails
GREEN: Write minimal code to pass → test passes
```

### 3. Incremental Loop

For each remaining behavior:

```
RED:   Write next test → fails
GREEN: Minimal code to pass → passes
```

Rules:
- One test at a time
- Only enough code to pass current test
- Don't anticipate future tests
- Keep tests focused on observable behavior

### 4. Refactor

After all tests pass:

- [ ] Extract duplication
- [ ] Deepen modules (move complexity behind simple interfaces)
- [ ] Apply SOLID principles where natural
- [ ] Run tests after each refactor step

**Never refactor while RED.** Get to GREEN first.

---

## RoboView Backend TDD

### Test Structure

```python
# packages/roboview/tests/utest/services_tests/test_new_service.py

import pytest
from uuid import uuid4
from roboview.registries import KeywordRegistry, FileRegistry
from roboview.services import NewService
from roboview.schemas.domain import KeywordProperties

# Test data factories
def _make_keyword(**kwargs) -> KeywordProperties:
    defaults = {
        "keyword_id": uuid4(),
        "file_name": "test.robot",
        "keyword_name_without_prefix": "Test Keyword",
        "keyword_name_with_prefix": "test.Test Keyword",
        "is_user_defined": True,
        "code": "    Log    Hello",
        "source": "/path/to/test.robot",
    }
    defaults.update(kwargs)
    return KeywordProperties(**defaults)

def _make_registries(keywords: list[KeywordProperties]) -> tuple[KeywordRegistry, FileRegistry]:
    kw_registry = KeywordRegistry()
    file_registry = FileRegistry()
    for kw in keywords:
        kw_registry.register(kw)
    return kw_registry, file_registry


class TestNewServiceGetSomething:
    """Tests for NewService.get_something method."""
    
    def test_returns_empty_list_when_no_keywords(self):
        """When registry is empty, should return empty list."""
        kw_registry, file_registry = _make_registries([])
        service = NewService(kw_registry, file_registry)
        
        result = service.get_something()
        
        assert result == []
    
    def test_returns_matching_keywords_when_filter_applies(self):
        """When filter matches, should return matching keywords."""
        keyword = _make_keyword(keyword_name_without_prefix="Matching")
        kw_registry, file_registry = _make_registries([keyword])
        service = NewService(kw_registry, file_registry)
        
        result = service.get_something(filter="Match")
        
        assert len(result) == 1
        assert result[0].keyword_name_without_prefix == "Matching"
```

### Running Tests

```bash
# All tests
pytest packages/roboview/tests/utest/ -v

# Specific service tests
pytest packages/roboview/tests/utest/services_tests/test_new_service.py -v

# Specific test method
pytest packages/roboview/tests/utest/services_tests/test_new_service.py -k "test_returns_empty" -v

# With coverage
pytest packages/roboview/tests/utest/ --cov=roboview --cov-report=term-missing
```

### API Endpoint Testing

```python
# packages/roboview/tests/utest/api_tests/test_new_endpoint.py

import pytest
from fastapi.testclient import TestClient
from roboview.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_endpoint_returns_200_with_valid_data(client, initialized_app):
    """Endpoint should return 200 with properly formatted data."""
    response = client.get("/new-endpoint")
    
    assert response.status_code == 200
    data = response.json()
    assert "expected_key" in data
```

---

## RoboView Webview TDD

### Component Testing Pattern

```tsx
// vscode-integration/webview-ui/src/__tests__/MetricCard.test.tsx

import { render, screen } from '@testing-library/react';
import { MetricCard } from '../components/MetricCard';

describe('MetricCard', () => {
    it('renders title and value', () => {
        render(<MetricCard title="Keywords" value={42} />);
        
        expect(screen.getByText('Keywords')).toBeInTheDocument();
        expect(screen.getByText('42')).toBeInTheDocument();
    });
    
    it('shows loading skeleton when loading', () => {
        render(<MetricCard title="Keywords" value={null} loading />);
        
        expect(screen.getByTestId('skeleton')).toBeInTheDocument();
    });
});
```

### Hook Testing

```tsx
import { renderHook, act } from '@testing-library/react';
import { useKeywordData } from '../hooks/useKeywordData';

describe('useKeywordData', () => {
    it('fetches data on mount', async () => {
        const { result } = renderHook(() => useKeywordData());
        
        expect(result.current.loading).toBe(true);
        
        await act(async () => {
            // Simulate message response
        });
        
        expect(result.current.loading).toBe(false);
        expect(result.current.data).toBeDefined();
    });
});
```

---

## Checklist Per Cycle

```
[ ] Test describes behavior, not implementation
[ ] Test uses public interface only
[ ] Test would survive internal refactor
[ ] Code is minimal for this test
[ ] No speculative features added
```
