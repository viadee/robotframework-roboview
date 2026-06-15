---
name: roboview-backend
description: Python backend development for RoboView. Use when modifying FastAPI services, registries, schemas, API endpoints, or the CLI. Covers service patterns, registry operations, schema design, and API development following the established architecture.
applyTo: "packages/roboview/**/*.py"
---

# RoboView Backend Development

## Architecture Overview

The RoboView backend is a FastAPI-based Python server providing RESTful APIs for Robot Framework keyword analysis. The architecture follows a layered pattern with clear separation of concerns.

### Directory Structure

```
packages/roboview/roboview/
├── api/                    # FastAPI endpoints
│   └── endpoints/          # Individual endpoint files
├── cli/                    # Typer-based CLI commands
├── core/                   # Config and logging
├── models/                 # Robot Framework parsers
│   └── robot_parsing/      # ModelVisitor implementations
├── registries/             # In-memory data stores
├── schemas/                # Data models
│   ├── domain/             # Domain models
│   └── dtos/               # API response DTOs
├── services/               # Business logic
└── utils/                  # Utilities and exporters
```

## Development Patterns

### 1. Service Development

Services contain business logic and operate on registries. Follow this pattern:

```python
class NewService:
    """Service description."""
    
    def __init__(
        self,
        keyword_registry: KeywordRegistry,
        file_registry: FileRegistry,
    ) -> None:
        self._keyword_registry = keyword_registry
        self._file_registry = file_registry
    
    def get_something(self, param: str) -> SomeSchema:
        """
        Get something meaningful.
        
        Args:
            param: Description of parameter.
            
        Returns:
            Meaningful result.
        """
        # Implementation using registries
        pass
```

**Key methods naming conventions:**
- `get_*` - Retrieve data
- `_build_*` - Internal construction methods
- `_load_*` - Internal data loading
- `_calculate_*` - Computation methods

### 2. Registry Development

Registries are in-memory caches with register/resolve patterns:

```python
class NewRegistry:
    """Registry description."""
    
    def __init__(self) -> None:
        self._store: dict[str, EntitySchema] = {}
    
    def register(self, entity: EntitySchema) -> None:
        self._store[entity.id] = entity
    
    def resolve(self, entity_id: str) -> EntitySchema | None:
        return self._store.get(entity_id)
    
    def get_all(self) -> list[EntitySchema]:
        return list(self._store.values())
```

### 3. API Endpoint Development

Endpoints follow FastAPI patterns with dependency injection:

```python
from fastapi import APIRouter, HTTPException, Request
from schemas.dtos.response import ResponseSchema

router = APIRouter()

@router.get("", response_model=ResponseSchema)
async def get_resource(request: Request, param: str | None = None) -> ResponseSchema:
    """
    Endpoint description.
    
    Args:
        request: FastAPI request with app state.
        param: Optional query parameter.
        
    Returns:
        Response data.
    """
    try:
        service = request.app.state.some_service
        result = service.get_something(param)
        return ResponseSchema.from_domain(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
```

### 4. Schema Development

**Domain schemas** (in `schemas/domain/`):
```python
from pydantic import BaseModel, Field
from uuid import UUID

class EntityProperties(BaseModel):
    """Domain model for Entity."""
    
    entity_id: UUID = Field(description="Unique identifier")
    name: str = Field(description="Entity name")
    
    model_config = {"frozen": True}
```

**DTO schemas** (in `schemas/dtos/`):
```python
class EntityResponse(BaseModel):
    """API response model for Entity."""
    
    entity_id: str
    name: str
    
    @classmethod
    def from_domain(cls, domain: EntityProperties) -> "EntityResponse":
        return cls(
            entity_id=str(domain.entity_id),
            name=domain.name,
        )
```

### 5. Robot Framework Parser Development

Parsers use `robot.api.parsing.ModelVisitor`:

```python
from robot.api.parsing import ModelVisitor, Token, Keyword

class NewFinder(ModelVisitor):
    """Finds something in Robot Framework files."""
    
    def __init__(self) -> None:
        self._results: list[str] = []
    
    def visit_Keyword(self, node: Keyword) -> None:
        """Process keyword nodes."""
        # Extract information from the keyword
        self._results.append(node.name)
        self.generic_visit(node)
    
    @property
    def results(self) -> list[str]:
        return self._results
```

## Validation Requirements

Before committing backend changes:

1. **Type checking**: `pyright packages/roboview/`
2. **Tests**: `pytest packages/roboview/tests/utest/`
3. **Linting**: Check for style consistency

## Key Dependencies

- **FastAPI** + **Uvicorn**: Web framework and ASGI server
- **Pydantic**: Data validation and serialization
- **Robot Framework**: `robot.api.parsing` for file parsing
- **Robocop**: Linting integration
- **Typer**: CLI framework
- **ReportLab** / **OpenPyXL**: Report generation

## Testing Patterns

Use factory helpers for test data:

```python
def _make_keyword(
    name: str = "Test Keyword",
    is_user_defined: bool = True,
    **kwargs
) -> KeywordProperties:
    return KeywordProperties(
        keyword_id=uuid4(),
        file_name="test.robot",
        keyword_name_without_prefix=name,
        keyword_name_with_prefix=f"test.{name}",
        is_user_defined=is_user_defined,
        **kwargs,
    )
```

Test function naming: `test_<method_name>_<scenario>`

```python
def test_get_keywords_without_usages_returns_empty_for_all_used(tmp_path):
    """Test that no unused keywords returns empty list."""
    # Arrange, Act, Assert
```
