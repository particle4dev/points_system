# python-training/lessons/points_system/src/seed/partner_pools.py

from core.db import get_session
from src.models import PartnerPool

# --- 1. Define Seed Data ---
partner_pools_data = [
    {
        "name": "Pendle Finance",
        "slug": "pendle_hahype",
        "partner_slug": "pendle",
        "tags": ["pendle", "hahype"]
    },
    {
        "name": "HyperSwap HaHype Hype Pool",
        "slug": "0xfde5b0626fc80e36885e2fa9cd5ad9d7768d725c",
        "partner_slug": "hyperswap",
        "tags": ["hyperswap", "hype", "hahype"]
    },
    {
        "name": "HyperSwap HaHype USDT Pool",
        "slug": "hyperswap_hahype_usdt",
        "partner_slug": "hyperswap",
        "tags": ["hyperswap", "usdt", "hahype"]
    },
]

# --- 2. Define Create and Delete Functions ---
def create_partner_pools():
    """Inserts partner pool records into the database."""
    print("Seeding partner pools...")
    with get_session() as session:
        
        partners_to_create = []
        for data in partner_pools_data:
            # Check if a pool already exists by its unique slug
            exists = session.query(PartnerPool).filter_by(
                slug=data["slug"]
            ).first()

            if not exists:
                # The data dictionary matches the model, so it can be passed directly.
                partners_to_create.append(PartnerPool(**data))

        if not partners_to_create:
            print("ℹ️  All partner pools already exist. No new records inserted.")
            return

        session.add_all(partners_to_create)
        print(f"✅ Inserted {len(partners_to_create)} new partner pool(s).")

def delete_partner_pools():
    """Deletes all partner pool records."""
    print("Deleting all partner pool records...")
    with get_session() as session:
        deleted_count = session.query(PartnerPool).delete()
        print(f"🗑️  Deleted {deleted_count} partner pool(s).")