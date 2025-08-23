# python-training/lessons/points_system/src/seed/points_point_types.py

from core.db import get_session
from src.models import PointsPointType

# --- 1. Define Seed Data ---
point_types_data = [
    {
        "slug": "hyperswap-points",
        "name": "HyperSwap Points",
        "description": "Points earned by providing liquidity and participating in HyperSwap pools.",
        "partner_slug": "hyperswap",
    },
    {
        "slug": "pendle-points",
        "name": "Pendle Points",
        "description": "Points earned through yield trading on Pendle Finance.",
        "partner_slug": "pendle",
    },
    {
        "slug": "harmonix-points",
        "name": "Harmonix Points",
        "description": "Points earned by optimizing yield through Harmonix Finance.",
        "partner_slug": "harmonix",
    },
]

# --- 2. Define Create and Delete Functions ---
def create_points_point_types():
    """Inserts point type definitions into the database."""
    print("Seeding points point types...")
    with get_session() as session:
        
        types_to_create = []
        for data in point_types_data:
            exists = session.query(PointsPointType).filter_by(slug=data["slug"]).first()
            if not exists:
                types_to_create.append(PointsPointType(**data))

        if not types_to_create:
            print("ℹ️  All points point types already exist.")
            return

        session.add_all(types_to_create)
        print(f"✅ Inserted {len(types_to_create)} new points point type(s).")

def delete_points_point_types():
    """Deletes all point type records."""
    print("Deleting all points point types...")
    with get_session() as session:
        deleted_count = session.query(PointsPointType).delete()
        print(f"🗑️  Deleted {deleted_count} points point type(s).")
