"""Add date_created to comment and user

Revision ID: c4b40246fa72
Revises: a8cc65989d34
Create Date: 2022-06-16 20:03:54.365018

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4b40246fa72'
down_revision = 'a8cc65989d34'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('date_created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('users', sa.Column('date_created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'date_created')
    op.drop_column('comments', 'date_created')
    # ### end Alembic commands ###
