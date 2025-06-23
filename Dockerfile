FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY . .

ARG GIT_COMMIT=unknown
RUN echo ${GIT_COMMIT} > .git_commit

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
EXPOSE 7923

ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV FASTAPI_DOMAIN=http://127.0.0.1
ENV FASTAPI_PORT=7923

CMD ["python", "app.py"]