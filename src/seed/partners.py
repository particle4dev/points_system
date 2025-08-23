# python-training/lessons/points_system/src/seed/partners.py

from core.db import get_session
from src.models import Partner

partners_data = [
    {
        "name": "HyperSwap",
        "slug": "hyperswap",
        "website": "https://hyperswap.exchange/",
        "description": "The HyperEVM Native Dex",
        "tags": ["dex", "native"],
    },
    {
        "name": "Pendle Finance",
        "slug": "pendle",
        "website": "https://www.pendle.finance/",
        "description": "Tokenizing and trading future yield.",
        "tags": ["yield", "defi"],
    },
    {
        "name": "Harmonix Finance",
        "slug": "harmonix",
        "website": "https://harmonix.fi/",
        "description": "Reshaping Yield Optimization.",
        "tags": ["vault", "defi"],
    }
]

def create_partners():
    print("Seeding partners...")
    with get_session() as session:
        to_create = [Partner(**data) for data in partners_data if not session.query(Partner).filter_by(slug=data["slug"]).first()]
        if not to_create:
            print("ℹ️  All partners already exist.")
            return
        session.add_all(to_create)
        print(f"✅ Inserted {len(to_create)} new partner(s).")

def delete_partners():
    print("Deleting all partners...")
    with get_session() as session:
        count = session.query(Partner).delete()
        print(f"🗑️  Deleted {count} partner(s).")