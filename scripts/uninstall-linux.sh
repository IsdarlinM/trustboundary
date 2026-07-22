#!/usr/bin/env sh
set -eu
INSTALL_ROOT="${HOME}/.trustboundary"
BIN="${HOME}/.local/bin/trustboundary"
rm -f "$BIN"
rm -rf "$INSTALL_ROOT"
echo "Removed TrustBoundary Mapper. User-created workspaces outside $INSTALL_ROOT were not touched."
