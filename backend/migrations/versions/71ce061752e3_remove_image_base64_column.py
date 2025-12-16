"""remove_image_base64_column

Revision ID: 71ce061752e3
Revises: a54024507562
Create Date: 2025-12-13 03:13:52.077055

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "71ce061752e3"
down_revision: Union[str, Sequence[str], None] = "a54024507562"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove the image_base64 column as images are now stored only in S3
    op.drop_column("cards", "image_base64")


def downgrade() -> None:
    """Downgrade schema."""
    # Re-add the image_base64 column if we need to rollback
    op.add_column("cards", sa.Column("image_base64", sa.String(), nullable=True))
