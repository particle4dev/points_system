# python-training/lessons/points_system/src/models/partner_protocol_event.py
    
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Field, SQLModel
from .partner_user_position import ProtocolType, QuantityType

class PartnerProtocolEvent(SQLModel, table=True):
    """
    Core immutable ledger for all partner protocol events. It stores the CHANGE
    in both raw quantity and USD value for a specific QuantityType, which 
    triggers updates to the PartnerUserPosition table.
    """
    __tablename__ = "partner_protocol_event"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tx_hash: str = Field(unique=True, index=True, nullable=False)
    block_number: int = Field(nullable=False, index=True)
    timestamp: datetime = Field(nullable=False, index=True)
    wallet_address: str = Field(index=True, nullable=False)
    protocol_slug: str = Field(index=True, nullable=False)
    protocol_type: ProtocolType = Field(sa_column=sa.Column(sa.Enum(ProtocolType), nullable=False))
    quantity_type: QuantityType = Field(sa_column=sa.Column(sa.Enum(QuantityType), nullable=False))
    
    # The change in raw token quantity for this event (e.g., in wei).
    quantity_change: Decimal = Field(sa_column=sa.Column(sa.Numeric(78, 0), nullable=False))

    # The delta for this event in USD.
    quantity_change_usd: Decimal = Field(sa_column=sa.Column(sa.Numeric(36, 18), nullable=False))

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": sa.func.now()},
    )