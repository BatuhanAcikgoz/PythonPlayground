FROM python:3.10-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Clone course repository (adjust if you want to do this at runtime instead)
RUN git clone https://github.com/msy-bilecik/ist204_2025 ./notebooks_repo || echo "Repository will be cloned at runtime"

EXPOSE 5000
EXPOSE 7923

# Use environment variables for configuration
ENV FLASK_APP=app.py
ENV SQLALCHEMY_DATABASE_URI=mysql+pymysql://user:password@db/python_platform

CMD ["python", "app.py"]