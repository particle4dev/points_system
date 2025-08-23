# python-training/lessons/points_system/src/models/points_user_campaign_points.py

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

class PointsUserCampaignPoints(SQLModel, table=True):
    """
    Represents the points a user has earned from a specific campaign.
    This acts as a ledger record.
    """
    __tablename__ = "points_user_campaign_points"
    __table_args__ = (
        # A user should only have one points entry per campaign.
        sa.UniqueConstraint("wallet_address", "campaign_id", name="uq_wallet_campaign"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    wallet_address: str = Field(index=True, nullable=False)
    
    # Foreign key to the specific campaign that awarded these points.
    campaign_id: UUID = Field(foreign_key="points_campaign.id", index=True, nullable=False)
    
    # Foreign key to the type of point that was awarded.
    point_type_slug: str = Field(foreign_key="points_point_types.slug", index=True, nullable=False)
    
    # The total points earned from this specific campaign.
    points_earned: Decimal = Field(
        default=0, 
        sa_column=sa.Column(sa.Numeric(36, 18), nullable=False)
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