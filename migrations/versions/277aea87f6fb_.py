"""empty message

Revision ID: 277aea87f6fb
Revises: 82211243eb8e
Create Date: 2020-04-30 05:28:16.199067

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '277aea87f6fb'
down_revision = '82211243eb8e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('start_time', sa.DateTime(), nullable=False))
    op.drop_column('Show', 'Date')
    op.drop_column('Show', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('Show', sa.Column('Date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.drop_column('Show', 'start_time')
    # ### end Alembic commands ###
