# Questions: What is the current tick of pool A?

# python-training/lessons/points_system/src/integration/partner_get_current_tick.py
# How to run:
# cd src
# PYTHONPATH=. poetry run python3 integration/partner_get_current_tick.py

from core.db import get_session
from models import PartnerUniswapV3Tick
from sqlmodel import select


def get_current_tick_for_pool(pool_slug: str):
    """
    Finds the most recent tick for a given pool based on the highest
    block number.
    """
    print(f"🔎  Querying for the current tick of pool: {pool_slug}\n")
    
    with get_session() as session:
        if session is None:
            print("🚫 Database session is not available.")
            return

        # Build the query:
        # 1. Select from the PartnerUniswapV3Tick table.
        # 2. Filter by the provided pool_slug.
        # 3. Order the results by block_number in descending order.
        statement = (
            select(PartnerUniswapV3Tick)
            .where(PartnerUniswapV3Tick.pool_slug == pool_slug)
            .order_by(PartnerUniswapV3Tick.block_number.desc())
        )

        # Execute the query and get the first result, which will be the latest.
        latest_tick = session.exec(statement).first()

        if not latest_tick:
            print(f"ℹ️  No tick data found for pool slug: {pool_slug}")
            return

        print("✅  Query successful! Found the latest tick.\n")
        print("--- Current Tick Information ---")
        print(f"  Pool Slug:     {latest_tick.pool_slug}")
        print(f"  Current Tick:  {latest_tick.tick_idx}")
        print(f"  Block Number:  {latest_tick.block_number}")
        print(f"  Record ID:     {latest_tick.id}")
        print("--------------------------------")


if __name__ == "__main__":
    # The pool address from your question is used as the pool_slug
    target_pool_slug = "0xfde5b0626fc80e36885e2fa9cd5ad9d7768d725c"
    get_current_tick_for_pool(target_pool_slug)