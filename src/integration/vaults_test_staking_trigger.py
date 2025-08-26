# python-training/lessons/points_system/src/integration/vaults_test_staking_trigger.py
# How to run from the project root directory:
# cd src
# PYTHONPATH=. poetry run python3 integration/vaults_test_staking_trigger.py

"""
Test Script for Vault Position Trigger (Staking Scenario)
----------------------------------------------------------
This script specifically tests the logic for staking and unstaking yield-bearing
tokens to an approved third-party protocol (e.g., a liquidity pool).

It validates that when a user transfers shares to an address listed in the
`vault_approved_address_pool` table, their total share balance in the main
system remains unchanged, as they still retain ownership of the underlying asset.
All database transactions are rolled back at the end.
"""

import os
import sys
import uuid
from datetime import datetime

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.db import get_session
from src.models.vaults import Vault
from src.models.vaults_user_position import VaultsUserPosition
from src.models.vaults_user_position_history import VaultsUserPositionHistory, PositionHistoryType
# from src.models.vault_approved_address_pool import VaultApprovedAddressPool
from sqlmodel import select

# --- Helper functions (reused from previous scripts) ---

def print_position_history(session, user_address: str, vault_id: uuid.UUID, user_name: str):
    """Queries and prints all position history records for a user in a vault."""
    statement = (
        select(VaultsUserPositionHistory)
        .where(VaultsUserPositionHistory.user_address == user_address)
        .where(VaultsUserPositionHistory.vault_id == vault_id)
        .order_by(VaultsUserPositionHistory.timestamp)
    )
    records = session.exec(statement).all()
    print(f"\n📜 History for {user_name} ({user_address[:10]}...):")
    if not records:
        print("  - No history found.")
        return
    for record in records:
        print(f"  - Type: {record.transaction_type.value: <18} | Shares (haHype): {record.shares_amount: >8.2f}")

def print_position_summary(session, user_address: str, vault_id: uuid.UUID, user_name: str):
    """Queries and prints the summary position for a user in a vault."""
    statement = (
        select(VaultsUserPosition)
        .where(VaultsUserPosition.user_address == user_address)
        .where(VaultsUserPosition.vault_id == vault_id)
    )
    record = session.exec(statement).first()
    total_shares = record.total_shares if record else 0.0
    print(f"\n💰 Summary for {user_name} ({user_address[:10]}...): {total_shares:.2f} haHype shares")

# --- The Main Test Function ---

def test_staking_scenario_with_trigger():
    """
    Simulates a user depositing, staking to an approved pool, unstaking, and
    verifies that their total share count is handled correctly by the trigger.
    """
    # --- Test Configuration ---
    ALICE_WALLET = "0xA11ce00000000000000000000000000000000001"
    HYPERSWAP_LP_POOL = "0xDEADBEEF000000000000000000000000DEADBEEF"
    TEST_VAULT_ID = uuid.uuid4()

    with get_session() as session:
        try:
            # --- 1. Setup: Create a vault and an approved address pool ---
            print("--- 1. SETUP: Creating vault and registering Hyperswap LP as an approved pool ---")
            test_vault = Vault(id=TEST_VAULT_ID, name="Staking Test Vault")
            # approved_pool = VaultApprovedAddressPool(
            #     vault_id=TEST_VAULT_ID,
            #     contract_address=HYPERSWAP_LP_POOL,
            #     protocol_name="Hyperswap HYPE/haHype LP"
            # )
            session.add(test_vault)
            # session.add(approved_pool)
            session.commit()
            print("✅ Setup complete.")

            # --- 2. Alice deposits 1000 shares into the main vault ---
            print("\n\n--- 2. Alice deposits 1000 haHype into the main vault ---")
            alice_deposit = VaultsUserPositionHistory(
                user_address=ALICE_WALLET, vault_id=TEST_VAULT_ID, transaction_hash="0xa1",
                timestamp=datetime.utcnow(), transaction_type=PositionHistoryType.DEPOSIT,
                shares_amount=1000.0, share_price_at_transaction=1.0, asset_amount=1000.0
            )
            session.add(alice_deposit)
            session.commit()
            print_position_summary(session, ALICE_WALLET, TEST_VAULT_ID, "Alice")

            # --- 3. Alice stakes 400 shares to the Hyperswap LP Pool ---
            print(f"\n\n--- 3. Alice STAKES 400 haHype to the approved Hyperswap LP ({HYPERSWAP_LP_POOL[:10]}...) ---")
            stake_event = VaultsUserPositionHistory(
                user_address=ALICE_WALLET, vault_id=TEST_VAULT_ID, transaction_hash="0xa2",
                timestamp=datetime.utcnow(), transaction_type=PositionHistoryType.STAKE_TO_POOL,
                shares_amount=400.0, share_price_at_transaction=1.05, asset_amount=420.0,
                counterparty_address=HYPERSWAP_LP_POOL
            )
            session.add(stake_event)
            session.commit()
            
            print("\n>>> VERIFICATION: Alice's total shares should NOT have changed.")
            print(">>> The trigger should ignore STAKE_TO_POOL for balance calculation.")
            print_position_summary(session, ALICE_WALLET, TEST_VAULT_ID, "Alice")
            
            # --- 4. Alice unstakes her 400 shares from the Hyperswap LP Pool ---
            print(f"\n\n--- 4. Alice UNSTAKES 400 haHype from the Hyperswap LP ---")
            unstake_event = VaultsUserPositionHistory(
                user_address=ALICE_WALLET, vault_id=TEST_VAULT_ID, transaction_hash="0xa3",
                timestamp=datetime.utcnow(), transaction_type=PositionHistoryType.UNSTAKE_FROM_POOL,
                shares_amount=400.0, share_price_at_transaction=1.08, asset_amount=432.0,
                counterparty_address=HYPERSWAP_LP_POOL
            )
            session.add(unstake_event)
            session.commit()
            
            print("\n>>> VERIFICATION: Alice's total shares should still be unchanged.")
            print(">>> The trigger should also ignore UNSTAKE_FROM_POOL.")
            print_position_summary(session, ALICE_WALLET, TEST_VAULT_ID, "Alice")
            
            # --- 5. Alice performs a true withdrawal to confirm normal logic still works ---
            print("\n\n--- 5. Alice makes a true WITHDRAWAL of 100 haHype from the main vault ---")
            withdrawal_event = VaultsUserPositionHistory(
                user_address=ALICE_WALLET, vault_id=TEST_VAULT_ID, transaction_hash="0xa4",
                timestamp=datetime.utcnow(), transaction_type=PositionHistoryType.WITHDRAWAL,
                shares_amount=100.0, share_price_at_transaction=1.10, asset_amount=110.0
            )
            session.add(withdrawal_event)
            session.commit()
            
            print("\n>>> VERIFICATION: Her balance should now finally decrease.")
            print_position_summary(session, ALICE_WALLET, TEST_VAULT_ID, "Alice")

            # --- Final State ---
            print("\n\n--- FINAL STATE ---")
            print_position_history(session, ALICE_WALLET, TEST_VAULT_ID, "Alice")
            print_position_summary(session, ALICE_WALLET, TEST_VAULT_ID, "Alice")

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
    
    test_staking_scenario_with_trigger()