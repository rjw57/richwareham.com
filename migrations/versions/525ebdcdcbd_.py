"""Create short links redirect db

Revision ID: 525ebdcdcbd
Revises: None
Create Date: 2014-09-08 13:27:54.711385

"""

# revision identifiers, used by Alembic.
revision = '525ebdcdcbd'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('redirects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('destination', sa.String(), nullable=True),
    sa.Column('reserved', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default='CURRENT_TIMESTAMP', nullable=True),
    sa.Column('modified_at', sa.DateTime(), server_default='CURRENT_TIMESTAMP', nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_redirects_key'), 'redirects', ['key'], unique=True)
    op.create_index(op.f('ix_redirects_reserved'), 'redirects', ['reserved'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_redirects_reserved'), table_name='redirects')
    op.drop_index(op.f('ix_redirects_key'), table_name='redirects')
    op.drop_table('redirects')
    ### end Alembic commands ###
