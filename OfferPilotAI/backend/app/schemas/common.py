"""Common API schemas."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    """Standard API error item."""

    code: str = Field(..., examples=["VALIDATION_ERROR"])
    message: str = Field(..., examples=["Field is required."])
    field: str | None = Field(default=None, examples=["email"])


class ResponseMeta(BaseModel):
    """Standard API response metadata."""

    request_id: str | None = None
    timestamp: str | None = None
    pagination: dict[str, Any] | None = None


class APIResponse(BaseModel, Generic[DataT]):
    """Standard API envelope."""

    data: DataT | None = None
    meta: ResponseMeta | dict[str, Any] = Field(default_factory=ResponseMeta)
    errors: list[ErrorDetail] = Field(default_factory=list)


class PaginationParams(BaseModel):
    """Validated pagination inputs."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)


class ORMModel(BaseModel):
    """Base schema for SQLAlchemy-backed models."""

    model_config = ConfigDict(from_attributes=True)


class DeleteResponse(BaseModel):
    """Response body for delete operations."""

    id: str
    deleted: bool = True
