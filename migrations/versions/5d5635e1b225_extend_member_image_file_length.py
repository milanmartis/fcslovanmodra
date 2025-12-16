from alembic import op
import sqlalchemy as sa

def upgrade():
    op.alter_column(
        "member",
        "image_file",
        existing_type=sa.String(length=20),
        type_=sa.String(length=255),
        existing_nullable=True,
    )

def downgrade():
    op.alter_column(
        "member",
        "image_file",
        existing_type=sa.String(length=255),
        type_=sa.String(length=20),
        existing_nullable=True,
    )