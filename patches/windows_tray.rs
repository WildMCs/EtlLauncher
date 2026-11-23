use tauri::{
    AppHandle, Manager, Window, WindowEvent,
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
};

const TRAY_ID: &str = "eternal-launcher";
const OPEN_ID: &str = "eternal-tray-open";
const EXIT_ID: &str = "eternal-tray-exit";

pub fn on_window_event(window: &Window, event: &WindowEvent) {
    if window.label() == "main"
        && let WindowEvent::CloseRequested { api, .. } = event
    {
        match hide_to_tray(window) {
            Ok(()) => api.prevent_close(),
            Err(error) => tracing::warn!("Failed to hide EternalLauncher to the tray: {error}"),
        }
    }
}

fn hide_to_tray(window: &Window) -> tauri::Result<()> {
    let app = window.app_handle();
    let tray = if let Some(tray) = app.tray_by_id(TRAY_ID) {
        tray.set_visible(true)?;
        tray
    } else {
        let open = MenuItem::with_id(app, OPEN_ID, "Abrir Eternal", true, None::<&str>)?;
        let exit = MenuItem::with_id(app, EXIT_ID, "Salir de Eternal", true, None::<&str>)?;
        let menu = Menu::with_items(app, &[&open, &exit])?;

        TrayIconBuilder::with_id(TRAY_ID)
            .icon(tauri::include_image!("icons/eternal-128.png"))
            .tooltip("EternalLauncher")
            .menu(&menu)
            .show_menu_on_left_click(false)
            .on_menu_event(|app, event| match event.id().as_ref() {
                OPEN_ID => restore(app),
                EXIT_ID => app.exit(0),
                _ => {}
            })
            .on_tray_icon_event(|tray, event| {
                if matches!(
                    event,
                    TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up,
                        ..
                    }
                ) {
                    restore(tray.app_handle());
                }
            })
            .build(app)?
    };

    if let Err(error) = window.hide() {
        let _ = tray.set_visible(false);
        return Err(error);
    }
    Ok(())
}

pub fn restore(app: &AppHandle) {
    if let Some(window) = app.get_window("main") {
        if let Err(error) = window.show() {
            tracing::warn!("Failed to restore EternalLauncher: {error}");
            return;
        }
        let _ = window.unminimize();
        let _ = window.set_focus();

        if let Some(tray) = app.tray_by_id(TRAY_ID)
            && let Err(error) = tray.set_visible(false)
        {
            tracing::warn!("Failed to hide the EternalLauncher tray icon: {error}");
        }
    }
}
