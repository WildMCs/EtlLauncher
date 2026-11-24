<script setup lang="ts">
import { HistoryIcon } from '@modrinth/assets'
import { FloatingMenu, IconButton } from '@modrinth/ui'
import { onMounted, shallowRef } from 'vue'

import { fetchEternalJson } from '@/features/news/eternal-remote-content'
import { openExternalUrl } from '@/platform/external-links'

import { checkReleaseOnStartup, latestReleaseEndpoint } from './release-check'

const update = shallowRef<Awaited<ReturnType<typeof checkReleaseOnStartup>>>(null)

onMounted(async () => {
	update.value = await checkReleaseOnStartup(window.localStorage, () =>
		fetchEternalJson(latestReleaseEndpoint, { maxBytes: 128_000, timeoutMs: 5000 }),
	)
})

function openRelease(event: MouseEvent, url: string): void {
	event.preventDefault()
	void openExternalUrl(url).catch(console.error)
}
</script>

<template>
	<FloatingMenu v-if="update" placement="bottom-end">
		<IconButton
			type="quiet"
			color="brand"
			label="Nueva versión de EternalLauncher"
			v-tooltip="'Nueva versión de EternalLauncher'"
		>
			<span class="eternal-release-glyph" aria-hidden="true">
				<HistoryIcon />
				<span class="eternal-release-petal" />
				<span class="eternal-release-alert">!</span>
			</span>
		</IconButton>
		<template #popper>
			<div class="max-w-64 p-3 text-sm">
				<p class="m-0 font-semibold text-contrast">Nueva versión de EternalLauncher</p>
				<p class="my-2 text-secondary">La versión v{{ update.version }} está disponible en GitHub.</p>
				<a :href="update.url" class="text-brand underline" @click="openRelease($event, update.url)">
					Ver versión en GitHub
				</a>
			</div>
		</template>
	</FloatingMenu>
</template>
