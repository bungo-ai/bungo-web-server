from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
from pathlib import Path
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
    if(is_first_message and data.request_context and sys_info_key in data.request_context.keys()):
        sys_info_details = data.request_context.get(sys_info_key, "Information not available")
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
    
    except openai.BadRequestError as e:
        raise HTTPException(500,f"OpenAI Request denied due to bad request: {e.response}")
    except openai.AuthenticationError as e:
        raise HTTPException(500,f"OpenAI Request denied due to authentication issue: {e.response}")
    except openai.PermissionDeniedError as e:
        raise HTTPException(500,f"OpenAI Request denied due to permission denied: {e.response}")
    except openai.NotFoundError as e:
        raise HTTPException(500,f"OpenAI Request denied due to resource not found: {e.response}")
    except openai.UnprocessableEntityError as e:
        raise HTTPException(522,f"OpenAI Request denied due to unprocessible entity: {e.response}")
    except openai.RateLimitError as e:
        raise HTTPException(529,f"OpenAI Request denied due to hitting rate limit: {e.response}")
    
    except openai.APIConnectionError as e:
        raise HTTPException(500,f"The OpenAI server could not be reached: {e.__cause__}")
    except openai.InternalServerError as e:
        raise HTTPException(502,f"The OpenAI server had an internal error: {e.__cause__}")

@app.post("/ask")
async def ask_openai(request: OpenAIRequest):
    try:
        response = await call_openai_api(request)
        return response
    except HTTPException as http_exc:
        raise http_exc