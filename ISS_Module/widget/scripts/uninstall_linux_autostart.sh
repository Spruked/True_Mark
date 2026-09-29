#!/usr/bin/env bash
set -euo pipefail

SERVICE_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user/iss-scale-widget.service"
API_SERVICE_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user/iss-scale-api.service"
systemctl --user disable --now iss-scale-widget.service 2>/dev/null || true
systemctl --user disable --now iss-scale-api.service 2>/dev/null || true
rm -f "$SERVICE_FILE"
rm -f "$API_SERVICE_FILE"
systemctl --user daemon-reload
echo "Removed $SERVICE_FILE"
