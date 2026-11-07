"""correct job columns

Revision ID: 8ca415dfec0b
Revises: c7c3cd078030
Create Date: 2026-10-23 15:18:03.235228

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ca415dfec0b'
down_revision: Union[str, Sequence[str], None] = 'c7c3cd078030'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""
    # Rename the existing column to preserve its data.
    op.alter_column(
        "jobs",
        "locaion",
        new_column_name="location",
        existing_type=sa.String(length=150),
        existing_nullable=False,
    )

    # Update the column definitions to match the model.
    op.alter_column(
        "jobs",
        "location",
        existing_type=sa.String(length=150),
        nullable=True,
    )

    op.alter_column(
        "jobs",
        "job_url",
        existing_type=sa.String(length=150),
        type_=sa.String(length=2048),
        existing_nullable=False,
        nullable=True,
    )

    op.alter_column(
        "jobs",
        "source",
        existing_type=sa.String(length=150),
        type_=sa.String(length=100),
        existing_nullable=False,
        nullable=True,
    )




def downgrade() -> None:
    """Downgrade schema."""

    # Restore the original source column definition.
    op.alter_column(
        "jobs",
        "source",
        existing_type=sa.String(length=100),
        type_=sa.String(length=150),
        existing_nullable=True,
        nullable=False,
    )

    # Restore the original job_url column definition.
    op.alter_column(
        "jobs",
        "job_url",
        existing_type=sa.String(length=2048),
        type_=sa.String(length=150),
        existing_nullable=True,
        nullable=False,
    )

    # Restore the original location column constraint.
    op.alter_column(
        "jobs",
        "location",
        existing_type=sa.String(length=150),
        existing_nullable=True,
        nullable=False,
    )

    # Rename the column back instead of dropping and recreating it.
    op.alter_column(
        "jobs",
        "location",
        new_column_name="locaion",
        existing_type=sa.String(length=150),
        existing_nullable=False,
    )

