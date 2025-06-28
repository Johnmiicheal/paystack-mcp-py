# 🚀 Deployment Guide: Paystack MCP Server

## Overview

This guide covers multiple deployment strategies for your Paystack MCP server, from local development to production-ready deployments.

## 🏗️ Architecture Options

### Option 1: Local Development
```
[Vercel AI Chatbot] ──► [Local Python MCP Server] ──► [Paystack API]
```

### Option 2: Containerized Deployment  
```
[Vercel AI Chatbot] ──► [Docker Container] ──► [Paystack API]
```

### Option 3: Cloud Function
```
[Vercel AI Chatbot] ──► [Cloud Run/Lambda] ──► [Paystack API]
```

### Option 4: Always-On Server
```
[Vercel AI Chatbot] ──► [VPS/Dedicated Server] ──► [Paystack API]
```

---

## 📦 Option 1: Local Development

**Best for**: Development, testing, local demos

### Setup Steps:

1. **Activate your environment:**
```bash
source venv/bin/activate
```

2. **Set environment variables:**
```bash
export PAYSTACK_SECRET_KEY="sk_test_your_key_here"
export PAYSTACK_ENVIRONMENT="test"
```

3. **Run the server:**
```bash
python -m paystack_mcp.server
```

4. **Connect from your Vercel app:**
```javascript
// In your Next.js API route
const transport = new StdioClientTransport({
    command: "python",
    args: ["-m", "paystack_mcp.server"],
    env: {
        PAYSTACK_SECRET_KEY: process.env.PAYSTACK_SECRET_KEY
    }
});
```

---

## 🐳 Option 2: Docker Deployment

**Best for**: Consistent environments, easy scaling, cloud deployment

### Create Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY paystack_mcp/ ./paystack_mcp/
COPY pyproject.toml .

# Install the package
RUN pip install -e .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port (for health checks)
EXPOSE 8000

# Run the MCP server
CMD ["python", "-m", "paystack_mcp.server"]
```

### Build and run:

```bash
# Build the image
docker build -t paystack-mcp .

# Run with environment variables
docker run -d \
  --name paystack-mcp-server \
  -e PAYSTACK_SECRET_KEY="sk_test_your_key" \
  -e PAYSTACK_ENVIRONMENT="test" \
  paystack-mcp

# Test the container
docker exec paystack-mcp-server python -c "import paystack_mcp; print('✅ Working')"
```

### Docker Compose for development:

```yaml
# docker-compose.yml
version: '3.8'

services:
  paystack-mcp:
    build: .
    environment:
      - PAYSTACK_SECRET_KEY=${PAYSTACK_SECRET_KEY}
      - PAYSTACK_ENVIRONMENT=test
    volumes:
      - ./paystack_mcp:/app/paystack_mcp
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import paystack_mcp"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Redis for caching
  redis:
    image: redis:7-alpine
    restart: unless-stopped
```

---

## ☁️ Option 3: Google Cloud Run

**Best for**: Serverless, pay-per-use, automatic scaling

### Setup Cloud Run deployment:

1. **Create cloudbuild.yaml:**
```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/paystack-mcp', '.']
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/paystack-mcp']
  # Deploy container image to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
    - 'run'
    - 'deploy'
    - 'paystack-mcp'
    - '--image'
    - 'gcr.io/$PROJECT_ID/paystack-mcp'
    - '--region'
    - 'us-central1'
    - '--platform'
    - 'managed'
    - '--allow-unauthenticated'
images:
  - 'gcr.io/$PROJECT_ID/paystack-mcp'
```

2. **Deploy:**
```bash
gcloud builds submit --config cloudbuild.yaml
```

3. **Set environment variables:**
```bash
gcloud run services update paystack-mcp \
  --set-env-vars PAYSTACK_SECRET_KEY="sk_live_your_key" \
  --set-env-vars PAYSTACK_ENVIRONMENT="live" \
  --region us-central1
```

### Connect from Vercel:

```javascript
// For Cloud Run, you'll need HTTP communication instead of stdio
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SseClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";

const transport = new SseClientTransport(
    new URL("https://paystack-mcp-xxxxxx-uc.a.run.app/sse")
);
```

---

## 🖥️ Option 4: VPS/Dedicated Server

**Best for**: High-traffic applications, full control, persistent connections

### Setup on Ubuntu/Debian:

1. **Install dependencies:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx supervisor
```

2. **Clone and setup:**
```bash
git clone <your-repo>
cd paystack-mcp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Create systemd service:**
```ini
# /etc/systemd/system/paystack-mcp.service
[Unit]
Description=Paystack MCP Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/paystack-mcp
Environment=PATH=/path/to/paystack-mcp/venv/bin
Environment=PAYSTACK_SECRET_KEY=sk_live_your_key
Environment=PAYSTACK_ENVIRONMENT=live
ExecStart=/path/to/paystack-mcp/venv/bin/python -m paystack_mcp.server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

4. **Enable and start:**
```bash
sudo systemctl enable paystack-mcp
sudo systemctl start paystack-mcp
sudo systemctl status paystack-mcp
```

---

## 🔒 Production Security Checklist

### Environment Variables:
- [ ] Use real Paystack live keys (sk_live_...)
- [ ] Set `PAYSTACK_ENVIRONMENT=live`
- [ ] Store secrets in secure secret management (AWS Secrets Manager, etc.)

### Network Security:
- [ ] Use HTTPS/TLS for all connections
- [ ] Implement rate limiting
- [ ] Whitelist IP addresses if possible
- [ ] Use VPN for sensitive environments

### Code Security:
- [ ] Input validation on all parameters
- [ ] Proper error handling (don't leak sensitive info)
- [ ] Logging and monitoring
- [ ] Regular dependency updates

### Monitoring:
```python
# Add to your server.py for production monitoring
import logging
import time
from datetime import datetime

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add request timing
@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]):
    start_time = time.time()
    logger.info(f"Tool called: {name}")
    
    try:
        result = await original_handle_call_tool(name, arguments)
        duration = time.time() - start_time
        logger.info(f"Tool {name} completed in {duration:.2f}s")
        return result
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Tool {name} failed after {duration:.2f}s: {str(e)}")
        raise
```

---

## 🚀 Vercel Integration Patterns

### Pattern 1: Direct stdio (Development)
```javascript
// Good for: Local development, testing
const transport = new StdioClientTransport({
    command: "python",
    args: ["-m", "paystack_mcp.server"]
});
```

### Pattern 2: HTTP Proxy (Production)
```javascript
// Good for: Production, scalability
// Create API route: /api/mcp-proxy
export async function POST(request) {
    const { tool, arguments } = await request.json();
    
    // Forward to your deployed MCP server
    const result = await fetch('https://your-mcp-server.com/tools', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool, arguments })
    });
    
    return result;
}
```

### Pattern 3: Serverless Functions
```javascript
// Good for: Event-driven, cost optimization
// Vercel function that spawns MCP server on-demand
export default async function handler(req, res) {
    const { spawn } = await import('child_process');
    
    const mcpServer = spawn('python', ['-m', 'paystack_mcp.server'], {
        env: { ...process.env, PAYSTACK_SECRET_KEY: process.env.PAYSTACK_SECRET_KEY }
    });
    
    // Handle communication...
}
```

---

## 📊 Performance Optimization

### Connection Pooling:
```python
# In client.py - reuse HTTP connections
class PaystackClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
            timeout=httpx.Timeout(30.0)
        )
```

### Caching:
```python
# Add Redis caching for bank lists, etc.
import aioredis

class PaystackClient:
    async def list_banks(self, country: str = "nigeria"):
        cache_key = f"banks:{country}"
        
        # Try cache first
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        
        # Fetch from API
        result = await self._make_request("GET", "/bank", params={"country": country})
        
        # Cache for 1 hour
        if self.redis:
            await self.redis.setex(cache_key, 3600, json.dumps(result))
        
        return result
```

### Error Recovery:
```python
# Implement retry logic
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def _make_request_with_retry(self, method, endpoint, **kwargs):
    return await self._make_request(method, endpoint, **kwargs)
```

---

## 🔍 Debugging & Troubleshooting

### Common Issues:

1. **"Command not found: python"**
   ```bash
   # Use absolute path
   /usr/bin/python3 -m paystack_mcp.server
   ```

2. **Environment variables not loaded**
   ```bash
   # Explicitly load .env
   export $(cat .env | xargs)
   ```

3. **Port conflicts**
   ```bash
   # Check what's using ports
   lsof -i :8000
   ```

4. **Memory issues**
   ```bash
   # Monitor memory usage
   ps aux | grep python
   ```

### Debug logging:
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add to your server
logger = logging.getLogger(__name__)
logger.debug(f"Received tool call: {name} with args: {arguments}")
```

---

This deployment guide should give you everything you need to get your Paystack MCP server running in any environment! Choose the option that best fits your use case and scale from there. 