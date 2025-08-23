# Question: How can I list all user point history records from the database in a structured format?

# python-training/lessons/points_system/src/integration/list_points_user_point_history.py
# How to run:
# cd src
# PYTHONPATH=. poetry run python3 integration/list_points_user_point_history.py

import os
import sys

# Add the project root to the python path to allow imports from `src`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.db import get_session
from models import PointsUserPointHistory
from sqlmodel import select


def list_user_point_history():
    """
    Queries and prints all user point history records from the database,
    grouped by wallet address and ordered by most recent first.
    """
    with get_session() as session:
        if session is None:
            print("🚫 Database session is not available.")
            return

        # Query all history records, ordering them for logical grouping
        statement = select(PointsUserPointHistory).order_by(
            PointsUserPointHistory.wallet_address,
            PointsUserPointHistory.created_at.desc(),
        )
        history_records = session.exec(statement).all()

        if not history_records:
            print("ℹ️ No user point history found in the database.")
            return

        print(
            f"📜 Found {len(history_records)} user point history record(s):\n"
        )

        current_wallet = None
        for record in history_records:
            # Add a header for each new wallet to group the results
            if record.wallet_address != current_wallet:
                current_wallet = record.wallet_address
                print(f"\n--- Wallet Address: {current_wallet} ---\n")

            # Format with commas and sign for easier reading
            print(f"  Point Type:    {record.point_type_slug}")
            print(f"  Points Change: {record.points_change:+,.2f}")
            print(f"  Timestamp:     {record.created_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"  Campaign ID:   {record.campaign_id}")
            print(f"  Source Event:  {record.source_event_id}")
            print("-" * 50)


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file for database connection.")
    except ImportError:
        print("dotenv not installed, skipping .env file load. Ensure DATABASE_URL is set.")

    list_user_point_history()