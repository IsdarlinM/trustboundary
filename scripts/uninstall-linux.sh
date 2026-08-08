#!/usr/bin/env sh
set -eu
INSTALL_ROOT="${HOME}/.trustboundary"
BIN="${HOME}/.local/bin/trustboundary"
rm -f "$BIN"
rm -rf "$INSTALL_ROOT/venv"
echo "Removed TrustBoundary Mapper runtime. Workspaces, configuration and evidence under $INSTALL_ROOT were preserved."
