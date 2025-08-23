# python-training/lessons/points_system/src/seed/tokens.py

from core.db import get_session
from src.models import Token

# --- 1. Define Seed Data ---
tokens_data = [
    {
        "address": "0x5555555555555555555555555555555555555555",
        "name": "WHYPE",
        "decimals": 18,
    },
    {
        "address": "0xfde5b0626fc80e36885e2fa9cd5ad9d7768d725c",
        "name": "haHYPE",
        "decimals": 18,
    },
]

# --- 2. Define Create and Delete Functions ---
def create_tokens():
    """Inserts token records into the database."""
    print("Seeding tokens...")
    with get_session() as session:
        tokens_to_create = []
        for data in tokens_data:
            exists = session.query(Token).filter_by(address=data["address"]).first()
            if not exists:
                tokens_to_create.append(Token(**data))
        
        if not tokens_to_create:
            print("ℹ️  All tokens already exist.")
            return

        session.add_all(tokens_to_create)
        print(f"✅ Inserted {len(tokens_to_create)} new token(s).")

def delete_tokens():
    """Deletes all token records."""
    print("Deleting all tokens...")
    with get_session() as session:
        deleted_count = session.query(Token).delete()
        print(f"🗑️  Deleted {deleted_count} token(s).")