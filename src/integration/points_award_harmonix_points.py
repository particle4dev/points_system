# python-training/lessons/points_system/src/integration/points_award_harmonix_points.py
# How to run:
# cd src
# PYTHONPATH=. poetry run python3 integration/points_award_harmonix_points.py

"""
Usecase Description:
This script simulates a common business scenario where a partner (Harmonix)
organizes a points campaign. After the event concludes, an administrative
process runs to award points to a participating user.

The script demonstrates the entire flow:
1. It programmatically creates a new, temporary campaign for Harmonix.
2. It then grants points to a new user for their participation in that campaign.
3. Finally, it queries the database to verify that the automated triggers have
   correctly:
   - Logged the transaction in the `PointsUserPointHistory` table.
   - Updated the user's total balance in the `PointsUserPoint` summary table.

The entire operation is wrapped in a transaction that is rolled back at the end,
ensuring that running this test script does not permanently alter the database.
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# Add the project root to the python path to allow imports from `src`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.db import get_session
from models import (
    PointsCampaign,
    PointsUserCampaignPoints,
    PointsUserPoint,
    PointsUserPointHistory,
)
from sqlmodel import select

def run_harmonix_award_scenario():
    """
    Simulates creating a Harmonix campaign, awarding points to a new user,
    and verifying the results in the database.
    """
    # --- 1. Define the Scenario ---
    PARTNER_SLUG = "harmonix"
    POINT_TYPE_SLUG = "harmonix-points"
    CAMPAIGN_NAME = "Harmonix Yield Rally"
    USER_WALLET = "0xABCDE1234567890ABCDE1234567890ABCDE12345"
    POINTS_AWARDED = Decimal("500.00")
    
    print("🚀 Starting Harmonix Points Award Scenario...")
    
    with get_session() as session:
        try:
            # --- 2. Create a New Campaign ---
            print(f"\n--- Step 1: Creating campaign '{CAMPAIGN_NAME}' ---")
            
            new_campaign = PointsCampaign(
                name=CAMPAIGN_NAME,
                partner_slug=PARTNER_SLUG,
                start_date=datetime.now(timezone.utc) - timedelta(days=1),
                end_date=datetime.now(timezone.utc) + timedelta(days=30),
                multiplier=1.0,
                tags=["yield", "rally", "special-event"],
            )
            session.add(new_campaign)
            session.commit()
            session.refresh(new_campaign) # Load the generated ID and defaults
            
            print(f"✅ Campaign created with ID: {new_campaign.id}")
            
            # --- 3. Award Points to the User ---
            print(f"\n--- Step 2: Awarding {POINTS_AWARDED} {POINT_TYPE_SLUG} to user {USER_WALLET} ---")
            
            new_point_award = PointsUserCampaignPoints(
                wallet_address=USER_WALLET,
                campaign_id=new_campaign.id,
                point_type_slug=POINT_TYPE_SLUG,
                points_earned=POINTS_AWARDED
            )
            session.add(new_point_award)
            session.commit()
            
            print("✅ Points awarded successfully. The database triggers should have fired.")

            # --- 4. Verify the Results ---
            print("\n--- Step 3: Verifying the results from all tables ---")
            
            # a) Verify the history log was created
            history_statement = (
                select(PointsUserPointHistory)
                .where(PointsUserPointHistory.wallet_address == USER_WALLET)
                .where(PointsUserPointHistory.campaign_id == new_campaign.id)
            )
            history_record = session.exec(history_statement).one_or_none()
            
            print("\n📜 Verifying Point History (Ledger):")
            if history_record and history_record.points_change == POINTS_AWARDED:
                print(f"  ✅ SUCCESS: Found history record with a change of +{history_record.points_change:.2f}")
            else:
                print("  ❌ FAILURE: Did not find a correct history record.")

            # b) Verify the summary balance was created/updated
            summary_statement = (
                select(PointsUserPoint)
                .where(PointsUserPoint.wallet_address == USER_WALLET)
                .where(PointsUserPoint.point_type_slug == POINT_TYPE_SLUG)
            )
            summary_record = session.exec(summary_statement).one_or_none()
            
            print("\n💰 Verifying Point Summary (Balance):")
            if summary_record and summary_record.points == POINTS_AWARDED:
                print(f"  ✅ SUCCESS: User's total balance is now {summary_record.points:.2f}")
            else:
                print("  ❌ FAILURE: User's summary balance is incorrect.")

        finally:
            # --- 5. Cleanup ---
            print("\n\n--- Scenario Complete: Rolling back all changes. ---")
            session.rollback()
            print("✅ Database state has been restored.")


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file for database connection.")
    except ImportError:
        print("dotenv not installed, skipping .env file load. Ensure DATABASE_URL is set.")
    
    run_harmonix_award_scenario()