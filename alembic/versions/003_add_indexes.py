"""Add indexes for performance optimization

Revision ID: 003
Revises: 002_add_audit_logs
Create Date: 2024-09-04
"""

from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002_add_audit_logs'
branch_labels = None
depends_on = None

def upgrade():
    # Add index on inventory_logs.chemical_id for faster foreign key lookups
    op.create_index('ix_inventory_logs_chemical_id', 'inventory_logs', ['chemical_id'])
    
    # Add indexes on audit_logs for faster filtering
    op.create_index('ix_audit_logs_table_name', 'audit_logs', ['table_name'])
    op.create_index('ix_audit_logs_operation', 'audit_logs', ['operation'])
    op.create_index('ix_audit_logs_record_id', 'audit_logs', ['record_id'])
    
    # Add composite index for common query pattern
    op.create_index('ix_audit_logs_table_record', 'audit_logs', ['table_name', 'record_id'])

def downgrade():
    op.drop_index('ix_audit_logs_table_record', 'audit_logs')
    op.drop_index('ix_audit_logs_record_id', 'audit_logs')
    op.drop_index('ix_audit_logs_operation', 'audit_logs')
    op.drop_index('ix_audit_logs_table_name', 'audit_logs')
    op.drop_index('ix_inventory_logs_chemical_id', 'inventory_logs')
