from pydantic import BaseModel

def changes_from(data: BaseModel, nullable: tuple[str, ...] = ()) -> dict:
    raw = data.model_dump(exclude_unset=True)
    return {key: value for key, value in raw.items() if value is not None or key in nullable}