# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Set the working directory to the project root
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy the project configuration files from the build context (root)
COPY pyproject.toml uv.lock ./

# Install dependencies from the lock file
RUN uv sync --frozen --no-install-project

# Copy the rest of the application
COPY . .

# Run the application
# --reload enables hot reloading for development
# --host 0.0.0.0 makes the server accessible outside the container
CMD ["uv", "run", "uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
