FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y netcat && \
    apt-get clean && rm -rf /var/cache/apt/*
RUN pip install -r requirements.txt
EXPOSE 9091