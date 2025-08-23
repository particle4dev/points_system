# python-training/lessons/points_system/src/models/partner.py

from datetime import datetime
# from typing import List, Optional, TYPE_CHECKING
from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
# from sqlmodel import Field, Relationship, SQLModel
from sqlmodel import Field, SQLModel

# if TYPE_CHECKING:
#     from .partner_pool import PartnerPool


class Partner(SQLModel, table=True):
    """Represents a top-level partner entity in the ecosystem."""
    __tablename__ = "partner"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    slug: str = Field(unique=True, index=True, nullable=False)
    website: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
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

    # # Relationship to the pools this partner offers
    # pools: List["PartnerPool"] = Relationship(back_populates="partner")