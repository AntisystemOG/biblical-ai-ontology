#!/bin/bash
# Probes current Node version against the hermes-web-ui engine requirement.
# If Node < 23, offers to upgrade in-place via tarball download.
# Safe to run multiple times; always backs up existing install.
#
# Usage: bash ~/.hermes/skills/devops/hermes-webui-setup/scripts/check-node-and-upgrade.sh

set -euo pipefail

REQUIRED_MAJOR=23
NODE_BIN="$(which node 2>/dev/null || true)"
WEBUI_DIR="${WEBUI_DIR:-$HOME/hermes-web-ui-ekko}"

if [[ -z "${NODE_BIN}" ]]; then
  echo "ERROR: Node not found in PATH."
  exit 1
fi

NODE_REAL="$(readlink -f "${NODE_BIN}")"
NODE_DIR="$(dirname "${NODE_REAL}")"
CURRENT_VERSION="$("${NODE_BIN}" --version)"
CURRENT_MAJOR="${CURRENT_VERSION#v}"
CURRENT_MAJOR="${CURRENT_MAJOR%%.*}"

echo "Node binary: ${NODE_BIN}"
echo "Real path:   ${NODE_REAL}"
echo "Version:     ${CURRENT_VERSION}"
echo ""

if [[ "${CURRENT_MAJOR}" -ge "${REQUIRED_MAJOR}" ]]; then
  echo "OK: Node ${CURRENT_VERSION} meets requirement (>= v${REQUIRED_MAJOR})"
  exit 0
fi

echo "WARNING: Node ${CURRENT_VERSION} is below requirement (>= v${REQUIRED_MAJOR})"
echo ""

# Try to infer the managed install root (e.g., ~/.hermes/node/bin/node -> ~/.hermes/node)
INSTALL_ROOT=""
if [[ "${NODE_DIR}" == *"/bin" ]]; then
  INSTALL_ROOT="$(dirname "${NODE_DIR}")"
fi

if [[ -z "${INSTALL_ROOT}" ]]; then
  echo "Could not auto-detect managed install root from ${NODE_DIR}"
  echo "Please upgrade Node manually via your package manager or nvm."
  exit 1
fi

echo "Detected managed install root: ${INSTALL_ROOT}"
read -r -p "Proceed with tarball upgrade? [y/N] " CONFIRM
if [[ "${CONFIRM}" != "y" && "${CONFIRM}" != "Y" ]]; then
  echo "Aborted."
  exit 0
fi

# Download latest v23 tarball
echo "Fetching latest v23.x Linux x64 tarball..."
LATEST_URL="$(curl -fsSL https://nodejs.org/dist/latest-v23.x/ | grep -oP 'href="\Knode-v23\.\d+\.\d+-linux-x64\.tar\.xz' | head -1)"
if [[ -z "${LATEST_URL}" ]]; then
  echo "ERROR: Could not determine latest v23 tarball URL"
  exit 1
fi
FULL_URL="https://nodejs.org/dist/latest-v23.x/${LATEST_URL}"
TMP_TAR="/tmp/${LATEST_URL}"

echo "Downloading ${FULL_URL}..."
curl -fsSL -o "${TMP_TAR}" "${FULL_URL}"

# Backup and extract
BACKUP_DIR="${INSTALL_ROOT}-backup-$(date +%Y%m%d-%H%M%S)"
echo "Backing up existing install to ${BACKUP_DIR}..."
cp -a "${INSTALL_ROOT}" "${BACKUP_DIR}"

echo "Extracting new Node into ${INSTALL_ROOT}..."
tar -xf "${TMP_TAR}" -C "$(dirname "${INSTALL_ROOT}")" --strip-components=1

# Verify
NEW_VERSION="$("${NODE_BIN}" --version || true)"
if [[ "${NEW_VERSION}" == v23.* ]]; then
  echo ""
  echo "SUCCESS: Upgraded to ${NEW_VERSION}"
  echo "Backup kept at: ${BACKUP_DIR}"
  echo "Run 'cd ${WEBUI_DIR} && npm run build' to rebuild."
else
  echo "ERROR: Upgrade failed. Version still shows: ${NEW_VERSION:-(not found)}"
  echo "Restore from backup: mv ${BACKUP_DIR} ${INSTALL_ROOT}"
  exit 1
fi
