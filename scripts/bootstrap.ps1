$ErrorActionPreference = "Stop"

python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements\dev.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue
Write-Host "Environment bootstrapped. Next steps:"
Write-Host "  1) update .env with your local values"
Write-Host "  2) docker compose up -d postgres redis"
Write-Host "  3) python manage.py migrate"
Write-Host "  4) python manage.py runserver 0.0.0.0:8000"
