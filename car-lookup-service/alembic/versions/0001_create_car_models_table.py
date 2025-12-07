"""create car_models table

Revision ID: 0001
Revises:
Create Date: 2025-12-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create car_models table in car service database."""
    op.create_table('car_models',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('make', sa.String(length=100), nullable=False),
    sa.Column('model', sa.String(length=100), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('battery_capacity_kwh', sa.Float(), nullable=True),
    sa.Column('max_range_km', sa.Float(), nullable=True),
    sa.Column('connector_type', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_car_models_id'), 'car_models', ['id'], unique=False)
    op.create_index(op.f('ix_car_models_make'), 'car_models', ['make'], unique=False)
    op.create_index(op.f('ix_car_models_model'), 'car_models', ['model'], unique=False)


def downgrade() -> None:
    """Drop car_models table."""
    op.drop_index(op.f('ix_car_models_model'), table_name='car_models')
    op.drop_index(op.f('ix_car_models_make'), table_name='car_models')
    op.drop_index(op.f('ix_car_models_id'), table_name='car_models')
    op.drop_table('car_models')
