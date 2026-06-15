---
name: improve-architecture
description: Find architectural improvements and deepening opportunities in the RoboView codebase. Use when reviewing code structure, identifying refactoring candidates, or improving testability and maintainability.
---

# Improve RoboView Architecture

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

## Glossary

Use these terms exactly in every suggestion:

- **Module** — anything with an interface and an implementation (function, class, package, slice)
- **Interface** — everything a caller must know to use the module: types, invariants, error modes, ordering, config
- **Implementation** — the code inside
- **Depth** — leverage at the interface: a lot of behavior behind a small interface. **Deep** = high leverage. **Shallow** = interface nearly as complex as the implementation
- **Seam** — where an interface lives; a place behavior can be altered without editing in place
- **Locality** — what maintainers get from depth: change, bugs, knowledge concentrated in one place

Key principles:
- **Deletion test**: imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.**
- **One adapter = hypothetical seam. Two adapters = real seam.**

## RoboView Architecture Assessment

### Current Architecture Strengths

1. **Clear surface separation**: Backend (`packages/roboview/`) and Extension (`vscode-integration/`) are cleanly separated
2. **Registry pattern**: In-memory caches with clear register/resolve interfaces
3. **Service layer**: Business logic isolated from API layer
4. **Schema separation**: Domain models vs DTOs

### Areas for Review

#### Backend

**Services** (`services/`):
- Are services deep enough? Do they hide complexity or just forward calls?
- Could services be consolidated where they share registries?
- Are service interfaces stable as implementation changes?

**Registries** (`registries/`):
- Are registries just dictionaries with methods, or do they provide meaningful abstraction?
- Could registries evolve to support more complex queries?

**Parsers** (`models/robot_parsing/`):
- Each parser is independent — is there shared parsing infrastructure that could be extracted?
- Could parsing be made more extensible for new Robot Framework constructs?

**Schemas** (`schemas/`):
- Is the domain/DTO split earning its keep?
- Are there domain models that are just data bags?

#### Extension

**Services** (`services/`):
- `BackendConnectionManager` — deep module handling HTTP, health, retries
- `LifecycleManager` — orchestrates startup sequence
- `PythonEnvironmentManager` — validates Python setup

**Message Protocol**:
- Is the webview message protocol well-defined?
- Could message handling be more type-safe?

#### Webview

**Component Structure**:
- Are components deep (encapsulate behavior) or shallow (just styling)?
- Is state management appropriate for complexity?

## Process

### 1. Explore

Walk the codebase organically and note friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called?
- Where do tightly-coupled modules leak across their seams?
- Which parts are hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow.

### 2. Present Candidates

For each refactoring candidate:

- **Files** — which files/modules are involved
- **Problem** — why the current architecture is causing friction
- **Solution** — plain English description of what would change
- **Benefits** — explained in terms of locality and leverage, and how tests would improve
- **Recommendation strength** — `Strong`, `Worth exploring`, `Speculative`

### 3. Validate Before Proposing

Before suggesting architectural changes:

- [ ] Have I understood why it was built this way?
- [ ] Would this change survive the deletion test?
- [ ] Does this make the codebase more testable?
- [ ] Does this make the codebase more AI-navigable?
- [ ] What are the risks of this change?

## Common Deepening Patterns for RoboView

### 1. Service Consolidation

If two services always operate together:

```python
# Before: Two shallow services
class KeywordUsageService:
    def get_usage(self): ...

class KeywordFilterService:
    def filter_unused(self, keywords): ...

# After: One deep service
class KeywordAnalysisService:
    def get_usage(self, filter_unused=False): ...
```

### 2. Registry Evolution

If registries need more complex queries:

```python
# Before: Simple dictionary
class KeywordRegistry:
    def resolve(self, id): return self._store.get(id)

# After: Query interface
class KeywordRegistry:
    def resolve(self, id): ...
    def find_by_file(self, file_name): ...
    def find_by_prefix(self, prefix): ...
    def find_user_defined(self): ...
```

### 3. Message Protocol Typing

```typescript
// Before: Loose typing
interface Message {
    command: string;
    data?: unknown;
}

// After: Discriminated union
type WebviewMessage =
    | { command: 'getKPIs' }
    | { command: 'openFile'; data: { path: string; line?: number } }
    | { command: 'getKeywords'; data: { file: string; filter: string } };
```

### 4. Component Deepening

```tsx
// Before: Shallow component
function KeywordList({ keywords, onSelect }) {
    return <ul>{keywords.map(k => <li onClick={() => onSelect(k)}>{k.name}</li>)}</ul>;
}

// After: Deep component encapsulating filtering, sorting, virtualization
function KeywordList({ keywords, onSelect }) {
    const [filter, setFilter] = useState('');
    const [sort, setSort] = useState<SortConfig>({ field: 'name', dir: 'asc' });
    const filtered = useMemo(() => filterAndSort(keywords, filter, sort), [keywords, filter, sort]);
    
    return (
        <div>
            <SearchInput value={filter} onChange={setFilter} />
            <VirtualizedList items={filtered} onSelect={onSelect} />
        </div>
    );
}
```

## Cross-Surface Changes

When architectural changes span surfaces:

1. **Schema changes** — Update Python schemas first, then TypeScript types
2. **API changes** — Version carefully, update extension consumers
3. **Message protocol changes** — Update both extension and webview together

Always verify both surfaces after cross-boundary changes.
