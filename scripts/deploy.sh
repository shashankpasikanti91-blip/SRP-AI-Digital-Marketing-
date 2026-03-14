#!/usr/bin/env bash
# =============================================================================
# SRP Marketing OS — Hetzner Server Deploy Script
# Usage:
#   First time:  bash deploy.sh --init
#   Updates:     bash deploy.sh
# =============================================================================
set -euo pipefail

REPO_URL="https://github.com/shashankpasikanti91-blip/SRP-AI-Digital-Marketing-.git"
APP_DIR="/opt/srp-marketing-os"
APP_SUB="ai-marketing-os"
DOMAIN="app.srpailabs.com"
SSL_DIR="${APP_DIR}/${APP_SUB}/nginx/ssl"
EMAIL="admin@srpailabs.com"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[$(date +%H:%M:%S)] $*${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $*${NC}"; }
die()  { echo -e "${RED}[ERROR] $*${NC}"; exit 1; }

# ── First-time init ──────────────────────────────────────────────────────────
init_server() {
    log "=== FIRST-TIME SERVER SETUP ==="

    # 1. System deps
    log "Installing system dependencies..."
    apt-get update -qq
    apt-get install -y -qq git curl certbot ufw fail2ban

    # 2. Docker
    if ! command -v docker &>/dev/null; then
        log "Installing Docker..."
        curl -fsSL https://get.docker.com | sh
        systemctl enable docker
        systemctl start docker
    fi
    if ! docker compose version &>/dev/null; then
        apt-get install -y -qq docker-compose-plugin
    fi

    # 3. Firewall
    log "Configuring firewall..."
    ufw allow OpenSSH
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable

    # 4. Clone or update repo
    if [ ! -d "${APP_DIR}" ]; then
        log "Cloning repository..."
        git clone "${REPO_URL}" "${APP_DIR}"
    else
        log "Repository already exists, pulling latest..."
        git -C "${APP_DIR}" pull origin main || git -C "${APP_DIR}" pull origin master
    fi

    cd "${APP_DIR}/${APP_SUB}"

    # 5. Create .env if missing
    if [ ! -f ".env" ]; then
        warn ".env not found — copying from template. EDIT IT BEFORE STARTING SERVICES."
        cp .env.production.template .env 2>/dev/null || cp .env.example .env 2>/dev/null || \
            die "No .env template found. Create .env manually."
        warn "→ Edit .env: nano .env"
        warn "→ Set POSTGRES_PASSWORD, REDIS_PASSWORD, SECRET_KEY, OPENAI_API_KEY"
        echo ""
        read -p "Press ENTER after editing .env to continue..." _
    fi

    # 6. SSL certificate
    obtain_ssl

    # 7. Start everything
    deploy
}

# ── Obtain SSL certificate ───────────────────────────────────────────────────
obtain_ssl() {
    cd "${APP_DIR}/${APP_SUB}"

    if [ -f "${SSL_DIR}/fullchain.pem" ] && [ -f "${SSL_DIR}/privkey.pem" ]; then
        log "SSL certificates already exist — skipping certbot."
        return
    fi

    log "Obtaining SSL certificate for ${DOMAIN}..."

    # Start nginx in HTTP-only mode to serve ACME challenges
    log "Starting HTTP-only nginx for ACME challenge..."
    docker compose -f docker-compose.yml run --rm -d \
        -p 80:80 \
        -v "$(pwd)/nginx/nginx-init.conf:/etc/nginx/nginx.conf:ro" \
        --name srp_nginx_init \
        nginx:1.27-alpine nginx -g "daemon off;" &>/dev/null || true

    sleep 3

    # Get cert via webroot (port 80 must be open)
    certbot certonly --standalone \
        -d "${DOMAIN}" \
        --non-interactive \
        --agree-tos \
        --email "${EMAIL}" \
        --preferred-challenges http \
        2>/dev/null || \
    certbot certonly --standalone \
        -d "${DOMAIN}" \
        --non-interactive \
        --agree-tos \
        --email "${EMAIL}"

    # Stop temp nginx
    docker stop srp_nginx_init &>/dev/null || true
    docker rm srp_nginx_init &>/dev/null || true

    # Copy certs to nginx/ssl volume
    log "Copying certificates to nginx/ssl..."
    mkdir -p "${SSL_DIR}"
    cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem "${SSL_DIR}/"
    cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem   "${SSL_DIR}/"
    chmod 600 "${SSL_DIR}/privkey.pem"

    # Set up auto-renew
    CRON_CMD="0 3 * * * certbot renew --quiet && cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem ${SSL_DIR}/ && cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem ${SSL_DIR}/ && docker compose -f ${APP_DIR}/${APP_SUB}/docker-compose.yml exec nginx nginx -s reload"
    (crontab -l 2>/dev/null; echo "${CRON_CMD}") | sort -u | crontab -
    log "SSL auto-renewal cron configured."
}

# ── Main deploy / update ─────────────────────────────────────────────────────
deploy() {
    cd "${APP_DIR}/${APP_SUB}"
    log "=== DEPLOYING SRP MARKETING OS ==="

    # Pull latest code
    log "Pulling latest code..."
    git pull origin main 2>/dev/null || git pull origin master

    # Build & start all services
    log "Building and starting all services..."
    docker compose up --build -d

    # Wait for backend health
    log "Waiting for backend to be healthy..."
    for i in $(seq 1 30); do
        if docker compose ps backend 2>/dev/null | grep -q "healthy"; then
            break
        fi
        sleep 5
    done

    # Run migrations
    log "Running database migrations..."
    docker compose exec backend alembic upgrade head

    # Seed data (idempotent — skips if already seeded)
    log "Seeding demo data..."
    docker compose exec backend python seed_demo.py        2>&1 | tail -3 || warn "seed_demo.py skipped (already seeded?)"
    docker compose exec backend python seed_bunty.py       2>&1 | tail -3 || warn "seed_bunty.py skipped (already seeded?)"
    docker compose exec backend python seed_global_demo.py 2>&1 | tail -3 || warn "seed_global_demo.py skipped"

    echo ""
    log "=========================================="
    log "  Deployment complete!"
    log "  https://${DOMAIN}"
    log "  Health: https://${DOMAIN}/health"
    log "  API:    https://${DOMAIN}/docs"
    log ""
    log "  Demo:   demo@srp.ai / Demo@12345"
    log "  Bunty:  bunty@srp.ai / Bunty@12345"
    log "=========================================="
    echo ""

    # Final status
    docker compose ps
}

# ── Entry point ──────────────────────────────────────────────────────────────
if [ "${1:-}" = "--init" ]; then
    init_server
else
    deploy
fi
