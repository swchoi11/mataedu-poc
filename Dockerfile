# Python 3.12-slim 이미지를 기반으로 합니다.
FROM python:3.12-slim

# 작업 디렉토리를 /app으로 설정합니다.
WORKDIR /app

# pyproject.toml과 uv.lock 파일을 복사합니다.
COPY pyproject.toml uv.lock ./

# uv를 설치하고 의존성을 설치합니다.
RUN pip install uv && uv sync

# 나머지 애플리케이션 코드를 복사합니다.
COPY . .

# core.py를 실행하는 명령어를 설정합니다.
CMD ["uv", "run", "python", "core.py"]
