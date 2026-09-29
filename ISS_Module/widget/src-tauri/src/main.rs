#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::menu::{Menu, MenuItem};
use tauri::tray::TrayIconBuilder;
use tauri::{Manager, Wry};

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let show = MenuItem::with_id(app, "show", "Show ISS Scale", true, None::<&str>)?;
            let quit = MenuItem::with_id(app, "quit", "Quit ISS Scale", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&show, &quit])?;

            TrayIconBuilder::<Wry>::new()
                .menu(&menu)
                .tooltip("ISS Scale")
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "show" => {
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                    "quit" => app.exit(0),
                    _ => {}
                })
                .build(app)?;
            if let Some(window) = app.get_webview_window("main") {
                window.set_always_on_top(true)?;
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running ISS Scale widget");
}
