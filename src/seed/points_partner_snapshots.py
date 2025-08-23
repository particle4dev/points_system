# python-training/lessons/points_system/src/seed/points_partner_snapshots.py

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from core.db import get_session
from src.models import PointsPartnerSnapshot

def create_points_partner_snapshots():
    """Inserts partner points snapshots into the database."""
    print("Seeding points partner snapshots...")
    with get_session() as session:
        
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        
        snapshots_data = [
            # Vault 1, Partner 'pendle' - snapshot from 2 hours ago
            {
                "vault_address": "0xVAULT_ALPHA",
                "partner_slug": "pendle",
                "points_total": Decimal("10000.00"),
                "snapshot_at": now - timedelta(hours=2),
            },
            # Vault 1, Partner 'pendle' - snapshot from 1 hour ago (delta is +5000)
            {
                "vault_address": "0xVAULT_ALPHA",
                "partner_slug": "pendle",
                "points_total": Decimal("15000.00"),
                "snapshot_at": now - timedelta(hours=1),
            },
            # Vault 2, Partner 'hyperswap' - snapshot from 1 hour ago
            {
                "vault_address": "0xVAULT_BETA",
                "partner_slug": "hyperswap",
                "points_total": Decimal("88000.50"),
                "snapshot_at": now - timedelta(hours=1),
            },
        ]
        
        to_create = [
            PointsPartnerSnapshot(**data)
            for data in snapshots_data
            if not session.query(PointsPartnerSnapshot).filter_by(
                vault_address=data["vault_address"], 
                partner_slug=data["partner_slug"], 
                snapshot_at=data["snapshot_at"]
            ).first()
        ]

        if not to_create:
            print("ℹ️  All points partner snapshots already exist.")
            return

        session.add_all(to_create)
        print(f"✅ Inserted {len(to_create)} new points partner snapshot(s).")


def delete_points_partner_snapshots():
    """Deletes all points partner snapshot records."""
    print("Deleting all points partner snapshots...")
    with get_session() as session:
        deleted_count = session.query(PointsPartnerSnapshot).delete()
        print(f"🗑️  Deleted {deleted_count} points partner snapshot(s).")