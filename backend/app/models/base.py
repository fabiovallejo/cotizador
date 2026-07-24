"""Base classes y mixins para todos los modelos."""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Base para modelos
Base = declarative_base()

class TimestampMixin:
    """Mixin para auditoría de fechas."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class SoftDeleteMixin:
    """Mixin para soft delete."""
    deleted_at = Column(DateTime, nullable=True, index=True)
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

class AuditMixin(TimestampMixin):
    """Mixin completo de auditoría."""
    pass