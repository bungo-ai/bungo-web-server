import pytest
from app.data_classes.requests.openairequest import OpenAIRequest
from app.prompt_engineering.roles import SystemRole
from app.prompt_engineering.system_info import SystemInfo


@pytest.fixture
def mock_openai_request():
    # Create an instance of OpenAIRequest with default parameters
    request = OpenAIRequest(messages=[])
    request.request_context = {}
    return request


@pytest.fixture
def mock_sys_info(monkeypatch):
    # Mock SystemInfo.get_sys_info
    def mock_get_sys_info(request):
        return {"shell": "bash", "platform": "linux"}
    monkeypatch.setattr(SystemInfo, "get_sys_info", mock_get_sys_info)


def test_get_role_with_valid_role_id(mock_openai_request):
    mock_openai_request.request_context = {"role_key": 2, "sys_info": {"shell": "bash", "platform": "linux"}}
    shell = mock_openai_request.request_context["sys_info"]["shell"]
    platform = mock_openai_request.request_context["sys_info"]["platform"]
    role_description = SystemRole.get_role(mock_openai_request)
    assert role_description == SystemRole.SHELL_ROLE.format(shell=shell, platform=platform)


def test_get_role_with_invalid_role_id_returns_default_role(mock_openai_request):
    mock_openai_request.request_context = {"role_key": "invalid_role"}
    role_description = SystemRole.get_role(mock_openai_request)
    assert role_description == SystemRole.DEFAULT_ROLE


def test_get_role_with_no_role_key_returns_default(mock_openai_request):
    role_description = SystemRole.get_role(mock_openai_request)
    assert role_description == SystemRole.DEFAULT_ROLE, "Default role not returned when no role key is provided."


def test_get_role_handles_missing_context_gracefully(mock_openai_request):
    mock_openai_request.request_context = None
    role_description = SystemRole.get_role(mock_openai_request)
    assert role_description == SystemRole.DEFAULT_ROLE, "Default role not returned when request context is missing."
