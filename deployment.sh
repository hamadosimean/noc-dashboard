#! /bin/bash

echo "Starting deployment process..."

set -e

echo "Deploying at $(date)..."

docker compose down
docker compose  up --build -d