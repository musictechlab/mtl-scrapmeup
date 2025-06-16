# Use Python 3.12 as specified in pyproject.toml
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry and add it to PATH
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VERSION=1.7.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION

# Copy pyproject.toml and poetry.lock first
COPY pyproject.toml ./
COPY poetry.lock ./

# Install dependencies
RUN poetry install --no-root

# Copy the rest of the application
COPY . .

# Install the project itself
RUN poetry install --only-root

# Expose the port Streamlit runs on
EXPOSE 8502

# Add healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health || exit 1

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the Streamlit app
ENTRYPOINT ["streamlit", "run", "mtl_scrapmeup.py", "--server.port=8502", "--server.address=0.0.0.0"] 