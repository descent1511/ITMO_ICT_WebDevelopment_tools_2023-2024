"""fix

Revision ID: 3bbcfd60db3d
Revises: 4a3df80314a6
Create Date: 2024-03-17 19:07:27.902838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel 


# revision identifiers, used by Alembic.
revision: str = '3bbcfd60db3d'
down_revision: Union[str, None] = '4a3df80314a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('skilluserlink', 'level')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('skilluserlink', sa.Column('level', sa.INTEGER(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###