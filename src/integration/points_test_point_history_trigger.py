# python-training/lessons/points_system/src/integration/points_test_point_history_trigger.py
# How to run:
# cd src
# PYTHONPATH=. poetry run python3 integration/points_test_point_history_trigger.py

import os
import sys
from decimal import Decimal

# Add the project root to the python path to allow imports from `src`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.db import get_session
from models import (
    PointsUserCampaignPoints,
    PointsUserPointHistory,
    PointsUserPoint,
    PointsCampaign,
)
from sqlmodel import select

# --- Helper functions for printing status ---

def print_history_for_user(session, wallet_address: str, point_type: str):
    """Queries and prints all history records for a user and point type."""
    statement = (
        select(PointsUserPointHistory)
        .where(PointsUserPointHistory.wallet_address == wallet_address)
        .where(PointsUserPointHistory.point_type_slug == point_type)
        .order_by(PointsUserPointHistory.created_at)
    )
    records = session.exec(statement).all()
    print(f"\n📜 History for {wallet_address} ({point_type}):")
    if not records:
        print("  - No history found.")
        return
    for record in records:
        print(f"  - Change: {record.points_change: >10.2f} | Timestamp: {record.created_at.strftime('%H:%M:%S')}")

def print_summary_for_user(session, wallet_address: str, point_type: str):
    """Queries and prints the summary balance for a user and point type."""
    statement = (
        select(PointsUserPoint)
        .where(PointsUserPoint.wallet_address == wallet_address)
        .where(PointsUserPoint.point_type_slug == point_type)
    )
    record = session.exec(statement).first()
    balance = record.points if record else Decimal("0.0")
    print(f"\n💰 Summary Balance for {wallet_address} ({point_type}): {balance:.2f}")

# --- The Main Test Function ---

def test_point_history_and_summary_triggers():
    """
    Performs a sequence of operations to test the database triggers that maintain
    the point history and summary tables. Rolls back changes at the end.
    """
    # --- Test Configuration ---
    TEST_WALLET = "0xB0b0000000000000000000000000000000000002" # Bob's wallet
    TEST_CAMPAIGN_NAME = "HyperSwap HaHype/wHype Pool"
    TEST_POINT_TYPE = "hyperswap-points"
    POINTS_TO_ADD = Decimal("100.00")

    with get_session() as session:
        try:
            print("--- Trigger Test Initial State ---")
            
            # Find the campaign and user record we're going to manipulate
            campaign = session.exec(select(PointsCampaign).where(PointsCampaign.name == TEST_CAMPAIGN_NAME)).one()
            user_campaign_points = session.exec(
                select(PointsUserCampaignPoints)
                .where(PointsUserCampaignPoints.wallet_address == TEST_WALLET)
                .where(PointsUserCampaignPoints.campaign_id == campaign.id)
            ).one()
            
            original_points = user_campaign_points.points_earned
            
            print_history_for_user(session, TEST_WALLET, TEST_POINT_TYPE)
            print_summary_for_user(session, TEST_WALLET, TEST_POINT_TYPE)

            # --- 1. UPDATE Test: Add points to an existing record ---
            print(f"\n\n--- 1. Testing UPDATE: Adding {POINTS_TO_ADD} points ---")
            user_campaign_points.points_earned += POINTS_TO_ADD
            session.add(user_campaign_points)
            session.commit()
            session.refresh(user_campaign_points) # Refresh to get latest db state
            
            print("✅ UPDATE committed.")
            print_history_for_user(session, TEST_WALLET, TEST_POINT_TYPE)
            print_summary_for_user(session, TEST_WALLET, TEST_POINT_TYPE)

            # --- 2. DELETE Test: Remove the campaign points record ---
            print(f"\n\n--- 2. Testing DELETE: Removing the record ---")
            points_at_deletion = user_campaign_points.points_earned
            session.delete(user_campaign_points)
            session.commit()

            print(f"✅ DELETE committed. A change of {-points_at_deletion} should be logged.")
            print_history_for_user(session, TEST_WALLET, TEST_POINT_TYPE)
            print_summary_for_user(session, TEST_WALLET, TEST_POINT_TYPE)

            # --- 3. INSERT Test: Re-add the record ---
            print(f"\n\n--- 3. Testing INSERT: Re-creating the record with original points ---")
            new_record = PointsUserCampaignPoints(
                wallet_address=TEST_WALLET,
                campaign_id=campaign.id,
                point_type_slug=TEST_POINT_TYPE,
                points_earned=original_points
            )
            session.add(new_record)
            session.commit()

            print(f"✅ INSERT committed. A change of {original_points} should be logged.")
            print_history_for_user(session, TEST_WALLET, TEST_POINT_TYPE)
            print_summary_for_user(session, TEST_WALLET, TEST_POINT_TYPE)


        finally:
            # --- Cleanup: Roll back all changes ---
            print("\n\n--- Test Complete: Rolling back all changes to restore initial state. ---")
            session.rollback()


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file for database connection.")
    except ImportError:
        print("dotenv not installed, skipping .env file load. Ensure DATABASE_URL is set.")
    
    test_point_history_and_summary_triggers()