from typing import Any, Dict
from app.data_classes.requests.openairequest import OpenAIRequest

SYS_INFO_KEY = "sys_info"


class SystemInfo:

    @classmethod
    def get_sys_info(cls, openai_request: OpenAIRequest) -> Dict[str, Any]:
        if openai_request.request_context is not None:
            sys_info_details = openai_request.request_context.get(SYS_INFO_KEY, "")
        else:
            sys_info_details = {}

        print(f"sys_info: {sys_info_details}")
        return sys_info_details
