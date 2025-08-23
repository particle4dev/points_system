# python-training/lessons/points_system/src/seed/partner_uniswapv3_lps.py

from decimal import Decimal
from core.db import get_session
from src.models import PartnerUniswapV3LP

# --- 1. Define Seed Data ---
# Use token addresses as placeholders for dynamic lookup
lps_data = [
    # --- SCENARIO DATA ---
    # User A (Alice): Added and then removed all liquidity. Her current liquidity is 0.
    {
        # "pool_slug": "hyperswap-hahype-whype-pool",
        "pool_slug": "0xfde5b0626fc80e36885e2fa9cd5ad9d7768d725c",
        "nft_id" : "101",
        "wallet_address" : "0xA11ce00000000000000000000000000000000001",
        "price_lower_tick" : -100,
        "price_upper_tick" : 100,
        "liquidity" : 0, # IMPORTANT: This is 0 because she has withdrawn everything.
    },
    # User B (Bob): Added liquidity and is still in the pool.
    {
        # "pool_slug": "hyperswap-hahype-whype-pool",
        "pool_slug": "0xfde5b0626fc80e36885e2fa9cd5ad9d7768d725c",
        "nft_id" : "102",
        "wallet_address" : "0xB0b0000000000000000000000000000000000002",
        "price_lower_tick" : -200,
        "price_upper_tick" : 200,
        "liquidity" : 150000, # This is his current, active liquidity.
    }
]

# --- 2. Define Create and Delete Functions ---
def create_partner_uniswapv3_lps():
    """Inserts user LP position records into the database."""
    print("Seeding Uniswap v3 LP positions...")
    with get_session() as session:
        
        lps_to_create = []
        for data in lps_data:
            # Check if this specific LP position (by its unique NFT ID) already exists.
            exists = session.query(PartnerUniswapV3LP).filter_by(nft_id=data["nft_id"]).first()
            if exists:
                continue

            # Prepare the data for model creation
            lp_data = data.copy()
            
            # The model expects a Decimal type for liquidity, so we cast it.
            lp_data["liquidity"] = Decimal(lp_data["liquidity"])
            
            lps_to_create.append(PartnerUniswapV3LP(**lp_data))

        if not lps_to_create:
            print("ℹ️  All specified Uniswap v3 LP positions already exist.")
            return

        session.add_all(lps_to_create)
        print(f"✅ Inserted {len(lps_to_create)} new Uniswap v3 LP position(s).")

def delete_partner_uniswapv3_lps():
    """Deletes all LP position records."""
    print("Deleting all Uniswap v3 LP positions...")
    with get_session() as session:
        deleted_count = session.query(PartnerUniswapV3LP).delete()
        print(f"🗑️  Deleted {deleted_count} Uniswap v3 LP position(s).")