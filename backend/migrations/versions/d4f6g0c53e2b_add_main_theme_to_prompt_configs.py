"""Add holiday_main_theme to prompt_configs

Revision ID: d4f6g0c53e2b
Revises: c3e5f9b42d1a
Create Date: 2026-02-04 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4f6g0c53e2b"
down_revision: Union[str, Sequence[str], None] = "c3e5f9b42d1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add the holiday_main_theme column with a default value
    op.add_column(
        "prompt_configs",
        sa.Column("holiday_main_theme", sa.Text(), nullable=False, server_default="Hero"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("prompt_configs", "holiday_main_theme")
