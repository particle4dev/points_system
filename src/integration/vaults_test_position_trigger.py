# src/integration/vaults_test_position_trigger.py
# How to run from the project root directory:
# cd src
# PYTHONPATH=. poetry run python3 integration/vaults_test_position_trigger.py

import os
import sys
import uuid
from datetime import datetime

# Add the project root to the python path to allow imports from `src`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.db import get_session
from src.models.vaults import Vault
from src.models.vaults_user_position import VaultsUserPosition
from src.models.vaults_user_position_history import VaultsUserPositionHistory, PositionHistoryType
from sqlmodel import select

# --- Helper functions for printing status ---

def print_position_history(session, user_address: str, vault_id: uuid.UUID):
    """Queries and prints all position history records for a user in a vault."""
    statement = (
        select(VaultsUserPositionHistory)
        .where(VaultsUserPositionHistory.user_address == user_address)
        .where(VaultsUserPositionHistory.vault_id == vault_id)
        .order_by(VaultsUserPositionHistory.timestamp)
    )
    records = session.exec(statement).all()
    print(f"\n📜 History for {user_address}:")
    if not records:
        print("  - No history found.")
        return
    for record in records:
        print(f"  - Type: {record.transaction_type.value: <12} | Shares: {record.shares_amount: >8.2f} @ ${record.share_price_at_transaction: <6.2f} | Hash: {record.transaction_hash[:10]}...")

def print_position_summary(session, user_address: str, vault_id: uuid.UUID):
    """Queries and prints the summary position for a user in a vault."""
    statement = (
        select(VaultsUserPosition)
        .where(VaultsUserPosition.user_address == user_address)
        .where(VaultsUserPosition.vault_id == vault_id)
    )
    record = session.exec(statement).first()
    total_shares = record.total_shares if record else 0.0
    print(f"\n💰 Summary Position for {user_address}: {total_shares:.2f} shares")

# --- The Main Test Function ---

def test_position_history_and_summary_trigger():
    """
    Performs a sequence of INSERTS into the history table to test the database
    trigger that maintains the summary position table. Rolls back all changes at the end.
    """
    # --- Test Configuration ---
    TEST_SENDER_WALLET = "0xA0A0000000000000000000000000000000000001"
    TEST_RECEIVER_WALLET = "0xB0B0000000000000000000000000000000000002"
    TEST_VAULT_ID = uuid.uuid4()
    TEST_VAULT_NAME = "Demo Delta Neutral Vault"

    with get_session() as session:
        try:
            # --- Setup: Create a temporary vault for the test ---
            test_vault = Vault(id=TEST_VAULT_ID, name=TEST_VAULT_NAME)
            session.add(test_vault)
            # We must commit the vault so the foreign key constraint is satisfied for the history table
            session.commit()

            print("--- Trigger Test Initial State ---")
            print_position_history(session, TEST_SENDER_WALLET, TEST_VAULT_ID)
            print_position_summary(session, TEST_SENDER_WALLET, TEST_VAULT_ID)

            # --- 1. DEPOSIT Test: User deposits 100 shares ---
            print("\n\n--- 1. Testing DEPOSIT: User deposits 100.0 shares ---")
            deposit_1 = VaultsUserPositionHistory(
                transaction_hash="0x" + "1" * 64,
                user_address=TEST_SENDER_WALLET,
                vault_id=TEST_VAULT_ID,
                timestamp=datetime.utcnow(),
                transaction_type=PositionHistoryType.DEPOSIT,
                shares_amount=100.0,
                share_price_at_transaction=1.00,
                asset_amount=100.0,
            )
            session.add(deposit_1)
            session.commit()
            
            print("✅ DEPOSIT committed. Trigger should have updated the summary.")
            print_position_history(session, TEST_SENDER_WALLET, TEST_VAULT_ID)
            print_position_summary(session, TEST_SENDER_WALLET, TEST_VAULT_ID)

            # --- 2. WITHDRAWAL Test: User withdraws 30 shares ---
            print("\n\n--- 2. Testing WITHDRAWAL: User withdraws 30.0 shares ---")
            withdrawal_1 = VaultsUserPositionHistory(
                transaction_hash="0x" + "2" * 64,
                user_address=TEST_SENDER_WALLET,
                vault_id=TEST_VAULT_ID,
                timestamp=datetime.utcnow(),
                transaction_type=PositionHistoryType.WITHDRAWAL,
                shares_amount=30.0,
                share_price_at_transaction=1.05, # Price may have gone up
                asset_amount=31.5,
            )
            session.add(withdrawal_1)
            session.commit()

            print("✅ WITHDRAWAL committed. Summary should be 70.0 shares.")
            print_position_history(session, TEST_SENDER_WALLET, TEST_VAULT_ID)
            print_position_summary(session, TEST_SENDER_WALLET, TEST_VAULT_ID)

            # --- 3. TRANSFER_OUT Test: Sender transfers 25 shares to Receiver ---
            print(f"\n\n--- 3. Testing TRANSFER_OUT: {TEST_SENDER_WALLET[:10]}... transfers 25.0 shares to {TEST_RECEIVER_WALLET[:10]}... ---")
            transfer_out = VaultsUserPositionHistory(
                transaction_hash="0x" + "3" * 64,
                user_address=TEST_SENDER_WALLET,
                vault_id=TEST_VAULT_ID,
                timestamp=datetime.utcnow(),
                transaction_type=PositionHistoryType.TRANSFER_OUT,
                shares_amount=25.0,
                share_price_at_transaction=1.08,
                asset_amount=27.0,
                counterparty_address=TEST_RECEIVER_WALLET # This is key for the trigger
            )
            
            # The on-chain event also creates a corresponding TRANSFER_IN for the receiver
            transfer_in = VaultsUserPositionHistory(
                transaction_hash="0x" + "3" * 64, # Same hash
                user_address=TEST_RECEIVER_WALLET,
                vault_id=TEST_VAULT_ID,
                timestamp=datetime.utcnow(),
                transaction_type=PositionHistoryType.TRANSFER_IN,
                shares_amount=25.0,
                share_price_at_transaction=1.08,
                asset_amount=27.0,
                counterparty_address=TEST_SENDER_WALLET
            )
            session.add(transfer_out)
            session.add(transfer_in)
            session.commit()

            print("✅ TRANSFER committed. Trigger should update BOTH users.")
            print("\n-- Sender's final state --")
            print_position_history(session, TEST_SENDER_WALLET, TEST_VAULT_ID)
            print_position_summary(session, TEST_SENDER_WALLET, TEST_VAULT_ID)
            
            print("\n-- Receiver's final state --")
            print_position_history(session, TEST_RECEIVER_WALLET, TEST_VAULT_ID)
            print_position_summary(session, TEST_RECEIVER_WALLET, TEST_VAULT_ID)


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
    
    test_position_history_and_summary_trigger()