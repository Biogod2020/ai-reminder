from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models."""
    pass

class Task(Base):
    """SQLAlchemy model representing a task, supporting recursive sub-tasks and proactive scheduling."""
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    notion_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    status: Mapped[str] = mapped_column(String(50), default='todo')
    cognitive_load_score: Mapped[float] = mapped_column(Float, default=0.0)
    sync_status: Mapped[str] = mapped_column(String(50), default='pending')
    
    # Proactive Scheduling Fields
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    slack_minutes: Mapped[int] = mapped_column(Integer, default=5)

    # Recursive Relationship
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey('tasks.id'))
    children: Mapped[List["Task"]] = relationship("Task", backref="parent", remote_side=[id])

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class UserSoul(Base):
    """SQLAlchemy model representing user-specific habits and preferences."""
    __tablename__ = 'user_soul'

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True)
    value: Mapped[str] = mapped_column(String(1024))
    category: Mapped[str] = mapped_column(String(50))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class VizMetadata(Base):
    """SQLAlchemy model representing metadata for architecture visualization nodes."""
    __tablename__ = 'viz_metadata'

    id: Mapped[int] = mapped_column(primary_key=True)
    node_id: Mapped[str] = mapped_column(String(100), unique=True)
    role: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(1024))
    code_mapping: Mapped[str] = mapped_column(String(255))
    io_schema: Mapped[str] = mapped_column(String(1024))  # Store as JSON string
    load_metrics: Mapped[str] = mapped_column(String(255)) # Store as JSON string or key-value
    metadata_json: Mapped[str] = mapped_column(String(1024), default='{}')

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
