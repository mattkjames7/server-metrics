#!/bin/bash
set -e

# ===== Configuration =====
PACKAGE_NAME="server-thermals"
VERSION=$(python3 -c "from thermals import __version__; print(__version__)")
MAINTAINER="Matt James https://github.com/mattkjames7"
DESCRIPTION="Server Thermals Monitoring Service"
PREFIX="/"  # root prefix for installation paths

# ===== Generate Wheel =====
python3 -m build --wheel
WHEEL="$(ls dist)"

# ===== Create a temporary build directory =====
BUILD_DIR=$(mktemp -d)
echo "Using build directory: ${BUILD_DIR}"

# Create directories that mirror the target install layout:
mkdir -p "${BUILD_DIR}/usr/local/bin"
mkdir -p "${BUILD_DIR}/lib/systemd/system"
mkdir -p "${BUILD_DIR}/etc/server-thermals"
mkdir -p "${BUILD_DIR}/var/lib/server-thermals"  # directory for the virtual environment

# ===== Copy Files =====
# Copy the executable script (ensure it’s executable)
cp server-thermals "${BUILD_DIR}/usr/local/bin/server-thermals"
chmod +x "${BUILD_DIR}/usr/local/bin/server-thermals"

# Copy the systemd unit file
cp systemd/server-thermals.service "${BUILD_DIR}/lib/systemd/system/server-thermals.service"

# Copy the default configuration file if it exists
if [ -f server-config.json ]; then
  cp default-config.json "${BUILD_DIR}/etc/server-thermals/server-config.json"
fi

# copy the wheel file
cp "dist/${WHEEL}" "${BUILD_DIR}/var/lib/server-thermals/${WHEEL}"

# ===== Create a post-install script =====
# This script creates a dedicated system user, ensures proper directory permissions,
# and sets up a Python virtual environment.
mkdir -p scripts
cat > scripts/postinst <<EOF
#!/bin/bash
set -e

# Create dedicated system user if it doesn't exist
if ! id -u server-thermals >/dev/null 2>&1; then
    useradd --system --no-create-home --shell /usr/sbin/nologin server-thermals
fi

# Ensure /var/lib/server-thermals exists and is owned by the dedicated user
mkdir -p /var/lib/server-thermals
chown server-thermals:server-thermals /var/lib/server-thermals

# Create a Python virtual environment if it does not already exist
if [ ! -d /var/lib/server-thermals/venv ]; then
    python3 -m venv /var/lib/server-thermals/venv
    chown -R server-thermals:server-thermals /var/lib/server-thermals/venv
fi

# Install your Python package inside the virtual environment using the provided wheel
/var/lib/server-thermals/venv/bin/pip install /var/lib/server-thermals/${WHEEL}

# Reload systemd configuration to pick up the new service file
systemctl daemon-reload

# Enable the service so it starts on boot
systemctl enable server-thermals.service

# Start the service immediately
systemctl start server-thermals.service

EOF
chmod +x scripts/postinst

cat > scripts/postrm << "EOF"
#!/bin/bash
set -e

# Ensure the script is run as root.
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (e.g., using sudo)."
    exit 1
fi

PACKAGE_NAME="server-thermals"
SERVICE_NAME="server-thermals.service"

# Target installation paths (as used in your install script)
TARGET_BIN="/usr/local/bin"
TARGET_SYSTEMD="/lib/systemd/system"
TARGET_CONFIG="/etc/server-thermals"
TARGET_APP="/var/lib/server-thermals"

echo "Stopping and disabling ${SERVICE_NAME}..."
systemctl stop ${SERVICE_NAME} || true
systemctl disable ${SERVICE_NAME} || true

echo "Removing systemd service unit file..."
rm -f "${TARGET_SYSTEMD}/${SERVICE_NAME}"

echo "Removing executable from ${TARGET_BIN}..."
rm -f "${TARGET_BIN}/${PACKAGE_NAME}"

echo "Removing configuration directory ${TARGET_CONFIG}..."
rm -rf "${TARGET_CONFIG}"

echo "Removing application directory ${TARGET_APP}..."
rm -rf "${TARGET_APP}"

echo "Reloading systemd daemon..."
systemctl daemon-reload

# Optionally, remove the dedicated system user if it exists.
if id "server-thermals" &>/dev/null; then
    echo "Removing dedicated system user 'server-thermals'..."
    userdel server-thermals || echo "Warning: Could not remove user 'server-thermals'."
fi

echo "Uninstallation of ${PACKAGE_NAME} complete."
EOF
chmod +x scripts/postrm

# ===== Build the .deb package using fpm =====
echo "Building .deb package with fpm..."
fpm -s dir -t deb \
    -n "${PACKAGE_NAME}" \
    -v "${VERSION}" \
    --prefix "${PREFIX}" \
    --after-install scripts/postinst \
    --after-remove scripts/postrm \
    -m "${MAINTAINER}" \
    --description "${DESCRIPTION}" \
    --depends python3-dev \
    --depends python3-venv \
    --depends gcc \
    --depends libsnmp-dev \
    -C "${BUILD_DIR}" .

echo "Debian package built successfully."

# Clean up the temporary build directory
rm -rf "${BUILD_DIR}"
