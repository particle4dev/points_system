# python-training/lessons/points_system/src/models/points_user_point.py

from datetime import datetime
from decimal import Decimal
# from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

class PointsUserPoint(SQLModel, table=True):
    """
    Represents an aggregated summary of a user's point balance for a specific
    point type. This table is maintained by a database trigger for efficiency.
    """
    __tablename__ = "points_user_point"
    __table_args__ = (
        # Ensures a user can only have one summary balance row per point type.
        sa.UniqueConstraint("wallet_address", "point_type_slug", name="uq_summary_wallet_point_type"),
    )

    id: UUID = Field(
        default_factory=uuid4, 
        primary_key=True,
        sa_column_kwargs={"server_default": sa.text("gen_random_uuid()")}
    )
    wallet_address: str = Field(index=True, nullable=False)
    
    # Foreign key to the type of point being summarized.
    point_type_slug: str = Field(foreign_key="points_point_types.slug", index=True, nullable=False)
    
    # The user's total, current balance for this point type, aggregated
    # from all their campaign earnings.
    points: Decimal = Field(
        default=0,
        sa_column=sa.Column(sa.Numeric(36, 18), nullable=False, server_default="0")
    )

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