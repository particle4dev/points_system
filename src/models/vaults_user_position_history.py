# src/models/vaults_user_position_history.py
from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum
from uuid import UUID
from datetime import datetime, timezone

class PositionHistoryType(str, Enum):
    """Defines the type of event that changed the user's position."""
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    
    # A true transfer where ownership changes
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"
    
    # A transfer to an approved pool where the user retains ownership
    STAKE_TO_POOL = "STAKE_TO_POOL"
    UNSTAKE_FROM_POOL = "UNSTAKE_FROM_POOL"

class VaultsUserPositionHistory(SQLModel, table=True):
    __tablename__ = "vaults_user_position_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Link to the on-chain event for auditability
    transaction_hash: str = Field(index=True)
    
    # The user and vault this record pertains to
    user_address: str = Field(index=True)
    vault_id: UUID = Field(foreign_key="vaults.id", index=True)
    
    # Event details
    timestamp: datetime = Field(index=True, description="The timestamp of the block containing the transaction")
    transaction_type: PositionHistoryType
    
    # Quantity of shares (yield-bearing tokens) involved in this event. Always positive.
    shares_amount: float
    
    # The price of a single share in terms of the underlying asset at the time of the transaction.
    # This captures the cost basis for DEPOSIT and TRANSFER_IN events.
    share_price_at_transaction: float
    
    # The corresponding amount of the underlying asset (e.g., USDC).
    # Calculated as shares_amount * share_price_at_transaction
    asset_amount: float
    
    # For transfers, this links the sender and receiver.
    counterparty_address: Optional[str] = Field(default=None, index=True)