# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base

# Prevents Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Required for matplotlib and other graphics libs
    libgl1 \
    libglib2.0-0t64 \
    libxcb1 \
    libxkbcommon0 \
    libdbus-1-3 \
    # Required for PySide6 (even in headless mode)
    libegl1 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    && rm -rf /var/lib/apt/lists/*

# Set Qt to run in offscreen mode (for matplotlib/PySide6)
ENV QT_QPA_PLATFORM=offscreen

# Install uv for fast Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application
COPY . .

# Install the project itself
RUN uv sync --frozen --no-dev

# Create directory for generated presentations
RUN mkdir -p /app/concluded_presentations/charts

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI application with uvicorn
CMD ["uv", "run", "uvicorn", "main:api", "--host", "0.0.0.0", "--port", "8000"]
