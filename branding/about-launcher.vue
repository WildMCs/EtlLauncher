<script setup lang="ts">
import { Button } from '@modrinth/ui'
import { ref } from 'vue'

import eternalLogo from '@/assets/eternal-logo.png'
import { fetchEternalJson } from '@/features/news/eternal-remote-content'
import { openExternalUrl } from '@/platform/external-links'

import { eternalVersion, latestReleaseEndpoint, newerRelease } from './release-check'
import upstreamBuild from './upstream-build.json'

const update = ref<ReturnType<typeof newerRelease>>(null)
const state = ref<'idle' | 'checking' | 'current' | 'available' | 'error'>('idle')
const projectUrl = 'https://github.com/Wildlx3/EtlLauncher'
const links = [
	{ label: 'Eternal en GitHub', url: projectUrl },
	{ label: 'Privacidad de Eternal', url: projectUrl + '#política-de-privacidad' },
	{ label: 'Privacidad de Microsoft', url: 'https://www.microsoft.com/es-es/privacy/privacystatement' },
	{ label: 'Privacidad de Modrinth', url: 'https://modrinth.com/legal/privacy/' },
]

async function checkNow() {
	if (state.value === 'checking') return
	state.value = 'checking'
	update.value = null
	try {
		const payload = await fetchEternalJson(latestReleaseEndpoint, {
			maxBytes: 128_000,
			timeoutMs: 5000,
		})
		update.value = newerRelease(payload)
		state.value = update.value ? 'available' : 'current'
	} catch {
		state.value = 'error'
	}
}

function openLink(url: string) {
	void openExternalUrl(url).catch(console.error)
}
</script>

<template>
	<section class="eternal-about-launcher flex flex-col gap-4">
		<div class="flex items-center gap-4 border-0 border-b border-solid border-surface-5 pb-4">
			<img :src="eternalLogo" alt="" class="size-14 shrink-0 object-contain" />
			<h2 class="m-0 text-3xl font-semibold text-contrast">Eternal</h2>
		</div>
		<p class="m-0 text-primary">
			Proyecto comunitario basado en Modrinth App que personaliza la forma de organizar y jugar tus
			instancias de Minecraft.
		</p>
		<dl class="m-0 grid grid-cols-[auto_1fr] gap-x-4 gap-y-2">
			<dt class="text-secondary">Versión de Eternal</dt>
			<dd class="m-0 font-semibold text-contrast">v{{ eternalVersion }}</dd>
			<dt class="text-secondary">Base de Modrinth App</dt>
			<dd class="m-0 font-semibold text-contrast">{{ upstreamBuild.tag ?? 'No indicada en esta compilación' }}</dd>
		</dl>
		<div class="flex flex-col items-start gap-2">
			<Button type="colored" color="brand" :disabled="state === 'checking'" @click="checkNow">
				{{ state === 'checking' ? 'Buscando actualizaciones…' : 'Buscar actualizaciones' }}
			</Button>
			<div role="status" class="text-secondary">
				<p v-if="state === 'current'" class="m-0">No hay una versión estable más reciente.</p>
				<p v-else-if="state === 'error'" class="m-0">
					No se pudo consultar GitHub. Inténtalo de nuevo en un momento.
				</p>
				<p v-else-if="update" class="m-0">
					Está disponible la versión v{{ update.version }}.
					<a :href="update.url" class="text-brand underline" @click.prevent="openLink(update.url)">
						Ver versión en GitHub
					</a>
				</p>
			</div>
		</div>
		<div class="flex flex-wrap gap-x-4 gap-y-2">
			<a
				v-for="link in links"
				:key="link.url"
				:href="link.url"
				class="text-brand underline"
				@click.prevent="openLink(link.url)"
			>{{ link.label }}</a>
		</div>
	</section>
</template>
