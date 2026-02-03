"""Remove config_type from prompt_configs

Revision ID: c3e5f9b42d1a
Revises: b2f4e8a31c9d
Create Date: 2026-02-03 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3e5f9b42d1a"
down_revision: Union[str, Sequence[str], None] = "b2f4e8a31c9d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the unique constraint on config_type
    op.drop_constraint("prompt_configs_config_type_key", "prompt_configs", type_="unique")

    # Drop the config_type column
    op.drop_column("prompt_configs", "config_type")

    # Drop the enum type
    op.execute("DROP TYPE IF EXISTS promptconfigtype")


def downgrade() -> None:
    """Downgrade schema."""
    # Recreate the enum type
    op.execute("CREATE TYPE promptconfigtype AS ENUM ('HOLIDAY', 'SUPERHERO')")

    # Add back the config_type column
    op.add_column(
        "prompt_configs",
        sa.Column(
            "config_type",
            sa.Enum("HOLIDAY", "SUPERHERO", name="promptconfigtype"),
            nullable=True,
        ),
    )

    # Set a default value for existing records
    op.execute("UPDATE prompt_configs SET config_type = 'HOLIDAY' WHERE config_type IS NULL")

    # Make the column non-nullable
    op.alter_column("prompt_configs", "config_type", nullable=False)

    # Recreate the unique constraint
    op.create_unique_constraint("prompt_configs_config_type_key", "prompt_configs", ["config_type"])
