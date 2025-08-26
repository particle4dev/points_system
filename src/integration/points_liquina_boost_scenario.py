# python-training/lessons/points_system/src/integration/points_liquina_boost_scenario.py
# How to run:
# cd src
# PYTHONPATH=. poetry run python3 integration/points_liquina_boost_scenario.py

"""
-------------------------------------------------------------------------------
-- LIQUINA Partner Points Boost Scenario (With Traceability) --
-------------------------------------------------------------------------------
Purpose:
This script simulates a partner campaign where eligible users receive a weekly
boost. Crucially, this version separates the "boost" points into their own
dedicated campaign for clear traceability, so the user can see exactly why
they received bonus points.

Scenario Simulated:
1.  SETUP:
    - TWO campaigns are created:
        1. "Harmonix Main Season 1": For all base points from regular activity.
        2. "LIQUINA Weekly Boost": A dedicated campaign to hold only the bonus
           points awarded from this partner initiative.
    - Historical user activity is pre-populated for the main campaign.

2.  BOOST CALCULATION & DISTRIBUTION:
    - The script calculates the weekly earnings from the "Harmonix Main Season 1"
      campaign history.
    - It then calculates the bonus amount.
    - Instead of adding the bonus to the main campaign, it AWARDS the points to
      the dedicated "LIQUINA Weekly Boost" campaign. This creates a separate
      `PointsUserCampaignPoints` record for the user.

3.  VERIFICATION & DISPLAY:
    - The user's total points (`PointsUserPoint`) are still aggregated correctly
      by the database trigger.
    - The `PointsUserPointHistory` now contains entries from BOTH campaigns.
    - The verification output has been enhanced to show the source campaign for
      each point transaction, proving that the system can tell a user:
      "You earned +1000 from 'Main Season 1' and +200 from 'LIQUINA Boost'".
-------------------------------------------------------------------------------
"""


import os
import sys
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from typing import List
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Session, select

# Add the project root to the python path to allow imports from `src`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.db import get_session
from models import (
    Partner,
    PointsCampaign,
    PointsPointType,
    PointsUserCampaignPoints,
    PointsUserPoint,
    PointsUserPointHistory,
)

# --- Constants for our scenario ---
HARMONIX_POINT_TYPE_SLUG = "harmonix-points"
HARMONIX_POINT_TYPE_NAME = "Harmonix Points"

LIQUINA_PARTNER_SLUG = "liquina"
LIQUINA_PARTNER_NAME = "LIQUINA"

# --- NEW: Constants for the two separate campaigns ---
HARMONIX_MAIN_CAMPAIGN_NAME = "Harmonix Main Season 1"
LIQUINA_BOOST_CAMPAIGN_NAME = "LIQUINA Weekly Boost" # Dedicated campaign for the bonus

CAMPAIGN_START = datetime.now(timezone.utc) - timedelta(seconds=5)
CAMPAIGN_END = CAMPAIGN_START + timedelta(days=42)

USER1_ADDRESS = "0xUser000000000000000000000000000000000001"
USER2_ADDRESS = "0xUser000000000000000000000000000000000002"
USER3_ADDRESS = "0xUser000000000000000000000000000000000003"

BOOST_MULTIPLIER = Decimal("1.2")


# --- Helper functions ---

def get_or_create_generic_point_type(session: Session) -> PointsPointType:
    point_type = session.exec(select(PointsPointType).where(PointsPointType.slug == HARMONIX_POINT_TYPE_SLUG)).first()
    if not point_type:
        point_type = PointsPointType(slug=HARMONIX_POINT_TYPE_SLUG, name=HARMONIX_POINT_TYPE_NAME, partner_slug="harmonix")
        harmonix_partner = session.exec(select(Partner).where(Partner.slug == "harmonix")).first()
        if not harmonix_partner:
            session.add(Partner(slug="harmonix", name="Harmonix Platform"))
        session.add(point_type)
        session.commit()
        session.refresh(point_type)
    return point_type

def get_or_create_campaign(session: Session, name: str, partner_slug: str, start: datetime, end: datetime) -> PointsCampaign:
    campaign = session.exec(select(PointsCampaign).where(PointsCampaign.name == name)).first()
    if not campaign:
        campaign = PointsCampaign(name=name, partner_slug=partner_slug, pool_address="all", start_date=start, end_date=end)
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
    return campaign

def print_summary_and_history(session: Session, wallet_address: str):
    """
    Consolidated print helper for verification.
    ENHANCED: Now fetches campaign names for better history logging.
    """
    statement_summary = select(PointsUserPoint).where(PointsUserPoint.wallet_address == wallet_address)
    summary = session.exec(statement_summary).first()
    balance = summary.points if summary else Decimal("0.0")
    print(f"\n  ✅ Verification for {wallet_address}:")
    print(f"    💰 Total Points Balance: {balance:.2f}")

    # Fetch all campaigns to create a lookup map for display
    all_campaigns = session.exec(select(PointsCampaign)).all()
    campaign_map = {c.id: c.name for c in all_campaigns}

    statement_history = (
        select(PointsUserPointHistory)
        .where(PointsUserPointHistory.wallet_address == wallet_address)
        .order_by(PointsUserPointHistory.created_at)
    )
    records = session.exec(statement_history).all()
    print(f"    📜 Point History (Traceable):")
    if not records:
        print("      - No history found.")
        return
    for record in records:
        campaign_name = campaign_map.get(record.campaign_id, "Unknown Campaign")
        print(f"      - Change: {record.points_change: >+10.2f} | Source: '{campaign_name}'")


# --- Core Boost Logic (Updated) ---

def apply_weekly_liquina_boost(
    session: Session,
    main_campaign_id: UUID,
    boost_campaign_id: UUID,  # NEW: The campaign to award the boost TO
    point_type_slug: str,
    eligible_wallets: List[str],
    week_start_date: datetime,
    week_end_date: datetime,
    boost_multiplier: Decimal,
):
    """
    Calculates a boost based on a main campaign's earnings and awards the
    bonus points to a separate, dedicated boost campaign for traceability.
    """
    print(f"\n--- 🚀 Applying {boost_multiplier}x LIQUINA Boost for Week: {week_start_date.date()} to {week_end_date.date()} ---")
    
    if not eligible_wallets:
        print("  No wallets eligible for boost this week.")
        return

    bonus_multiplier = boost_multiplier - 1

    for wallet in eligible_wallets:
        # Step 1: Query the history of the MAIN campaign to find weekly earnings
        statement = (
            select(sa.func.sum(PointsUserPointHistory.points_change))
            .where(PointsUserPointHistory.wallet_address == wallet)
            .where(PointsUserPointHistory.campaign_id == main_campaign_id) # Querying the main campaign
            .where(PointsUserPointHistory.created_at >= week_start_date)
            .where(PointsUserPointHistory.created_at < week_end_date)
            .where(PointsUserPointHistory.points_change > 0)
        )
        points_earned_this_week = session.exec(statement).first() or Decimal("0.0")

        if points_earned_this_week > 0:
            # Step 2: Calculate the bonus amount
            boost_amount = points_earned_this_week * bonus_multiplier
            
            print(f"  - User {wallet} earned {points_earned_this_week:.2f} base points this week.")
            print(f"    Awarding {bonus_multiplier:.0%} bonus ({boost_amount:.2f} points) to '{LIQUINA_BOOST_CAMPAIGN_NAME}'.")

            # Step 3: Find or create the user's record for the BOOST campaign
            boost_campaign_record = session.exec(
                select(PointsUserCampaignPoints)
                .where(PointsUserCampaignPoints.wallet_address == wallet)
                .where(PointsUserCampaignPoints.campaign_id == boost_campaign_id)
            ).first()
            
            if boost_campaign_record:
                boost_campaign_record.points_earned += boost_amount
            else:
                boost_campaign_record = PointsUserCampaignPoints(
                    wallet_address=wallet,
                    campaign_id=boost_campaign_id, # Linking to the boost campaign
                    point_type_slug=point_type_slug,
                    points_earned=boost_amount
                )
            session.add(boost_campaign_record)
        else:
            print(f"  - User {wallet} is eligible but had no new base earnings this week. No boost applied.")

    session.commit()
    print("--- ✅ Weekly Boost Application Complete ---")


# --- Main Scenario Script ---

def run_liquina_boost_scenario():
    print("--- Starting LIQUINA Weekly Points Boost Scenario ---")

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    with get_session() as session:
        # --- 1. Cleanup for Idempotency ---
        print("\n--- Cleaning up data from previous runs... ---")
        try:
            session.execute(sa.text("ALTER TABLE points_user_campaign_points DISABLE TRIGGER ALL;"))
            session.exec(sa.delete(PointsUserPointHistory))
            session.exec(sa.delete(PointsUserPoint))
            session.exec(sa.delete(PointsUserCampaignPoints))
            session.commit()
            print("  - Cleanup successful.")
        finally:
            session.execute(sa.text("ALTER TABLE points_user_campaign_points ENABLE TRIGGER ALL;"))
            session.commit()

        # --- 2. Initial Data Setup ---
        print("\n--- 0. Initial Data Setup ---")
        point_type = get_or_create_generic_point_type(session)
        # Create BOTH campaigns
        main_campaign = get_or_create_campaign(session, HARMONIX_MAIN_CAMPAIGN_NAME, "harmonix", CAMPAIGN_START, CAMPAIGN_END)
        boost_campaign = get_or_create_campaign(session, LIQUINA_BOOST_CAMPAIGN_NAME, LIQUINA_PARTNER_SLUG, CAMPAIGN_START, CAMPAIGN_END)

        # --- 3. Pre-populate Historical Data for the MAIN campaign ---
        print("\n--- 🔧 Pre-populating historical data for the main campaign ---")
        now = datetime.now(timezone.utc)
        week1_event_time = now - timedelta(days=8)
        week2_event_time = now - timedelta(days=1)
        
        historical_events = [
            (USER1_ADDRESS, Decimal("1000"), week1_event_time),
            (USER2_ADDRESS, Decimal("500"), week1_event_time),
            (USER1_ADDRESS, Decimal("200"), week2_event_time),
            (USER2_ADDRESS, Decimal("1500"), week2_event_time),
            (USER3_ADDRESS, Decimal("3000"), week2_event_time),
        ]
        
        try:
            session.execute(sa.text("ALTER TABLE points_user_campaign_points DISABLE TRIGGER ALL;"))
            
            for user, points, ts in historical_events:
                campaign_record = session.exec(select(PointsUserCampaignPoints).where(PointsUserCampaignPoints.wallet_address == user).where(PointsUserCampaignPoints.campaign_id == main_campaign.id)).first()
                if not campaign_record:
                    campaign_record = PointsUserCampaignPoints(wallet_address=user, campaign_id=main_campaign.id, point_type_slug=point_type.slug, points_earned=points)
                else:
                    campaign_record.points_earned += points
                session.add(campaign_record)
                session.flush()

                session.execute(sa.text("INSERT INTO points_user_point_history (id, source_event_id, wallet_address, campaign_id, point_type_slug, points_change, created_at) VALUES (:id, :src, :w, :cid, :slug, :chg, :ts)"),
                    {"id": uuid4(), "src": campaign_record.id, "w": user, "cid": main_campaign.id, "slug": point_type.slug, "chg": points, "ts": ts})
            
            # Recalculate summaries
            all_users = {e[0] for e in historical_events}
            for user in all_users:
                total_points = session.exec(select(sa.func.sum(PointsUserPointHistory.points_change)).where(PointsUserPointHistory.wallet_address == user)).first() or Decimal("0.0")
                summary = session.exec(select(PointsUserPoint).where(PointsUserPoint.wallet_address == user)).first()
                if not summary:
                    summary = PointsUserPoint(wallet_address=user, point_type_slug=point_type.slug, points=total_points)
                else:
                    summary.points = total_points
                session.add(summary)
            session.commit()
            print("  - Historical data created successfully.")
        finally:
            session.execute(sa.text("ALTER TABLE points_user_campaign_points ENABLE TRIGGER ALL;"))
            session.commit()

        # --- 4. Run The Boost Logic on the Historical Data ---
        week1_start = now - timedelta(days=14)
        week1_end = week1_start + timedelta(days=7)
        week2_start = week1_end
        week2_end = week2_start + timedelta(days=7)

        apply_weekly_liquina_boost(session, main_campaign.id, boost_campaign.id, point_type.slug, [USER1_ADDRESS, USER3_ADDRESS], week1_start, week1_end, BOOST_MULTIPLIER)
        apply_weekly_liquina_boost(session, main_campaign.id, boost_campaign.id, point_type.slug, [USER2_ADDRESS, USER3_ADDRESS], week2_start, week2_end, BOOST_MULTIPLIER)

        # --- 5. Final Verification ---
        print("\n\n--- 📊 Final State Verification ---")
        print_summary_and_history(session, USER1_ADDRESS)
        print_summary_and_history(session, USER2_ADDRESS)
        print_summary_and_history(session, USER3_ADDRESS)

    print("\n--- LIQUINA Scenario Complete ---")

if __name__ == "__main__":
    run_liquina_boost_scenario()