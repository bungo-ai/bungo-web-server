from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()


class OpenAIRequest(BaseModel):
    messages: list
    request_context: Optional[Dict[str, Any]] = None


app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY not found in environment variables")

openai.api_key = OPENAI_API_KEY


async def call_openai_api(data: OpenAIRequest):
    is_first_message = len(data.messages) == 2

    sys_info_key = "sys_info"
    context_has_sys_info = (data.request_context and
                            sys_info_key in data.request_context.keys())

    if (is_first_message and context_has_sys_info):
        sys_info_details = data.request_context[sys_info_key]
        data.messages[0]['content'] += f"""
        Here is information about my computer:\n
        {sys_info_key}: {sys_info_details}
        """
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=data.messages
        )
        return response

    except Exception as e:
        HandleOpenAICallFailures(e)


def HandleOpenAICallFailures(e: Exception):
    if isinstance(e, openai.BadRequestError):
        raise HTTPException(
            500,
            "OpenAI Request denied due to bad request: {}"
            .format(e.response)
        )
    elif isinstance(e, openai.AuthenticationError):
        raise HTTPException(
            500,
            "OpenAI Request denied due to authentication issue: {}"
            .format(e.response)
        )
    elif isinstance(e, openai.PermissionDeniedError):
        raise HTTPException(
            500,
            "OpenAI Request denied due to permission denied: {}"
            .format(e.response)
        )
    elif isinstance(e, openai.NotFoundError):
        raise HTTPException(
            500,
            "OpenAI Request denied due to resource not found: {}"
            .format(e.response)
        )
    elif isinstance(e, openai.UnprocessableEntityError):
        raise HTTPException(
            522,
            "OpenAI Request denied due to unprocessable entity: {}"
            .format(e.response)
        )
    elif isinstance(e, openai.RateLimitError):
        raise HTTPException(
            529,
            "OpenAI Request denied due to hitting rate limit: {}"
            .format(e.response)
        )
    elif isinstance(e, openai.APIConnectionError):
        raise HTTPException(
            500,
            "The OpenAI server could not be reached: {}"
            .format(e.__cause__)
        )
    elif isinstance(e, openai.InternalServerError):
        raise HTTPException(
            502,
            "The OpenAI server had an internal error: {}"
            .format(e.__cause__)
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
