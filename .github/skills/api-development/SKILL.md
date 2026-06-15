---
name: api-development
description: FastAPI endpoint development for RoboView backend. Use when adding new API endpoints, modifying existing routes, or designing API contracts. Covers request/response schemas, dependency injection, error handling, and OpenAPI documentation.
applyTo: "packages/roboview/roboview/api/**/*.py"
---

# FastAPI API Development for RoboView

## API Architecture

```
packages/roboview/roboview/api/
├── __init__.py
├── app.py              # FastAPI app creation with lifespan
└── endpoints/          # Individual endpoint modules
    ├── health.py       # /system/health
    ├── initialize.py   # /system/initialize
    ├── kpis.py         # /overview/kpis
    └── ...
```

## Creating New Endpoints

### 1. Define Response Schema

First, create or update schemas in `schemas/`:

```python
# schemas/domain/new_feature.py
from pydantic import BaseModel, Field
from uuid import UUID

class FeatureData(BaseModel):
    """Domain model for feature data."""
    
    feature_id: UUID = Field(description="Unique identifier")
    name: str = Field(description="Feature name")
    value: int = Field(ge=0, description="Feature value, must be non-negative")
    
    model_config = {"frozen": True}
```

```python
# schemas/dtos/new_feature_response.py
from pydantic import BaseModel

class FeatureResponse(BaseModel):
    """API response model for feature data."""
    
    feature_id: str
    name: str
    value: int
    
    @classmethod
    def from_domain(cls, domain: FeatureData) -> "FeatureResponse":
        return cls(
            feature_id=str(domain.feature_id),
            name=domain.name,
            value=domain.value,
        )

class FeatureListResponse(BaseModel):
    """API response for list of features."""
    
    features: list[FeatureResponse]
    total_count: int
```

### 2. Create Endpoint Module

```python
# api/endpoints/new_feature.py
from fastapi import APIRouter, HTTPException, Query, Request
from roboview.schemas.dtos.new_feature_response import (
    FeatureResponse,
    FeatureListResponse,
)

router = APIRouter()


@router.get(
    "",
    response_model=FeatureListResponse,
    summary="Get all features",
    description="Returns a list of all features with optional filtering.",
)
async def get_features(
    request: Request,
    name_filter: str | None = Query(
        default=None,
        description="Filter features by name (case-insensitive contains)",
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of results",
    ),
) -> FeatureListResponse:
    """
    Get all features with optional filtering.
    
    Args:
        request: FastAPI request containing app state with services.
        name_filter: Optional filter string for feature names.
        limit: Maximum results to return.
        
    Returns:
        FeatureListResponse with filtered features.
        
    Raises:
        HTTPException: If service fails.
    """
    try:
        service = request.app.state.feature_service
        features = service.get_features(name_filter=name_filter, limit=limit)
        
        return FeatureListResponse(
            features=[FeatureResponse.from_domain(f) for f in features],
            total_count=len(features),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve features: {str(e)}",
        ) from e


@router.get(
    "/{feature_id}",
    response_model=FeatureResponse,
    summary="Get feature by ID",
    responses={
        404: {"description": "Feature not found"},
    },
)
async def get_feature_by_id(
    request: Request,
    feature_id: str,
) -> FeatureResponse:
    """Get a specific feature by its ID."""
    try:
        service = request.app.state.feature_service
        feature = service.get_feature_by_id(feature_id)
        
        if feature is None:
            raise HTTPException(
                status_code=404,
                detail=f"Feature with ID '{feature_id}' not found",
            )
        
        return FeatureResponse.from_domain(feature)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve feature: {str(e)}",
        ) from e
```

### 3. Register Router

Add the router to the app:

```python
# api/app.py
from fastapi import FastAPI
from roboview.api.endpoints import (
    health,
    initialize,
    new_feature,  # Add import
)

def create_app() -> FastAPI:
    app = FastAPI(
        title="RoboView API",
        description="Robot Framework keyword analysis API",
        version="1.0.0",
    )
    
    # Register routers
    app.include_router(health.router, prefix="/system", tags=["System"])
    app.include_router(initialize.router, prefix="/system", tags=["System"])
    app.include_router(new_feature.router, prefix="/features", tags=["Features"])
    
    return app
```

## Dependency Injection Pattern

Services are stored in `app.state` during initialization:

```python
# main.py or app.py lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize services
    keyword_registry = KeywordRegistry()
    file_registry = FileRegistry()
    
    app.state.keyword_usage_service = KeywordUsageService(
        keyword_registry, file_registry
    )
    app.state.feature_service = FeatureService(keyword_registry)
    
    yield
    
    # Shutdown: Cleanup if needed
```

Access in endpoints:

```python
@router.get("")
async def get_data(request: Request):
    service = request.app.state.keyword_usage_service
    return service.get_data()
```

## Error Handling Patterns

### Standard Error Response

```python
from fastapi import HTTPException

# Not found
raise HTTPException(status_code=404, detail="Resource not found")

# Validation error
raise HTTPException(status_code=422, detail="Invalid parameter: x must be positive")

# Internal error with context
try:
    result = service.process()
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e)) from e
except Exception as e:
    raise HTTPException(status_code=500, detail="Internal server error") from e
```

### Custom Error Model

```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None

@router.get(
    "/risky",
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def risky_endpoint():
    ...
```

## Request Body Handling

```python
from pydantic import BaseModel, Field

class InitializeRequest(BaseModel):
    """Request body for initialization."""
    
    project_path: str = Field(description="Path to Robot Framework project")
    robocop_config: str | None = Field(
        default=None,
        description="Path to Robocop config file",
    )

@router.post("/initialize")
async def initialize(
    request: Request,
    body: InitializeRequest,
) -> dict[str, str]:
    service = request.app.state.init_service
    service.initialize(body.project_path, body.robocop_config)
    return {"status": "initialized"}
```

## Testing Endpoints

```python
# tests/utest/api_tests/test_new_feature.py
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client(initialized_app):
    from roboview.main import app
    return TestClient(app)

def test_get_features_returns_empty_list_when_no_data(client):
    response = client.get("/features")
    
    assert response.status_code == 200
    data = response.json()
    assert data["features"] == []
    assert data["total_count"] == 0

def test_get_features_filters_by_name(client, sample_features):
    response = client.get("/features?name_filter=test")
    
    assert response.status_code == 200
    data = response.json()
    assert all("test" in f["name"].lower() for f in data["features"])

def test_get_feature_by_id_returns_404_when_not_found(client):
    response = client.get("/features/nonexistent-id")
    
    assert response.status_code == 404
```

## OpenAPI Documentation

Add rich documentation for better API discoverability:

```python
@router.get(
    "",
    response_model=FeatureListResponse,
    summary="Get all features",
    description="""
    Returns a paginated list of all features in the project.
    
    ## Filtering
    
    Use `name_filter` to search for features by name (case-insensitive).
    
    ## Example
    
    ```
    GET /features?name_filter=login&limit=10
    ```
    """,
    response_description="List of matching features",
    tags=["Features"],
)
```
