"""add user role

Revision ID: c1efbc840651
Revises: 6ba988803718
Create Date: 2026-09-13 18:14:52.552905

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c1efbc840651'
down_revision: Union[str, Sequence[str], None] = '6ba988803718'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    user_role_enum = postgresql.ENUM(
        "USER",
        "MANAGER",
        "ADMIN",
        name="user_role"
    )

    user_role_enum.create(
        op.get_bind(),
        checkfirst=True
    )

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role_enum,
            nullable=False,
            server_default="USER"
        )
    )

    op.alter_column(
        "users",
        "role",
        server_default=None
    )


def downgrade() -> None:

    op.drop_column(
        "users",
        "role"
    )

    user_role_enum = postgresql.ENUM(
        "USER",
        "MANAGER",
        "ADMIN",
        name="user_role"
    )

    user_role_enum.drop(
        op.get_bind(),
        checkfirst=True
    )