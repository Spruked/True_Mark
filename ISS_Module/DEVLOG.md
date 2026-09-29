# ISS Module development log

## 2026-09-28 — Tauri desktop widget and supervision

- Added a compact Tauri 2/Rust widget under `widget/`.
- Set the window to 360×190, borderless, draggable, non-resizable, and always-on-top.
- Added live rendering of Epoch, Standard, Julian, ISS, raw nanoseconds, reference frame, and anchor hash.
- Added 250 ms polling against `http://127.0.0.1:8000/api/time`.
- Added Linux user-systemd installation scripts for start-after-login/reboot and indefinite `Restart=always` crash recovery.
- Added `PROJECT_TREE.txt` and `SITE_MAP.md` as maintained repository records.
- Corrected the API response collision so `epoch_label` and numeric `epoch` are separate fields.
- Vite frontend build passes.
- Native Rust compilation remains pending because this development environment does not have `cargo` or `rustc` installed.

## Authority

The widget is a read-only display client. `iss_time_ns`, derived from the fixed 2000-01-01 TAI epoch, remains the sole authoritative ordering value.
