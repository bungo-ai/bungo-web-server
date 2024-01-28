FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

## THIS IS NOT A GOOD WAY TO HANDLE SECRETS IN DOCKER, FIX ASAP ##
COPY ./.env /code/.env
##################################################################

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]