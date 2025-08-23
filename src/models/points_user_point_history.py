# python-training/lessons/points_system/src/models/points_user_point_history.py

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

class PointsUserPointHistory(SQLModel, table=True):
    """
    Represents a single transaction or change in a user's point balance for a
    specific campaign. This is an immutable, append-only ledger maintained by a
    database trigger for auditing and historical analysis.
    """
    __tablename__ = "points_user_point_history"

    id: UUID = Field(
        default_factory=uuid4, 
        primary_key=True,
        sa_column_kwargs={"server_default": sa.text("gen_random_uuid()")}
    )
    
    # A reference to the specific record in points_user_campaign_points that
    # triggered this history entry, for easy traceability.
    source_event_id: UUID = Field(foreign_key="points_user_campaign_points.id", index=True, nullable=False)
    
    wallet_address: str = Field(index=True, nullable=False)
    campaign_id: UUID = Field(foreign_key="points_campaign.id", index=True, nullable=False)
    point_type_slug: str = Field(foreign_key="points_point_types.slug", index=True, nullable=False)
    
    # The delta or change in points for this event. Can be positive or negative.
    points_change: Decimal = Field(
        sa_column=sa.Column(sa.Numeric(36, 18), nullable=False)
    )
    
    # The timestamp of when this specific change occurred.
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": sa.func.now()},
    )