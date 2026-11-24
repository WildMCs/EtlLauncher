#!/usr/bin/env python3
"""Small, guarded UI fixes for EternalLauncher on Modrinth App v0.23.5.

No changes to game launching, skin selection, user data, or Rust.
Patch only well-known Vue markers; fail the build if upstream changes.
"""
from __future__ import annotations

import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
FRONTEND = BASE / "upstream/apps/app-frontend/src"


def replace_once(path: Path, before: str, after: str) -> None:
    source = path.read_text(encoding="utf-8")
    found = source.count(before)
    if found != 1:
        raise RuntimeError(
            f"Eternal UI polish: expected one occurrence in {path.name}, "
            f"found {found}: {before[:72]!r}"
        )
    path.write_text(source.replace(before, after, 1), encoding="utf-8")


def mark_icon(match: re.Match[str], icon: str, marker: str) -> str:
    attrs = match[1]
    attrs, count = re.subn(r' class="([^"]*)"', rf' class="{marker} \1"', attrs, count=1)
    if not count:
        attrs = f' class="{marker}"' + attrs
    return f'<{icon}{attrs.rstrip()} />'


def style_game_actions() -> None:
    paths = (
        "components/ui/library/instance-group/instance-card.vue",
        "components/ui/Instance.vue",
        "components/ui/world/InstanceItem.vue",
        "components/ui/world/WorldItem.vue",
        "pages/instance/components/page-header/index.vue",
    )
    for relative in paths:
        path = FRONTEND / relative
        source = path.read_text(encoding="utf-8")
        for icon, marker in (("PlayIcon", "eternal-play-glyph"), ("StopCircleIcon", "eternal-stop-glyph")):
            source, count = re.subn(
                rf'<{icon}(?=[\s/>])([^<>]*?)/>',
                lambda match: mark_icon(match, icon, marker),
                source,
            )
            if not count:
                raise RuntimeError(f"Eternal UI polish: missing {icon} in {relative}")
        path.write_text(source, encoding="utf-8")

    replace_once(
        FRONTEND / "components/ui/world/InstanceItem.vue",
        ':disabled="playDisabled"\n\t\t\t\t\t\ttype="colored"',
        'class="eternal-play-action"\n\t\t\t\t\t\t:disabled="playDisabled"\n\t\t\t\t\t\ttype="colored"',
    )
    replace_once(
        FRONTEND / "components/ui/world/WorldItem.vue",
        'v-else-if="showPlayButton"\n\t\t\t\t\t\tv-tooltip="playTooltip"',
        'v-else-if="showPlayButton"\n\t\t\t\t\t\tclass="eternal-play-action"\n\t\t\t\t\t\tv-tooltip="playTooltip"',
    )

    replace_once(
        FRONTEND / "app/shell/title-bar/action-bar.vue",
        'class="flex border-solid border-surface-5 text-sm font-medium',
        'class="eternal-instance-status flex border-solid border-surface-5 text-sm font-medium',
    )
    replace_once(
        FRONTEND / "app/shell/title-bar/breadcrumbs.vue",
        'class="size-5 shrink-0 text-primary"\n\t\t\t\t\t\taria-hidden="true"',
        'class="size-5 shrink-0 text-primary"\n'
        "\t\t\t\t\t\t:class=\"{ 'eternal-home-glyph': breadcrumb.id === 'home' }\"\n"
        '\t\t\t\t\t\taria-hidden="true"',
    )
    replace_once(
        FRONTEND / "App.vue",
        '<PlayIcon class="ml-0.5" />',
        '<PlayIcon class="eternal-home-glyph ml-0.5" />',
    )


def mark_content_glass() -> None:
    content = BASE / "upstream/packages/ui/src/layouts/shared/content-tab"
    replace_once(
        content / "layout.vue",
        'class="@container flex items-start gap-2"',
        'class="eternal-content-toolbar @container flex items-start gap-2"',
    )
    table = content / "components/ContentCardTable.vue"
    replace_once(
        table,
        'class="@container relative border border-solid border-surface-4 shadow-sm overflow-clip"',
        'class="eternal-content-table @container relative border border-solid border-surface-4 shadow-sm overflow-clip"',
    )
    replace_once(
        table,
        'class="sticky top-0 z-10 grid grid-cols-[var(--content-columns)]',
        'class="eternal-content-table-header sticky top-0 z-10 grid grid-cols-[var(--content-columns)]',
    )
    browse = content.parent / "browse-tab/layout.vue"
    replace_once(
        browse,
        'v-if="ctx.showProjectTypeTabs.value"',
        'v-if="ctx.showProjectTypeTabs.value"\n\t\tclass="eternal-browse-tabs"',
    )
    replace_once(
        browse,
        'wrapper-class="w-full"\n\t\tsize="large"',
        'wrapper-class="eternal-browse-search w-full"\n\t\tsize="large"',
    )
    replace_once(
        browse,
        '<div class="flex flex-wrap items-center gap-2">\n\t\t<Combobox',
        '<div class="eternal-browse-toolbar flex flex-wrap items-center gap-2">\n\t\t<Combobox',
    )
    replace_once(
        browse,
        '<ProjectCardList v-else :layout="ctx.effectiveLayout.value">',
        '<ProjectCardList v-else class="eternal-browse-results" :layout="ctx.effectiveLayout.value">',
    )


def remove_ad_report() -> None:
    path = FRONTEND / "features/settings/system/troubleshooting-settings.vue"
    source = path.read_text(encoding="utf-8")
    for before, after in (
        ("\tCheckIcon,\n", ""),
        ("\tCopyIcon,\n", ""),
        ("\tLoaderCircleIcon,\n", ""),
        ("\tinjectPageContext,\n", ""),
        ("\tIntlFormatted,\n", ""),
        ("import { openUrl } from '@tauri-apps/plugin-opener'\n", ""),
        ("import { get_ads_debug_state } from '@/helpers/ads.js'\n", ""),
        ("import { useCopyAsPaste } from '@/shared/composables/use-copy-as-paste'\n", ""),
        ("const { addNotification, handleError }", "const { handleError }"),
        ("const { adConsentAvailable } = injectPageContext()\n", ""),
        ("const copyAsPaste = useCopyAsPaste()\n", ""),
        ("const copyingAdDetails = ref(false)\nconst copiedAdDetails = ref(false)\n", ""),
    ):
        if source.count(before) != 1:
            raise RuntimeError(f"Eternal UI polish: missing ad-report marker {before!r}")
        source = source.replace(before, after, 1)
    for start, end in (
        ("\treportAdTitle: {", "\tappCacheTitle: {"),
        ("\nfunction openSupport() {", "</script>"),
        (
            '\t\t<div class="flex flex-col gap-2.5">\n'
            '\t\t\t<h2 class="m-0 text-lg font-semibold text-contrast">\n'
            "\t\t\t\t{{ formatMessage(messages.reportAdTitle) }}",
            '\t\t<div class="flex items-center justify-between gap-4">',
        ),
    ):
        begin = source.index(start)
        finish = source.index(end, begin + len(start))
        source = source[:begin] + source[finish:]
    path.write_text(source, encoding="utf-8")


def main() -> None:
    style_game_actions()
    mark_content_glass()
    remove_ad_report()
    replace_once(
        FRONTEND / "components/ui/library/library-toolbar/index.vue",
        '<Button type="colored" color="brand" @click="showCreationModal?.()">',
        '<Button class="eternal-play-action" type="colored" color="brand" @click="showCreationModal?.()">',
    )

    # The add-skin tile's focus outline protrudes outside the virtual grid.
    # A named class lets CSS render the highlight INSIDE the tile instead.
    skin_list = FRONTEND / "components/ui/skin/VirtualSkinSectionList.vue"
    replace_once(
        skin_list,
        'ref="addSkinButton"\n'
        '\t\t\t\t\t\t\tclass="aspect-[31/40] w-full min-w-0 box-border rounded-[20px]"',
        'ref="addSkinButton"\n'
        '\t\t\t\t\t\t\tclass="eternal-skin-add-card aspect-[31/40] w-full min-w-0 box-border rounded-[20px]"',
    )

    # Profile pages teleport badges to the right sidebar. They hide the
    # standard account/friends/news blocks even when that content is empty.
    # Add a route-specific marker; CSS will show BOTH sets of content.
    profile = FRONTEND / "pages/User.vue"
    replace_once(
        profile,
        '<div class="w-full p-2">',
        '<div class="eternal-user-profile-page w-full p-2">',
    )
    print("Eternal: game controls, content glass, skin focus and profile sidebar markers installed.")


if __name__ == "__main__":
    main()
