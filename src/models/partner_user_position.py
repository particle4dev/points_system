# python-training/lessons/points_system/src/models/partner_user_position.py
# python-training/lessons/points_system/src/models/partner_user_position.py

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

class ProtocolType(str, Enum):
    """ High-level category of the protocol for application logic. """
    DEX_UNISWAPV3 = "DEX_UNISWAPV3"
    LENDING_HYPURRFI = "LENDING_HYPURRFI"
    YIELD_PENDLE = "YIELD_PENDLE"

class QuantityType(str, Enum):
    """ The specific type of financial activity that earns points. """
    LP = "LP"
    YT = "YT"
    BORROW = "BORROW"

class PartnerUserPosition(SQLModel, table=True):
    """
    Consolidated table storing the CURRENT USD VALUE and raw quantity of a user's 
    specific pointable activity for a specific token within a given partner protocol.
    """
    __tablename__ = "partner_user_position"
    __table_args__ = (
        # A user can have one position per token for a given activity type and protocol.
        sa.UniqueConstraint(
            "wallet_address", "protocol_slug", "quantity_type", "token_address", 
            name="uq_user_protocol_quantity_token"
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    wallet_address: str = Field(index=True, nullable=False)
    protocol_slug: str = Field(index=True, nullable=False)
    protocol_type: ProtocolType = Field(sa_column=sa.Column(sa.Enum(ProtocolType), nullable=False))
    quantity_type: QuantityType = Field(sa_column=sa.Column(sa.Enum(QuantityType), nullable=False, index=True))
    
    # The specific token this position is for.
    # token_address: str = Field(foreign_key="tokens.address", index=True, nullable=False)
    token_address: str = Field(index=False, nullable=False)

    # The current raw token quantity (e.g., in wei).
    quantity: Decimal = Field(
        default=0,
        sa_column=sa.Column(sa.Numeric(78, 0), nullable=False, server_default="0")
    )
    
    # The current total value of this activity in USD.
    quantity_usd: Decimal = Field(
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