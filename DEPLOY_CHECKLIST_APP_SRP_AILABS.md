# SRP Marketing OS — Production Deployment Checklist
## Target: https://app.srpailabs.com (Hetzner srp-ai-server)

---

## 1. FILES CHANGED IN THIS COMMIT

| File | Change |
|------|--------|
| `nginx/nginx.conf` | `server_name` set to `app.srpailabs.com` in both HTTP and HTTPS blocks |
| `backend/app/config.py` | Added `https://app.srpailabs.com` to `ALLOWED_ORIGINS`; updated `APP_URL` |
| `.env.production.template` | Updated `ALLOWED_HOSTS`, `CORS_ORIGINS`, `APP_URL` to `app.srpailabs.com` |
| `docker-compose.yml` | Added `certbot_webroot` volume to nginx and volumes list |
| `frontend/.env.production` | Created — sets `VITE_API_URL=/api/v1` (relative, nginx proxies) |
| `README.md` | Updated all deployment placeholders with real domain/IP/repo |
| `DEPLOY_CHECKLIST_APP_SRP_AILABS.md` | This file |

---

## 2. CONFIGURED DOMAIN

```
https://app.srpailabs.com
```

- Nginx `server_name`: `app.srpailabs.com`
- Backend `ALLOWED_ORIGINS`: includes `https://app.srpailabs.com`
- Frontend API: uses `/api/v1` (relative path, proxied by nginx — no hardcoded domain)

---

## 3. CLOUDFLARE DNS RECORD TO ADD

Log in to Cloudflare → Select your domain `srpailabs.com` → DNS → Add record:

| Type | Name | Content | TTL | Proxy |
|------|------|---------|-----|-------|
| **A** | **app** | **5.223.67.236** | Auto | DNS only (grey cloud) during SSL setup |

> After SSL is working, you can enable Cloudflare Proxy (orange cloud) if desired.

---

## 4. NGINX SERVER_NAME CONFIGURED

```nginx
# HTTP redirect block
server {
    listen 80;
    server_name app.srpailabs.com;
    ...
}

# HTTPS main block
server {
    listen 443 ssl http2;
    server_name app.srpailabs.com;
    ...
}
```

File: `nginx/nginx.conf`

---

## 5. EXACT COMMANDS TO RUN ON SERVER AFTER GIT PULL

### 5.1 — Connect to Server
```bash
ssh root@5.223.67.236
```

### 5.2 — First Time Setup (only run once)
```bash
# Update and install Docker
apt update && apt upgrade -y
apt install -y git curl wget ufw fail2ban

# Install Docker Engine
curl -fsSL https://get.docker.com | sh
apt install -y docker-compose-plugin

# Configure firewall
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Start Docker
systemctl start docker
systemctl enable docker
```

### 5.3 — Clone Repository (first time only)
```bash
cd /root
git clone https://github.com/shashankpasikanti91-blip/srp-marketing-os.git
cd srp-marketing-os
```

### 5.4 — Create Production .env (first time only)
```bash
cd /root/srp-marketing-os

# Copy template and edit
cp .env.production.template .env
nano .env
```

**Minimum .env values required:**
```env
POSTGRES_USER=srp
POSTGRES_PASSWORD=YourStrongPasswordHere
POSTGRES_DB=srp_marketing
DATABASE_URL=postgresql+asyncpg://srp:YourStrongPasswordHere@db:5432/srp_marketing

REDIS_PASSWORD=YourRedisPassword
REDIS_URL=redis://:YourRedisPassword@redis:6379/0

SECRET_KEY=<run: openssl rand -hex 32>
ACCESS_TOKEN_EXPIRE_MINUTES=60

ENVIRONMENT=production
DEBUG=false
APP_URL=https://app.srpailabs.com
ALLOWED_ORIGINS=https://app.srpailabs.com

OPENAI_API_KEY=sk-proj-YOUR_OPENAI_KEY
# Optional:
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY
OPENROUTER_API_KEY=sk-or-YOUR_KEY
```

### 5.5 — SSL Certificate (first time — before starting nginx with HTTPS)

> Make sure Cloudflare DNS record points to `5.223.67.236` BEFORE running this.

```bash
# Install certbot
apt install -y certbot

# Stop nginx if running
docker compose stop nginx 2>/dev/null || true

# Get certificate
certbot certonly --standalone \
  -d app.srpailabs.com \
  --email admin@srpailabs.com \
  --agree-tos \
  --non-interactive

# Copy certs to nginx/ssl (mounted by docker-compose)
mkdir -p /root/srp-marketing-os/nginx/ssl
cp /etc/letsencrypt/live/app.srpailabs.com/fullchain.pem /root/srp-marketing-os/nginx/ssl/
cp /etc/letsencrypt/live/app.srpailabs.com/privkey.pem /root/srp-marketing-os/nginx/ssl/

# Auto-renew cron
echo "0 12 * * * root certbot renew --quiet && cp /etc/letsencrypt/live/app.srpailabs.com/fullchain.pem /root/srp-marketing-os/nginx/ssl/ && cp /etc/letsencrypt/live/app.srpailabs.com/privkey.pem /root/srp-marketing-os/nginx/ssl/ && docker compose -f /root/srp-marketing-os/docker-compose.yml restart nginx" >> /etc/crontab
```

### 5.6 — Build & Start All Services
```bash
cd /root/srp-marketing-os

# Build all images and start (first time takes 3-5 min)
docker compose up -d --build

# Watch startup logs
docker compose logs -f
# Press Ctrl+C when all services are up
```

### 5.7 — Run Migrations & Seed Data
```bash
cd /root/srp-marketing-os

# Run Alembic migrations (creates all tables)
docker compose exec backend alembic upgrade head

# Seed demo accounts
docker compose exec backend python seed_demo.py
docker compose exec backend python seed_bunty.py

# Verify tables
docker compose exec db psql -U srp -d srp_marketing -c "\dt"

# Verify tenants
docker compose exec db psql -U srp -d srp_marketing -c "SELECT email, name FROM tenants;"
```

### 5.8 — Subsequent Deployments (after git push from dev machine)
```bash
cd /root/srp-marketing-os

# Pull latest code
git pull origin main

# Rebuild and restart updated services
docker compose up -d --build backend frontend

# Run any new migrations
docker compose exec backend alembic upgrade head

# Check status
docker compose ps
```

---

## 6. HOW TO VERIFY DEPLOYMENT

```bash
# 1. All containers running?
docker compose ps
# Expected: backend, frontend, db, redis, nginx — all "Up"

# 2. Backend health check
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# 3. From your machine — check via domain
curl -I https://app.srpailabs.com/health
# Expected: HTTP/2 200

# 4. API docs accessible
curl -I https://app.srpailabs.com/docs
# Expected: HTTP/2 200

# 5. Frontend loads
curl -sI https://app.srpailabs.com/ | head -5
# Expected: HTTP/2 200, content-type: text/html
```

**Verification URLs (open in browser):**
- App: https://app.srpailabs.com
- API Health: https://app.srpailabs.com/health
- API Docs (Swagger): https://app.srpailabs.com/docs
- API ReDoc: https://app.srpailabs.com/redoc

**Demo Login:**
- Email: `demo@srp.ai` | Password: `Demo@12345`
- Email: `bunty@srp.ai` | Password: `Bunty@12345`

---

## 7. TROUBLESHOOTING

### App does not open / ERR_CONNECTION_REFUSED
```bash
# Check if containers are running
docker compose ps

# Check nginx logs
docker compose logs nginx --tail=50

# Check if port 80/443 is open
ufw status
netstat -tlnp | grep -E '80|443'
```

### 502 Bad Gateway
```bash
# Backend not healthy — check backend logs
docker compose logs backend --tail=50

# Check backend health directly
docker compose exec backend curl localhost:8000/health

# Restart backend
docker compose restart backend
```

### SSL / HTTPS not working
```bash
# Verify cert files exist
ls -la /root/srp-marketing-os/nginx/ssl/
# Must have: fullchain.pem  privkey.pem

# Re-copy from letsencrypt
cp /etc/letsencrypt/live/app.srpailabs.com/fullchain.pem /root/srp-marketing-os/nginx/ssl/
cp /etc/letsencrypt/live/app.srpailabs.com/privkey.pem /root/srp-marketing-os/nginx/ssl/

# Restart nginx
docker compose restart nginx
```

### DNS not resolving / domain not reachable
```bash
# From your local machine:
nslookup app.srpailabs.com
# Must return: 5.223.67.236

# Also verify from server:
curl -I http://app.srpailabs.com
```

### Database migration errors
```bash
# Check migration status
docker compose exec backend alembic current

# Force re-run migrations
docker compose exec backend alembic upgrade head

# Check DB connection
docker compose exec backend python check_db.py
```

### Login not working / 401 errors
```bash
# Verify SECRET_KEY is set in .env
grep SECRET_KEY .env

# Check backend CORS config
docker compose exec backend python -c "from app.config import settings; print(settings.ALLOWED_ORIGINS)"
# Must include https://app.srpailabs.com

# Restart backend to reload config
docker compose restart backend
```

### Docker build fails
```bash
# Check disk space
df -h

# Clean old images if disk full
docker system prune -f

# Rebuild specific service
docker compose build --no-cache backend
docker compose up -d backend
```

---

## 8. SERVER & DEPLOYMENT REFERENCE

| Item | Value |
|------|-------|
| Provider | Hetzner |
| Server Name | srp-ai-server |
| Server IP | 5.223.67.236 |
| Domain | app.srpailabs.com |
| GitHub Repo | shashankpasikanti91-blip |
| OS | Ubuntu 22.04 LTS |
| Stack | Docker Compose (nginx + FastAPI + React + PostgreSQL + Redis) |
| SSL | Let's Encrypt via Certbot |
| Nginx `server_name` | `app.srpailabs.com` |

---

*Generated: 2026-03-13*
