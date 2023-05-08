"""Artifact Visualizations [9971237fa937].

Revision ID: 9971237fa937
Revises: fbd7f18ced1e
Create Date: 2023-04-06 16:40:44.430701

"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision = "9971237fa937"
down_revision = "fbd7f18ced1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema and/or data, creating a new revision."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "artifact_visualization",
        sa.Column("artifact_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.Column("type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("uri", sa.TEXT(), nullable=False),
        sa.ForeignKeyConstraint(
            ["artifact_id"],
            ["artifact.id"],
            name="fk_artifact_visualization_artifact_id_artifact",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("artifact", schema=None) as batch_op:
        batch_op.alter_column(
            "uri",
            existing_type=sa.VARCHAR(),
            type_=sa.TEXT(),
            existing_nullable=False,
        )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade database schema and/or data back to the previous revision."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("artifact_visualization")

    with op.batch_alter_table("artifact", schema=None) as batch_op:
        batch_op.alter_column(
            "uri",
            existing_type=sa.TEXT(),
            type_=sa.VARCHAR(),
            existing_nullable=False,
        )
    # ### end Alembic commands ###
