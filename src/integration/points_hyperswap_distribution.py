# python-training/lessons/points_system/src/integration/points_hyperswap_distribution.py
# How to run:
# cd src
# PYTHONPATH=. poetry run python3 integration/points_hyperswap_distribution.py

"""
-------------------------------------------------------------------------------
-- HyperSwap Points Distribution Scenario (Corrected Cumulative Logic) --
-------------------------------------------------------------------------------
Purpose:
This script demonstrates and tests the end-to-end points distribution logic for a
partner protocol (e.g., HyperSwap). It simulates a real-world scenario where a
vault accrues points over time and those points are then distributed to the
vault's users.

Scenario Simulated:
1.  SETUP:
    - A 'HyperSwap' partner, its specific point type ('hyperswap-points'), a
      vault ('HyperSwap USDC Pool Vault'), and a points campaign are created.
    - Two initial users (User1, User2) contribute to the vault, establishing
      their positions ('VaultsUserPosition').

2.  ROUND 1 DISTRIBUTION:
    - The vault earns its first batch of points from HyperSwap. This is recorded
      as a CUMULATIVE total in `PointsPartnerSnapshot`.
    - The distribution logic runs, calculates the new points earned (the total
      in the snapshot since there was no previous snapshot), and distributes
      them to User1 and User2 based on their share ratio.
    - The script verifies that `PointsUserCampaignPoints` is created and that the
      summary (`PointsUserPoint`) and history (`PointsUserPointHistory`) tables
      are correctly updated via database triggers.

3.  ROUND 2 DISTRIBUTION:
    - A new user (User3) contributes to the vault, changing the total shares
      and the contribution ratios.
    - The vault earns MORE points. A new `PointsPartnerSnapshot` is created with
      a NEW CUMULATIVE total.
    - The distribution logic runs again. It correctly calculates the INCREMENT
      (new cumulative total - previous cumulative total) of points to be awarded.
    - This increment is distributed to all three users (User1, User2, User3)
      based on the NEW share ratios.
    - The script verifies that the users' `PointsUserCampaignPoints` balances are
      incremented correctly and that the history table shows this new change.

Key Logic Tested:
- The script correctly handles the CUMULATIVE nature of `PointsPartnerSnapshot`.
- It calculates and distributes only the DELTA (increment) of new points.
- It correctly applies the user share proportions at the time of each distribution.
- It relies on database triggers to maintain the user's total point summary and
  the immutable history ledger.
-------------------------------------------------------------------------------
"""


import os
import sys
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Session, select

# Add the project root to the python path to allow imports from `src`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.db import get_session
from models import (
    Partner,
    PointsCampaign,
    PointsPartnerSnapshot,
    PointsPointType,
    PointsUserCampaignPoints,
    PointsUserPoint,
    PointsUserPointHistory,
    Vault,
    VaultsUserPosition,
    VaultsUserPositionHistory,
    PositionHistoryType,
)

# --- Constants for our scenario ---
HYPERSWAP_PARTNER_SLUG = "hyperswap"
HYPERSWAP_PARTNER_NAME = "HyperSwap"
HYPERSWAP_POINT_TYPE_SLUG = "hyperswap-points"
HYPERSWAP_POINT_TYPE_NAME = "HyperSwap Points"
HYPERSWAP_POINT_TYPE_DESCRIPTION = "Points earned from HyperSwap protocol activity."

TEST_VAULT_NAME = "HyperSwap USDC Pool Vault"
TEST_VAULT_CONTRACT_ADDRESS = "0xVaultA123456789012345678901234567890"

USER1_ADDRESS = "0xUser000000000000000000000000000000000001"
USER2_ADDRESS = "0xUser000000000000000000000000000000000002"
USER3_ADDRESS = "0xUser000000000000000000000000000000000003" # New user for second distribution

USER1_INITIAL_SHARES = 100.0
USER2_INITIAL_SHARES = 50.0
USER3_INITIAL_SHARES = 75.0 # For second distribution

CAMPAIGN_NAME = f"{HYPERSWAP_PARTNER_NAME} {TEST_VAULT_NAME} Campaign"
CAMPAIGN_POOL_ADDRESS = TEST_VAULT_CONTRACT_ADDRESS # Campaign tied to the vault's contract address

# CUMULATIVE points totals for each snapshot
CUMULATIVE_POINTS_ROUND1 = Decimal("1000.00")
CUMULATIVE_POINTS_ROUND2 = Decimal("1500.00") # 500 new points earned

# --- Helper functions for printing status ---

def print_user_campaign_points(session: Session, wallet_address: str, campaign_id: UUID):
    statement = (
        select(PointsUserCampaignPoints)
        .where(PointsUserCampaignPoints.wallet_address == wallet_address)
        .where(PointsUserCampaignPoints.campaign_id == campaign_id)
    )
    record = session.exec(statement).first()
    points = record.points_earned if record else Decimal("0.0")
    print(f"    User {wallet_address} in campaign {campaign_id}: {points:.2f} points.")

def print_summary_for_user_and_point_type(session: Session, wallet_address: str, point_type_slug: str):
    statement = (
        select(PointsUserPoint)
        .where(PointsUserPoint.wallet_address == wallet_address)
        .where(PointsUserPoint.point_type_slug == point_type_slug)
    )
    record = session.exec(statement).first()
    balance = record.points if record else Decimal("0.0")
    print(f"  💰 Summary Balance for {wallet_address} ({point_type_slug}): {balance:.2f}")

def print_history_for_user_and_point_type(session: Session, wallet_address: str, point_type_slug: str):
    statement = (
        select(PointsUserPointHistory)
        .where(PointsUserPointHistory.wallet_address == wallet_address)
        .where(PointsUserPointHistory.point_type_slug == point_type_slug)
        .order_by(PointsUserPointHistory.created_at)
    )
    records = session.exec(statement).all()
    print(f"  📜 History for {wallet_address} ({point_type_slug}):")
    if not records:
        print("    - No history found.")
        return
    for record in records:
        print(f"    - Change: {record.points_change: >10.2f} | Source Event ID: {record.source_event_id} | Timestamp: {record.created_at.strftime('%H:%M:%S')}")


# --- Helper functions for getting/creating models ---

def get_or_create_partner(session: Session, slug: str, name: str) -> Partner:
    partner = session.exec(select(Partner).where(Partner.slug == slug)).first()
    if not partner:
        partner = Partner(slug=slug, name=name)
        session.add(partner)
        session.commit()
        session.refresh(partner)
        print(f"  Created Partner: {name} ({slug})")
    else:
        print(f"  Found existing Partner: {name} ({slug})")
    return partner

def get_or_create_point_type(session: Session, slug: str, name: str, partner_slug: str, description: Optional[str] = None) -> PointsPointType:
    point_type = session.exec(select(PointsPointType).where(PointsPointType.slug == slug)).first()
    if not point_type:
        point_type = PointsPointType(slug=slug, name=name, partner_slug=partner_slug, description=description)
        session.add(point_type)
        session.commit()
        session.refresh(point_type)
        print(f"  Created Point Type: {name} ({slug})")
    else:
        print(f"  Found existing Point Type: {name} ({slug})")
    return point_type

def get_or_create_vault(session: Session, name: str, contract_address: str) -> Vault:
    vault = session.exec(select(Vault).where(Vault.contract_address == contract_address)).first()
    if not vault:
        vault = Vault(name=name, contract_address=contract_address)
        session.add(vault)
        session.commit()
        session.refresh(vault)
        print(f"  Created Vault: {name} ({contract_address})")
    else:
        print(f"  Found existing Vault: {name} ({contract_address})")
    return vault

def get_or_create_user_position(session: Session, user_address: str, vault_id: UUID, initial_shares: float) -> VaultsUserPosition:
    position = session.exec(
        select(VaultsUserPosition)
        .where(VaultsUserPosition.user_address == user_address)
        .where(VaultsUserPosition.vault_id == vault_id)
    ).first()
    if not position:
        position = VaultsUserPosition(
            user_address=user_address,
            vault_id=vault_id,
            total_shares=initial_shares
        )
        session.add(position)
        session.commit()
        session.refresh(position)
        print(f"  Created User Position: {user_address} in Vault {vault_id} with {initial_shares} shares.")
        history_entry = VaultsUserPositionHistory(
            transaction_hash=f"0xinit{uuid4().hex}",
            user_address=user_address,
            vault_id=vault_id,
            timestamp=datetime.now(timezone.utc),
            transaction_type=PositionHistoryType.DEPOSIT,
            shares_amount=initial_shares,
            share_price_at_transaction=1.0,
            asset_amount=initial_shares
        )
        session.add(history_entry)
        session.commit()
    else:
        if position.total_shares != initial_shares:
            print(f"  Updating existing user position for {user_address} in Vault {vault_id} from {position.total_shares} to {initial_shares} shares.")
            position.total_shares = initial_shares
            session.add(position)
            session.commit()
            session.refresh(position)
        else:
            print(f"  Found existing User Position: {user_address} in Vault {vault_id} with {initial_shares} shares.")
    return position

def get_or_create_campaign(session: Session, name: str, partner_slug: str, pool_address: str, start_date: datetime, end_date: Optional[datetime] = None) -> PointsCampaign:
    # In a real system, you might look up by a unique slug or ID. For this script, name is sufficient.
    campaign = session.exec(
        select(PointsCampaign)
        .where(PointsCampaign.name == name)
    ).first()
    if not campaign:
        campaign = PointsCampaign(
            name=name,
            partner_slug=partner_slug,
            pool_address=pool_address,
            start_date=start_date,
            end_date=end_date
        )
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
        print(f"  Created Points Campaign: {name}")
    else:
        print(f"  Found existing Points Campaign: {name}")
    return campaign

def add_partner_snapshot(session: Session, vault_contract_address: str, partner_slug: str, points_total: Decimal, snapshot_at: datetime) -> PointsPartnerSnapshot:
    snapshot = PointsPartnerSnapshot(
        vault_address=vault_contract_address,
        partner_slug=partner_slug,
        points_total=points_total,
        snapshot_at=snapshot_at
    )
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    print(f"  Added Partner Snapshot: Vault {vault_contract_address}, Partner {partner_slug}, CUMULATIVE Points {points_total:.2f} at {snapshot_at.isoformat()}")
    return snapshot

# --- Core Distribution Logic (CORRECTED) ---

def distribute_hyperswap_points(
    session: Session,
    vault_id: UUID,
    vault_contract_address: str,
    partner_slug: str,
    campaign_id: UUID,
    point_type_slug: str,
    snapshot_timestamp: datetime
):
    """
    Distributes the INCREMENT of points from a partner snapshot to users based on their vault contribution.
    """
    print(f"\n--- Starting Points Distribution for Vault {vault_id} at {snapshot_timestamp.isoformat()} ---")

    current_snapshot = session.exec(
        select(PointsPartnerSnapshot)
        .where(PointsPartnerSnapshot.vault_address == vault_contract_address)
        .where(PointsPartnerSnapshot.partner_slug == partner_slug)
        .where(PointsPartnerSnapshot.snapshot_at == snapshot_timestamp)
    ).first()

    if not current_snapshot:
        print(f"  No PointsPartnerSnapshot found for this exact time. Skipping distribution.")
        return

    previous_snapshot = session.exec(
        select(PointsPartnerSnapshot)
        .where(PointsPartnerSnapshot.vault_address == vault_contract_address)
        .where(PointsPartnerSnapshot.partner_slug == partner_slug)
        .where(PointsPartnerSnapshot.snapshot_at < snapshot_timestamp)
        .order_by(PointsPartnerSnapshot.snapshot_at.desc())
    ).first()

    previous_total_points = previous_snapshot.points_total if previous_snapshot else Decimal("0.0")
    
    points_increment_to_distribute = current_snapshot.points_total - previous_total_points

    print(f"  Current cumulative points from snapshot: {current_snapshot.points_total:.2f}")
    print(f"  Previous cumulative points: {previous_total_points:.2f}")
    print(f"  => Points increment to distribute this round: {points_increment_to_distribute:.2f}")

    if points_increment_to_distribute <= 0:
        print("  No new points to distribute (increment <= 0).")
        return

    user_positions = session.exec(select(VaultsUserPosition).where(VaultsUserPosition.vault_id == vault_id)).all()
    if not user_positions:
        print(f"  No user positions found for vault {vault_id}. Skipping.")
        return

    total_shares_in_vault = sum(pos.total_shares for pos in user_positions)
    if total_shares_in_vault == 0:
        print(f"  Total shares in vault is zero. Cannot distribute. Skipping.")
        return
    print(f"  Total shares in vault for ratio calculation: {total_shares_in_vault:.2f}")

    for position in user_positions:
        user_address = position.user_address
        user_shares = Decimal(str(position.total_shares))
        
        contribution_ratio = user_shares / Decimal(str(total_shares_in_vault))
        points_for_user_this_round = points_increment_to_distribute * contribution_ratio

        user_campaign_points = session.exec(
            select(PointsUserCampaignPoints)
            .where(PointsUserCampaignPoints.wallet_address == user_address)
            .where(PointsUserCampaignPoints.campaign_id == campaign_id)
        ).first()

        if user_campaign_points:
            original_points = user_campaign_points.points_earned
            user_campaign_points.points_earned += points_for_user_this_round
            session.add(user_campaign_points)
            print(f"    - User {user_address}: Awarding {points_for_user_this_round: >7.2f} points. Total: {original_points:.2f} -> {user_campaign_points.points_earned:.2f}")
        else:
            user_campaign_points = PointsUserCampaignPoints(
                wallet_address=user_address,
                campaign_id=campaign_id,
                point_type_slug=point_type_slug,
                points_earned=points_for_user_this_round
            )
            session.add(user_campaign_points)
            print(f"    - User {user_address}: Creating record with {points_for_user_this_round: >7.2f} points.")

    session.commit()
    print("--- Points Distribution Complete ---")


# --- Main Scenario Script ---

def run_hyperswap_points_scenario():
    print("--- Starting HyperSwap Points Distribution Scenario (FIXED LOGIC) ---")

    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env')))
        print("Loaded .env file for database connection.")
    except ImportError:
        print("dotenv not installed, skipping .env file load. Ensure DATABASE_URL is set.")
    
    with get_session() as session:
        # --------------------------------------------------------------------
        # -- CLEANUP: Delete data from previous runs for an idempotent test --
        # --------------------------------------------------------------------
        # The order of deletion is important to respect foreign key constraints.
        # We delete the "downstream" data first.
        print("\n--- Cleaning up data from previous script runs... ---")
        
        tables_to_clear = [
            PointsUserPointHistory,
            PointsUserPoint,
            PointsUserCampaignPoints,
            PointsPartnerSnapshot,
            VaultsUserPositionHistory,
            VaultsUserPosition,
        ]
        
        for table in tables_to_clear:
            statement = sa.delete(table)
            results = session.exec(statement)
            print(f"  - Deleted {results.rowcount} rows from {table.__tablename__}")

        session.commit()
        print("--- Cleanup Complete ---")


        # --------------------------------------------------------------------
        # -- SETUP: Create the foundational data for the scenario --
        # --------------------------------------------------------------------
        print("\n--- 0. Initial Data Setup ---")
        get_or_create_partner(session, HYPERSWAP_PARTNER_SLUG, HYPERSWAP_PARTNER_NAME)
        get_or_create_point_type(session, HYPERSWAP_POINT_TYPE_SLUG, HYPERSWAP_POINT_TYPE_NAME, HYPERSWAP_PARTNER_SLUG, HYPERSWAP_POINT_TYPE_DESCRIPTION)
        vault = get_or_create_vault(session, TEST_VAULT_NAME, TEST_VAULT_CONTRACT_ADDRESS)
        current_time = datetime.now(timezone.utc)
        campaign = get_or_create_campaign(session, CAMPAIGN_NAME, HYPERSWAP_PARTNER_SLUG, TEST_VAULT_CONTRACT_ADDRESS, start_date=current_time)
        
        # Create initial user positions
        get_or_create_user_position(session, USER1_ADDRESS, vault.id, USER1_INITIAL_SHARES)
        get_or_create_user_position(session, USER2_ADDRESS, vault.id, USER2_INITIAL_SHARES)
        

        # --------------------------------------------------------------------
        # -- ROUND 1: First distribution --
        # --------------------------------------------------------------------
        print("\n\n--- 1. Simulating Round 1: Receiving and Distributing Points ---")
        snapshot_time_round1 = datetime.now(timezone.utc)
        add_partner_snapshot(session, TEST_VAULT_CONTRACT_ADDRESS, HYPERSWAP_PARTNER_SLUG, CUMULATIVE_POINTS_ROUND1, snapshot_time_round1)
        
        distribute_hyperswap_points(session, vault.id, TEST_VAULT_CONTRACT_ADDRESS, HYPERSWAP_PARTNER_SLUG, campaign.id, HYPERSWAP_POINT_TYPE_SLUG, snapshot_time_round1)

        print("\n--- Verification after Round 1 Distribution ---")
        print("\n  User Summary & History:")
        print_summary_for_user_and_point_type(session, USER1_ADDRESS, HYPERSWAP_POINT_TYPE_SLUG)
        print_history_for_user_and_point_type(session, USER1_ADDRESS, HYPERSWAP_POINT_TYPE_SLUG)
        print("") # Spacer
        print_summary_for_user_and_point_type(session, USER2_ADDRESS, HYPERSWAP_POINT_TYPE_SLUG)
        print_history_for_user_and_point_type(session, USER2_ADDRESS, HYPERSWAP_POINT_TYPE_SLUG)


        # --------------------------------------------------------------------
        # -- ROUND 2: New user joins, second distribution --
        # --------------------------------------------------------------------
        print("\n\n--- 2. Simulating Round 2: New User joins, more points received ---")
        get_or_create_user_position(session, USER3_ADDRESS, vault.id, USER3_INITIAL_SHARES)
        
        snapshot_time_round2 = datetime.now(timezone.utc)
        add_partner_snapshot(session, TEST_VAULT_CONTRACT_ADDRESS, HYPERSWAP_PARTNER_SLUG, CUMULATIVE_POINTS_ROUND2, snapshot_time_round2)

        distribute_hyperswap_points(session, vault.id, TEST_VAULT_CONTRACT_ADDRESS, HYPERSWAP_PARTNER_SLUG, campaign.id, HYPERSWAP_POINT_TYPE_SLUG, snapshot_time_round2)

        print("\n--- Verification after Round 2 Distribution ---")
        print("\n  User Summary & History:")
        print_summary_for_user_and_point_type(session, USER1_ADDRESS, HYPERSWAP_POINT_TYPE_SLUG)
        print_history_for_user_and_point_type(session, USER1_ADDRESS, HYPERSWAP_POINT_TYPE_SLUG)
        print("") # Spacer
        print_summary_for_user_and_point_type(session, USER2_ADDRESS, HYPERSWAP_POINT_TYPE_SLUG)
        print_history_for_user_and_point_type(session, USER2_ADDRESS, HYPERSWAP_POINT_TYPE_SLUG)
        print("") # Spacer
        print_summary_for_user_and_point_type(session, USER3_ADDRESS, HYPERSWAP_POINT_TYPE_SLUG)
        print_history_for_user_and_point_type(session, USER3_ADDRESS, HYPERSWAP_POINT_TYPE_SLUG)


    print("\n--- HyperSwap Points Distribution Scenario Complete ---")

if __name__ == "__main__":
    run_hyperswap_points_scenario()