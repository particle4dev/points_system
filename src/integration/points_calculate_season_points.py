# python-training/lessons/points_system/src/integration/points_calculate_season_points.py
# How to run:
# cd src
# PYTHONPATH=. poetry run python3 integration/points_calculate_season_points.py

"""
Calculate Total Points Distributed for a Season (Self-Contained)
-----------------------------------------------------------------
This script runs a complete, self-contained test to answer the question:
"How many points have been distributed for a specific season?"

It operates within a single database transaction and performs three steps:
1.  SETUP: It inserts temporary point types, campaigns, and user point data.
2.  EXECUTE: It runs a query to calculate the total points for the target season.
3.  CLEANUP: It rolls back the transaction, deleting all temporary data.
"""

import os
import sys
import uuid
from decimal import Decimal
from datetime import datetime

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.db import get_session
from models import PointsCampaign, PointsUserCampaignPoints, PointsPointType
from sqlmodel import select, SQLModel, Field
from sqlalchemy import func


def calculate_points_for_season(session, season_tag: str):
    """
    Calculates and prints the total points distributed for a given season tag
    using the data available in the current session.
    """
    print(f"\n--- Calculating total points for campaigns tagged with: '{season_tag}' ---\n")
    
    # 1. Find all campaign IDs that are part of the specified season
    campaigns_in_season = session.exec(
        select(PointsCampaign).where(PointsCampaign.tags.any(season_tag))
    ).all()

    if not campaigns_in_season:
        print(f"ℹ️ No campaigns found for season '{season_tag}'.")
        return

    campaign_ids = [c.id for c in campaigns_in_season]
    campaign_map = {c.id: c.name for c in campaigns_in_season}
    print(f"Found {len(campaign_ids)} campaign(s) in this season.")

    # 2. Calculate the total points distributed across all these campaigns
    total_points_statement = (
        select(func.sum(PointsUserCampaignPoints.points_earned))
        .where(PointsUserCampaignPoints.campaign_id.in_(campaign_ids))
    )
    scalar_result = session.exec(total_points_statement).first()
    total_points = scalar_result if scalar_result is not None else Decimal("0")

    # 3. Get a detailed breakdown of points per campaign
    breakdown_results = session.exec(
        select(
            PointsUserCampaignPoints.campaign_id,
            func.sum(PointsUserCampaignPoints.points_earned).label("total_points")
        )
        .where(PointsUserCampaignPoints.campaign_id.in_(campaign_ids))
        .group_by(PointsUserCampaignPoints.campaign_id)
    ).all()

   # 4. Display the summary results
    print("\n==============================================")
    print(f"      Total Points Distributed in {season_tag}      ")
    print("==============================================")
    print(f"\n      {total_points:,.2f} points\n")
    
    print("--- Breakdown by Campaign (Summary) ---")
    if not breakdown_results:
        print("  No points have been distributed for any campaign in this season yet.")
    else:
        for result in breakdown_results:
            campaign_name = campaign_map.get(result.campaign_id, "Unknown Campaign")
            print(f"  - {campaign_name:<40}: {result.total_points: >15,.2f} points")

    # --- NEW: Query and display the detailed breakdown by user ---
    print("\n--- Detailed Points by User ---")
    
    detailed_points_statement = (
        select(PointsUserCampaignPoints)
        .where(PointsUserCampaignPoints.campaign_id.in_(campaign_ids))
        .order_by(PointsUserCampaignPoints.campaign_id, PointsUserCampaignPoints.wallet_address)
    )
    user_point_records = session.exec(detailed_points_statement).all()

    if not user_point_records:
        print("  No individual user point records found for this season.")
        return

    current_campaign_id = None
    for record in user_point_records:
        # Print a header for each new campaign
        if record.campaign_id != current_campaign_id:
            current_campaign_id = record.campaign_id
            campaign_name = campaign_map.get(current_campaign_id, "Unknown Campaign")
            print(f"\n  Campaign: {campaign_name}")
        
        # Print the individual user record
        print(f"    - User: {record.wallet_address:<12} | Points Earned: {record.points_earned: >15,.2f}")

def run_self_contained_calculation():
    """
    The main function that sets up data, runs the calculation, and cleans up.
    """
    # --- CONFIGURATION ---
    TARGET_SEASON_TAG = "season_1"
    
    with get_session() as session:
        try:
            # --- 1. SETUP: Create temporary data for the test ---
            print("--- 1. Seeding temporary test data... ---")

            # Get or create Point Types
            point_types_to_ensure = [
                {"slug": "h-pts", "name": "Hyperswap Points", "partner_slug": "hyperswap"},
                {"slug": "p-pts", "name": "Pendle Points", "partner_slug": "pendle"},
                {"slug": "x-pts", "name": "PartnerX Points", "partner_slug": "partner_x"},
            ]
            for pt_data in point_types_to_ensure:
                existing_pt = session.exec(select(PointsPointType).where(PointsPointType.slug == pt_data["slug"])).first()
                if not existing_pt:
                    session.add(PointsPointType(**pt_data))
            
            # Create two "Season 1" campaigns and one "Season 2" campaign
            print("  - Creating temporary campaigns...")
            campaigns_data = [
                PointsCampaign(id=uuid.uuid4(), name="Hyperswap Main Pool (S1)", partner_slug="hyperswap", pool_address="0x123", tags=["season_1", "core"]),
                PointsCampaign(id=uuid.uuid4(), name="Pendle Yield Trading (S1)", partner_slug="pendle", pool_address="0x456", tags=["season_1", "yield"]),
                PointsCampaign(id=uuid.uuid4(), name="Future Airdrop Event (S2)", partner_slug="partner_x", pool_address="0x789", tags=["season_2", "airdrop"]),
            ]
            session.add_all(campaigns_data)
            
            # Map names to IDs for easy linking
            s1_hyperswap_id = campaigns_data[0].id
            s1_pendle_id = campaigns_data[1].id
            s2_airdrop_id = campaigns_data[2].id

            # Distribute points to users for these campaigns
            print("  - Creating temporary user point records...")
            user_points_data = [
                # Points for Season 1 campaigns (these should be counted)
                PointsUserCampaignPoints(campaign_id=s1_hyperswap_id, partner_slug="hyperswap", point_type_slug="h-pts", wallet_address="0xAlice", points_earned=Decimal("1500.50")),
                PointsUserCampaignPoints(campaign_id=s1_hyperswap_id, partner_slug="hyperswap", point_type_slug="h-pts", wallet_address="0xBob", points_earned=Decimal("2500.00")),
                PointsUserCampaignPoints(campaign_id=s1_pendle_id, partner_slug="pendle", point_type_slug="p-pts", wallet_address="0xAlice", points_earned=Decimal("5000.75")),
                
                # Points for a Season 2 campaign (this should be IGNORED by the query)
                PointsUserCampaignPoints(campaign_id=s2_airdrop_id, partner_slug="partner_x", point_type_slug="x-pts", wallet_address="0xCharlie", points_earned=Decimal("10000.00")),
            ]
            session.add_all(user_points_data)
            session.commit() # Commit to make data available for querying
            print("✅ Temporary data created successfully.")

            # --- 2. EXECUTE: Run the calculation on the temporary data ---
            calculate_points_for_season(session=session, season_tag=TARGET_SEASON_TAG)

        finally:
            # --- 3. CLEANUP: Roll back the transaction to delete all temporary data ---
            print("\n--- 3. Rolling back transaction to clean up test data... ---")
            session.rollback()
            print("✅ Cleanup complete. Database restored to its original state.")


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file for database connection.")
    except ImportError:
        print("dotenv not installed, skipping .env file load. Ensure DATABASE_URL is set.")
    
    run_self_contained_calculation()