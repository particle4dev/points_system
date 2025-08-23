# python-training/lessons/points_system/src/models/points_partner_snapshot.py

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

class PointsPartnerSnapshot(SQLModel, table=True):
    """
    Represents a periodic snapshot of the cumulative total points a Vault has
    generated with a specific partner. This table is populated by an hourly
    job and serves as the source for the point redistribution calculation.
    """
    __tablename__ = "points_partner_snapshots"
    __table_args__ = (
        # A vault can only have one snapshot per partner at a given time.
        sa.UniqueConstraint("vault_address", "partner_slug", "snapshot_at", name="uq_vault_partner_snapshot_time"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # The unique address of the Vault. This is the identifier used to
    # communicate with the Vaults context. It could be an EOA or a smart contract.
    vault_address: str = Field(index=True, nullable=False)
    
    # The partner who reported these points (e.g., 'pendle', 'hyperswap').
    partner_slug: str = Field(index=True, nullable=False)
    
    # The CUMULATIVE total points for the vault at this specific time.
    points_total: Decimal = Field(
        sa_column=sa.Column(sa.Numeric(36, 18), nullable=False)
    )
    
    # The precise timestamp of the snapshot.
    snapshot_at: datetime = Field(index=True, nullable=False)

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": sa.func.now()},
    )