@echo off
echo [1/3] uv 설치 확인 중...
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo uv가 없습니다. 설치 중...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo uv 설치 완료. 터미널을 재시작 후 다시 run.bat를 실행하세요.
    pause
    exit /b
)

echo [2/3] 의존성 설치 중...
uv sync

echo [3/3] 앱 실행 중...
uv run streamlit run app.py
