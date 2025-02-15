#!/bin/bash
set -e

# ===== Configuration =====
PACKAGE_NAME="server-thermals"
VERSION="0.1.0"
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

# ===== Build the .deb package using fpm =====
echo "Building .deb package with fpm..."
fpm -s dir -t deb \
    -n "${PACKAGE_NAME}" \
    -v "${VERSION}" \
    --prefix "${PREFIX}" \
    --after-install scripts/postinst \
    -m "${MAINTAINER}" \
    --description "${DESCRIPTION}" \
    -C "${BUILD_DIR}" .

echo "Debian package built successfully."

# Clean up the temporary build directory
rm -rf "${BUILD_DIR}"
