#!/usr/bin/env python3
"""Apply EternalLauncher Sakura branding to the upstream desktop app.

Runs after patches/patch_launcher.py. Fails closed when upstream UI layout changes.
"""
from __future__ import annotations

import base64
import json
import re
import shutil
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
UPSTREAM = PROJECT / "upstream"
FRONTEND = UPSTREAM / "apps/app-frontend/src"


def replace_once(path: Path, original: str, updated: str) -> None:
    contents = path.read_text(encoding="utf-8")
    count = contents.count(original)
    if count != 1:
        raise RuntimeError(f"Expected one occurrence in {path}: {original[:70]!r}; found {count}")
    path.write_text(contents.replace(original, updated, 1), encoding="utf-8")


def main() -> None:
    icons = PROJECT / "branding/icons"
    # The Tauri CLI still generates other platform assets from this PNG.
    shutil.copyfile(icons / "512.png", PROJECT / "branding/logo.png")
    shutil.copyfile(icons / "512.png", FRONTEND / "assets/eternal-logo.png")

    app_dir = UPSTREAM / "apps/app"
    windows_icon = "icons/eternal.ico"
    shutil.copyfile(icons / "EternalLauncher.ico", app_dir / windows_icon)
    shutil.copyfile(icons / "128.png", app_dir / "icons/eternal-128.png")
    config = app_dir / "tauri.conf.json"
    data = json.loads(config.read_text(encoding="utf-8"))
    bundle = data["bundle"]
    # Keep the Windows ICO on a dedicated path so `tauri icon` cannot overwrite it.
    bundle["icon"] = [windows_icon, *(path for path in bundle["icon"] if not path.endswith(".ico"))]
    bundle["windows"]["nsis"].update(installerIcon=windows_icon, uninstallerIcon=windows_icon)
    config.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Ship the supplied Sakura illustration with the app, so the default
    # wallpaper works offline and does not depend on a remote image server.
    wallpaper_b64 = (PROJECT / "branding/default-sakura.webp.b64").read_text(encoding="ascii").strip()
    wallpaper = base64.b64decode(wallpaper_b64, validate=True)
    if (
        len(wallpaper) > 1_000_000
        or not wallpaper.startswith(b"RIFF")
        or wallpaper[8:12] != b"WEBP"
    ):
        raise RuntimeError("Invalid bundled default Sakura WebP image")
    bundled_wallpaper = UPSTREAM / "apps/app-frontend/public/eternal-default-sakura.webp"
    bundled_wallpaper.parent.mkdir(parents=True, exist_ok=True)
    bundled_wallpaper.write_bytes(wallpaper)

    theme = (PROJECT / "branding/theme.css").read_text(encoding="utf-8")
    (FRONTEND / "eternal-theme.css").write_text(theme, encoding="utf-8")
    index = UPSTREAM / "apps/app-frontend/index.html"
    replace_once(
        index,
        "<title>Modrinth App</title>",
        '<title>Eternal</title>',
    )
    replace_once(
        index,
        '<link rel="icon" type="image/svg+xml" href="/vite.svg" />',
        '<link rel="icon" type="image/png" href="/src/assets/eternal-logo.png" />',
    )
    replace_once(
        index,
        '<link rel="stylesheet" href="/src/assets/stylesheets/global.scss" />',
        '<link rel="stylesheet" href="/src/assets/stylesheets/global.scss" />'
        '\n\t\t<link rel="stylesheet" href="/src/eternal-theme.css" />',
    )

    title = FRONTEND / "app/shell/title-bar/index.vue"
    replace_once(title, "IconButton, TextLogo, useVIntl", "IconButton, useVIntl")
    replace_once(
        title,
        "import AppActionBar from './action-bar.vue'",
        "import eternalLogo from '@/assets/eternal-logo.png'\n\nimport AppActionBar from './action-bar.vue'",
    )
    replace_once(
        title,
        '<TextLogo class="h-7 w-auto shrink-0 text-contrast pointer-events-none" />',
        '<img :src="eternalLogo" alt="" class="h-7 w-7 shrink-0 object-contain pointer-events-none" />\n'
        '\t\t\t<span class="ml-1 text-base font-semibold tracking-wide text-brand pointer-events-none">'
        'Eternal</span>',
    )

    splash = FRONTEND / "components/ui/SplashScreen.vue"
    old = splash.read_text(encoding="utf-8")
    new, count = re.subn(
        r'<svg\s+class="app-logo".*?</svg>',
        '<div class="eternal-splash-brand">'
        '<img :src="eternalLogo" alt="" class="eternal-splash-icon" />'
        '<strong class="eternal-splash-name">Eternal</strong>'
        '</div>',
        old,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise RuntimeError("Cannot locate exactly one Modrinth splash SVG")
    if "<script setup>" not in new:
        raise RuntimeError("Cannot locate splash script setup")
    new = new.replace(
        "<script setup>",
        "<script setup>\nimport eternalLogo from '@/assets/eternal-logo.png'",
        1,
    )
    css = """
.eternal-splash-brand {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}
.eternal-splash-icon {
  width: 3.2rem;
  height: 3.2rem;
  object-fit: contain;
}
.eternal-splash-name {
  font-size: 1.7rem;
  letter-spacing: 0.01em;
  color: var(--color-brand);
  font-weight: 750;
}
"""
    if "<style scoped lang=\"scss\">" not in new:
        raise RuntimeError("Cannot locate splash scoped stylesheet")
    new = new.replace("<style scoped lang=\"scss\">", "<style scoped lang=\"scss\">\n" + css, 1)
    splash.write_text(new, encoding="utf-8")

    settings = FRONTEND / "features/settings/app-settings-modal/index.vue"
    replace_once(settings, "defaultMessage: 'Modrinth App {version}'", "defaultMessage: 'Eternal {version}'")
    replace_once(
        settings,
        "{{ formatMessage(messages.appVersion, { version: appInfo.version }) }}",
        "Eternal {{ appInfo.version }}",
    )
    replace_once(settings, "\tModrinthIcon,\n", "")
    replace_once(
        settings,
        "import { useAppSettings } from '@/composables/use-app-settings.ts'",
        "import eternalLogo from '@/assets/eternal-logo.png'\n"
        "import { useAppSettings } from '@/composables/use-app-settings.ts'",
    )
    replace_once(
        settings,
        '<ModrinthIcon aria-hidden="true" class="w-6 h-6" />',
        '<img :src="eternalLogo" alt="" class="w-6 h-6 object-contain" />',
    )

    # Hide only the subscription upsell from the account dropdown; keep all
    # account handling, subscriptions, authentication and server APIs intact.
    app = FRONTEND / "App.vue"
    replace_once(app, "\tArrowBigUpDashIcon,\n", "")
    replace_once(
        app,
        "\tupgradeToModrinthPlus: {\n"
        "\t\tid: 'app.nav.upgrade-to-modrinth-plus',\n"
        "\t\tdefaultMessage: 'Upgrade to Modrinth+',\n"
        "\t},\n",
        "",
    )
    replace_once(
        app,
        "\t{\n"
        "\t\tid: 'plus',\n"
        "\t\tlabel: formatMessage(messages.upgradeToModrinthPlus),\n"
        "\t\ticon: ArrowBigUpDashIcon,\n"
        "\t\ttype: 'link',\n"
        "\t\thref: 'https://modrinth.plus?app',\n"
        "\t\ttarget: '_blank',\n"
        "\t\ttone: 'purple',\n"
        "\t\tshown: !hasPlus.value,\n"
        "\t},\n",
        "",
    )

    # Windows shell/taskbar can use the running window icon rather than the
    # NSIS shortcut icon. Use the same PNG as the tray icon.
    main_rs = app_dir / "src/main.rs"
    replace_once(
        main_rs,
        '    let win = app.get_window("main").unwrap();\n',
        '    let win = app.get_window("main").unwrap();\n'
        '    #[cfg(target_os = "windows")]\n'
        '    if let Err(err) = win.set_icon(tauri::include_image!("icons/eternal-128.png")) {\n'
        '        tracing::warn!("Failed to set EternalLauncher taskbar icon: {err}");\n'
        '    }\n',
    )

    print("Removed profile upgrade upsell and configured Windows runtime taskbar icon.")

    print("Sakura branding applied to the desktop titlebar, splash, settings and CSS.")
    print("Eternal icons configured for the launcher and NSIS.")


if __name__ == "__main__":
    main()
