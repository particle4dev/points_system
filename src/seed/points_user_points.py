# python-training/lessons/points_system/src/seed/points_user_point.py
from core.db import get_session
from src.models import PointsUserPoint

def delete_user_points():
    """Deletes all user point summary records."""
    print("Deleting all user point summary records...")
    with get_session() as session:
        deleted_count = session.query(PointsUserPoint).delete()
        print(f"🗑️  Deleted {deleted_count} user point summary record(s).")