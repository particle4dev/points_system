# python-training/lessons/points_system/src/integration/list_uniswapv3_events.py
# How to run:
# cd src
# PYTHONPATH=. poetry run python3 integration/list_uniswapv3_events.py

import os
import sys

# Add the project root to the python path to allow imports from `src`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.db import get_session
from models import PartnerUniswapV3Event
from sqlmodel import select


def list_uniswapv3_events():
    """
    Queries and prints all Uniswap V3 LP historical event records from the database,
    grouped by pool slug and wallet address, and ordered by block number.
    """
    with get_session() as session:
        if session is None:
            print("🚫 Database session is not available.")
            return

        # Query all event records, ordering them for logical grouping and chronological display
        statement = select(PartnerUniswapV3Event).order_by(
            PartnerUniswapV3Event.pool_slug,
            PartnerUniswapV3Event.wallet_address,
            PartnerUniswapV3Event.block_number,
        )
        event_records = session.exec(statement).all()

        if not event_records:
            print("ℹ️ No Uniswap V3 LP events found in the database.")
            return

        print(
            f"📜 Found {len(event_records)} Uniswap V3 LP event record(s):\n"
        )

        current_pool = None
        current_wallet = None
        for record in event_records:
            # Add a header for each new pool to group the results
            if record.pool_slug != current_pool:
                current_pool = record.pool_slug
                print(f"\n--- Pool: {current_pool} ---\n")
                # Reset wallet tracker when pool changes
                current_wallet = None

            # Add a sub-header for each new wallet within a pool
            if record.wallet_address != current_wallet:
                current_wallet = record.wallet_address
                print(f"  --- Wallet: {current_wallet} ---")

            print(f"    Event Type:       {record.event_type.value}")
            print(f"    Block Number:     {record.block_number}")
            print(f"    NFT ID:           {record.nft_id}")
            print(f"    Tx Hash:          {record.tx_hash}")
            print(f"    Liquidity Change: {record.liquidity_change}")
            print(f"    Amount0 Change:   {record.amount0_change}")
            print(f"    Amount1 Change:   {record.amount1_change}")
            print(f"    Timestamp:        {record.created_at}")
            print("    " + "-" * 40)


if __name__ == "__main__":
    # Ensure the script can load the .env file for database connection
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file for database connection.")
    except ImportError:
        print("dotenv not installed, skipping .env file load. Ensure DATABASE_URL is set.")
    
    list_uniswapv3_events()