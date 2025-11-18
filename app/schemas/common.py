"""Common schemas"""
from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, Field

DataT = TypeVar('DataT')


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class SortParams(BaseModel):
    """Sorting parameters"""
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field("asc", regex="^(asc|desc)$", description="Sort order")


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Generic paginated response"""
    items: List[DataT]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
