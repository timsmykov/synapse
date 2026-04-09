FROM python:3.12-slim

WORKDIR /workspace

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libgl1 \
      libglib2.0-0 \
      libice6 \
      libsm6 \
      libx11-6 \
      libxcb1 \
      libxext6 && \
    rm -rf /var/lib/apt/lists/*

ARG SYNAPSE_INSTALL_EXTRAS=""
ARG SYNAPSE_PIP_EXTRA_INDEX_URL=""

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip && \
    if [ -n "$SYNAPSE_INSTALL_EXTRAS" ]; then \
      PIP_EXTRA_INDEX_URL="$SYNAPSE_PIP_EXTRA_INDEX_URL" pip install --no-cache-dir -e ".[${SYNAPSE_INSTALL_EXTRAS}]"; \
    else \
      PIP_EXTRA_INDEX_URL="$SYNAPSE_PIP_EXTRA_INDEX_URL" pip install --no-cache-dir -e .; \
    fi

CMD ["uvicorn", "synapse.server:app", "--host", "0.0.0.0", "--port", "8000"]
