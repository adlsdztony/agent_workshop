# syntax=docker/dockerfile:1.6

FROM python:3.11-slim as base

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WORKSHOP_HOME=/workspace \
    PATH="/root/.local/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    build-essential \
    tini \
    libssl-dev \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR ${WORKSHOP_HOME}

COPY pyproject.toml requirements.txt ./
COPY README.md .

COPY stages ./stages

RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Create a non-root user for day-to-day workshop commands.
RUN useradd -ms /bin/bash workshop \
    && chown -R workshop:workshop ${WORKSHOP_HOME}

USER workshop
WORKDIR ${WORKSHOP_HOME}

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash"]
