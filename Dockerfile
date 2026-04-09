FROM python:3.12-slim

WORKDIR /workspace

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG SYNAPSE_INSTALL_EXTRAS=""

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip && \
    if [ -n "$SYNAPSE_INSTALL_EXTRAS" ]; then \
      pip install -e ".[${SYNAPSE_INSTALL_EXTRAS}]"; \
    else \
      pip install -e .; \
    fi

CMD ["uvicorn", "synapse.server:app", "--host", "0.0.0.0", "--port", "8000"]
