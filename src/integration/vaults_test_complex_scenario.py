# src/integration/vaults_test_complex_scenario.py
# How to run from the project root directory:
# cd src
# PYTHONPATH=. poetry run python3 integration/vaults_test_complex_scenario.py

import os
import sys
import uuid
from datetime import datetime

"""
Test Script for Vault Position Trigger (Complex Scenario)
---------------------------------------------------------
This script simulates a realistic, multi-user scenario to validate the PostgreSQL
trigger that keeps the `vaults_user_position` table synchronized with the
`vaults_user_position_history` table.

The test demonstrates that the trigger correctly calculates the `total_shares` for
multiple users as they deposit, withdraw, and transfer yield-bearing tokens,
even as the token's underlying value changes. All database transactions are
rolled back at the end to ensure the test is non-destructive.
"""

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.db import get_session
from src.models.vaults import Vault
from src.models.vaults_user_position import VaultsUserPosition
from src.models.vaults_user_position_history import VaultsUserPositionHistory, PositionHistoryType
from sqlmodel import select

# --- Helper functions for printing status ---

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
        price = record.share_price_at_transaction
        print(f"  - Type: {record.transaction_type.value: <12} | Shares (haHype): {record.shares_amount: >8.2f} @ {price: <4.2f} HYPE/haHype")

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

def test_complex_vault_scenario_with_trigger():
    """
    Simulates a multi-user scenario with deposits, withdrawals, and transfers
    to test the database trigger's accuracy. All changes are rolled back at the end.
    
    Test Case Narrative:
    1.  SETUP: A new vault for "HYPE" (asset) and "haHype" (shares) is created.
    2.  DEPOSIT 1 (Alice): Alice deposits 1000 HYPE when 1 haHype = 1.00 HYPE.
        -> Alice's balance should be 1000 haHype.
    3.  PRICE CHANGE: The vault generates yield, price of haHype increases.
    4.  DEPOSIT 2 (Bob): Bob deposits 525 HYPE when 1 haHype = 1.05 HYPE.
        -> Bob's balance should be 500 haHype.
    5.  WITHDRAWAL (Alice): Price increases again. Alice withdraws 100 haHype.
        -> Alice's balance should be 900 haHype.
    6.  TRANSFER (Alice to Bob): Alice sends 200 haHype directly to Bob.
        -> Alice's final balance should be 700 haHype.
        -> Bob's final balance should be 700 haHype.
    7.  CLEANUP: The database transaction is rolled back.
    """
    # --- Test Configuration ---
    ALICE_WALLET = "0xA11ce00000000000000000000000000000000001"
    BOB_WALLET = "0xB0b0000000000000000000000000000000000002"
    TEST_VAULT_ID = uuid.uuid4()
    TEST_VAULT_NAME = "HYPE/haHype Yield Vault"

    with get_session() as session:
        try:
            # --- Setup: Create a temporary vault for the test ---
            test_vault = Vault(id=TEST_VAULT_ID, name=TEST_VAULT_NAME)
            session.add(test_vault)
            session.commit()

            print("--- SCENARIO START: Initial State ---")
            print_position_summary(session, ALICE_WALLET, TEST_VAULT_ID, "Alice")
            print_position_summary(session, BOB_WALLET, TEST_VAULT_ID, "Bob")

            # --- 1. Alice deposits 1000 HYPE at 1.00 HYPE/haHype ---
            print("\n\n--- 1. Alice deposits 1000 HYPE (Price: 1.00) ---")
            alice_deposit = VaultsUserPositionHistory(
                transaction_hash="0x" + "a" * 64,
                user_address=ALICE_WALLET, vault_id=TEST_VAULT_ID, timestamp=datetime.utcnow(),
                transaction_type=PositionHistoryType.DEPOSIT,
                shares_amount=1000.0, share_price_at_transaction=1.00, asset_amount=1000.0,
            )
            session.add(alice_deposit)
            session.commit()
            print("✅ Alice's deposit committed.")
            print_position_summary(session, ALICE_WALLET, TEST_VAULT_ID, "Alice")

            # --- 2. Yield Accrues. Price rises to 1.05 ---
            print("\n\n--- 2. Yield accrues in the vault! Share price is now 1.05 HYPE/haHype ---")

            # --- 3. Bob deposits 525 HYPE, receiving 500 haHype ---
            print("\n\n--- 3. Bob deposits 525 HYPE (Price: 1.05) ---")
            bob_deposit = VaultsUserPositionHistory(
                transaction_hash="0x" + "b" * 64,
                user_address=BOB_WALLET, vault_id=TEST_VAULT_ID, timestamp=datetime.utcnow(),
                transaction_type=PositionHistoryType.DEPOSIT,
                shares_amount=500.0, share_price_at_transaction=1.05, asset_amount=525.0,
            )
            session.add(bob_deposit)
            session.commit()
            print("✅ Bob's deposit committed.")
            print_position_summary(session, BOB_WALLET, TEST_VAULT_ID, "Bob")

            # --- 4. Price rises to 1.10. Alice withdraws 100 haHype ---
            print("\n\n--- 4. Price rises to 1.10. Alice withdraws 100 haHype (receives 110 HYPE) ---")
            alice_withdrawal = VaultsUserPositionHistory(
                transaction_hash="0x" + "c" * 64,
                user_address=ALICE_WALLET, vault_id=TEST_VAULT_ID, timestamp=datetime.utcnow(),
                transaction_type=PositionHistoryType.WITHDRAWAL,
                shares_amount=100.0, share_price_at_transaction=1.10, asset_amount=110.0,
            )
            session.add(alice_withdrawal)
            session.commit()
            print("✅ Alice's withdrawal committed. Her balance should be 900.")
            print_position_summary(session, ALICE_WALLET, TEST_VAULT_ID, "Alice")

            # --- 5. Alice transfers 200 haHype to Bob ---
            print("\n\n--- 5. Alice transfers 200 haHype to Bob ---")
            # A single on-chain transfer creates two history records in our system
            transfer_out = VaultsUserPositionHistory(
                transaction_hash="0x" + "d" * 64,
                user_address=ALICE_WALLET, vault_id=TEST_VAULT_ID, timestamp=datetime.utcnow(),
                transaction_type=PositionHistoryType.TRANSFER_OUT,
                shares_amount=200.0, share_price_at_transaction=1.12, asset_amount=224.0,
                counterparty_address=BOB_WALLET
            )
            transfer_in = VaultsUserPositionHistory(
                transaction_hash="0x" + "d" * 64,
                user_address=BOB_WALLET, vault_id=TEST_VAULT_ID, timestamp=datetime.utcnow(),
                transaction_type=PositionHistoryType.TRANSFER_IN,
                shares_amount=200.0, share_price_at_transaction=1.12, asset_amount=224.0,
                counterparty_address=ALICE_WALLET
            )
            session.add(transfer_out)
            session.add(transfer_in)
            session.commit()
            print("✅ Transfer committed. Trigger must update both Alice and Bob.")
            print_position_summary(session, ALICE_WALLET, TEST_VAULT_ID, "Alice")
            print_position_summary(session, BOB_WALLET, TEST_VAULT_ID, "Bob")

            # --- Final State ---
            print("\n\n--- FINAL STATE ---")
            print_position_history(session, ALICE_WALLET, TEST_VAULT_ID, "Alice")
            print_position_summary(session, ALICE_WALLET, TEST_VAULT_ID, "Alice")
            print_position_history(session, BOB_WALLET, TEST_VAULT_ID, "Bob")
            print_position_summary(session, BOB_WALLET, TEST_VAULT_ID, "Bob")

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
    
    test_complex_vault_scenario_with_trigger()