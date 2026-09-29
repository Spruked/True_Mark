# ISS Scale desktop widget

This is the compact Tauri 2/Rust desktop and system-tray surface for the Interplanetary Stardate Syncrometer Scale. It stays always-on-top, can be dragged by its header, and polls the local ISS service for the four required representations: Epoch, Standard, Julian, and ISS. Hiding the window leaves the tray process running; use the tray menu to show it or quit.

## Run

Start the time service from the parent module:

```bash
cd ..
python -m iss_module.service
```

Then, with Rust/Cargo installed:

```bash
cd widget
npm install
npm run tauri:dev
```

For a distributable build, run `npm run tauri:build`.

The widget expects the service at `http://127.0.0.1:8000/api/time`.

The Tauri shell also registers a system-tray icon. Selecting **Show ISS Scale**
restores and focuses the widget; selecting **Quit ISS Scale** exits the process.
The window's `×` control only hides the window so the tray process remains
available.

## Automatic start and crash recovery

On Linux, install the user-level supervisor after building:

```bash
./scripts/install_linux_autostart.sh
```

It starts the widget after login/reboot and restarts it indefinitely after a crash. Remove it with `./scripts/uninstall_linux_autostart.sh`.
