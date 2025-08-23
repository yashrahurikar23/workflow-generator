FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy pyproject.toml and uv.lock if they exist
COPY pyproject.toml ./
COPY uv.lock* ./

# Install dependencies
RUN uv sync --no-dev

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8003

# Run the application
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
