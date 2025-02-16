#!/bin/bash
set -e

# =============================
# Generic Uninstall Script for server-metrics
# =============================

# Ensure the script is run as root.
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (e.g., using sudo)."
    exit 1
fi

PACKAGE_NAME="server-metrics"
SERVICE_NAME="server-metrics.service"

# Target paths (must match those used in the install script)
TARGET_BIN="/usr/local/bin"
TARGET_SYSTEMD="/lib/systemd/system"
TARGET_CONFIG="/etc/server-metrics"
TARGET_APP="/var/lib/server-metrics"

EXECUTABLE="${TARGET_BIN}/${PACKAGE_NAME}"

echo "Stopping and disabling ${SERVICE_NAME}..."
systemctl stop ${SERVICE_NAME} || true
systemctl disable ${SERVICE_NAME} || true

echo "Removing systemd service unit file..."
rm -f "${TARGET_SYSTEMD}/${SERVICE_NAME}"

echo "Removing executable from ${TARGET_BIN}..."
rm -f "${EXECUTABLE}"

echo "Removing configuration directory ${TARGET_CONFIG}..."
rm -rf "${TARGET_CONFIG}"

echo "Removing application directory ${TARGET_APP}..."
rm -rf "${TARGET_APP}"

echo "Reloading systemd daemon..."
systemctl daemon-reload

# Optionally, remove the dedicated system user if it exists.
if id "server-metrics" &>/dev/null; then
    echo "Removing dedicated system user 'server-metrics'..."
    userdel server-metrics || echo "Warning: Could not remove user 'server-metrics'."
fi

echo "Uninstallation of ${PACKAGE_NAME} complete."
