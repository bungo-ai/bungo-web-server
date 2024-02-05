import pytest
from unittest.mock import patch, Mock
from fastapi import HTTPException
from app.main import ask_openai, OpenAIRequest, update_message_content
import openai


SYS_INFO_KEY = "sys_info"


def test_update_message_content_appends_role_data_to_first_message():
    role_data = "Some role data"
    data = OpenAIRequest(
        messages=[{"role": "user", "content": "Hello"}], request_context=None
    )
    sys_info_details = {}
    update_message_content(data, sys_info_details, role_data)
    assert data.messages[0]["content"] == "HelloSome role data"
    assert len(data.messages) == 1


def test_update_message_content_appends_sys_info_to_first_message_if_first_message():
    role_data = ""
    data = OpenAIRequest(
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": "Hello"},
        ],
    )
    sys_info_details = {"key": "value"}
    update_message_content(data, sys_info_details, role_data)
    expected_content = f"\nHere is information about my computer:\n \
        {SYS_INFO_KEY}: {sys_info_details}\n"
    update_data = data.messages[0]["content"]
    assert update_data == expected_content
    assert len(data.messages) == 2


def test_update_message_content_does_not_append_sys_info_if_not_first_message():
    role_data = ""
    data = OpenAIRequest(
        messages=[{"role": "system", "content": "System message"}], request_context=None
    )
    sys_info_details = {"key": "value"}
    update_message_content(data, sys_info_details, role_data)
    assert data.messages[0]["content"] == "System message"


@pytest.mark.asyncio
async def test_request_context_not_provided__no_additional_info_added():
    messages = [
        {"role": "system", "content": "I am a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]
    data = OpenAIRequest(messages=messages)
    with patch("openai.chat.completions.create"):
        await ask_openai(data)
        assert "I am a helpful assistant" in data.messages[0]["content"]


@pytest.mark.asyncio
async def test_request_context_provided__info_added_to_first_system_message():
    request_context = {"sys_info": {"os": "linux", "shell": "bash"}}
    request_context_str = ["sys_info: {'os': 'linux', 'shell': 'bash'}"]
    messages = [
        {"role": "system", "content": "I am a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]
    data = OpenAIRequest(messages=messages, request_context=request_context)
    with patch("openai.chat.completions.create") as mock_openai_call:
        mock_openai_call.return_value = mock_openai_response_200
        await ask_openai(data)
        mock_openai_call.assert_called_once()
        called_with_messages = mock_openai_call.call_args[1]["messages"]
        for contextStr in request_context_str:
            assert contextStr in called_with_messages[0]["content"]


@pytest.mark.asyncio
async def test_ask_openai__success__return_json():
    with patch("openai.chat.completions.create", return_value=mock_openai_response_200):
        data = OpenAIRequest(messages=[{"role": "user", "content": "Hello"}])
        response = await ask_openai(data)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_ask_openai__openai_server_issue__502_inform_client():
    with patch(
        "openai.chat.completions.create", side_effect=mock_openai_response_502_error
    ):
        data = OpenAIRequest(messages=[{"role": "user", "content": "Hello"}])
        with pytest.raises(HTTPException) as exc_info:
            await ask_openai(data)
        assert exc_info.value.status_code == 502


@pytest.mark.asyncio
async def test_ask_openai__bungo_server_issue__500_inform_client():
    with patch(
        "openai.chat.completions.create", side_effect=mock_openai_response_500_error
    ):
        data = OpenAIRequest(messages=[{"role": "user", "content": "Hello"}])
        with pytest.raises(HTTPException) as exc_info:
            await ask_openai(data)
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_ask_openai__malformed_openai_request__500_inform_client():
    with patch(
        "openai.chat.completions.create", side_effect=mock_openai_response_400_error
    ):
        data = OpenAIRequest(messages=[{"role": "user", "content": "Hello"}])
        with pytest.raises(HTTPException) as exc_info:
            await ask_openai(data)
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_ask_openai__malformed_openai_auth__500_inform_client():
    with patch(
        "openai.chat.completions.create", side_effect=mock_openai_response_401_error
    ):
        data = OpenAIRequest(messages=[{"role": "user", "content": "Hello"}])
        with pytest.raises(HTTPException) as exc_info:
            await ask_openai(data)
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_ask_openai__openai_denies_access__500_inform_client():
    with patch(
        "openai.chat.completions.create", side_effect=mock_openai_response_403_error
    ):
        data = OpenAIRequest(messages=[{"role": "user", "content": "Hello"}])
        with pytest.raises(HTTPException) as exc_info:
            await ask_openai(data)
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_ask_openai__no_openai_resource__500_inform_client():
    with patch(
        "openai.chat.completions.create", side_effect=mock_openai_response_404_error
    ):
        data = OpenAIRequest(messages=[{"role": "user", "content": "Hello"}])
        with pytest.raises(HTTPException) as exc_info:
            await ask_openai(data)
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_openai_reports_unprocessable_entity__500_inform_client():
    with patch(
        "openai.chat.completions.create", side_effect=mock_openai_response_422_error
    ):
        data = OpenAIRequest(messages=[{"role": "user", "content": "Hello"}])
        with pytest.raises(HTTPException) as exc_info:
            await ask_openai(data)
        assert exc_info.value.status_code == 522


@pytest.mark.asyncio
async def test_openai_reports_rate_limit_reached__529_inform_client():
    with patch(
        "openai.chat.completions.create", side_effect=mock_openai_response_429_error
    ):
        data = OpenAIRequest(messages=[{"role": "user", "content": "Hello"}])
        with pytest.raises(HTTPException) as exc_info:
            await ask_openai(data)
        assert exc_info.value.status_code == 529


# Mock response for successful calls
mock_openai_response_200 = Mock()
mock_openai_response_200.status_code = 200
mock_openai_response_200.json.return_value = {
    "choices": [{"message": {"content": "Test successful response from OpenAI"}}]
}

# Mock response for error calls
mock_openai_response_400 = Mock()
mock_openai_response_400.status_code = 400
mock_openai_response_400.message = "Bad Request Error!"
mock_openai_response_400_error = openai.BadRequestError(
    message=mock_openai_response_400.message,
    response=mock_openai_response_400,
    body=None,
)

mock_openai_response_401 = Mock()
mock_openai_response_401.status_code = 401
mock_openai_response_401.message = "Authentication Error!"
mock_openai_response_401_error = openai.AuthenticationError(
    message=mock_openai_response_401.message,
    response=mock_openai_response_401,
    body=None,
)

mock_openai_response_403 = Mock()
mock_openai_response_403.status_code = 403
mock_openai_response_403.message = "Permission Denied Error!"
mock_openai_response_403_error = openai.PermissionDeniedError(
    message=mock_openai_response_403.message,
    response=mock_openai_response_403,
    body=None,
)

mock_openai_response_404 = Mock()
mock_openai_response_404.status_code = 404
mock_openai_response_404.message = "Not Found Error!"
mock_openai_response_404_error = openai.NotFoundError(
    message=mock_openai_response_404.message,
    response=mock_openai_response_404,
    body=None,
)

mock_openai_response_422 = Mock()
mock_openai_response_422.status_code = 422
mock_openai_response_422.message = "Unprocessable Entity Error!"
mock_openai_response_422_error = openai.UnprocessableEntityError(
    message=mock_openai_response_422.message,
    response=mock_openai_response_422,
    body=None,
)

mock_openai_response_429 = Mock()
mock_openai_response_429.status_code = 429
mock_openai_response_429.message = "Rate Limit Error!"
mock_openai_response_429_error = openai.RateLimitError(
    message=mock_openai_response_429.message,
    response=mock_openai_response_429,
    body=None,
)

mock_openai_response_502 = Mock()
mock_openai_response_502.status_code = 502
mock_openai_response_502.message = "Internal Server Error!"
mock_openai_response_502_error = openai.InternalServerError(
    message=mock_openai_response_502.message,
    response=mock_openai_response_502,
    body=None,
)

mock_openai_response_500 = Mock()
mock_openai_response_500.message = "API Connection Error!"
mock_openai_response_500_error = openai.APIConnectionError(request=None)
