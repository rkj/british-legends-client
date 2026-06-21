#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${APP_DIR:-/opt/british-legends-client}"
ENV_DIR="${ENV_DIR:-/etc/british-legends-client}"
SERVICE_NAME="${SERVICE_NAME:-british-legends}"
SERVICE_USER="${SERVICE_USER:-britishlegends}"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this uninstaller with sudo:"
  echo "  sudo bash deploy/uninstall-pi.sh"
  exit 1
fi

systemctl disable --now "${SERVICE_NAME}.service" >/dev/null 2>&1 || true
rm -f "/etc/systemd/system/${SERVICE_NAME}.service"
systemctl daemon-reload

if [[ "${REMOVE_ENV:-0}" == "1" ]]; then
  rm -rf "${ENV_DIR}"
fi

if [[ "${REMOVE_APP:-0}" == "1" ]]; then
  case "${APP_DIR}" in
    /opt/british-legends-client|/opt/british-legends-client/)
      rm -rf "${APP_DIR}"
      ;;
    *)
      echo "Refusing to remove non-default APP_DIR: ${APP_DIR}"
      echo "Remove it manually if that is really what you want."
      ;;
  esac
fi

if [[ "${REMOVE_USER:-0}" == "1" ]] && id -u "${SERVICE_USER}" >/dev/null 2>&1; then
  userdel "${SERVICE_USER}" || true
fi

echo "British Legends service removed."
echo "App files kept at ${APP_DIR} unless REMOVE_APP=1 was used."
