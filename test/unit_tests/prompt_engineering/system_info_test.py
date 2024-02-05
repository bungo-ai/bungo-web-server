import pytest
from unittest.mock import patch, Mock
from app.main import ask_openai, OpenAIRequest
from app.prompt_engineering.system_info import SystemInfo


def test_get_sys_info__request_context_provided__context_included():
    platform = "linux"
    shell = "bash"
    request = OpenAIRequest(
        messages=[],
        request_context={"sys_info": {"platform": "linux", "shell": "bash"}},
    )
    result = SystemInfo.get_sys_info(request)
    print(result.keys())
    assert platform in result["platform"]
    assert shell in result["shell"]


def test_get_sys_info__no_request_context__empty_dict_returned():
    openai_request = OpenAIRequest(messages=[], request_context=None)
    result = SystemInfo.get_sys_info(openai_request)
    assert result == {}
