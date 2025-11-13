FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv && uv sync

COPY . .

CMD ["uv", "run","streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
