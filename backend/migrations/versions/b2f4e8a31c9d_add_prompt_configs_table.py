"""Add prompt_configs table

Revision ID: b2f4e8a31c9d
Revises: 71ce061752e3
Create Date: 2026-02-02 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2f4e8a31c9d"
down_revision: Union[str, Sequence[str], None] = "71ce061752e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "prompt_configs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "config_type",
            sa.Enum("HOLIDAY", "SUPERHERO", name="promptconfigtype"),
            nullable=False,
        ),
        sa.Column("validation_prompt", sa.Text(), nullable=False),
        sa.Column("image_prompt", sa.Text(), nullable=False),
        sa.Column("themes", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("config_type"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("prompt_configs")
    op.execute("DROP TYPE IF EXISTS promptconfigtype")
