FROM python:3.9-alpine

WORKDIR /app

RUN apk add --update --no-cache g++ gcc libxslt-dev 

COPY requirements.txt requirements.txt

RUN pip3.9 install -r requirements.txt

RUN pip3.9 install uvicorn

COPY . . 

CMD ["uvicorn", "main:app", "--reload","--host","0.0.0.0"]

EXPOSE 8000

