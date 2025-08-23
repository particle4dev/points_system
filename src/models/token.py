# python-training/lessons/points_system/src/models/token.py
# contract token context

from typing import Optional
from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field, SQLModel

class Token(SQLModel, table=True):
    """Represents an ERC20 token."""
    __tablename__ = "tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    address: str = Field(index=True, unique=True, nullable=False)
    name: str = Field(nullable=False)
    decimals: int = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": sa.func.now()},
    )