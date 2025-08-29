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
from sqlalchemy import delete

# --- Helper function for printing status ---

def print_position_for_user(session, wallet_address: str):
    """Queries and prints all current positions for a user."""
    statement = (
        select(PartnerUserPosition)
        .where(PartnerUserPosition.wallet_address == wallet_address)
        .order_by(PartnerUserPosition.protocol_slug, PartnerUserPosition.quantity_type, PartnerUserPosition.token_address)
    )
    records = session.exec(statement).all()
    print(f"\n💰 Current Positions for {wallet_address}:")
    if not records:
        print("  - No positions found.")
        return
    for record in records:
        print(f"  - Protocol: {record.protocol_slug} | Type: {record.quantity_type.value}")
        print(f"    Token: {record.token_address}")
        print(f"    Raw Quantity: {record.quantity}")

# --- The Main Test Function ---

def test_partner_position_trigger():
    """
    Tests the database trigger that maintains the partner_user_position table
    by inserting a sequence of events into partner_protocol_event.
    """
    # --- Test Configuration ---
    ALICE_WALLET = "0xA11ce00000000000000000000000000000000001"
    BOB_WALLET = "0xB0b0000000000000000000000000000000000002"
    
    # Define protocol slugs
    HYPERSWAP_SLUG = "hyperswap"
    HYPURRFI_SLUG = "hypurrfi"
    
    # Define token/asset addresses
    HYPERSWAP_POOL_ADDRESS = "0xfde5b0626fc80e36885e2fa9cd5ad9d7768d725c" # Represents the LP token
    HYPE_TOKEN_ADDRESS = "0xHYPE_TOKEN_ADDRESS_HERE"
    STHYPE_TOKEN_ADDRESS = "0xSTHYPE_TOKEN_ADDRESS_HERE"
    
    with get_session() as session:
        try:
            print("--- Trigger Test Initial State ---")
            # Clear any existing test data for these wallets to ensure a clean run
            delete_statement = delete(PartnerUserPosition).where(
                PartnerUserPosition.wallet_address.in_([ALICE_WALLET, BOB_WALLET])
            )
            session.execute(delete_statement)
            session.commit()
            
            print_position_for_user(session, ALICE_WALLET)
            print_position_for_user(session, BOB_WALLET)

            # --- 1. INSERT (Create): Alice adds HyperSwap liquidity ---
            print(f"\n\n--- 1. Testing INSERT (Create): Alice adds HyperSwap LP ---")
            alice_deposit = PartnerProtocolEvent(
                tx_hash=f"0xa001-test-{datetime.now().timestamp()}",
                block_number=2000, timestamp=datetime.now(timezone.utc),
                wallet_address=ALICE_WALLET, protocol_slug=HYPERSWAP_SLUG,
                protocol_type=ProtocolType.DEX_UNISWAPV3, quantity_type=QuantityType.LP,
                token_address=HYPERSWAP_POOL_ADDRESS,
                quantity_change=Decimal("100000")
            )
            session.add(alice_deposit)
            session.commit()
            print("✅ Event committed. Position should be created.")
            print_position_for_user(session, ALICE_WALLET)

            # --- 2. INSERT (Update): Alice withdraws all HyperSwap liquidity ---
            print(f"\n\n--- 2. Testing INSERT (Update): Alice withdraws all HyperSwap LP ---")
            alice_withdrawal = PartnerProtocolEvent(
                tx_hash=f"0xa002-test-{datetime.now().timestamp()}",
                block_number=2500, timestamp=datetime.now(timezone.utc),
                wallet_address=ALICE_WALLET, protocol_slug=HYPERSWAP_SLUG,
                protocol_type=ProtocolType.DEX_UNISWAPV3, quantity_type=QuantityType.LP,
                token_address=HYPERSWAP_POOL_ADDRESS,
                quantity_change=Decimal("-100000")
            )
            session.add(alice_withdrawal)
            session.commit()
            print("✅ Event committed. Position should be updated to zero.")
            print_position_for_user(session, ALICE_WALLET)

            # --- 3. INSERT (Create): Bob adds HyperSwap liquidity ---
            print(f"\n\n--- 3. Testing INSERT (Create): Bob adds HyperSwap LP ---")
            bob_deposit = PartnerProtocolEvent(
                tx_hash=f"0xb001-test-{datetime.now().timestamp()}",
                block_number=3000, timestamp=datetime.now(timezone.utc),
                wallet_address=BOB_WALLET, protocol_slug=HYPERSWAP_SLUG,
                protocol_type=ProtocolType.DEX_UNISWAPV3, quantity_type=QuantityType.LP,
                token_address=HYPERSWAP_POOL_ADDRESS,
                quantity_change=Decimal("150000")
            )
            session.add(bob_deposit)
            session.commit()
            print("✅ Event committed. Bob's position should be created.")
            print_position_for_user(session, BOB_WALLET)

            # --- 4. INSERT (Create): Alice supplies HYPE to HypurrFi ---
            print(f"\n\n--- 4. Testing INSERT (Multi-token): Alice supplies HYPE to HypurrFi ---")
            alice_hype_supply = PartnerProtocolEvent(
                tx_hash=f"0xc001-test-{datetime.now().timestamp()}",
                block_number=3500, timestamp=datetime.now(timezone.utc),
                wallet_address=ALICE_WALLET, protocol_slug=HYPURRFI_SLUG,
                protocol_type=ProtocolType.LENDING_HYPURRFI, quantity_type=QuantityType.LP,
                token_address=HYPE_TOKEN_ADDRESS,
                quantity_change=Decimal("500000000000000000000")
            )
            session.add(alice_hype_supply)
            session.commit()
            print("✅ Event committed. Alice should now have a new HypurrFi position.")
            print_position_for_user(session, ALICE_WALLET)

            # --- 5. INSERT (Create): Alice supplies stHYPE to HypurrFi ---
            print(f"\n\n--- 5. Testing INSERT (Multi-token): Alice supplies stHYPE to HypurrFi ---")
            alice_sthype_supply = PartnerProtocolEvent(
                tx_hash=f"0xd001-test-{datetime.now().timestamp()}",
                block_number=4000, timestamp=datetime.now(timezone.utc),
                wallet_address=ALICE_WALLET, protocol_slug=HYPURRFI_SLUG,
                protocol_type=ProtocolType.LENDING_HYPURRFI, quantity_type=QuantityType.LP,
                token_address=STHYPE_TOKEN_ADDRESS,
                quantity_change=Decimal("200000000000000000000")
            )
            session.add(alice_sthype_supply)
            session.commit()
            print("✅ Event committed. Alice should have a second, distinct HypurrFi position.")
            print_position_for_user(session, ALICE_WALLET)

        finally:
            print("\n\n--- Test Complete ---")
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