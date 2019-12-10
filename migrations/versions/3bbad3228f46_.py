"""empty message

Revision ID: 3bbad3228f46
Revises: 41b384041031
Create Date: 2019-12-10 13:32:47.660144

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3bbad3228f46'
down_revision = '41b384041031'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('artist', sa.Column('is_seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('venue', sa.Column('is_seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'seeking_description')
    op.drop_column('venue', 'is_seeking_talent')
    op.drop_column('artist', 'seeking_description')
    op.drop_column('artist', 'is_seeking_venue')
    op.drop_table('show')
    # ### end Alembic commands ###
