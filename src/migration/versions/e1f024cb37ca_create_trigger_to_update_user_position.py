"""Create trigger to update user position from snapshot

Revision ID: e1f024cb37ca
Revises: 811cbc8e30b4
Create Date: 2025-08-29 18:08:29.072802

"""
import sqlmodel
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1f024cb37ca'
down_revision: Union[str, None] = '811cbc8e30b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# The SQL to create the trigger function.
# Using a multi-line string makes it easy to write and format SQL.
CREATE_TRIGGER_FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION fn_update_user_position_from_snapshot()
RETURNS TRIGGER AS $$
BEGIN
    -- This function performs an "UPSERT" on the PartnerUserPosition table.
    -- It uses the unique constraint 'uq_user_protocol_quantity_token' to
    -- identify if a row already exists for this position.

    INSERT INTO partner_user_position (
        id, -- Let the default UUID generation work on new inserts
        wallet_address,
        protocol_slug,
        protocol_type,
        quantity_type,
        token_address,
        quantity,
        created_at,
        updated_at
    )
    VALUES (
        gen_random_uuid(), -- Generate a new UUID for the position table
        NEW.wallet_address,
        NEW.protocol_slug,
        NEW.protocol_type,
        NEW.quantity_type,
        NEW.token_address,
        NEW.quantity,
        NOW(), -- Set created_at for a new position
        NOW()  -- Set updated_at for a new position
    )
    ON CONFLICT (wallet_address, protocol_slug, quantity_type, token_address)
    DO UPDATE SET
        quantity = EXCLUDED.quantity, -- 'EXCLUDED' refers to the value that was proposed for insertion
        updated_at = NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

# The SQL to create the trigger itself.
CREATE_TRIGGER_SQL = """
CREATE TRIGGER trg_after_snapshot_insert
AFTER INSERT ON partner_protocol_snapshot
FOR EACH ROW
EXECUTE FUNCTION fn_update_user_position_from_snapshot();
"""

# The SQL to drop the trigger and function for the downgrade path.
# Note the use of "IF EXISTS" to make the downgrade operation idempotent.
DROP_TRIGGER_SQL = "DROP TRIGGER IF EXISTS trg_after_snapshot_insert ON partner_protocol_snapshot;"
DROP_FUNCTION_SQL = "DROP FUNCTION IF EXISTS fn_update_user_position_from_snapshot;"


def upgrade() -> None:
    """
    Applies the migration.
    Creates the trigger function first, then creates the trigger that uses it.
    """
    print("Creating trigger function: fn_update_user_position_from_snapshot")
    op.execute(CREATE_TRIGGER_FUNCTION_SQL)
    
    print("Creating trigger: trg_after_snapshot_insert")
    op.execute(CREATE_TRIGGER_SQL)


def downgrade() -> None:
    """
    Reverts the migration.
    Drops the trigger first, as it depends on the function. Then drops the function.
    """
    print("Dropping trigger: trg_after_snapshot_insert")
    op.execute(DROP_TRIGGER_SQL)
    
    print("Dropping trigger function: fn_update_user_position_from_snapshot")
    op.execute(DROP_FUNCTION_SQL)