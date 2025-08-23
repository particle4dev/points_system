# python-training/lessons/points_system/src/seed/points_user_point_history.py
from core.db import get_session
from src.models import PointsUserPointHistory

def delete_user_point_history():
    """Deletes all user point history records."""
    print("Deleting all user point history records...")
    with get_session() as session:
        deleted_count = session.query(PointsUserPointHistory).delete()
        print(f"🗑️  Deleted {deleted_count} user point history record(s).")