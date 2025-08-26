# src/integration/list_vault_user_positions.py
# How to run from the project root directory:
# cd src
# PYTHONPATH=. poetry run python3 integration/list_vault_user_positions.py

"""
List All Vault User Positions
-----------------------------
This script queries and displays all user position summary records from the
`vaults_user_position` table.

It joins with the `vaults` table to get the vault name, then groups the
results by vault and orders them by the highest share balance first for
easy viewing.
"""

import os
import sys

# Add the project root to the python path to allow imports from `src`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.db import get_session
from src.models.vaults import Vault
from src.models.vaults_user_position import VaultsUserPosition
from sqlmodel import select


def list_vault_user_positions():
    """
    Queries and prints all user position summary records from the database,
    grouped by vault and ordered by the highest share balance first.
    """
    with get_session() as session:
        if session is None:
            print("🚫 Database session is not available.")
            return

        # Query all user positions, joining with Vaults to get the vault name.
        # Order by vault name first, then by total shares descending.
        statement = (
            select(VaultsUserPosition, Vault)
            .join(Vault, VaultsUserPosition.vault_id == Vault.id)
            .order_by(
                Vault.name,
                VaultsUserPosition.total_shares.desc()
            )
        )
        position_records = session.exec(statement).all()

        if not position_records:
            print("ℹ️ No user positions found in the database.")
            return

        print(
            f"📜 Found {len(position_records)} user position record(s) across all vaults:\n"
        )

        current_vault_name = None
        for position, vault in position_records:
            # Add a header for each new vault to group the results
            if vault.name != current_vault_name:
                current_vault_name = vault.name
                print(f"\n--- Vault: {current_vault_name} (ID: {vault.id}) ---\n")

            print(f"  User Address:    {position.user_address}")
            # Format with commas for easier reading of large numbers
            print(f"  Total Shares:    {position.total_shares:,.4f}")
            print(f"  Last Updated:    {position.last_updated.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print("-" * 60)


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file for database connection.")
    except ImportError:
        print("dotenv not installed, skipping .env file load. Ensure DATABASE_URL is set.")
    
    list_vault_user_positions()