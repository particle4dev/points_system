# python-training/lessons/points_system/src/models/partner_uniswapv3_event.py

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlmodel import Field, SQLModel
from enum import Enum

class EventType(str, Enum):
    """Defines the type of Uniswap V3 LP event."""
    INCREASE_LIQUIDITY = "INCREASE_LIQUIDITY"
    DECREASE_LIQUIDITY = "DECREASE_LIQUIDITY"

class PartnerUniswapV3Event(SQLModel, table=True):
    """
    Represents a single historical event (add/remove) for a Uniswap V3 LP position.
    This table acts as an immutable log for calculating points over time.
    """
    __tablename__ = "partner_uniswapv3_events"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # Event Identification
    event_type: EventType = Field(
        sa_column=sa.Column(sa.Enum(EventType), nullable=False, index=True)
    )
    tx_hash: str = Field(unique=True, index=True, nullable=False)
    block_number: int = Field(nullable=False, index=True)
    # timestamp: datetime = Field(nullable=False, index=True)

    # Position and Ownership
    pool_slug: str = Field(index=True, nullable=False)
    nft_id: str = Field(index=True, nullable=False) # The NFT this event is for
    wallet_address: str = Field(index=True, nullable=False)

    # Change in Value
    # The raw change in liquidity for this specific event.
    liquidity_change: Decimal = Field(max_digits=36, decimal_places=0)
    # The corresponding change in token0 for this event.
    amount0_change: Decimal = Field(max_digits=78, decimal_places=0)
    # The corresponding change in token1 for this event.
    amount1_change: Decimal = Field(max_digits=78, decimal_places=0)

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": sa.func.now()},
    )