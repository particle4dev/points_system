# Questions: How to get the balance of a user in a Uniswap V3 pool at a specific time?

# python-training/lessons/points_system/src/integration/partner_get_user_balance_at_time.py
# How to run:
# cd src
# PYTHONPATH=. poetry run python3 integration/partner_get_user_balance_at_time.py

import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict

# Add the project root to the python path to allow imports from `src`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlmodel import select, Session
from sqlalchemy import func, case
from sqlalchemy.orm import aliased

from core.db import get_session
from src.models import (
    PartnerUniswapV3Event, 
    PartnerPoolUniswapV3, 
    Token
)
from src.models.partner_uniswapv3_event import EventType

def get_lp_balance_at_time(
    session: Session,
    wallet_address: str, 
    pool_slug: str, 
    target_datetime: datetime
) -> Dict[str, Decimal]:
    """
    Calculates the net balance of token0 and token1 for a user in a specific pool
    at a given point in time by performing an efficient aggregation query at the
    database level.

    Args:
        session: The database session to use for queries.
        wallet_address: The user's wallet address.
        pool_slug: The slug of the Uniswap V3 pool.
        target_datetime: The specific date and time for the balance snapshot.

    Returns:
        A dictionary containing the user's balances, including raw (wei) and
        human-readable formats. Returns zero balances if no history is found.
    """
    # Step 1: Build the optimized aggregation query using SUM and CASE.
    # This query calculates the net change in a single pass at the database level.
    
    # Define the conditional sum for amount0.
    # We use func.coalesce to ensure that if there are no events (sum is NULL),
    # we get back 0 instead of None.
    sum_amount0 = func.coalesce(func.sum(
        case(
            (PartnerUniswapV3Event.event_type == EventType.INCREASE_LIQUIDITY, PartnerUniswapV3Event.amount0_change),
            (PartnerUniswapV3Event.event_type == EventType.DECREASE_LIQUIDITY, -PartnerUniswapV3Event.amount0_change),
        )
    ), Decimal(0)).label("net_amount0_raw")

    # Define the conditional sum for amount1.
    sum_amount1 = func.coalesce(func.sum(
        case(
            (PartnerUniswapV3Event.event_type == EventType.INCREASE_LIQUIDITY, PartnerUniswapV3Event.amount1_change),
            (PartnerUniswapV3Event.event_type == EventType.DECREASE_LIQUIDITY, -PartnerUniswapV3Event.amount1_change),
        )
    ), Decimal(0)).label("net_amount1_raw")

    # Construct the final statement, filtering by user, pool, and time.
    statement = (
        select(sum_amount0, sum_amount1)
        .where(PartnerUniswapV3Event.wallet_address == wallet_address)
        .where(PartnerUniswapV3Event.pool_slug == pool_slug)
        .where(PartnerUniswapV3Event.created_at <= target_datetime)
    )

    # Execute the query. This will return a single row with the two net amounts.
    balances_raw = session.exec(statement).one()
    net_amount0_raw = balances_raw.net_amount0_raw
    net_amount1_raw = balances_raw.net_amount1_raw

    # Step 2: Fetch token metadata (decimals) to format the output.
    # This part remains the same as it's an efficient lookup.
    Token0 = aliased(Token)
    Token1 = aliased(Token)
    
    meta_statement = (
        select(
            Token0.decimals.label("token0_decimals"),
            Token1.decimals.label("token1_decimals"),
            Token0.name.label("token0_name"),
            Token1.name.label("token1_name"),
        )
        .select_from(PartnerPoolUniswapV3)
        .join(Token0, PartnerPoolUniswapV3.token0_address == Token0.address)
        .join(Token1, PartnerPoolUniswapV3.token1_address == Token1.address)
        .where(PartnerPoolUniswapV3.pool_slug == pool_slug)
    )
    
    token_meta = session.exec(meta_statement).first()

    if not token_meta:
        raise ValueError(f"Could not find token metadata for pool: {pool_slug}")

    # Step 3: Calculate human-readable balances
    token0_decimals = token_meta.token0_decimals
    token1_decimals = token_meta.token1_decimals

    net_amount0_readable = net_amount0_raw / (Decimal(10) ** token0_decimals)
    net_amount1_readable = net_amount1_raw / (Decimal(10) ** token1_decimals)

    return {
        "token0_name": token_meta.token0_name,
        "token1_name": token_meta.token1_name,
        "balance_token0_raw": net_amount0_raw,
        "balance_token1_raw": net_amount1_raw,
        "balance_token0_readable": net_amount0_readable,
        "balance_token1_readable": net_amount1_readable,
    }


if __name__ == "__main__":
    # --- EXAMPLE USAGE (This part remains unchanged) ---
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file for database connection.")
    except ImportError:
        print("dotenv not installed, skipping .env file load. Ensure DATABASE_URL is set.")

    HAHYPE_WHYPE_POOL = "0xfde5b0626fc80e36885e2fa9cd5ad9d7768d725c"
    ALICE_WALLET = "0xA11ce00000000000000000000000000000000001"
    BOB_WALLET = "0xB0b0000000000000000000000000000000000002"

    with get_session() as session:
        print("\n--- Analyzing Alice's Balance ---")

        alice_deposit_event = session.exec(select(PartnerUniswapV3Event).where(PartnerUniswapV3Event.tx_hash == "0xa001")).one()
        print(f"Alice's deposit event found at: {alice_deposit_event.created_at}")
        time_after_alice_deposit = alice_deposit_event.created_at

        balance1 = get_lp_balance_at_time(
            session,
            wallet_address=ALICE_WALLET,
            pool_slug=HAHYPE_WHYPE_POOL,
            target_datetime=time_after_alice_deposit
        )
        print(f"\nAlice's balance AT {time_after_alice_deposit}:")
        print(f"  {balance1['token0_name']}: {balance1['balance_token0_readable']:.2f}")
        print(f"  {balance1['token1_name']}: {balance1['balance_token1_readable']:.2f}")

        alice_withdraw_event = session.exec(select(PartnerUniswapV3Event).where(PartnerUniswapV3Event.tx_hash == "0xa002")).one()
        time_after_alice_withdrawal = alice_withdraw_event.created_at

        balance2 = get_lp_balance_at_time(
            session,
            wallet_address=ALICE_WALLET,
            pool_slug=HAHYPE_WHYPE_POOL,
            target_datetime=time_after_alice_withdrawal
        )
        print(f"\nAlice's balance AT {time_after_alice_withdrawal}:")
        print(f"  {balance2['token0_name']}: {balance2['balance_token0_readable']:.2f}")
        print(f"  {balance2['token1_name']}: {balance2['balance_token1_readable']:.2f}")

        print("\n--- Analyzing Bob's Balance ---")

        bob_deposit_event = session.exec(select(PartnerUniswapV3Event).where(PartnerUniswapV3Event.tx_hash == "0xb001")).one()
        time_after_bob_deposit = bob_deposit_event.created_at

        balance3 = get_lp_balance_at_time(
            session,
            wallet_address=BOB_WALLET,
            pool_slug=HAHYPE_WHYPE_POOL,
            target_datetime=time_after_bob_deposit
        )
        print(f"\nBob's balance AT {time_after_bob_deposit}:")
        print(f"  {balance3['token0_name']}: {balance3['balance_token0_readable']:.2f}")
        print(f"  {balance3['token1_name']}: {balance3['balance_token1_readable']:.2f}")