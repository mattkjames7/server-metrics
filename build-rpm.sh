#!/bin/bash
set -e

# ===== Configuration =====
PACKAGE_NAME="server-metrics"
VERSION=$(grep -oP '^__version__\s*=\s*"\K[^"]+' metrics/__init__.py)
MAINTAINER="Matt James https://github.com/mattkjames7"
DESCRIPTION="Server Metrics Monitoring Service"
PREFIX="/"  # root prefix for installation paths

# ===== Generate Wheel =====
echo "Building the Python wheel..."
python3 setup.py sdist
WHEEL="$(ls dist/*.tar.gz | head -n 1 | xargs -n 1 basename)"
echo "Found wheel file: ${WHEEL}"

# ===== Create a temporary build directory =====
BUILD_DIR=$(mktemp -d)
echo "Using build directory: ${BUILD_DIR}"

# Create directories that mirror the target install layout:
mkdir -p "${BUILD_DIR}/usr/local/bin"
mkdir -p "${BUILD_DIR}/lib/systemd/system"
mkdir -p "${BUILD_DIR}/etc/server-metrics"
mkdir -p "${BUILD_DIR}/var/lib/server-metrics"  # for the virtual environment and wheel

# ===== Copy Files =====
# Copy the executable script (ensure it’s executable)
cp server-metrics "${BUILD_DIR}/usr/local/bin/server-metrics"
chmod +x "${BUILD_DIR}/usr/local/bin/server-metrics"

# Copy the systemd unit file
cp systemd/server-metrics.service "${BUILD_DIR}/lib/systemd/system/server-metrics.service"

# Copy the default configuration file if it exists
if [ -f default-config.json ]; then
  cp default-config.json "${BUILD_DIR}/etc/server-metrics/server-config.json"
fi

# Copy the wheel file into the app directory
cp "dist/${WHEEL}" "${BUILD_DIR}/var/lib/server-metrics/${WHEEL}"

# ===== Create a post-install script =====
mkdir -p scripts
cat > scripts/postinst <<EOF
#!/bin/bash
set -e

# Create dedicated system user if it doesn't exist
if ! id -u server-metrics >/dev/null 2>&1; then
    useradd --system --no-create-home --shell /usr/sbin/nologin server-metrics
fi

# Ensure /var/lib/server-metrics exists and is owned by the dedicated user
mkdir -p /var/lib/server-metrics
chown server-metrics:server-metrics /var/lib/server-metrics

# Create a Python virtual environment if it does not already exist
if [ ! -d /var/lib/server-metrics/venv ]; then
    python3 -m venv /var/lib/server-metrics/venv
    chown -R server-metrics:server-metrics /var/lib/server-metrics/venv
fi

# Install your Python package inside the virtual environment using the provided wheel
/var/lib/server-metrics/venv/bin/pip install /var/lib/server-metrics/${WHEEL}

# Reload systemd configuration to pick up the new service file
systemctl daemon-reload

# Enable the service so it starts on boot
systemctl enable server-metrics.service

# Start the service immediately
systemctl start server-metrics.service
EOF
chmod +x scripts/postinst

cat > scripts/postun << "EOF"
#!/bin/bash
set -e

# Ensure the script is run as root.
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (e.g., using sudo)."
    exit 1
fi

PACKAGE_NAME="server-metrics"
SERVICE_NAME="server-metrics.service"

# Target installation paths (as used in your install script)
TARGET_BIN="/usr/local/bin"
TARGET_SYSTEMD="/lib/systemd/system"
TARGET_CONFIG="/etc/server-metrics"
TARGET_APP="/var/lib/server-metrics"

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
if id "server-metrics" &>/dev/null; then
    echo "Removing dedicated system user 'server-metrics'..."
    userdel server-metrics || echo "Warning: Could not remove user 'server-metrics'."
fi

echo "Uninstallation of ${PACKAGE_NAME} complete."
EOF
chmod +x scripts/postun

# ===== Build the RPM package using fpm =====
echo "Building RPM package with fpm..."
fpm -s dir -t rpm \
    -n "${PACKAGE_NAME}" \
    -v "${VERSION}" \
    --prefix "${PREFIX}" \
    --after-install scripts/postinst \
    --after-remove scripts/postun \
    -m "${MAINTAINER}" \
    --description "${DESCRIPTION}" \
    --depends python3-devel \
    --depends gcc \
    --depends net-snmp-devel \
    -C "${BUILD_DIR}" .

echo "RPM package built successfully."

# Clean up the temporary build directory
rm -rf "${BUILD_DIR}"
