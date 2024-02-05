from pydantic import BaseModel
from typing import Dict, Any, Optional


class OpenAIRequest(BaseModel):
    messages: list
    request_context: Optional[Dict[str, Any]] = None
