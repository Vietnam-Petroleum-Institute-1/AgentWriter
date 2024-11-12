"""add_conversation_dify_id_to_notebook

Revision ID: 041ca97befa8
Revises: c24594d6b148
Create Date: 2024-11-12 10:37:44.670836

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "041ca97befa8"
down_revision: Union[str, None] = "c24594d6b148"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "notebook", sa.Column("conversation_dify_id", sa.String(255), nullable=True)
    )


def downgrade():
    op.drop_column("notebook", "conversation_dify_id")
