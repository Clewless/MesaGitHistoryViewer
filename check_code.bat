@echo off
echo Installing dev tools...
pip install -r requirements-dev.txt

echo.
echo Running Ruff (Lint & Format Check)...
ruff check .

echo.
echo Running Mypy (Type Check)...
mypy mesa_viewer.py

echo.
echo Running Pytest...
pytest tests/ -v

echo.
echo Check complete.
pause
