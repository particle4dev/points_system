# python-training/lessons/points_system/src/integration/points_get_total_tokens_in_season.py
# How to run:
# cd src
# PYTHONPATH=. poetry run python3 integration/points_get_total_tokens_in_season.py \
#   --campaign-name "HyperSwap HaHype/wHype Pool" \
#   --token-address "0xfde5b0626fc80e36885e2fa9cd5ad9d7768d725c"

import os
import sys
from decimal import Decimal
from typing import Optional

import click

# Add the project root to the python path to allow imports from `src`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.db import get_session
from src.models import (
    PartnerProtocolEvent,
    PointsCampaign,
    Token,
)
from src.models.partner_user_position import QuantityType
from sqlmodel import select, func

@click.command()
@click.option(
    '--campaign-name',
    required=True,
    help="The name of the points campaign to query (e.g., 'HyperSwap HaHype/wHype Pool')."
)
@click.option(
    '--token-address',
    required=True,
    help="The address of the token to calculate the total for."
)
@click.option(
    '--quantity-type',
    type=click.Choice([q.value for q in QuantityType]),
    default=None,
    help="Optional: Filter by a specific quantity type (e.g., 'LP' or 'BORROW')."
)
def get_total_tokens_in_season(campaign_name: str, token_address: str, quantity_type: Optional[str]):
    """
    Calculates the net change of a specific token within a given points campaign season
    by summing all its corresponding events in the protocol event ledger.
    """
    print(f"🔍 Searching for campaign '{campaign_name}' and token '{token_address}'...")

    with get_session() as session:
        # 1. Find the campaign to get its start and end dates
        campaign = session.exec(select(PointsCampaign).where(PointsCampaign.name == campaign_name)).first()
        if not campaign:
            print(f"❌ Error: Campaign '{campaign_name}' not found in the database.")
            return

        # 2. Find the token to get its metadata (name, decimals) for formatting
        token = session.exec(select(Token).where(Token.address == token_address)).first()
        if not token:
            print(f"❌ Error: Token with address '{token_address}' not found in the database.")
            return
            
        print(f" campaigning from {campaign.start_date} to {campaign.end_date or 'Present'}")

        # 3. Build the aggregation query
        # We use func.coalesce to ensure that if SUM returns NULL (no events), we get 0.
        statement = select(func.coalesce(func.sum(PartnerProtocolEvent.quantity_change), 0))

        # Filter by the specified token address
        statement = statement.where(PartnerProtocolEvent.token_address == token_address)

        # Filter by the campaign's time range
        statement = statement.where(PartnerProtocolEvent.timestamp >= campaign.start_date)
        if campaign.end_date:
            statement = statement.where(PartnerProtocolEvent.timestamp <= campaign.end_date)
        
        # Optionally, filter by a specific quantity type
        if quantity_type:
            statement = statement.where(PartnerProtocolEvent.quantity_type == quantity_type)

        # 4. Execute the query
        net_change_raw = session.exec(statement).one()

        # 5. Format the result into a human-readable number
        net_change_readable = net_change_raw / (Decimal(10) ** token.decimals)

        # 6. Print the final answer
        print("\n" + "="*50)
        print("📊 Query Result")
        print("="*50)
        print(f"Campaign:       {campaign.name} (Season 1)")
        print(f"Token:          {token.name} ({token.address})")
        if quantity_type:
            print(f"Filtered by:    QuantityType = {quantity_type}")
        print("-" * 50)
        print(f"Net change of tokens: {net_change_readable:,.4f} {token.name}")
        print("="*50)


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded .env file for database connection.")
    except ImportError:
        print("dotenv not installed, skipping .env file load. Ensure DATABASE_URL is set.")
    
    get_total_tokens_in_season()