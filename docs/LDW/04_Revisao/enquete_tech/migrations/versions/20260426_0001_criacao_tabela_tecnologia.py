"""Criacao da tabela tecnologia

Revision ID: 20260426_0001
Revises:
Create Date: 2026-04-26 00:00:00

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260426_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tecnologia",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=50), nullable=False),
        sa.Column("votos", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome"),
    )


def downgrade() -> None:
    op.drop_table("tecnologia")
