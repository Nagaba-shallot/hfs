from collections import defaultdict
from collections.abc import Iterable, Sequence

from hospital_feedback_system.core.constants import (
    MAX_RATING,
    MIN_RATING,
    QUESTION_TYPE_RATING,
    QUESTION_TYPE_TEXT,
    QUESTION_TYPE_YES_NO,
)

_ANSWER_FIELD_BY_TYPE = {
    QUESTION_TYPE_RATING: "rating_value",
    QUESTION_TYPE_TEXT: "text_response",
    QUESTION_TYPE_YES_NO: "yes_no_value",
}


def answer_shape_error(
    question_type: str,
    rating_value: int | None,
    text_response: str | None,
    yes_no_value: bool | None,
) -> str | None:
    expected = _ANSWER_FIELD_BY_TYPE.get(question_type)
    if expected is None:
        return f"unsupported question type '{question_type}'"

    provided = {
        "rating_value": rating_value is not None,
        "text_response": text_response is not None,
        "yes_no_value": yes_no_value is not None,
    }
    if not provided[expected]:
        return f"{expected} is required for a {question_type} question"

    extras = [name for name, given in provided.items() if given and name != expected]
    if extras:
        return (
            f"only {expected} may be provided for a {question_type} question "
            f"(got {', '.join(extras)})"
        )

    if question_type == QUESTION_TYPE_RATING and not (MIN_RATING <= rating_value <= MAX_RATING):
        return f"rating_value must be between {MIN_RATING} and {MAX_RATING}"
    return None


def survey_position(
    categories: Sequence[tuple[int, int]],
    questions: Sequence[tuple[int, int, bool]],
    answered_ids: Iterable[int],
) -> tuple[int, list[int]]:
    answered = set(answered_ids)

    by_category: dict[int, list[int]] = defaultdict(list)
    for question_id, category_id, _required in questions:
        by_category[category_id].append(question_id)

    ordered = sorted(categories, key=lambda c: (c[1], c[0]))
    with_questions = [(cid, order) for cid, order in ordered if by_category.get(cid)]

    current = with_questions[0][1] if with_questions else (ordered[0][1] if ordered else 1)
    for category_id, order in with_questions:
        if any(qid not in answered for qid in by_category[category_id]):
            current = order
            break
    else:
        if with_questions:
            current = with_questions[-1][1]

    missing_required = sorted(
        qid for qid, _cid, required in questions if required and qid not in answered
    )
    return current, missing_required