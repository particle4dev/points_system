# python-training/lessons/points_system/src/seed/cli.py

import click
import os
import sys

# Add the project root to the python path to allow imports from `src`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.seed.partner_pools import create_partner_pools, delete_partner_pools
from src.seed.tokens import create_tokens, delete_tokens
from src.seed.partners import create_partners, delete_partners
from src.seed.partner_uniswapv3_lps import create_partner_uniswapv3_lps, delete_partner_uniswapv3_lps
from src.seed.partner_uniswapv3_ticks import create_partner_uniswapv3_ticks, delete_partner_uniswapv3_ticks
from src.seed.partner_pool_uniswapv3 import create_partner_pool_uniswapv3, delete_partner_pool_uniswapv3
# from src.seed.partner_uniswapv3_events import create_partner_uniswapv3_events, delete_partner_uniswapv3_events
from src.seed.points_point_types import create_points_point_types, delete_points_point_types
from src.seed.points_campaigns import create_points_campaigns, delete_points_campaigns
from src.seed.points_user_campaign_points import create_user_campaign_points, delete_user_campaign_points
from src.seed.points_partner_snapshots import create_points_partner_snapshots, delete_points_partner_snapshots
from src.seed.points_user_point_history import delete_user_point_history
from src.seed.points_user_points import delete_user_points

@click.group()
def cli():
    """Database Seeder CLI for the Alembic Learning Lab"""

@cli.command()
def create():
    """Creates and seeds all tables with default development data."""
    print("🚀 Starting database seeding process...")
    # Core data first
    create_partners()
    create_tokens()
    create_points_point_types() 
    create_partner_pools()
    
    # Raw data ingestion/ledgers
    create_points_partner_snapshots()
    
    # Uniswap V3 specific data
    create_partner_pool_uniswapv3()
    create_partner_uniswapv3_lps()
    create_partner_uniswapv3_ticks()
    # create_partner_uniswapv3_events()
    
    # User and campaign data
    create_points_campaigns()
    create_user_campaign_points()

    print("\n✅ All data seeded successfully!")

@cli.command()
def delete():
    """Deletes all data from seeded tables."""
    print("🔥 Deleting all development data...")
    # delete_user_points()

    # --- CORRECT DELETION ORDER ---
    # Delete tables with the most dependencies first.
    delete_user_point_history()        # Depends on campaigns, campaign_points
    delete_user_points()               # Depends on point_types
    # delete_points_partner_activity()   # Depends on campaigns, point_types
    delete_user_campaign_points()      # Depends on campaigns, point_types
    # delete_user_point_balances()       # Depends on point_types

    # Now it's safe to delete the tables they depend on.
    delete_points_campaigns()
    delete_points_partner_snapshots()
    delete_points_point_types()

    # The rest of the partner context
    # delete_partner_uniswapv3_events()
    delete_partner_uniswapv3_ticks()
    delete_partner_uniswapv3_lps()
    delete_partner_pool_uniswapv3()
    delete_partner_pools()
    delete_tokens()
    delete_partners()
    print("\n🗑️ All data deleted successfully!")

if __name__ == "__main__":
    # This allows the script to be run directly
    # Example: python src/seed/cli.py create
    # Make sure your .env file with DATABASE_URL is loaded
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file")
    except ImportError:
        print("dotenv not installed, skipping .env file load.")

    cli()