# python-training/lessons/points_system/src/models/partner_uniswapv3_tick.py

from datetime import datetime
# from typing import Optional
from uuid import UUID, uuid4
import sqlalchemy as sa
# from sqlmodel import Field, Relationship, SQLModel
from sqlmodel import Field, SQLModel

# if TYPE_CHECKING:
#     from .partner_uniswapv3_lp import PartnerUniswapV3LP


class PartnerUniswapV3Tick(SQLModel, table=True):
    """Represents a single tick for a Uniswap V3 Liquidity Pool."""
    __tablename__ = "partner_uniswapv3_ticks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    pool_slug: str = Field(index=True, nullable=False)
    tick_idx: int = Field(nullable=False)
    block_number: int = Field(nullable=False)
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

    # # Relationship back to the parent LP
    # pool: "PartnerUniswapV3LP" = Relationship(back_populates="ticks")