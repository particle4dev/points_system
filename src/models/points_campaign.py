# python-training/lessons/points_system/src/models/points_campaign.py

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, SQLModel


class PointsCampaign(SQLModel, table=True):
    """Represents a points campaign or season from a partner."""
    __tablename__ = "points_campaign"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, nullable=False)
    # type: Optional[str] = Field(default=None)
    multiplier: float = Field(default=1.0, nullable=False)
    
    start_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={"server_default": sa.func.now()},
    )
    end_date: Optional[datetime] = Field(default=None)
    
    partner_slug: str = Field(nullable=False)
    
    # The specific pool address this campaign is associated with (if any)
    pool_address: str = Field(nullable=True)

    tags: List[str] = Field(
        default_factory=list,
        sa_column=sa.Column(postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
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