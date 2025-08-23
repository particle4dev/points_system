# Question: How can I list all user points from the database in a structured format?

# python-training/lessons/points_system/src/integration/list_points_user_points.py
# How to run:
# cd src
# PYTHONPATH=. poetry run python3 integration/list_points_user_points.py

import os
import sys

# Add the project root to the python path to allow imports from `src`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.db import get_session
from models import PointsUserPoint
from sqlmodel import select


def list_user_points():
    """
    Queries and prints all user point summary records from the database,
    grouped by point type and ordered by the highest point balance first.
    """
    with get_session() as session:
        if session is None:
            print("🚫 Database session is not available.")
            return

        # Query all user point records, ordering them for logical grouping
        statement = select(PointsUserPoint).order_by(
            PointsUserPoint.point_type_slug,
            PointsUserPoint.points.desc(),
        )
        user_points_records = session.exec(statement).all()

        if not user_points_records:
            print("ℹ️ No user points found in the database.")
            return

        print(
            f"📜 Found {len(user_points_records)} user point summary record(s):\n"
        )

        current_point_type = None
        for record in user_points_records:
            # Add a header for each new point type to group the results
            if record.point_type_slug != current_point_type:
                current_point_type = record.point_type_slug
                print(f"\n--- Point Type: {current_point_type} ---\n")

            print(f"  Wallet Address:  {record.wallet_address}")
            # Format with commas for easier reading of large numbers
            print(f"  Total Points:    {record.points:,.2f}")
            print(f"  Last Updated:    {record.updated_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"  Record ID:       {record.id}")
            print("-" * 50)


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file for database connection.")
    except ImportError:
        print("dotenv not installed, skipping .env file load. Ensure DATABASE_URL is set.")
    
    list_user_points()