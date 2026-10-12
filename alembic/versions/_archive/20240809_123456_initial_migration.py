from alembic import op
import sqlalchemy as sa

revision = "20240809_123456"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admin",
        sa.Column("admin_id", sa.Integer(), primary_key=True),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("hospital_name", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="admin"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_admin_admin_id", "admin", ["admin_id"])
    op.create_index("ix_admin_email", "admin", ["email"])

    op.create_table(
        "patients",
        sa.Column("patient_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_token", sa.String(), nullable=False, unique=True),
        sa.Column("phone_number", sa.String(), nullable=True),
        sa.Column("department_visited", sa.String(), nullable=False),
        sa.Column("visit_date", sa.Date(), nullable=True),
        sa.Column("is_anonymous", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_patients_patient_id", "patients", ["patient_id"])

    op.create_table(
        "department",
        sa.Column("department_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("qr_code_token", sa.String(), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_department_department_id", "department", ["department_id"])

    op.create_table(
        "feedback_category",
        sa.Column("feedback_category_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("icon", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_feedback_category_feedback_category_id",
        "feedback_category",
        ["feedback_category_id"],
    )

    op.create_table(
        "questions",
        sa.Column("question_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "feedback_category_id",
            sa.Integer(),
            sa.ForeignKey("feedback_category.feedback_category_id"),
            nullable=False,
        ),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(), nullable=False, server_default="rating"),
        sa.Column("order_in_feedback_category", sa.Integer(), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("min_rating_label", sa.String(), nullable=True),
        sa.Column("max_rating_label", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_questions_question_id", "questions", ["question_id"])

    op.create_table(
        "feedback_response",
        sa.Column("feedback_response_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "patient_id", sa.Integer(), sa.ForeignKey("patients.patient_id"), nullable=False
        ),
        sa.Column(
            "question_id", sa.Integer(), sa.ForeignKey("questions.question_id"), nullable=False
        ),
        sa.Column("rating_value", sa.Integer(), nullable=True),
        sa.Column("text_response", sa.Text(), nullable=True),
        sa.Column("yes_no_value", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_feedback_response_feedback_response_id",
        "feedback_response",
        ["feedback_response_id"],
    )
    # One answer per patient per question — the service layer upserts on this.
    op.create_unique_constraint(
        "uq_feedback_response_patient_question",
        "feedback_response",
        ["patient_id", "question_id"],
    )

    op.create_table(
        "survey_progress",
        sa.Column("survey_progress_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "patient_id",
            sa.Integer(),
            sa.ForeignKey("patients.patient_id"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "current_feedback_category_order", sa.Integer(), nullable=False, server_default="1"
        ),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "total_questions_answered", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "last_activity_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_index(
        "ix_survey_progress_survey_progress_id", "survey_progress", ["survey_progress_id"]
    )

    op.create_table(
        "qr_scan",
        sa.Column("qr_scan_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("qr_code_token", sa.String(), nullable=False),
        sa.Column("department", sa.String(), nullable=False),
        sa.Column(
            "patient_id", sa.Integer(), sa.ForeignKey("patients.patient_id"), nullable=True
        ),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("scanned_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_qr_scan_qr_scan_id", "qr_scan", ["qr_scan_id"])

    op.create_table(
        "admin_reply",
        sa.Column("admin_reply_id", sa.Integer(), primary_key=True),
        sa.Column(
            "feedback_response_id",
            sa.Integer(),
            sa.ForeignKey("feedback_response.feedback_response_id"),
            nullable=False,
        ),
        sa.Column("admin_id", sa.Integer(), sa.ForeignKey("admin.admin_id"), nullable=False),
        sa.Column("reply_text", sa.Text(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_admin_reply_admin_reply_id", "admin_reply", ["admin_reply_id"])


def downgrade():
    # Reverse dependency order.
    op.drop_table("admin_reply")
    op.drop_table("qr_scan")
    op.drop_table("survey_progress")
    op.drop_table("feedback_response")
    op.drop_table("questions")
    op.drop_table("feedback_category")
    op.drop_table("department")
    op.drop_table("patients")
    op.drop_table("admin")