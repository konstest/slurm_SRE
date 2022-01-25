FROM python:3.8-slim

RUN apt-get update && apt-get install -y wget curl && rm -rf /var/lib/apt/lists/* && apt-get clean
WORKDIR provider_api
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip && pip3 install -U -r requirements.txt

COPY src src/
COPY src/main.py main.py

CMD ["python3", "-u", "main.py"]
