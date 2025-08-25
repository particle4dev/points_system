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
    
    # The current value of the user's holdings in the underlying asset
    # Calculated as: total_shares * current_share_price_of_vault
    total_assets_value: float = Field(default=0)

    # PnL metrics calculated from the history table
    unrealized_pnl: float = Field(default=0)
    realized_pnl: float = Field(default=0)

    # An average entry price for all currently held shares. Useful for UI display.
    # Calculated as: (total cost of remaining lots) / total_shares
    average_cost_basis: float = Field(default=0)

    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))