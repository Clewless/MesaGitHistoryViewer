@echo off
echo Installing dev tools...
pip install -r requirements-dev.txt

echo.
echo Running Ruff (Format)...
ruff format .

echo.
echo Running Ruff (Lint)...
ruff check . --fix

echo.
echo Running Bandit (Security Scan)...
bandit -r .

echo.
echo Running Mypy (Type Check)...
mypy mesa_viewer.py

echo.
echo Running Pytest (with Coverage and Timeout)...
pytest --cov=mesa_viewer --cov-report=term-missing --timeout=300 tests/ -v

echo.
echo Check complete.
pause
