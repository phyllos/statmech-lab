# Build the locked Python environment separately from the runtime image.
FROM ghcr.io/astral-sh/uv:0.13.5 AS uv
FROM python:3.12-slim AS build
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1
COPY .python-version pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

FROM python:3.12-slim AS runtime
WORKDIR /app
RUN useradd --create-home --uid 10001 statmech
COPY --from=build /app/.venv /app/.venv
COPY app.py physics.py shared.py state.py i18n.py glossary.py interactions.py distribution_ui.py plot_theme.py ./
COPY labs/ ./labs/
COPY styles/ ./styles/
COPY .streamlit/config.toml ./.streamlit/config.toml
ENV PATH="/app/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER statmech
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3).read()"
ENTRYPOINT ["python", "-m", "streamlit", "run", "app.py"]
CMD ["--server.address=0.0.0.0", "--server.port=8501", "--server.fileWatcherType=none"]
