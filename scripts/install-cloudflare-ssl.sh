#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# SRP Marketing OS — Cloudflare Origin SSL Certificate Installer
# Run this ON THE SERVER as root after cloning the repo.
#
# Usage:
#   chmod +x scripts/install-cloudflare-ssl.sh
#   ./scripts/install-cloudflare-ssl.sh
#
# The script will prompt you to paste the certificate and private key.
# Certs are stored in nginx/ssl/ (gitignored — never committed to git).
# ──────────────────────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SSL_DIR="$REPO_ROOT/nginx/ssl"

echo ""
echo "=== SRP Marketing OS — Cloudflare Origin SSL Setup ==="
echo ""
echo "SSL directory: $SSL_DIR"
mkdir -p "$SSL_DIR"
chmod 700 "$SSL_DIR"

# ── Write fullchain.pem ────────────────────────────────────────────────────
echo ""
echo "Paste your Cloudflare Origin CERTIFICATE below."
echo "Start with: -----BEGIN CERTIFICATE-----"
echo "End with:   -----END CERTIFICATE-----"
echo "Then press Ctrl+D on a new line."
echo ""
cat > "$SSL_DIR/fullchain.pem"
chmod 644 "$SSL_DIR/fullchain.pem"
echo "✓ fullchain.pem written"

# ── Write privkey.pem ──────────────────────────────────────────────────────
echo ""
echo "Paste your Cloudflare Origin PRIVATE KEY below."
echo "Start with: -----BEGIN PRIVATE KEY-----"
echo "End with:   -----END PRIVATE KEY-----"
echo "Then press Ctrl+D on a new line."
echo ""
cat > "$SSL_DIR/privkey.pem"
chmod 600 "$SSL_DIR/privkey.pem"
echo "✓ privkey.pem written"

# ── Verify ────────────────────────────────────────────────────────────────
echo ""
echo "=== Verifying certificate ==="
openssl x509 -in "$SSL_DIR/fullchain.pem" -noout -subject -dates -issuer
echo ""
echo "=== Verifying key matches certificate ==="
CERT_MOD=$(openssl x509 -noout -modulus -in "$SSL_DIR/fullchain.pem" | md5sum)
KEY_MOD=$(openssl rsa -noout -modulus -in "$SSL_DIR/privkey.pem" 2>/dev/null | md5sum || \
          openssl pkey -noout -pubout -in "$SSL_DIR/privkey.pem" | openssl md5)
if [ "$CERT_MOD" = "$KEY_MOD" ]; then
    echo "✓ Certificate and private key MATCH"
else
    echo "✗ WARNING: Certificate and private key do NOT match — check your files!"
    exit 1
fi

echo ""
echo "=== SSL setup complete ==="
echo "Files:"
ls -la "$SSL_DIR/"
echo ""
echo "Next step: docker compose up -d --build"
echo ""
