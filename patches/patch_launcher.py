#!/usr/bin/env python3
"""Apply the EternalLauncher UI patch to a fresh checkout of modrinth/code.

Fail closed when upstream changes the required source snippets.
"""
from __future__ import annotations
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "upstream"

def replace_once(path: Path, old: str, new: str) -> None:
    content = path.read_text(encoding="utf-8")
    if content.count(old) != 1:
        raise RuntimeError(f"Expected exactly one match in {path.relative_to(ROOT)}: {old[:65]!r}")
    path.write_text(content.replace(old, new, 1), encoding="utf-8")


def configure_installer(data: dict, app: Path) -> None:
    patch_dir = Path(__file__).resolve().parent
    notice = (patch_dir / "installer_notice.txt").read_text(encoding="utf-8")
    license_text = (app / "LICENSE").read_text(encoding="utf-8")
    (app / "eternal-install-notice.txt").write_text(
        notice.rstrip() + "\n\n" + license_text,
        encoding="utf-8-sig",
    )
    # makensis detects the encoding of included files from their BOM.
    hook = (patch_dir / "installer_notice.nsh").read_text(encoding="utf-8")
    (app / "nsis" / "eternal-notice.nsh").write_text(hook, encoding="utf-8-sig")

    data["bundle"]["licenseFile"] = "eternal-install-notice.txt"
    nsis = data["bundle"]["windows"]["nsis"]
    nsis["installerHooks"] = "nsis/eternal-notice.nsh"
    nsis["languages"] = ["Spanish"]

def configure_windows_tray(app: Path) -> None:
    shutil.copyfile(Path(__file__).with_name("windows_tray.rs"), app / "src/windows_tray.rs")
    replace_once(
        app / "Cargo.toml",
        "[dev-dependencies]\n",
        "[target.'cfg(target_os = \"windows\")'.dependencies.tauri]\n"
        'workspace = true\nfeatures = ["tray-icon"]\n\n'
        "[dev-dependencies]\n",
    )
    main = app / "src/main.rs"
    replace_once(
        main, "mod api;\n", 'mod api;\n#[cfg(target_os = "windows")]\nmod windows_tray;\n'
    )
    replace_once(
        main,
        '            if let Some(win) = app.get_window("main") {\n'
        '                let _ = win.set_focus();\n'
        '            }\n',
        '            #[cfg(target_os = "windows")]\n'
        '            windows_tray::restore(app);\n'
        '            #[cfg(not(target_os = "windows"))]\n'
        '            if let Some(win) = app.get_window("main") {\n'
        '                let _ = win.set_focus();\n'
        '            }\n',
    )
    replace_once(
        main,
        "    builder = builder\n        .plugin(api::auth::init())",
        '    #[cfg(target_os = "windows")]\n'
        '    let builder = builder.on_window_event(windows_tray::on_window_event);\n\n'
        "    let builder = builder\n        .plugin(api::auth::init())",
    )
    replace_once(
        ROOT / "packages/app-lib/src/state/process.rs",
        "                    crate::EventState::get_main_window().await?\n"
        "            {\n                window.unminimize()?;",
        "                    crate::EventState::get_main_window().await?\n"
        '                && (!cfg!(target_os = "windows") || window.is_visible()?)\n'
        "            {\n                window.unminimize()?;",
    )


def main() -> None:
    config = ROOT / "apps/app/tauri.conf.json"
    data = json.loads(config.read_text(encoding="utf-8"))
    assert data["productName"] == "Modrinth App"
    assert data["mainBinaryName"] == "Modrinth App"
    assert data["app"]["windows"][0]["title"] == "Modrinth App"
    data["productName"] = "EternalLauncher"
    data["mainBinaryName"] = "EternalLauncher"
    data["app"]["windows"][0]["title"] = "Eternal"
    data["identifier"] = "com.eternal.launcher"
    data["build"]["beforeBuildCommand"] = (
        "pnpm -w i18n:coverage && pnpm --filter @modrinth/app-frontend run build"
    )
    data["bundle"].pop("fileAssociations", None)
    configure_installer(data, config.parent)
    data["plugins"]["deep-link"]["desktop"]["schemes"] = []
    config.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    configure_windows_tray(config.parent)

    replace_once(
        ROOT / "packages/app-lib/src/state/db_backup.rs",
        'Ok(base.join("Modrinth").join("Backups").join("app-db"))',
        'Ok(base.join("com.eternal.launcher").join("Backups").join("app-db"))',
    )

    app = ROOT / "apps/app-frontend/src/App.vue"
    replace_once(
        app,
        "const showAd = computed(\n\t() => sidebarVisible.value && !hasPlus.value && credentials.value !== undefined,\n)",
        "const showAd = computed(() => false)",
    )
    replace_once(
        app,
        "const adConsentAvailable = computed(() => credentials.value !== undefined && !hasPlus.value)",
        "const adConsentAvailable = computed(() => false)",
    )
    # Prevent the app from initiating the ads Tauri window at all.
    replace_once(
        app,
        "if (showAds) {\n\t\t\tawait init_ads_window(true)",
        "if (false && showAds) {\n\t\t\tawait init_ads_window(true)",
    )
    # Disable official update checks, which would replace this customized build.
    utils = ROOT / "apps/app-frontend/src/helpers/utils.js"
    replace_once(
        utils,
        "export async function areUpdatesEnabled() {\n\treturn await invoke('are_updates_enabled')\n}",
        "export async function areUpdatesEnabled() {\n\treturn false\n}",
    )
    print("EternalLauncher executable name, ad UI and updater patch applied.")
    print("Note: backend ad code remains; this is NOT a complete removal of ad infrastructure.")

if __name__ == "__main__":
    main()
