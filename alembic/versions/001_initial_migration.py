"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-01-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('chemicals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('cas_number', sa.String(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cas_number')
    )
    op.create_index(op.f('ix_chemicals_id'), 'chemicals', ['id'], unique=False)
    
    op.create_table('inventory_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chemical_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.Enum('ADD', 'REMOVE', 'UPDATE', name='actiontype'), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['chemical_id'], ['chemicals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_logs_id'), 'inventory_logs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_inventory_logs_id'), table_name='inventory_logs')
    op.drop_table('inventory_logs')
    op.drop_index(op.f('ix_chemicals_id'), table_name='chemicals')
    op.drop_table('chemicals')
    op.execute('DROP TYPE IF EXISTS actiontype')