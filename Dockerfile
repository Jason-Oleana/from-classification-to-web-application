# Get image
FROM python:3.7

ENV PYTHONUNBUFFERED 1

# working directory
WORKDIR /app

# Copy current web app directory to working directory
COPY ./app /app

# Copy Fastapi .py file to working directory
COPY ./main.py /app

# Copy requirements.txt to working directory
COPY requirements.txt /app

# Install environment dependencies
RUN pip install --upgrade pip \
  && pip install -r requirements.txt
