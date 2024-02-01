# Bungo Web Server
### What is it?
Bungo web server is our python FastAPI based web API that allows for fast querying of OpenAI's public APIs to be able to quickly query for anything from our Bungo client.

### How do I run it?
Right now my flow is as follows:
1. Add your OpenAI secret key in the .env file (it should look like OPENAI_API_KEY=sk-ABCD...., you can get yours here, it is very cheap, I have only spent $.25 after using it for a week and a half pretty constantly.
https://platform.openai.com/api-keys. This step is temporary until we move server auth out of the container.
2. Once this is done, from the root of the project directory, all you need to do is run docker build to build the image, then docker run to run the container

```
docker build -t bungo-web-server .
docker run -d --name bungo-web-server-container -p 80:80 bungo-web-server
```

3. Profit! now you can run POST requests to the service and get responses back

## Example request:
```
curl -X 'POST' \
  'http://127.0.0.1:80/ask' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Hello, who won the world series in 2020?"
    }
  ]
}'
```
## Example request with request_context:
```
curl -X 'POST' \
  'http://127.0.0.1:80/ask' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "What is my OS and how can I list all the files in my home dir?"
    }
  ],
  "request_context": {
    "sys_info": {
      "hostname": "DevBox",
      "os": "Linux",
      "shell": "bash",
      "arch": "x64",
      "release": "6.5.0-15-generic",
      "type": "Linux",
      "version": "#15~22.04.1-Ubuntu SMP PREEMPT_DYNAMIC Fri Jan 12 18:54:30 UTC 2",
      "nullPath": "/dev/null",
      "homedir": "/home/dylan",
      "tempdir": "/tmp",
      "freeMemory": 1598173184,
      "totalMemory": 8118837248,
      "lineEnding": "\n"
    },
    "role_key": "1"
  }
}'
```
## Example response:
```
{
  "id": "chatcmpl-8lZFuQfRPqpLa7EU0lCzjsytGSFLW",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "message": {
        "content": "The Los Angeles Dodgers won the World Series in 2020. They defeated the Tampa Bay Rays in six games to capture their first championship since 1988.",
        "role": "assistant",
        "function_call": null,
        "tool_calls": null
      }
    }
  ],
  "created": 1706347630,
  "model": "gpt-4-0125-preview",
  "object": "chat.completion",
  "system_fingerprint": "fp_376b7f78b9",
  "usage": {
    "completion_tokens": 32,
    "prompt_tokens": 29,
    "total_tokens": 61
  }
}
```
## How do I test it?
This is done in a very un-dockerized setup... i need to figure out how to make this part of the normal docker flow... Someone teach me how to CI/CD with containers :D

1. Since it is not dockerized at all, you will need to pip install the requirements from the root of the project directory
```
pip install -r requirements.txt
```

2. Right now the process to run the test suite is to navigate to the root of the project directory and run the following command (-v just makes it verbose)
```
pytest -v
```
With any luck you will see the tests run
```
====================== test session starts =======================
platform darwin -- Python 3.10.9, pytest-7.4.4, pluggy-1.4.0 -- /Users/tomshaffer/bungo-web-server/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/tomshaffer/bungo-web-server
plugins: asyncio-0.23.3, anyio-4.2.0
asyncio: mode=strict
collected 9 items                                                

test/main_test.py::test_ask_openai__success__return_json PASSED [ 11%]
test/main_test.py::test_ask_openai__openai_server_issue__502_inform_client PASSED [ 22%]
test/main_test.py::test_ask_openai__bungo_server_issue__500_inform_client PASSED [ 33%]
test/main_test.py::test_ask_openai__malformed_openai_request__500_inform_client PASSED [ 44%]
test/main_test.py::test_ask_openai__malformed_openai_auth__500_inform_client PASSED [ 55%]
test/main_test.py::test_ask_openai__openai_denies_access__500_inform_client PASSED [ 66%]
test/main_test.py::test_ask_openai__no_openai_resource__500_inform_client PASSED [ 77%]
test/main_test.py::test_ask_openai__openai_reports_unprocessible_entity__500_inform_client PASSED [ 88%]
test/main_test.py::test_ask_openai__openai_reports_rate_limit_reached__529_inform_client PASSED [100%]

======================= 9 passed in 0.35s ========================
```

# RULES FOR WORKING WITH THIS REPO
We follow Trunk-Based development where we merge into main with small branches
1. You must work on a feature not NOT ON MAIN.
2. You must open a PR with your feature branch, and get a green build + 1 PR approval from someone else.
3. You can then merge your branch into main after there are no merge conflicts. (Merge and Squash Commits)
