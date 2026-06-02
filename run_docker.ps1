# Build and run the Docker Compose stack for AI Money Mentor
# Usage: In PowerShell: .\run_docker.ps1

# Ensure .env exists
if (-Not (Test-Path .env)) {
  Write-Host ".env not found. Copy .env.example to .env and edit values before running." -ForegroundColor Yellow
  exit 1
}

# Build and start containers
docker-compose up --build -d

Write-Host "Containers started. API should be available at http://localhost:8000" -ForegroundColor Green
