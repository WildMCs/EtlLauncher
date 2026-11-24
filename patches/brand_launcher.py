#!/usr/bin/env python3
"""Apply EternalLauncher Sakura branding to the upstream desktop app.

Runs after patches/patch_launcher.py. Fails closed when upstream UI layout changes.
"""
from __future__ import annotations

import base64
import json
import os
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


def install_release_notice() -> None:
    feature = FRONTEND / "features/eternal-updates"
    feature.mkdir(parents=True, exist_ok=True)
    for filename in ("eternal-version.json", "release-check.ts", "release-notice.vue", "about-launcher.vue"):
        shutil.copyfile(PROJECT / "branding" / filename, feature / filename)
    (feature / "upstream-build.json").write_text(
        json.dumps({"tag": os.environ.get("ETERNAL_UPSTREAM_TAG") or None}) + "\n",
        encoding="utf-8",
    )

    action_bar = FRONTEND / "app/shell/title-bar/action-bar.vue"
    replace_once(
        action_bar,
        "import AppUpdateButton from '@/components/ui/app-update-button/index.vue'",
        "import EternalReleaseNotice from '@/features/eternal-updates/release-notice.vue'",
    )
    replace_once(action_bar, "<AppUpdateButton />", "<EternalReleaseNotice />")

    behavior = FRONTEND / "features/settings/display/behavior-settings.vue"
    replace_once(
        behavior,
        "import { onBeforeUnmount, onMounted } from 'vue'",
        "import { onBeforeUnmount, onMounted, ref } from 'vue'",
    )
    replace_once(
        behavior,
        "const appSettings = useAppSettings()",
        "import { checksEnabled, saveCheckPreference } from '@/features/eternal-updates/release-check'\n\n"
        "const checkEternalUpdates = ref(checksEnabled(window.localStorage))\n"
        "function setCheckEternalUpdates(enabled: boolean) {\n"
        "\tsaveCheckPreference(window.localStorage, enabled)\n"
        "\tcheckEternalUpdates.value = enabled\n"
        "}\n\n"
        "const appSettings = useAppSettings()",
    )
    replace_once(
        behavior,
        '\t\t\t\t<Toggle id="minimize-launcher" v-model="current.minimizeApp" />\n\t\t\t</div>',
        '\t\t\t\t<Toggle id="minimize-launcher" v-model="current.minimizeApp" />\n\t\t\t</div>\n'
        """
			<div class="flex items-center justify-between gap-4">
				<div>
					<h3 id="eternal-updates-label" class="m-0 text-lg font-semibold text-contrast">
						Buscar actualizaciones al abrir el lanzador
					</h3>
					<p id="eternal-updates-description" class="m-0 mt-1">
						Consulta GitHub una vez al iniciar Eternal y avisa si hay una nueva versión.
					</p>
				</div>
				<Toggle
					id="eternal-check-updates"
					:model-value="checkEternalUpdates"
					aria-labelledby="eternal-updates-label"
					aria-describedby="eternal-updates-description"
					@update:model-value="setCheckEternalUpdates"
				/>
			</div>""",
    )


def main() -> None:
    # Store the user-supplied (compressed) transparent Sakura logo as a base64
    # text asset in Git; decode it to a regular PNG before Vite and Tauri run.
    logo_b64 = (PROJECT / "branding/logo.png.b64").read_text(encoding="ascii").strip()
    icon = base64.b64decode(logo_b64, validate=True)
    if not icon.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("branding/logo.png.b64 does not contain a PNG image")
    (PROJECT / "branding/logo.png").write_bytes(icon)
    (FRONTEND / "assets/eternal-logo.png").write_bytes(icon)

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
    replace_once(settings, "\tGaugeIcon,\n", "\tGaugeIcon,\n\tInfoIcon,\n")
    replace_once(
        settings,
        "import PrivacySettings from '@/features/settings/account/privacy-settings.vue'",
        "import AboutLauncher from '@/features/eternal-updates/about-launcher.vue'\n"
        "import PrivacySettings from '@/features/settings/account/privacy-settings.vue'",
    )
    replace_once(
        settings,
        "\t\tcontent: TroubleshootingSettings,\n\t},\n]",
        "\t\tcontent: TroubleshootingSettings,\n\t},\n"
        "\t{\n\t\tname: defineMessage({\n"
        "\t\t\tid: 'eternal.settings.about-launcher',\n"
        "\t\t\tdefaultMessage: 'Sobre el launcher',\n"
        "\t\t}),\n\t\tcategory: tabCategories.system,\n"
        "\t\ticon: InfoIcon,\n\t\tcontent: AboutLauncher,\n\t},\n]",
    )
    replace_once(
        settings,
        "formatMessage(messages.appVersion, { version: appInfo.version })",
        "formatMessage(messages.appVersion, { version: eternalVersion })",
    )
    replace_once(settings, "defaultMessage: 'Modrinth App {version}'", "defaultMessage: 'EternalLauncher v{version}'")
    replace_once(settings, "id: 'app.settings.app-version'", "id: 'eternal.settings.app-version'")
    replace_once(settings, "\tModrinthIcon,\n", "")
    replace_once(
        settings,
        "import { useAppSettings } from '@/composables/use-app-settings.ts'",
        "import eternalLogo from '@/assets/eternal-logo.png'\n"
        "import { useAppSettings } from '@/composables/use-app-settings.ts'\n"
        "import { eternalVersion } from '@/features/eternal-updates/release-check'",
    )
    replace_once(
        settings,
        '<ModrinthIcon aria-hidden="true" class="w-6 h-6" />',
        '<img :src="eternalLogo" alt="" class="w-6 h-6 object-contain" />',
    )
    install_release_notice()

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
    # NSIS shortcut icon. Set it explicitly from the same PNG generated by
    # the Tauri icon build step (macro path is relative to Cargo manifest).
    main_rs = UPSTREAM / "apps/app/src/main.rs"
    replace_once(
        main_rs,
        '    let win = app.get_window("main").unwrap();\n',
        '    let win = app.get_window("main").unwrap();\n'
        '    #[cfg(target_os = "windows")]\n'
        '    if let Err(err) = win.set_icon(tauri::include_image!("icons/128x128.png")) {\n'
        '        tracing::warn!("Failed to set EternalLauncher taskbar icon: {err}");\n'
        '    }\n',
    )

    print("Removed profile upgrade upsell and configured Windows runtime taskbar icon.")

    print("Sakura branding applied to the desktop titlebar, splash, settings and CSS.")
    print("Icon conversion for Tauri is handled separately by the workflow.")


if __name__ == "__main__":
    main()
