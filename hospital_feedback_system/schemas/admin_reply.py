from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AdminReplyCreate(BaseModel):
    feedback_response_id: int
    reply_text: str
    is_public: bool = True


class AdminReplyUpdate(BaseModel):
    reply_text: str | None = None
    is_public: bool | None = None


class AdminReplyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    admin_reply_id: int
    feedback_response_id: int
    admin_id: int
    reply_text: str
    is_public: bool
    created_at: datetime