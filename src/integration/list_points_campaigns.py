# Question: How can I list all point campaigns from the database in a structured format?

# python-training/lessons/points_system/src/integration/list_points_campaigns.py
# How to run:
# cd src
# PYTHONPATH=. poetry run python3 integration/list_points_campaigns.py

import os
import sys

# Add the project root to the python path to allow imports from `src`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.db import get_session
from models import PointsCampaign
from sqlmodel import select


def list_points_campaigns():
    """
    Queries and prints all point campaign records from the database,
    grouped by partner slug and ordered by start date.
    """
    with get_session() as session:
        if session is None:
            print("🚫 Database session is not available.")
            return

        # Query all campaign records, ordering them for logical grouping
        statement = select(PointsCampaign).order_by(
            PointsCampaign.partner_slug,
            PointsCampaign.start_date.desc(),
        )
        campaign_records = session.exec(statement).all()

        if not campaign_records:
            print("ℹ️ No point campaigns found in the database.")
            return

        print(
            f"📜 Found {len(campaign_records)} point campaign record(s):\n"
        )

        current_partner = None
        for record in campaign_records:
            # Add a header for each new partner to group the results
            if record.partner_slug != current_partner:
                current_partner = record.partner_slug
                print(f"\n--- Partner: {current_partner} ---\n")

            print(f"  Campaign Name: {record.name}")
            # print(f"  Campaign Type: {record.type or 'N/A'}")
            print(f"  Multiplier:    {record.multiplier}")
            print(f"  Start Date:    {record.start_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            # Handle the optional end date for display
            print(f"  End Date:      {record.end_date.strftime('%Y-%m-%d %H:%M:%S %Z') if record.end_date else 'Ongoing'}")
            print(f"  Tags:          {', '.join(record.tags) or 'None'}")
            print(f"  Updated At:    {record.updated_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"  Campaign ID:   {record.id}")
            print("-" * 50)


if __name__ == "__main__":
    # Ensure the script can load the .env file for database connection
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file for database connection.")
    except ImportError:
        print("dotenv not installed, skipping .env file load. Ensure DATABASE_URL is set.")

    list_points_campaigns()