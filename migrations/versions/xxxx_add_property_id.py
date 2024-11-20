"""add property id

Revision ID: xxxx
Revises: previous_revision
Create Date: 2024-xx-xx

"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Add the new column
    op.add_column("equipment", sa.Column("property_id", sa.String(20), nullable=True))

    # Create temporary property IDs for existing records
    equipment_table = sa.table(
        "equipment", sa.column("id", sa.Integer), sa.column("property_id", sa.String)
    )

    connection = op.get_bind()
    equipment_records = connection.execute(sa.select([equipment_table.c.id]))

    for record in equipment_records:
        connection.execute(
            equipment_table.update()
            .where(equipment_table.c.id == record[0])
            .values(property_id=f"PROP-2024-{record[0]:05d}")
        )

    # Make the column non-nullable and unique
    op.alter_column(
        "equipment", "property_id", existing_type=sa.String(20), nullable=False
    )
    op.create_unique_constraint(
        "uq_equipment_property_id", "equipment", ["property_id"]
    )


def downgrade():
    op.drop_constraint("uq_equipment_property_id", "equipment", type_="unique")
    op.drop_column("equipment", "property_id")
