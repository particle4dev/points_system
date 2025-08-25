
# Note: reuse the old model
from datetime import datetime
# from typing import List, Optional
import uuid

import sqlmodel
from sqlmodel import Field, SQLModel
import sqlalchemy as sa

# Database model for the main vault table
class Vault(SQLModel, table=True):
    __tablename__ = "vaults"

    id: uuid.UUID = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    contract_address: str | None = None
    
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
