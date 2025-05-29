"""create ingredients

Revision ID: e6080fd0667b
Revises: 450c8d26062e
Create Date: 2025-05-25 21:34:34.818414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision: str = 'e6080fd0667b'
down_revision: Union[str, None] = '450c8d26062e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
