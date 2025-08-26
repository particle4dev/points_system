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
                # Reset user when vault changes to print the user header again
                current_user_address = None
                print(f"\n{'='*25}\n Vault: {current_vault_name}\n{'='*25}")

            # Add a sub-header for each new user within a vault
            if history.user_address != current_user_address:
                current_user_address = history.user_address
                print(f"\n  -- User: {current_user_address} --")

            # Print the detailed transaction line
            timestamp_str = history.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            tx_type_str = history.transaction_type.value.ljust(18) # Pad for alignment
            shares_str = f"{history.shares_amount:,.4f}".rjust(14) # Pad for alignment
            price_str = f"{history.share_price_at_transaction:,.4f}".rjust(10)

            print(
                f"    {timestamp_str} | Type: {tx_type_str} | Shares: {shares_str} | "
                f"Price: {price_str} | Hash: {history.transaction_hash[:10]}..."
            )


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file for database connection.")
    except ImportError:
        print("dotenv not installed, skipping .env file load. Ensure DATABASE_URL is set.")
    
    list_vault_position_history()