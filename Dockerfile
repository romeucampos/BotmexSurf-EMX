FROM python:3.7.4-slim-buster

COPY . .

RUN apt-get update && apt-get install -y git && pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "run.py"]
