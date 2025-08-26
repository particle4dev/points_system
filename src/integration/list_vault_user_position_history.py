# src/integration/list_vault_user_position_history.py
# How to run from the project root directory:
# cd src
# PYTHONPATH=. poetry run python3 integration/list_vault_user_position_history.py

"""
List All Vault User Position History
------------------------------------
This script queries and displays all historical transaction records from the
`vaults_user_position_history` table.

It provides a complete, chronologically ordered ledger of all user interactions
with the vaults, such as deposits, withdrawals, and transfers. The results
are grouped by vault and then by user for clear, structured auditing.
"""

import os
import sys

# Add the project root to the python path to allow imports from `src`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.db import get_session
from src.models.vaults import Vault
from src.models.vaults_user_position_history import VaultsUserPositionHistory
from sqlmodel import select


def list_vault_position_history():
    """
    Queries and prints all user position history records from the database,
    grouped by vault and user, and ordered chronologically.
    """
    with get_session() as session:
        if session is None:
            print("🚫 Database session is not available.")
            return

        # Query all history records, joining with Vaults to get the vault name.
        # Order by vault, then user, then timestamp for a structured log.
        statement = (
            select(VaultsUserPositionHistory, Vault)
            .join(Vault, VaultsUserPositionHistory.vault_id == Vault.id)
            .order_by(
                Vault.name,
                VaultsUserPositionHistory.user_address,
                VaultsUserPositionHistory.timestamp
            )
        )
        history_records = session.exec(statement).all()

        if not history_records:
            print("ℹ️ No position history found in the database.")
            return

        print(
            f"📜 Found {len(history_records)} historical transaction record(s):\n"
        )

        current_vault_name = None
        current_user_address = None
        for history, vault in history_records:
            # Add a header for each new vault
            if vault.name != current_vault_name:
                current_vault_name = vault.name
                current_user_address = None  # Reset user for new vault section
                print(f"\n{'='*70}\n Vault: {current_vault_name}\n{'='*70}")

            # Add a sub-header for each new user within a vault
            if history.user_address != current_user_address:
                current_user_address = history.user_address
                print(f"\n  --- User Log: {current_user_address} ---\n")

            # --- Print the detailed, multi-line transaction log entry ---
            print(f"  Record ID:         {history.id}")
            print(f"  Timestamp:         {history.timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"  Transaction Type:  {history.transaction_type.value}")
            print(f"  Transaction Hash:  {history.transaction_hash}")
            # print("-" * 70)
            # Use placeholder token names for clarity
            print(f"  Shares (haHype):   {history.shares_amount:,.4f}")
            print(f"  Share Price:       {history.share_price_at_transaction:,.4f} HYPE per haHype")
            print(f"  Asset Value (HYPE):{history.asset_amount:,.4f}")

            if history.counterparty_address:
                print(f"  Counterparty:      {history.counterparty_address}")

            print("-" * 70)
            print() # Add a blank line for spacing

if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file for database connection.")
    except ImportError:
        print("dotenv not installed, skipping .env file load. Ensure DATABASE_URL is set.")
    
    list_vault_position_history()