# python-training/lessons/points_system/src/seed/point_campaigns.py

from datetime import datetime, timedelta, timezone
from core.db import get_session
from src.models import PointsCampaign

# --- 1. Define Seed Data ---
point_campaigns_data = [
    {
        "name": "HyperSwap HaHype/wHype Pool",
        # "type": "Season 1",
        "partner_slug": "hyperswap",
        "start_date": datetime.now(timezone.utc) - timedelta(days=30),
        "end_date": datetime.now(timezone.utc) + timedelta(days=30),
        "tags": ["hyperswap", "liquidity_pool", "season_1", "pool:0xfde5b0626fc80e36885e2fa9cd5ad9d7768d725c"],
        "multiplier": 2.0,
    },
    {
        "name": "HyperSwap Stablecoin Pool",
        # "type": "Launch Event",
        "partner_slug": "hyperswap",
        "start_date": datetime.now(timezone.utc) - timedelta(days=90),
        "end_date": datetime.now(timezone.utc) - timedelta(days=60),
        "tags": ["hyperswap", "stablecoin", "season_1", "launch", "pool:hyperswap_hahype_usdt"],
        "multiplier": 1.5,
    },
    {
        "name": "Pendle Yield Trading Program",
        # "type": "Perpetual",
        "partner_slug": "pendle",
        "start_date": datetime.now(timezone.utc) - timedelta(days=180),
        "end_date": None,
        "tags": ["pendle", "yield", "season_1", "defi", "loyalty"],
        "multiplier": 1.0,
    },
]

# --- 2. Define Create and Delete Functions ---
def create_points_campaigns():
    """Inserts point campaign records into the database."""
    print("Seeding point campaigns...")
    with get_session() as session:
        
        campaigns_to_create = []
        for data in point_campaigns_data:
            # Check if a campaign with the same name and partner slug already exists
            exists = session.query(PointsCampaign).filter_by(
                name=data["name"],
                partner_slug=data["partner_slug"]
            ).first()

            if not exists:
                campaigns_to_create.append(PointsCampaign(**data))

        if not campaigns_to_create:
            print("ℹ️  All point campaigns already exist. No new records inserted.")
            return

        session.add_all(campaigns_to_create)
        print(f"✅ Inserted {len(campaigns_to_create)} new point campaign(s).")

def delete_points_campaigns():
    """Deletes all point campaign records."""
    print("Deleting all point campaigns...")
    with get_session() as session:
        deleted_count = session.query(PointsCampaign).delete()
        print(f"🗑️  Deleted {deleted_count} point campaign(s).")