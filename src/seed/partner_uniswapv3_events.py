# python-training/lessons/points_system/src/seed/partner_uniswapv3_events.py
from decimal import Decimal
from core.db import get_session
from src.models import PartnerUniswapV3Event
from src.models.partner_uniswapv3_event import EventType

# --- 1. Define Seed Data Based on the Scenario ---
# This data represents the historical events from our HaHype/wHype pool scenario.
events_data = [
    # # Step 1: Mint a New Position (Initial Liquidity Add)
    # {
    #     "event_type": EventType.INCREASE_LIQUIDITY,
    #     "tx_hash": "0xabc001",
    #     "block_number": 1000,
    #     "pool_slug": "hyperswap-hahype-whype-pool",
    #     "nft_id": "101",
    #     "wallet_address": "0x1234567890123456789012345678901234567890",
    #     "liquidity_change": "50000",
    #     "amount0_change": "100000000000000000000", # 100 HaHype
    #     "amount1_change": "200000000000000000000", # 200 wHype
    # },
    # # Step 2: Add More Liquidity
    # {
    #     "event_type": EventType.INCREASE_LIQUIDITY,
    #     "tx_hash": "0xabc002",
    #     "block_number": 1050,
    #     "pool_slug": "hyperswap-hahype-whype-pool",
    #     "nft_id": "101",
    #     "wallet_address": "0x1234567890123456789012345678901234567890",
    #     "liquidity_change": "25000",
    #     "amount0_change": "50000000000000000000",  # 50 HaHype
    #     "amount1_change": "100000000000000000000", # 100 wHype
    # },
    # # Step 3: Remove Partial Liquidity
    # {
    #     "event_type": EventType.DECREASE_LIQUIDITY,
    #     "tx_hash": "0xabc003",
    #     "block_number": 1100,
    #     "pool_slug": "hyperswap-hahype-whype-pool",
    #     "nft_id": "101",
    #     "wallet_address": "0x1234567890123456789012345678901234567890",
    #     "liquidity_change": "25000",
    #     "amount0_change": "50000000000000000000",  # 50 HaHype
    #     "amount1_change": "100000000000000000000", # 100 wHype
    # },
    # Note: We don't seed the final removal event to keep the LP position active in the DB.
    # Event 1: User A (Alice) adds initial liquidity.
    {
        "event_type": EventType.INCREASE_LIQUIDITY,
        "tx_hash": "0xa001", # Alice's first transaction
        "block_number": 2000,
        # "pool_slug": "hyperswap-hahype-whype-pool",
        "pool_slug": "0xfde5b0626fc80e36885e2fa9cd5ad9d7768d725c",
        "nft_id": "101",
        "wallet_address": "0xA11ce00000000000000000000000000000000001",
        "liquidity_change": "100000",
        "amount0_change": "100000000000000000000", # 100 HaHype
        "amount1_change": "200000000000000000000", # 200 wHype
    },
    # Event 2: User A (Alice) removes all of her liquidity.
    {
        "event_type": EventType.DECREASE_LIQUIDITY,
        "tx_hash": "0xa002", # Alice's second transaction
        "block_number": 2500,
        # "pool_slug": "hyperswap-hahype-whype-pool",
        "pool_slug": "0xfde5b0626fc80e36885e2fa9cd5ad9d7768d725c",
        "nft_id": "101",
        "wallet_address": "0xA11ce00000000000000000000000000000000001",
        "liquidity_change": "100000",
        "amount0_change": "100000000000000000000", # 100 HaHype
        "amount1_change": "200000000000000000000", # 200 wHype
    },
    # Event 3: User B (Bob) adds his liquidity later.
    {
        "event_type": EventType.INCREASE_LIQUIDITY,
        "tx_hash": "0xb001", # Bob's first transaction
        "block_number": 3000,
        # "pool_slug": "hyperswap-hahype-whype-pool",
        "pool_slug": "0xfde5b0626fc80e36885e2fa9cd5ad9d7768d725c",
        "nft_id": "102",
        "wallet_address": "0xB0b0000000000000000000000000000000000002",
        "liquidity_change": "150000",
        "amount0_change": "150000000000000000000",  # 150 HaHype
        "amount1_change": "300000000000000000000", # 300 wHype
    },
]

def create_partner_uniswapv3_events():
    """Inserts historical LP events into the database."""
    print("Seeding Uniswap v3 historical LP events...")
    with get_session() as session:
        
        events_to_create = []
        for data in events_data:
            # Check if this event (by its unique transaction hash) already exists.
            exists = session.query(PartnerUniswapV3Event).filter_by(tx_hash=data["tx_hash"]).first()
            if exists:
                continue

            # Prepare the data for model creation, casting numbers to Decimal
            event_data = data.copy()
            event_data["liquidity_change"] = Decimal(event_data["liquidity_change"])
            event_data["amount0_change"] = Decimal(event_data["amount0_change"])
            event_data["amount1_change"] = Decimal(event_data["amount1_change"])
            
            events_to_create.append(PartnerUniswapV3Event(**event_data))

        if not events_to_create:
            print("ℹ️  All specified Uniswap v3 LP events already exist.")
            return

        session.add_all(events_to_create)
        print(f"✅ Inserted {len(events_to_create)} new Uniswap v3 LP event(s).")

def delete_partner_uniswapv3_events():
    """Deletes all historical LP event records."""
    print("Deleting all Uniswap v3 historical LP events...")
    with get_session() as session:
        deleted_count = session.query(PartnerUniswapV3Event).delete()
        print(f"🗑️  Deleted {deleted_count} Uniswap v3 LP event(s).")