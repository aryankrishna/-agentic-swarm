#!/bin/bash
echo "🌐 Starting Agentic Swarm Infrastructure..."

# Step 1: Ensure Docker is up
open -a Docker
echo "🐳 Waiting for Docker to start..."
sleep 5

# Step 2: Build and start containers
cd infra
docker compose up -d --build
echo "✅ Containers are up!"

# Step 3: Display running containers
docker ps | grep "infra-graph-1\|agentic-app"

# Step 4: Wait a moment to ensure app is ready
sleep 5

# Step 5: Start Cloudflare Tunnel
echo "☁️  Launching Cloudflare Tunnel for Streamlit..."
cloudflared tunnel --url http://localhost:8501
