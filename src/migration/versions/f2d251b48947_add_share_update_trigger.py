"""Add share update trigger

Revision ID: f2d251b48947
Revises: 7d766f5a3758
Create Date: 2025-08-25 17:46:58.329853

"""
import sqlmodel
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2d251b48947'
down_revision: Union[str, None] = '7d766f5a3758'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# SQL for creating the function
CREATE_FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION update_user_position_shares()
RETURNS TRIGGER AS $$
DECLARE
    v_user_address VARCHAR;
    v_vault_id UUID;
    v_total_shares NUMERIC;
    v_counterparty_address VARCHAR;
    v_counterparty_total_shares NUMERIC;
BEGIN
    -- Get the user and vault from the newly inserted row
    v_user_address := NEW.user_address;
    v_vault_id := NEW.vault_id;

    -- === Calculate and update for the primary user of the transaction ===
    SELECT
        COALESCE(SUM(
            CASE
                WHEN transaction_type IN ('DEPOSIT', 'TRANSFER_IN') THEN shares_amount
                WHEN transaction_type IN ('WITHDRAWAL', 'TRANSFER_OUT') THEN -shares_amount
                ELSE 0
            END
        ), 0)
    INTO v_total_shares
    FROM vaults_user_position_history
    WHERE user_address = v_user_address AND vault_id = v_vault_id;

    -- Upsert the new total_shares into the snapshot table.
    -- FIX: Provide default 0 values for all NOT NULL columns on initial insert.
    INSERT INTO vaults_user_position (
        user_address, vault_id, total_shares, total_assets_value, 
        unrealized_pnl, realized_pnl, average_cost_basis, last_updated
    )
    VALUES (
        v_user_address, v_vault_id, v_total_shares, 0, 
        0, 0, 0, NOW()
    )
    ON CONFLICT (user_address, vault_id)
    DO UPDATE SET
        total_shares = EXCLUDED.total_shares,
        last_updated = NOW();

    -- === Handle the counterparty for TRANSFER events ===
    v_counterparty_address := NEW.counterparty_address;
    
    IF v_counterparty_address IS NOT NULL THEN
        SELECT
            COALESCE(SUM(
                CASE
                    WHEN transaction_type IN ('DEPOSIT', 'TRANSFER_IN') THEN shares_amount
                    WHEN transaction_type IN ('WITHDRAWAL', 'TRANSFER_OUT') THEN -shares_amount
                    ELSE 0
                END
            ), 0)
        INTO v_counterparty_total_shares
        FROM vaults_user_position_history
        WHERE user_address = v_counterparty_address AND vault_id = v_vault_id;
        
        -- FIX: Also provide default 0 values here for the counterparty.
        INSERT INTO vaults_user_position (
            user_address, vault_id, total_shares, total_assets_value, 
            unrealized_pnl, realized_pnl, average_cost_basis, last_updated
        )
        VALUES (
            v_counterparty_address, v_vault_id, v_counterparty_total_shares, 0, 
            0, 0, 0, NOW()
        )
        ON CONFLICT (user_address, vault_id)
        DO UPDATE SET
            total_shares = EXCLUDED.total_shares,
            last_updated = NOW();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

# SQL for creating the trigger
CREATE_TRIGGER_SQL = """
CREATE TRIGGER trg_after_history_insert_update_shares
AFTER INSERT ON vaults_user_position_history
FOR EACH ROW
EXECUTE FUNCTION update_user_position_shares();
"""

# SQL for dropping the trigger and function in the downgrade
DROP_TRIGGER_SQL = "DROP TRIGGER IF EXISTS trg_after_history_insert_update_shares ON vaults_user_position_history;"
DROP_FUNCTION_SQL = "DROP FUNCTION IF EXISTS update_user_position_shares();"


def upgrade() -> None:
    op.execute(CREATE_FUNCTION_SQL)
    op.execute(CREATE_TRIGGER_SQL)


def downgrade() -> None:
    op.execute(DROP_TRIGGER_SQL)
    op.execute(DROP_FUNCTION_SQL)