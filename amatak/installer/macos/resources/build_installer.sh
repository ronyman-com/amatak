#!/bin/bash

# Build the Mac OS installer for Amatak Language

# Configuration
APP_NAME="Amatak"
VERSION="1.0"
INSTALL_DIR="/usr/local/amatak"
PKG_ID="org.amatak.pkg"
PRODUCT_ID="org.amatak.product"
SCRIPTS_DIR="installer/macos/scripts"
RESOURCES_DIR="installer/macos/resources"
DIST_FILE="installer/macos/Distribution.xml"
OUTPUT_DIR="dist/macos"
COMPONENT_PKG="${OUTPUT_DIR}/AmatakComponent.pkg"
PRODUCT_PKG="${OUTPUT_DIR}/Amatak-${VERSION}.pkg"

# Create directory structure
mkdir -p "${OUTPUT_DIR}/root${INSTALL_DIR}/bin"
mkdir -p "${OUTPUT_DIR}/scripts"

# Copy binaries
cp -R dist/macos/bin/* "${OUTPUT_DIR}/root${INSTALL_DIR}/bin/"

# Copy scripts
cp "${SCRIPTS_DIR}/preinstall" "${OUTPUT_DIR}/scripts/"
cp "${SCRIPTS_DIR}/postinstall" "${OUTPUT_DIR}/scripts/"
chmod +x "${OUTPUT_DIR}/scripts/"*

# Build component package
pkgbuild \
    --root "${OUTPUT_DIR}/root" \
    --scripts "${OUTPUT_DIR}/scripts" \
    --identifier "${PKG_ID}" \
    --version "${VERSION}" \
    --install-location "/" \
    "${COMPONENT_PKG}"

# Build product archive
productbuild \
    --distribution "${DIST_FILE}" \
    --resources "${RESOURCES_DIR}" \
    --package-path "${OUTPUT_DIR}" \
    --version "${VERSION}" \
    "${PRODUCT_PKG}"

# Clean up
rm -rf "${OUTPUT_DIR}/root" "${OUTPUT_DIR}/scripts" "${COMPONENT_PKG}"

echo "Installer created at: ${PRODUCT_PKG}"