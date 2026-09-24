from typing import Literal

ROLE_ADMIN = "admin"
ROLE_SUPER_ADMIN = "super_admin"
Role = Literal["admin", "super_admin"]

QUESTION_TYPE_RATING = "rating"
QUESTION_TYPE_TEXT = "text"
QUESTION_TYPE_YES_NO = "yes_no"
QuestionType = Literal["rating", "text", "yes_no"]

MIN_RATING = 1
MAX_RATING = 5

SESSION_HEADER_NAME = "X-Session-Token"

MAX_PASSWORD_BYTES = 72
MIN_PASSWORD_LENGTH = 12