"""empty message

Revision ID: 68677e4b25c7
Revises: 96d50d0dd3a6
Create Date: 2022-05-27 10:52:25.483748

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68677e4b25c7'
down_revision = '96d50d0dd3a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'area_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('area_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('Venue_area_id_fkey', 'Venue', 'Areas', ['area_id'], ['id'])
    op.create_table('Areas',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Areas_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('city', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('state', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='Areas_pkey')
    )
    # ### end Alembic commands ###
