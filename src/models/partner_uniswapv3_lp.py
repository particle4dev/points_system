# python-training/lessons/points_system/src/models/partner_uniswapv3_lp.py

from datetime import datetime
from decimal import Decimal
# from typing import Optional
from uuid import UUID, uuid4
import sqlalchemy as sa
# from sqlmodel import Field, Relationship, SQLModel
from sqlmodel import Field, SQLModel
# from .token import Token

class PartnerUniswapV3LP(SQLModel, table=True):
    """Represents a partner's Uniswap V3 Liquidity Pool eligible for points."""
    __tablename__ = "partner_uniswapv3_lp"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pool_slug: str = Field(index=True, nullable=False)
    nft_id: str = Field(index=True) # NFT ID representing user's LP position
    wallet_address: str = Field(index=True) # User's wallet address
    price_lower_tick: int # Lower price tick of the active price range
    price_upper_tick: int # Upper price tick of the active price range
    liquidity: Decimal = Field(max_digits=36, decimal_places=0) # Total liquidity value

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

    # # Foreign Keys to the Token table
    # token0_id: int = Field(foreign_key="tokens.id")
    # token1_id: int = Field(foreign_key="tokens.id")

    # # Relationships to load Token objects
    # token0: Optional[Token] = Relationship(sa_relationship_kwargs={"foreign_keys": "[PartnerUniswapV3LP.token0_id]"})
    # token1: Optional[Token] = Relationship(sa_relationship_kwargs={"foreign_keys": "[PartnerUniswapV3LP.token1_id]"})
