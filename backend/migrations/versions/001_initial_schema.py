# backend/migrations/versions/001_initial_schema.py
"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2023-09-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Divisions table
    op.create_table('divisions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Ranks table
    op.create_table('ranks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Racers table
    op.create_table('racers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('firstname', sa.String(length=100), nullable=False),
        sa.Column('lastname', sa.String(length=100), nullable=False),
        sa.Column('divisionid', sa.Integer(), nullable=False),
        sa.Column('rankid', sa.Integer(), nullable=True),
        sa.Column('carno', sa.String(length=20), nullable=True),
        sa.Column('carname', sa.String(length=200), nullable=True),
        sa.Column('exclude', sa.Boolean(), nullable=True),
        sa.Column('imagefile', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['divisionid'], ['divisions.id'], ),
        sa.ForeignKeyConstraint(['rankid'], ['ranks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Cars table
    op.create_table('cars',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('racer_id', sa.Integer(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('car_number', sa.String(length=20), nullable=False),
        sa.Column('color', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['racer_id'], ['racers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('racer_id')
    )
    
    # Rounds table
    op.create_table('rounds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('divisionid', sa.Integer(), nullable=True),
        sa.Column('roundno', sa.Integer(), nullable=False),
        sa.Column('phase', sa.String(length=50), nullable=False),
        sa.Column('charttype', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['divisionid'], ['divisions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Heats table
    op.create_table('heats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('roundid', sa.Integer(), nullable=False),
        sa.Column('heat', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('completed_time', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['roundid'], ['rounds.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Racer heats table for lane assignments
    op.create_table('racer_heats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('heat_id', sa.Integer(), nullable=False),
        sa.Column('lane', sa.Integer(), nullable=False),
        sa.Column('racer_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['heat_id'], ['heats.id'], ),
        sa.ForeignKeyConstraint(['racer_id'], ['racers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Race results table
    op.create_table('race_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('heat_id', sa.Integer(), nullable=False),
        sa.Column('racer_id', sa.Integer(), nullable=False),
        sa.Column('lane', sa.Integer(), nullable=False),
        sa.Column('time', sa.Float(), nullable=True),
        sa.Column('place', sa.Integer(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['heat_id'], ['heats.id'], ),
        sa.ForeignKeyConstraint(['racer_id'], ['racers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Awards table
    op.create_table('awards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('divisionid', sa.Integer(), nullable=True),
        sa.Column('rankid', sa.Integer(), nullable=True),
        sa.Column('awardtype', sa.String(length=20), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['divisionid'], ['divisions.id'], ),
        sa.ForeignKeyConstraint(['rankid'], ['ranks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Award winners table
    op.create_table('award_winners',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('award_id', sa.Integer(), nullable=False),
        sa.Column('racer_id', sa.Integer(), nullable=False),
        sa.Column('place', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['award_id'], ['awards.id'], ),
        sa.ForeignKeyConstraint(['racer_id'], ['racers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Settings table
    op.create_table('settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    
    # Timer configuration table
    op.create_table('timer_configuration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timer_type', sa.String(length=50), nullable=False),
        sa.Column('connection_type', sa.String(length=20), nullable=False),
        sa.Column('connection_details', sa.Text(), nullable=False),
        sa.Column('lanes', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('timer_configuration')
    op.drop_table('settings')
    op.drop_table('award_winners')
    op.drop_table('awards')
    op.drop_table('race_results')
    op.drop_table('racer_heats')
    op.drop_table('heats')
    op.drop_table('rounds')
    op.drop_table('cars')
    op.drop_table('racers')
    op.drop_table('ranks')
    op.drop_table('divisions')