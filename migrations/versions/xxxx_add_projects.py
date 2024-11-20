"""add projects

Revision ID: xxxx
Revises: previous_revision
Create Date: 2024-xx-xx
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Create projects table
    op.create_table(
        "project",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("manager_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["manager_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create project_members association table
    op.create_table(
        "project_members",
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("project_id", "user_id"),
    )

    # Create project_equipment association table
    op.create_table(
        "project_equipment",
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
        ),
        sa.ForeignKeyConstraint(
            ["equipment_id"],
            ["equipment.id"],
        ),
        sa.PrimaryKeyConstraint("project_id", "equipment_id"),
    )


def downgrade():
    op.drop_table("project_equipment")
    op.drop_table("project_members")
    op.drop_table("project")
