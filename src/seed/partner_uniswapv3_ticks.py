# python-training/lessons/points_system/src/seed/partner_uniswapv3_ticks.py

# from datetime import datetime, timezone
from core.db import get_session
from src.models import PartnerPool, PartnerUniswapV3Tick
from sqlmodel import select

# --- 1. Define Seed Data ---
ticks_data_raw = {
    "pool_slug": "0xfde5b0626fc80e36885e2fa9cd5ad9d7768d725c",
    "ticks": [
        {
            "tickIdx": 10,
            "block_number": "9175192"
        },
        {
            "tickIdx": 100,
            "block_number": "9181517"
        },
        {
            "tickIdx": -101,
            "block_number": "9175459"
        },
        # Add more tick data here if you wish...
    ]
}

# --- 2. Define Create and Delete Functions ---
def create_partner_uniswapv3_ticks():
    """Inserts tick records, linking them to an existing LP."""
    print("Seeding Uniswap v3 ticks...")
    with get_session() as session:
        # Find the parent Liquidity Pool by its address
        pool_slug = ticks_data_raw["pool_slug"]
        statement = select(PartnerPool).where(PartnerPool.slug == pool_slug)
        pool = session.exec(statement).first()

        if not pool:
            print(f"⚠️  LP with address {pool_slug} not found. Skipping ticks seeding.")
            return

        ticks_to_create = []
        for data in ticks_data_raw["ticks"]:
            tick_idx = int(data["tickIdx"])
            block_number = int(data["block_number"])
            print(f"Processing tick {tick_idx} for pool {pool.slug}...")
            # Check if this specific tick already exists for this pool
            statement = select(PartnerUniswapV3Tick).where(
                PartnerUniswapV3Tick.pool_slug == pool_slug,
                PartnerUniswapV3Tick.tick_idx == tick_idx
            )
            exists = session.exec(statement).first()
            if not exists:
                ticks_to_create.append(
                    PartnerUniswapV3Tick(
                        pool_slug=pool_slug,
                        tick_idx=tick_idx,
                        block_number=block_number,
                        # created_at=datetime.fromtimestamp(int(data["createdAtTimestamp"]), tz=timezone.utc),
                    )
                )

        if not ticks_to_create:
            print("ℹ️  All ticks already exist for this pool.")
            return

        session.add_all(ticks_to_create)
        print(f"✅ Inserted {len(ticks_to_create)} new tick(s) for pool {pool_slug}.")

def delete_partner_uniswapv3_ticks():
    """Deletes all tick records."""
    print("Deleting all Uniswap v3 ticks...")
    with get_session() as session:
        deleted_count = session.query(PartnerUniswapV3Tick).delete()
        print(f"🗑️  Deleted {deleted_count} tick(s).")