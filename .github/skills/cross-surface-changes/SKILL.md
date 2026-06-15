---
name: cross-surface-changes
description: Coordinating changes that span multiple surfaces (Python backend, VS Code extension, React webview). Use when implementing features that require changes across the stack, updating APIs, or modifying message protocols.
---

# Cross-Surface Development for RoboView

## Surface Overview

RoboView has three connected surfaces:

```
┌─────────────────────────────────────────────────────────────────┐
│                         VS Code                                  │
│  ┌──────────────────────┐    ┌──────────────────────────────┐  │
│  │   Extension (TS)     │◄──►│      Webview (React)         │  │
│  │                      │    │                               │  │
│  │  - Commands          │    │  - Dashboard                  │  │
│  │  - Services          │    │  - Keyword Usage Panel        │  │
│  │  - Webview Panel     │    │  - Robocop Panel              │  │
│  └──────────┬───────────┘    └──────────────────────────────┘  │
│             │                                                    │
│             │ HTTP (axios)                                       │
│             ▼                                                    │
│  ┌──────────────────────┐                                       │
│  │   Backend (Python)   │                                       │
│  │                      │                                       │
│  │  - FastAPI Server    │                                       │
│  │  - Services          │                                       │
│  │  - Registries        │                                       │
│  └──────────────────────┘                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Communication Protocols

### Backend ↔ Extension (HTTP/REST)

```
Extension                    Backend
    │                           │
    │  GET /system/health       │
    │──────────────────────────►│
    │  200 { status: "ok" }     │
    │◄──────────────────────────│
    │                           │
    │  POST /system/initialize  │
    │  { project_path: "..." }  │
    │──────────────────────────►│
    │  200 { status: "init" }   │
    │◄──────────────────────────│
    │                           │
    │  GET /overview/kpis       │
    │──────────────────────────►│
    │  200 { kpis: {...} }      │
    │◄──────────────────────────│
```

### Extension ↔ Webview (postMessage)

```
Webview                      Extension
    │                           │
    │  { command: 'getKPIs' }   │
    │──────────────────────────►│
    │                           │  (Extension fetches from backend)
    │  { command: 'kpisData',   │
    │    data: {...} }          │
    │◄──────────────────────────│
    │                           │
    │  { command: 'openFile',   │
    │    data: { path, line }}  │
    │──────────────────────────►│
    │                           │  (Extension opens file in editor)
```

## Adding a New Feature Across Surfaces

### Example: Adding "Get Keyword Details" Feature

#### Step 1: Backend Schema & Endpoint

```python
# 1a. Domain schema (packages/roboview/roboview/schemas/domain/keywords.py)
class KeywordDetails(BaseModel):
    keyword_id: UUID
    name: str
    documentation: str | None
    code: str
    source: str
    line_number: int
    called_keywords: list[str]
    usage_count: int

# 1b. DTO (packages/roboview/roboview/schemas/dtos/keyword_details.py)
class KeywordDetailsResponse(BaseModel):
    keyword_id: str
    name: str
    documentation: str | None
    code: str
    source: str
    line_number: int
    called_keywords: list[str]
    usage_count: int
    
    @classmethod
    def from_domain(cls, domain: KeywordDetails) -> "KeywordDetailsResponse":
        return cls(
            keyword_id=str(domain.keyword_id),
            # ... map fields
        )

# 1c. Endpoint (packages/roboview/roboview/api/endpoints/keyword_details.py)
@router.get("/{keyword_id}", response_model=KeywordDetailsResponse)
async def get_keyword_details(request: Request, keyword_id: str):
    service = request.app.state.keyword_usage_service
    details = service.get_keyword_details(keyword_id)
    if not details:
        raise HTTPException(404, "Keyword not found")
    return KeywordDetailsResponse.from_domain(details)
```

#### Step 2: Extension Backend Client

```typescript
// 2a. Type definition (vscode-integration/src/types/keywords.ts)
interface KeywordDetails {
    keyword_id: string;
    name: string;
    documentation: string | null;
    code: string;
    source: string;
    line_number: number;
    called_keywords: string[];
    usage_count: number;
}

// 2b. Backend client method (vscode-integration/src/services/backendConnectionManager.ts)
async getKeywordDetails(keywordId: string): Promise<KeywordDetails> {
    const response = await this.client.get<KeywordDetails>(
        `/keyword-usage/${keywordId}`
    );
    return response.data;
}
```

#### Step 3: Extension Message Handler

```typescript
// 3. Webview panel handler (vscode-integration/src/roboViewPanel.ts)
private async handleMessage(message: WebviewMessage): Promise<void> {
    switch (message.command) {
        case 'getKeywordDetails':
            const details = await this.backendManager.getKeywordDetails(
                message.data.keywordId
            );
            this._panel.webview.postMessage({
                command: 'keywordDetailsData',
                data: details,
            });
            break;
    }
}
```

#### Step 4: Webview Types & Hooks

```typescript
// 4a. Type (vscode-integration/webview-ui/src/types/keywords.ts)
export interface KeywordDetails {
    keyword_id: string;
    name: string;
    documentation: string | null;
    code: string;
    source: string;
    line_number: number;
    called_keywords: string[];
    usage_count: number;
}

// 4b. Hook (vscode-integration/webview-ui/src/hooks/useKeywordDetails.ts)
export function useKeywordDetails(keywordId: string | null) {
    const [details, setDetails] = useState<KeywordDetails | null>(null);
    const [loading, setLoading] = useState(false);
    
    useEffect(() => {
        if (!keywordId) return;
        setLoading(true);
        vscode.postMessage({ command: 'getKeywordDetails', data: { keywordId } });
    }, [keywordId]);
    
    useMessageListener((message) => {
        if (message.command === 'keywordDetailsData') {
            setDetails(message.data as KeywordDetails);
            setLoading(false);
        }
    });
    
    return { details, loading };
}
```

#### Step 5: Webview Component

```tsx
// 5. Component (vscode-integration/webview-ui/src/components/KeywordDetailsPanel.tsx)
export function KeywordDetailsPanel({ keywordId }: { keywordId: string | null }) {
    const { details, loading } = useKeywordDetails(keywordId);
    
    if (loading) return <Skeleton />;
    if (!details) return <EmptyState message="Select a keyword" />;
    
    return (
        <Card>
            <CardHeader>
                <CardTitle>{details.name}</CardTitle>
            </CardHeader>
            <CardContent>
                <p>{details.documentation}</p>
                <CodeBlock code={details.code} />
            </CardContent>
        </Card>
    );
}
```

## Change Coordination Checklist

### When Changing Backend Schemas

- [ ] Update domain model in `schemas/domain/`
- [ ] Update DTO in `schemas/dtos/`
- [ ] Update any services that use the schema
- [ ] Run `pyright` to check type errors
- [ ] Run `pytest` to verify tests pass
- [ ] **Then** update TypeScript types in extension
- [ ] **Then** update TypeScript types in webview
- [ ] Run `npm run check-types` in both

### When Changing API Endpoints

- [ ] Update endpoint implementation
- [ ] Update OpenAPI documentation
- [ ] Update backend tests
- [ ] **Then** update extension client methods
- [ ] **Then** update webview message handlers (if applicable)
- [ ] Test end-to-end with Extension Development Host

### When Changing Message Protocol

- [ ] Update message types in extension
- [ ] Update webview panel handler
- [ ] **Then** update webview message types
- [ ] **Then** update webview hooks/components
- [ ] Test with both surfaces running

## Validation Sequence

Execute validations in order:

```bash
# 1. Backend
cd packages/roboview
pyright
pytest tests/utest/ -v

# 2. Extension
cd vscode-integration
npm run check-types
npm run lint

# 3. Webview
cd vscode-integration/webview-ui
npm run typecheck
npm run build

# 4. Integration
# Press F5 in VS Code to test full stack
```

## Common Pitfalls

### Type Drift
**Problem**: Python schema and TypeScript types get out of sync.
**Solution**: Always update both in the same PR. Consider generating TS types from OpenAPI.

### Message Protocol Mismatch
**Problem**: Webview sends command extension doesn't handle.
**Solution**: Define message types in one place, import in both extension and webview.

### Null/Undefined Handling
**Problem**: Python returns `None`, TypeScript expects `undefined`.
**Solution**: Explicitly handle `null` in TypeScript types, use `| null` not `| undefined`.

### CORS Issues
**Problem**: Webview can't reach backend directly.
**Solution**: All backend communication must go through extension. Webview only uses postMessage.
