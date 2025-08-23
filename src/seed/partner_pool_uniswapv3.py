# python-training/lessons/points_system/src/seed/partner_pool_uniswapv3.py
from core.db import get_session
from src.models import PartnerPool, PartnerPoolUniswapV3, Token
from sqlmodel import select

# This data assumes that tokens with these names have been seeded in the tokens table.
uniswap_v3_pools_data = [
    {
        "pool_slug": "0xfde5b0626fc80e36885e2fa9cd5ad9d7768d725c",
        "token0_address": "0xfde5b0626fc80e36885e2fa9cd5ad9d7768d725c",
        "token1_address": "0x5555555555555555555555555555555555555555",
    },
    # Add other Uniswap V3 pools here if needed
]

def create_partner_pool_uniswapv3():
    """Inserts Uniswap V3 metadata for partner pools."""
    print("Seeding partner pool Uniswap V3 metadata...")
    with get_session() as session:
        
        metadata_to_create = []
        for data in uniswap_v3_pools_data:
            # Check if metadata for this pool slug already exists
            exists = session.query(PartnerPoolUniswapV3).filter_by(pool_slug=data["pool_slug"]).first()
            if exists:
                continue

            # 1. Verify the parent PartnerPool exists
            pool = session.query(PartnerPool).filter_by(slug=data["pool_slug"]).first()
            if not pool:
                print(f"⚠️  PartnerPool with slug '{data['pool_slug']}' not found. Skipping metadata seeding.")
                continue

            # 2. Verify that the tokens exist in the database to maintain foreign key integrity
            token0 = session.exec(select(Token).where(Token.address == data["token0_address"])).first()
            token1 = session.exec(select(Token).where(Token.address == data["token1_address"])).first()

            if not token0 or not token1:
                print(f"⚠️  Tokens with addresses '{data['token0_address']}' or '{data['token1_address']}' not found in 'tokens' table. Skipping metadata for pool '{data['pool_slug']}'.")
                continue
            
            # 3. Prepare the data for model creation
            metadata = PartnerPoolUniswapV3(
                pool_slug=data["pool_slug"],
                token0_address=data["token0_address"],
                token1_address=data["token1_address"],
            )
            metadata_to_create.append(metadata)

        if not metadata_to_create:
            print("ℹ️  All Uniswap V3 pool metadata already exists.")
            return

        session.add_all(metadata_to_create)
        print(f"✅ Inserted {len(metadata_to_create)} new Uniswap V3 pool metadata record(s).")


def delete_partner_pool_uniswapv3():
    """Deletes all partner pool Uniswap V3 metadata records."""
    print("Deleting all partner pool Uniswap V3 metadata records...")
    with get_session() as session:
        deleted_count = session.query(PartnerPoolUniswapV3).delete()
        print(f"🗑️  Deleted {deleted_count} partner pool Uniswap V3 metadata record(s).")