# python-training/lessons/points_system/src/models/partner_pool.py

# Note: we use slug if in case the pools don't have pool address
# if there is pool address then it will be slug

from datetime import datetime
# from typing import List, Optional, TYPE_CHECKING
from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
# from sqlmodel import Field, SQLModel, Relationship
from sqlmodel import Field, SQLModel

# # Conditionally import the LP model
# if TYPE_CHECKING:
#     from .partner_uniswapv3_lp import PartnerUniswapV3LP

class PartnerPool(SQLModel, table=True):
    """Represents a partner in the points ecosystem."""
    __tablename__ = "partner_pool"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    slug: str = Field(index=True, nullable=False, unique=True)
    partner_slug: str = Field(index=True, nullable=False)
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
    
    # # Add the relationship to the LP table
    # uniswap_v3_lps: List["PartnerUniswapV3LP"] = Relationship(back_populates="pool")