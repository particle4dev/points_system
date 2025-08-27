# python-training/lessons/points_system/src/integration/vault_calculate_pnl.py
# How to run:
# cd src
# PYTHONPATH=. poetry run python3 integration/vault_calculate_pnl.py

"""
On-Demand PnL Reporting Script for Vault Positions
--------------------------------------------------
This script calculates and displays realized and unrealized Profit and Loss (PnL)
for user vault positions.

It reads the complete transaction log from the `vaults_user_position_history`
table and applies the First-In, First-Out (FIFO) accounting method in memory
to generate a financial report. The results are printed to the console and are
not persisted, as the `VaultsUserPosition` table is designed to only store
the current share balance.
"""

import os
import sys
import uuid
from datetime import datetime
from collections import deque, namedtuple

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.db import get_session
from models.vaults import Vault
from models.vaults_user_position_history import VaultsUserPositionHistory, PositionHistoryType
from sqlmodel import select

# A simple data structure to hold the results of our calculation
PnlResult = namedtuple(
    "PnlResult",
    ["total_shares", "average_cost_basis", "unrealized_pnl", "realized_pnl"]
)


# --- The Core PnL Calculation Logic ---

def calculate_pnl_for_user(session, user_address: str, vault_id: uuid.UUID, current_share_price: float) -> PnlResult:
    """
    Calculates PnL for a user's vault position using the FIFO method.

    This function is read-only and returns the calculated metrics without
    writing to the database.

    Args:
        session: The database session object.
        user_address: The user's wallet address.
        vault_id: The ID of the vault.
        current_share_price: The current market price of one share (haHype).

    Returns:
        A PnlResult object containing the calculated financial metrics.
    """
    # 1. Fetch all historical transactions, ordered by time for FIFO
    history_statement = (
        select(VaultsUserPositionHistory)
        .where(VaultsUserPositionHistory.user_address == user_address)
        .where(VaultsUserPositionHistory.vault_id == vault_id)
        .order_by(VaultsUserPositionHistory.timestamp)
    )
    history_records = session.exec(history_statement).all()

    # 2. Separate into inflows (acquiring shares) and outflows (disposing of shares)
    inflows = deque([tx for tx in history_records if tx.transaction_type in [PositionHistoryType.DEPOSIT, PositionHistoryType.TRANSFER_IN]])
    outflows = [tx for tx in history_records if tx.transaction_type in [PositionHistoryType.WITHDRAWAL, PositionHistoryType.TRANSFER_OUT]]

    realized_pnl = 0.0

    # 3. Calculate Realized PnL: Match each outflow against the oldest inflows
    for outflow in outflows:
        shares_to_sell = outflow.shares_amount
        price_at_sale = outflow.share_price_at_transaction

        while shares_to_sell > 0 and inflows:
            oldest_inflow = inflows[0]
            shares_from_lot = min(shares_to_sell, oldest_inflow.shares_amount)
            
            cost_basis = oldest_inflow.share_price_at_transaction
            realized_pnl += shares_from_lot * (price_at_sale - cost_basis)
            
            shares_to_sell -= shares_from_lot
            oldest_inflow.shares_amount -= shares_from_lot

            if oldest_inflow.shares_amount < 1e-9:
                inflows.popleft()

    # 4. Calculate metrics from the remaining inflows (shares still held)
    unrealized_pnl = 0.0
    total_remaining_shares = 0.0
    total_cost_of_remaining_shares = 0.0

    for lot in inflows:
        cost_basis = lot.share_price_at_transaction
        unrealized_pnl += lot.shares_amount * (current_share_price - cost_basis)
        total_remaining_shares += lot.shares_amount
        total_cost_of_remaining_shares += lot.shares_amount * cost_basis

    # 5. Calculate Average Cost Basis
    average_cost_basis = 0.0
    if total_remaining_shares > 0:
        average_cost_basis = total_cost_of_remaining_shares / total_remaining_shares

    return PnlResult(
        total_shares=total_remaining_shares,
        average_cost_basis=average_cost_basis,
        unrealized_pnl=unrealized_pnl,
        realized_pnl=realized_pnl
    )


# --- The Main Scenario Function ---

def run_pnl_report_scenario():
    """Sets up a vault scenario with 3 price points and runs the PnL report."""
    ALICE_WALLET = "0xA11ce00000000000000000000000000000000001"
    BOB_WALLET = "0xB0b0000000000000000000000000000000000002"
    TEST_VAULT_ID = uuid.uuid4()

    with get_session() as session:
        try:
            # --- 1. Setup: Create vault and populate a detailed history in a temporary transaction ---
            print("--- Setting up test data (this will be rolled back)... ---")
            test_vault = Vault(id=TEST_VAULT_ID, name="HYPE/haHype PnL Report Vault")
            session.add(test_vault)

            # The story unfolds over time with 3 different prices
            history = [
                # TIME 1: Price is 1.00 HYPE per haHype
                VaultsUserPositionHistory(user_address=ALICE_WALLET, vault_id=TEST_VAULT_ID, transaction_hash="0xa1", timestamp=datetime(2025, 1, 1), transaction_type=PositionHistoryType.DEPOSIT, shares_amount=1000.0, share_price_at_transaction=1.00, asset_amount=1000.0),
                
                # TIME 2: Price has risen to 1.20 HYPE per haHype
                VaultsUserPositionHistory(user_address=BOB_WALLET, vault_id=TEST_VAULT_ID, transaction_hash="0xb1", timestamp=datetime(2025, 2, 1), transaction_type=PositionHistoryType.DEPOSIT, shares_amount=500.0, share_price_at_transaction=1.20, asset_amount=600.0),
                VaultsUserPositionHistory(user_address=ALICE_WALLET, vault_id=TEST_VAULT_ID, transaction_hash="0xa2", timestamp=datetime(2025, 2, 15), transaction_type=PositionHistoryType.DEPOSIT, shares_amount=200.0, share_price_at_transaction=1.20, asset_amount=240.0),
                
                # TIME 3: Price is now 1.50 HYPE per haHype
                VaultsUserPositionHistory(user_address=ALICE_WALLET, vault_id=TEST_VAULT_ID, transaction_hash="0xa4", timestamp=datetime(2025, 3, 10), transaction_type=PositionHistoryType.WITHDRAWAL, shares_amount=300.0, share_price_at_transaction=1.50, asset_amount=450.0)
            ]
            session.add_all(history)
            
            # --- 2. Run the PnL Calculation ---
            # Assume the current haHype price is now 1.60 HYPE
            current_hahype_price = 1.60
            
            print(f"\n--- Generating PnL Report (Current haHype Price: {current_hahype_price:.2f} HYPE) ---")
            alice_pnl = calculate_pnl_for_user(session, ALICE_WALLET, TEST_VAULT_ID, current_hahype_price)
            bob_pnl = calculate_pnl_for_user(session, BOB_WALLET, TEST_VAULT_ID, current_hahype_price)

            # --- 3. Display Final Calculated Results ---
            print("\n==============================================")
            print("         PNL REPORTING RESULTS        ")
            print("==============================================")
            
            print(f"\n--- PnL Report for Alice ---")
            print(f"  Current Shares (haHype):       {alice_pnl.total_shares:,.4f}")
            print(f"  Average Cost (HYPE/haHype):  {alice_pnl.average_cost_basis:,.4f}")
            print(f"  Unrealized PnL (HYPE):       {alice_pnl.unrealized_pnl:+,.4f}")
            print(f"  Realized PnL (HYPE):         {alice_pnl.realized_pnl:+,.4f}")
            
            print(f"\n--- PnL Report for Bob ---")
            print(f"  Current Shares (haHype):       {bob_pnl.total_shares:,.4f}")
            print(f"  Average Cost (HYPE/haHype):  {bob_pnl.average_cost_basis:,.4f}")
            print(f"  Unrealized PnL (HYPE):       {bob_pnl.unrealized_pnl:+,.4f}")
            print(f"  Realized PnL (HYPE):         {bob_pnl.realized_pnl:+,.4f}")

        finally:
            print("\n\n--- Scenario Complete: Rolling back all test data. ---")
            session.rollback()

if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file for database connection.")
    except ImportError:
        print("dotenv not installed, skipping .env file load. Ensure DATABASE_URL is set.")
    
    run_pnl_report_scenario()