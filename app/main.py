from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
from typing import Dict, Any
from prompt_engineering.roles import SystemRole
from data_classes.requests.openairequest import OpenAIRequest
from prompt_engineering.system_info import SystemInfo

load_dotenv()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "FETCH"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OpenAI API key not found. Make sure the environment\
         variable OPENAI_API_KEY is set."
    )


openai.api_key = OPENAI_API_KEY

SYS_INFO_KEY = "sys_info"


def update_message_content(
    data: OpenAIRequest, sys_info_details: Dict[str, Any], role_data: str
) -> None:
    is_first_message = len(data.messages) == 2
    if role_data:
        data.messages[0]["content"] += role_data
    if is_first_message and sys_info_details:
        sys_info_content = f"\nHere is information about my computer:\n \
        {SYS_INFO_KEY}: {sys_info_details}\n"
        data.messages[0]["content"] += sys_info_content


async def call_openai_api(openai_request: OpenAIRequest):
    sys_info = SystemInfo.get_sys_info(openai_request)
    role = SystemRole.get_role(openai_request)
    update_message_content(openai_request, sys_info, role)
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo-preview", messages=openai_request.messages
        )
        return response

    except Exception as e:
        HandleOpenAICallFailures(e)


def HandleOpenAICallFailures(e: Exception):
    if isinstance(e, openai.BadRequestError):
        raise HTTPException(
            500, "OpenAI Request denied due to bad request: {}".format(e.response)
        )
    elif isinstance(e, openai.AuthenticationError):
        raise HTTPException(
            500,
            "OpenAI Request denied due to authentication issue: {}".format(e.response),
        )
    elif isinstance(e, openai.PermissionDeniedError):
        raise HTTPException(
            500, "OpenAI Request denied due to permission denied: {}".format(e.response)
        )
    elif isinstance(e, openai.NotFoundError):
        raise HTTPException(
            500,
            "OpenAI Request denied due to resource not found: {}".format(e.response),
        )
    elif isinstance(e, openai.UnprocessableEntityError):
        raise HTTPException(
            522,
            "OpenAI Request denied due to unprocessable entity: {}".format(e.response),
        )
    elif isinstance(e, openai.RateLimitError):
        raise HTTPException(
            529,
            "OpenAI Request denied due to hitting rate limit: {}".format(e.response),
        )
    elif isinstance(e, openai.APIConnectionError):
        raise HTTPException(
            500, "The OpenAI server could not be reached: {}".format(e.__cause__)
        )
    elif isinstance(e, openai.InternalServerError):
        raise HTTPException(
            502, "The OpenAI server had an internal error: {}".format(e.__cause__)
        )
    else:
        raise e  # Re-raise the exception if it's not one of the known types


@app.post("/ask")
async def ask_openai(request: OpenAIRequest):
    try:
        response = await call_openai_api(request)
        return response
    except HTTPException as http_exc:
        raise http_exc
