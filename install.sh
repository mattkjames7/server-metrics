#!/bin/bash
set -e

# =============================
# Generic Install Script for server-thermals
# =============================

# Check for root privileges.
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (e.g., using sudo)."
    exit 1
fi

# --- Configuration Variables ---
PACKAGE_NAME="server-thermals"
VERSION="0.1.0"
MAINTAINER="Matt James https://github.com/mattkjames7"
DESCRIPTION="Server Thermals Monitoring Service"

# File paths for your artifacts.
EXECUTABLE="server-thermals"                # The executable script to install.
SYSTEMD_UNIT="systemd/server-thermals.service"  # Your systemd service unit file.
CONFIG_FILE="default-config.json"           # The default configuration file.
DIST_DIR="dist"                             # Directory for the built wheel.

# --- Target Installation Directories ---
TARGET_BIN="/usr/local/bin"
TARGET_SYSTEMD="/lib/systemd/system"
TARGET_CONFIG="/etc/server-thermals"
TARGET_APP="/var/lib/server-thermals"

# =============================
# Build the Python Wheel
# =============================

echo "Building the Python wheel file..."
python3 setup.py sdist

# Automatically pick up the generated wheel file.
WHEEL=$(ls ${DIST_DIR}/*.tar.gz | head -n 1 | xargs -n 1 basename)
if [ -z "$WHEEL" ]; then
    echo "Error: No wheel file found in ${DIST_DIR}."
    exit 1
fi
echo "Found wheel file: ${WHEEL}"

# =============================
# Installation Steps
# =============================

echo "Installing ${PACKAGE_NAME} version ${VERSION}..."

# 1. Install the executable script.
echo "Installing executable to ${TARGET_BIN}..."
install -m 0755 "${EXECUTABLE}" "${TARGET_BIN}/${PACKAGE_NAME}"

# 2. Install the systemd unit file.
echo "Installing systemd service unit to ${TARGET_SYSTEMD}..."
mkdir -p "${TARGET_SYSTEMD}"
cp "${SYSTEMD_UNIT}" "${TARGET_SYSTEMD}/"

# 3. Install the configuration file.
echo "Installing default configuration to ${TARGET_CONFIG}..."
mkdir -p "${TARGET_CONFIG}"
if [ -f "${CONFIG_FILE}" ]; then
    cp "${CONFIG_FILE}" "${TARGET_CONFIG}/server-config.json"
else
    echo "Warning: ${CONFIG_FILE} not found; skipping config installation."
fi

# 4. Install the wheel file.
echo "Installing wheel file to ${TARGET_APP}..."
mkdir -p "${TARGET_APP}"
cp "${DIST_DIR}/${WHEEL}" "${TARGET_APP}/"

# 5. Create a dedicated system user if it doesn't exist.
if ! id -u server-thermals >/dev/null 2>&1; then
    echo "Creating dedicated system user 'server-thermals'..."
    useradd --system --no-create-home --shell /usr/sbin/nologin server-thermals
fi

# 6. Ensure the app directory is owned by the dedicated user.
chown -R server-thermals:server-thermals "${TARGET_APP}"

# 7. Create a Python virtual environment if not already present.
if [ ! -d "${TARGET_APP}/venv" ]; then
    echo "Creating Python virtual environment in ${TARGET_APP}/venv..."
    python3 -m venv "${TARGET_APP}/venv"
    chown -R server-thermals:server-thermals "${TARGET_APP}/venv"
fi

# 8. Install the Python package from the wheel file in the virtual environment.
echo "Installing Python package from wheel..."
"${TARGET_APP}/venv/bin/pip" install --upgrade pip
"${TARGET_APP}/venv/bin/pip" install "${TARGET_APP}/${WHEEL}"

# 9. Reload systemd to pick up the new service file.
echo "Reloading systemd daemon..."
systemctl daemon-reload

# 10. Enable the service to start on boot.
echo "Enabling ${PACKAGE_NAME}.service..."
systemctl enable server-thermals.service

# 11. Start the service immediately.
echo "Starting ${PACKAGE_NAME}.service..."
systemctl start server-thermals.service

echo "Installation of ${PACKAGE_NAME} complete."
