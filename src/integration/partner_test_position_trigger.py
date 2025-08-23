# python-training/lessons/points_system/src/integration/partner_test_position_trigger.py
# How to run:
# cd src
# PYTHONPATH=. poetry run python3 integration/partner_test_position_trigger.py

import os
import sys
from decimal import Decimal
from datetime import datetime, timezone

# Add the project root to the python path to allow imports from `src`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.db import get_session
from src.models import (
    PartnerProtocolEvent,
    PartnerUserPosition,
)
from src.models.partner_user_position import ProtocolType, QuantityType
from sqlmodel import select
from sqlalchemy import delete # FIX: Import the delete function

# --- Helper function for printing status ---

def print_position_for_user(session, wallet_address: str):
    """Queries and prints all current positions for a user."""
    statement = (
        select(PartnerUserPosition)
        .where(PartnerUserPosition.wallet_address == wallet_address)
        .order_by(PartnerUserPosition.protocol_slug, PartnerUserPosition.quantity_type)
    )
    records = session.exec(statement).all()
    print(f"\n💰 Current Positions for {wallet_address}:")
    if not records:
        print("  - No positions found.")
        return
    for record in records:
        print(f"  - Protocol: {record.protocol_slug} | Type: {record.quantity_type.value}")
        print(f"    Raw Quantity: {record.quantity} | USD Value: {record.quantity_usd:.2f}")

# --- The Main Test Function ---

def test_partner_position_trigger():
    """
    Tests the database trigger that maintains the partner_user_position table
    by inserting a sequence of events into partner_protocol_event.
    """
    # --- Test Configuration ---
    ALICE_WALLET = "0xA11ce00000000000000000000000000000000001"
    BOB_WALLET = "0xB0b0000000000000000000000000000000000002"
    PROTOCOL_SLUG = "hyperswap"
    
    with get_session() as session:
        try:
            print("--- Trigger Test Initial State ---")
            # Clear any existing test data for these wallets to ensure a clean run
            
            # --- FIX: Replace session.query().delete() with session.execute(delete()) ---
            delete_statement = delete(PartnerUserPosition).where(
                PartnerUserPosition.wallet_address.in_([ALICE_WALLET, BOB_WALLET])
            )
            session.execute(delete_statement)
            # --- END FIX ---
            
            session.commit()
            
            print_position_for_user(session, ALICE_WALLET)
            print_position_for_user(session, BOB_WALLET)

            # --- 1. INSERT Test: Alice adds liquidity (Creates a new position) ---
            print(f"\n\n--- 1. Testing INSERT (Create): Alice adds liquidity ---")
            # Use a unique tx_hash for each test run to avoid unique constraint violations
            alice_deposit = PartnerProtocolEvent(
                tx_hash=f"0xa001-test-{datetime.now().timestamp()}",
                block_number=2000,
                timestamp=datetime.now(timezone.utc),
                wallet_address=ALICE_WALLET,
                protocol_slug=PROTOCOL_SLUG,
                protocol_type=ProtocolType.DEX_UNISWAPV3,
                quantity_type=QuantityType.LP,
                quantity_change=Decimal("100000"),
                quantity_change_usd=Decimal("10000.00")
            )
            session.add(alice_deposit)
            session.commit()
            
            print("✅ Event committed. Position should be created.")
            print_position_for_user(session, ALICE_WALLET)

            # --- 2. UPDATE Test: Alice withdraws all liquidity (Updates position to zero) ---
            print(f"\n\n--- 2. Testing INSERT (Update): Alice withdraws all liquidity ---")
            alice_withdrawal = PartnerProtocolEvent(
                tx_hash=f"0xa002-test-{datetime.now().timestamp()}",
                block_number=2500,
                timestamp=datetime.now(timezone.utc),
                wallet_address=ALICE_WALLET,
                protocol_slug=PROTOCOL_SLUG,
                protocol_type=ProtocolType.DEX_UNISWAPV3,
                quantity_type=QuantityType.LP,
                quantity_change=Decimal("-100000"), # Note the negative value
                quantity_change_usd=Decimal("-10000.00")
            )
            session.add(alice_withdrawal)
            session.commit()
            
            print("✅ Event committed. Position should be updated to zero.")
            print_position_for_user(session, ALICE_WALLET)

            # --- 3. INSERT Test: Bob adds liquidity (Creates a new, separate position) ---
            print(f"\n\n--- 3. Testing INSERT (Create): Bob adds liquidity ---")
            bob_deposit = PartnerProtocolEvent(
                tx_hash=f"0xb001-test-{datetime.now().timestamp()}",
                block_number=3000,
                timestamp=datetime.now(timezone.utc),
                wallet_address=BOB_WALLET,
                protocol_slug=PROTOCOL_SLUG,
                protocol_type=ProtocolType.DEX_UNISWAPV3,
                quantity_type=QuantityType.LP,
                quantity_change=Decimal("150000"),
                quantity_change_usd=Decimal("18000.00")
            )
            session.add(bob_deposit)
            session.commit()

            print("✅ Event committed. Bob's position should be created.")
            print_position_for_user(session, BOB_WALLET)
            # Also check Alice again to ensure her position was not affected
            print_position_for_user(session, ALICE_WALLET)

        finally:
            print("\n\n--- Test Complete ---")
            # Cleanup after the test run to ensure idempotency
            print("--- Cleaning up test data ---")
            cleanup_statement = delete(PartnerUserPosition).where(
                PartnerUserPosition.wallet_address.in_([ALICE_WALLET, BOB_WALLET])
            )
            session.execute(cleanup_statement)
            session.commit()
            print("✅ Test data cleaned up.")


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file for database connection.")
    except ImportError:
        print("dotenv not installed, skipping .env file load. Ensure DATABASE_URL is set.")
    
    test_partner_position_trigger()