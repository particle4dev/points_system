# src/models/partner_protocol_snapshot.py

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

from .enums import ProtocolType, QuantityType # Import from shared file

class PartnerProtocolSnapshot(SQLModel, table=True):
    """
    Stores a historical, point-in-time snapshot of a user's position.
    This table is the source of truth in a snapshot-based architecture.
    """
    __tablename__ = "partner_protocol_snapshot"

    # A composite index is highly recommended for querying the latest snapshot
    __table_args__ = (
        sa.Index("ix_snapshot_position_time", "wallet_address", "protocol_slug", "quantity_type", "token_address", "block_number"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    wallet_address: str = Field(index=True, nullable=False)
    protocol_slug: str = Field(index=True, nullable=False)
    protocol_type: ProtocolType = Field(sa_column=sa.Column(sa.Enum(ProtocolType), nullable=False))
    quantity_type: QuantityType = Field(sa_column=sa.Column(sa.Enum(QuantityType), nullable=False, index=True))
    token_address: str = Field(index=True, nullable=False)

    # The block number at which this snapshot was taken.
    block_number: int = Field(nullable=False)
    
    # The timestamp of the block at which this snapshot was taken.
    timestamp: datetime = Field(nullable=False, index=True)

    # The raw token quantity at the time of the snapshot.
    quantity: Decimal = Field(
        default=0,
        sa_column=sa.Column(sa.Numeric(78, 0), nullable=False, server_default="0")
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": sa.func.now()},
    )