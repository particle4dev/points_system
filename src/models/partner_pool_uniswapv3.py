# python-training/lessons/points_system/src/models/partner_pool_uniswapv3.py

from datetime import datetime
# from typing import Optional, TYPE_CHECKING
from typing import Optional

import sqlalchemy as sa
from sqlmodel import Field, SQLModel, Relationship

# if TYPE_CHECKING:
#     from .token import Token
#     from .partner_pool import PartnerPool

class PartnerPoolUniswapV3(SQLModel, table=True):
    """
    Acts as an extension table to PartnerPool for Uniswap V3 specific metadata.
    """
    __tablename__ = "partner_pool_uniswapv3"

    id: Optional[int] = Field(default=None, primary_key=True)

    pool_slug: str = Field(
        sa_column=sa.Column(sa.String, sa.ForeignKey("partner_pool.slug"), unique=True, index=True, nullable=False)
    )
    token0_address: str = Field(
        sa_column=sa.Column(sa.String, sa.ForeignKey("tokens.address"), nullable=False)
    )
    token1_address: str = Field(
        sa_column=sa.Column(sa.String, sa.ForeignKey("tokens.address"), nullable=False)
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

    # # Relationship to the parent PartnerPool
    # pool: "PartnerPool" = Relationship(back_populates="uniswap_v3_metadata")

    # # Relationships to load Token objects
    # token0: "Token" = Relationship(sa_relationship_kwargs={"foreign_keys": "[PartnerPoolUniswapV3.token0_address]", "primaryjoin": "PartnerPoolUniswapV3.token0_address == Token.address"})
    # token1: "Token" = Relationship(sa_relationship_kwargs={"foreign_keys": "[PartnerPoolUniswapV3.token1_address]", "primaryjoin": "PartnerPoolUniswapV3.token1_address == Token.address"})