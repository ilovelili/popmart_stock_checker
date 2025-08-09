# Use Playwright's official Python image (includes Chromium + deps)
FROM mcr.microsoft.com/playwright/python:latest

# Optional: keep Python snappy and logs unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv (fast Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv

# Copy only project metadata first for better layer caching
COPY pyproject.toml uv.lock* ./

# Install deps (no project code yet, so this layer is cached until deps change)
RUN uv sync --frozen || uv sync

# Copy the app code
COPY main.py ./

# (Normally browsers are preinstalled in this base image, but this is harmless)
RUN uv run playwright install chromium

# Default command (override URL via `-e URL=...` or arguments)
ENV URL=https://www.popmart.com/jp/products/3884
CMD ["uv", "run", "python", "main.py", "$URL"]
