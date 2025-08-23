# python-training/lessons/points_system/src/models/points_point_type.py

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

class PointsPointType(SQLModel, table=True):
    """
    Defines a type of point that can be earned, linked to a specific partner.
    e.g., 'HyperSwap Points', 'Pendle Points'.
    """
    __tablename__ = "points_point_types"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # The unique, machine-readable identifier for the point type.
    slug: str = Field(unique=True, index=True, nullable=False)
    
    # The human-readable name of the points.
    name: str = Field(nullable=False)
    
    description: Optional[str] = Field(default=None)
    
    # The partner this point type is associated with.
    # NOTE: This is NOT a foreign key to maintain bounded context separation.
    partner_slug: str = Field(index=True, nullable=False)

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": sa.func.now()},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": sa.func.now(), "onupdate": sa.func.now()},
    )