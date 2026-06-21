#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${APP_DIR:-/opt/british-legends-client}"
ENV_DIR="${ENV_DIR:-/etc/british-legends-client}"
SERVICE_NAME="${SERVICE_NAME:-british-legends}"
SERVICE_USER="${SERVICE_USER:-britishlegends}"
WEB_HOST="${BL_WEB_HOST:-127.0.0.1}"
WEB_PORT="${BL_WEB_PORT:-8080}"
CONNECT_ON_START="${BL_CONNECT_ON_START:-0}"
TELNET_DEBUG="${BL_TELNET_DEBUG:-0}"
MUD_HOST="${BL_MUD_HOST:-british-legends.com}"
MUD_PORT="${BL_MUD_PORT:-27750}"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this installer with sudo:"
  echo "  sudo bash deploy/install-pi.sh"
  exit 1
fi

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== British Legends Mobile Bridge Pi installer =="
echo "Source: ${SOURCE_DIR}"
echo "Install: ${APP_DIR}"
echo "Service: ${SERVICE_NAME}.service"
echo

apt-get update
apt-get install -y python3 python3-venv rsync curl

if ! getent group "${SERVICE_USER}" >/dev/null 2>&1; then
  groupadd --system "${SERVICE_USER}"
fi

if ! id -u "${SERVICE_USER}" >/dev/null 2>&1; then
  useradd --system --gid "${SERVICE_USER}" --home "${APP_DIR}" --shell /usr/sbin/nologin "${SERVICE_USER}"
fi

install -d -m 0755 "${APP_DIR}"
if [[ "${SOURCE_DIR}" != "${APP_DIR}" ]]; then
  rsync -a \
    --exclude ".git" \
    --exclude ".codex-remote-attachments" \
    --exclude "__pycache__" \
    --exclude "*.log" \
    --exclude "*.err.log" \
    --exclude "build" \
    --exclude "dist" \
    "${SOURCE_DIR}/" "${APP_DIR}/"
fi

python3 -m venv "${APP_DIR}/.venv"
"${APP_DIR}/.venv/bin/python" -m pip install --upgrade pip
"${APP_DIR}/.venv/bin/python" -m pip install -r "${APP_DIR}/requirements.txt"

chown -R "${SERVICE_USER}:${SERVICE_USER}" "${APP_DIR}"

install -d -m 0755 "${ENV_DIR}"
cat > "${ENV_DIR}/british-legends.env" <<ENV
BL_WEB_HOST=${WEB_HOST}
BL_WEB_PORT=${WEB_PORT}
BL_CONNECT_ON_START=${CONNECT_ON_START}
BL_TELNET_DEBUG=${TELNET_DEBUG}
BL_TELNET_DEBUG_FILE=${APP_DIR}/telnet_debug.txt
BL_MUD_HOST=${MUD_HOST}
BL_MUD_PORT=${MUD_PORT}
PYTHONUNBUFFERED=1
ENV
chmod 0644 "${ENV_DIR}/british-legends.env"

install -m 0644 "${APP_DIR}/deploy/british-legends.service" "/etc/systemd/system/${SERVICE_NAME}.service"
systemctl daemon-reload
systemctl enable --now "${SERVICE_NAME}.service"

echo
echo "Service status:"
systemctl --no-pager --full status "${SERVICE_NAME}.service" || true

echo
echo "Health check:"
if curl -fsS "http://127.0.0.1:${WEB_PORT}/healthz"; then
  echo "Local service is answering."
else
  echo "Local health check failed. Read logs with:"
  echo "  journalctl -u ${SERVICE_NAME}.service -f"
fi

LAN_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"

echo
echo "Next steps:"
echo "1. In Cloudflare Tunnel, add a public hostname such as mud.example.com."
if [[ "${WEB_HOST}" == "127.0.0.1" || "${WEB_HOST}" == "localhost" ]]; then
  echo "2. Point the tunnel service URL to: http://localhost:${WEB_PORT}"
  echo "   Use this when cloudflared runs directly on the Pi host."
else
  echo "2. Point the tunnel service URL to: http://${LAN_IP:-<pi-lan-ip>}:${WEB_PORT}"
  echo "   Use this when cloudflared runs in Docker or another network namespace."
fi
echo "3. Protect the hostname with Cloudflare Access before sharing it."
echo "4. Test on your phone, tap Reconnect MUD, then log in."
echo
echo "Logs:"
echo "  journalctl -u ${SERVICE_NAME}.service -f"
echo
echo "To reinstall after pulling updates:"
echo "  sudo bash deploy/install-pi.sh"
