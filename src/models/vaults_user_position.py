# src/models/vaults_user_position.py
from typing import Optional
from sqlmodel import SQLModel, Field
from uuid import UUID
from datetime import datetime, timezone

class VaultsUserPosition(SQLModel, table=True):
    __tablename__ = "vaults_user_position"

    # A user's position in a single vault is unique
    user_address: str = Field(primary_key=True)
    vault_id: UUID = Field(foreign_key="vaults.id", primary_key=True)

    # The most critical field for reward calculation
    total_shares: float = Field(default=0, description="The current total number of shares held by the user.")

    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
