# Installation and uninstallation

| Platform | Install | Uninstall |
|---|---|---|
| Linux / Termux | `sh scripts/install-linux.sh` | `sh scripts/uninstall-linux.sh` |
| Windows | `scripts\install-windows.cmd` | `scripts\uninstall-windows.cmd` |

The Windows uninstaller removes the `trustboundary.cmd` shim and isolated TrustBoundary venv while preserving workspaces, configuration and evidence. It does not remove the shared `%USERPROFILE%\.local\bin` PATH entry. Linux follows the same preservation contract.
