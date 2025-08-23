# python-training/lessons/points_system/src/seed/points_user_campaign_points.py

from decimal import Decimal
from core.db import get_session
from src.models import PointsUserCampaignPoints, PointsCampaign

# --- 1. Define Seed Data ---
# This data describes which user earned how many points from which campaign.
# It's based on the user and campaign data provided.
user_campaign_points_data = [
    {
        # Alice participated in the HaHype/wHype campaign.
        "wallet_address": "0xA11ce00000000000000000000000000000000001",
        "campaign_name": "HyperSwap HaHype/wHype Pool",
        "point_type_slug": "hyperswap-points",
        "points_earned": Decimal("1500.00"),
    },
    {
        # Bob is also participating in the HaHype/wHype campaign and has earned more points.
        "wallet_address": "0xB0b0000000000000000000000000000000000002",
        "campaign_name": "HyperSwap HaHype/wHype Pool",
        "point_type_slug": "hyperswap-points",
        "points_earned": Decimal("3500.50"),
    },
    {
        # Bob is also participating in the ongoing Pendle program.
        "wallet_address": "0xB0b0000000000000000000000000000000000002",
        "campaign_name": "Pendle Yield Trading Program",
        "point_type_slug": "pendle-points",
        "points_earned": Decimal("850.25"),
    },
]

# --- 2. Define Create and Delete Functions ---
def create_user_campaign_points():
    """Inserts user campaign point records into the database."""
    print("Seeding user campaign points...")
    with get_session() as session:
        
        records_to_create = []
        for data in user_campaign_points_data:
            # Dynamically find the campaign_id from the campaign name.
            campaign = session.query(PointsCampaign).filter_by(name=data["campaign_name"]).first()
            if not campaign:
                print(f"⚠️  Could not find campaign '{data['campaign_name']}'. Skipping this record.")
                continue

            # Check if a record for this wallet and campaign already exists.
            exists = session.query(PointsUserCampaignPoints).filter_by(
                wallet_address=data["wallet_address"], 
                campaign_id=campaign.id
            ).first()

            if not exists:
                record = PointsUserCampaignPoints(
                    wallet_address=data["wallet_address"],
                    campaign_id=campaign.id,
                    point_type_slug=data["point_type_slug"],
                    points_earned=data["points_earned"]
                )
                records_to_create.append(record)

        if not records_to_create:
            print("ℹ️  All user campaign point records already exist.")
            return

        session.add_all(records_to_create)
        print(f"✅ Inserted {len(records_to_create)} new user campaign point record(s).")

def delete_user_campaign_points():
    """Deletes all user campaign point records."""
    print("Deleting all user campaign points...")
    with get_session() as session:
        deleted_count = session.query(PointsUserCampaignPoints).delete()
        print(f"🗑️  Deleted {deleted_count} user campaign point record(s).")