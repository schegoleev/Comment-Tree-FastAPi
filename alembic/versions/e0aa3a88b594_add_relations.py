"""Add relations

Revision ID: e0aa3a88b594
Revises: 511a247791ce
Create Date: 2022-06-16 14:52:14.761416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0aa3a88b594'
down_revision = '511a247791ce'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('comments', sa.Column('parent_comment_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'comments', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'comments', 'comments', ['parent_comment_id'], ['id'])
    op.add_column('posts', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'posts', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'posts', type_='foreignkey')
    op.drop_column('posts', 'user_id')
    op.drop_constraint(None, 'comments', type_='foreignkey')
    op.drop_constraint(None, 'comments', type_='foreignkey')
    op.drop_column('comments', 'parent_comment_id')
    op.drop_column('comments', 'user_id')
    # ### end Alembic commands ###
