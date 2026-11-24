<script setup lang="ts">
import { onUnmounted, ref } from 'vue'

import {
	getEternalWallpaperEffects,
	getEternalSidebarTransparency,
	addEternalWallpapers,
	listEternalWallpapers,
	removeEternalWallpaper,
	selectEternalWallpaper,
	setEternalWallpaperEffects,
	setEternalSidebarTransparency,
} from './eternal-wallpaper'
import {
	getEternalParticleChoice,
	getEternalParticleMotionOverride,
	getEternalWallpaperChoice,
	refreshWindowsWallpaper,
	setEternalParticleChoice,
	setEternalParticleMotionOverride,
	setEternalWallpaperChoice,
	type ParticleChoice,
	type WallpaperChoice,
} from './eternal-appearance'

const initialEffects = getEternalWallpaperEffects()
const darkness = ref(initialEffects.darkness)
const blur = ref(initialEffects.blur)
const sidebarTransparency = ref(getEternalSidebarTransparency())
const wallpaperChoice = ref<WallpaperChoice>(getEternalWallpaperChoice())
const particleChoice = ref<ParticleChoice>(getEternalParticleChoice())
const forceParticleMotion = ref(getEternalParticleMotionOverride())
const input = ref<HTMLInputElement | null>(null)
const gallery = ref<{ items: { id: string; name: string; preview?: string }[]; activeId: string | null }>({
	items: [],
	activeId: null,
})
let mounted = true
const busy = ref(false)
const error = ref('')
const notice = ref('')
function releasePreviews() {
	for (const item of gallery.value.items) {
		if (item.preview) URL.revokeObjectURL(item.preview)
	}
}
async function loadGallery() {
	const { items, activeId } = await listEternalWallpapers()
	if (!mounted) return
	releasePreviews()
	gallery.value = {
		activeId,
		items: items.map(({ id, name, thumbnail }) => ({
			id, name, preview: thumbnail ? URL.createObjectURL(thumbnail) : undefined,
		})),
	}
}
onUnmounted(() => {
	mounted = false
	releasePreviews()
})
void loadGallery().then(() => {
	wallpaperChoice.value = getEternalWallpaperChoice()
})

async function runWallpaperAction(action: () => Promise<void>, message = '') {
	if (busy.value) return
	busy.value = true
	error.value = ''
	notice.value = ''
	try {
		await action()
		await loadGallery()
		notice.value = message
	} catch (e) {
		error.value = typeof e === 'string' ? e : e instanceof Error ? e.message : 'No se pudo cambiar el fondo.'
	} finally {
		busy.value = false
	}
}

function selectImages(event: Event) {
	const element = event.target as HTMLInputElement
	const files = Array.from(element.files ?? [])
	element.value = ''
	if (!files.length) return
	void runWallpaperAction(() => addEternalWallpapers(files), 'Imágenes guardadas en tu galería.')
}

function updateEffects() {
	setEternalWallpaperEffects(darkness.value, blur.value)
}

function updateWallpaperMode(mode: WallpaperChoice) {
	wallpaperChoice.value = mode
	setEternalWallpaperChoice(mode)
	error.value = ''
	notice.value = ''
	if (mode === 'windows') void runWallpaperAction(refreshWindowsWallpaper)
}

function updateParticleMode() {
	setEternalParticleChoice(particleChoice.value)
}

function updateParticleMotionOverride() {
	setEternalParticleMotionOverride(forceParticleMotion.value)
}

function updateSidebarTransparency() {
	setEternalSidebarTransparency(sidebarTransparency.value)
}

</script>

<template>
	<section class="eternal-wallpaper-settings">
		<h3>Fondo de Eternal</h3>
		<div class="eternal-wallpaper-mode-group" role="group" aria-label="Fondo de pantalla" :aria-busy="busy">
			<button type="button" class="eternal-wallpaper-mode" :class="{ 'is-selected': wallpaperChoice === 'default' }" :aria-pressed="wallpaperChoice === 'default'" :disabled="busy" @click="updateWallpaperMode('default')">Sincronizado</button>
			<button type="button" class="eternal-wallpaper-mode" :class="{ 'is-selected': wallpaperChoice === 'sakura' }" :aria-pressed="wallpaperChoice === 'sakura'" :disabled="busy" @click="updateWallpaperMode('sakura')">Sakura</button>
			<button type="button" class="eternal-wallpaper-mode" :class="{ 'is-selected': wallpaperChoice === 'custom' }" :aria-pressed="wallpaperChoice === 'custom'" :disabled="busy" @click="updateWallpaperMode('custom')">Personalizado</button>
			<button type="button" class="eternal-wallpaper-mode" :class="{ 'is-selected': wallpaperChoice === 'windows' }" :aria-pressed="wallpaperChoice === 'windows'" :disabled="busy" @click="updateWallpaperMode('windows')">Escritorio de Windows</button>
		</div>
		<div v-if="wallpaperChoice === 'custom'" class="eternal-wallpaper-actions">
			<input
				ref="input"
				type="file"
				accept="image/jpeg,image/png,image/webp,image/gif"
				multiple
				class="eternal-wallpaper-file"
				aria-label="Seleccionar imágenes de fondo"
				@change="selectImages"
			/>
			<button type="button" class="eternal-wallpaper-primary" :disabled="busy" @click="input?.click()">
				{{ busy ? 'Procesando…' : 'Agregar imágenes o GIF' }}
			</button>
			<ul v-if="gallery.items.length" class="eternal-wallpaper-gallery" aria-label="Fondos guardados">
				<li v-for="item in gallery.items" :key="item.id">
					<button type="button" class="eternal-wallpaper-mode" :aria-pressed="item.id === gallery.activeId"
						:class="{ 'is-selected': item.id === gallery.activeId }" :disabled="busy" :title="item.name"
						@click="runWallpaperAction(() => selectEternalWallpaper(item.id))">
						<img v-if="item.preview" :src="item.preview" alt="" loading="lazy" />
						<span>{{ item.name }}</span>
					</button>
					<button type="button" class="eternal-wallpaper-secondary" :aria-label="'Quitar ' + item.name"
						:disabled="busy" @click="runWallpaperAction(() => removeEternalWallpaper(item.id))">Quitar</button>
				</li>
			</ul>
		</div>
		<div v-else-if="wallpaperChoice === 'windows'" class="eternal-wallpaper-actions">
			<button type="button" class="eternal-wallpaper-secondary" :disabled="busy" @click="runWallpaperAction(refreshWindowsWallpaper)">
				{{ busy ? 'Leyendo el escritorio…' : 'Actualizar desde Windows' }}
			</button>
		</div>
		<div class="eternal-wallpaper-effects">
			<div class="eternal-wallpaper-effect">
				<div class="eternal-wallpaper-effect-heading">
					<label for="eternal-wallpaper-darkness">Oscurecimiento</label>
					<output for="eternal-wallpaper-darkness">{{ darkness }}%</output>
				</div>
				<input
					id="eternal-wallpaper-darkness"
					v-model.number="darkness"
					type="range"
					min="0"
					max="100"
					step="1"
					@input="updateEffects"
				/>
			</div>
			<div class="eternal-wallpaper-effect">
				<div class="eternal-wallpaper-effect-heading">
					<label for="eternal-wallpaper-blur">Desenfoque</label>
					<output for="eternal-wallpaper-blur">{{ blur }} px</output>
				</div>
				<input
					id="eternal-wallpaper-blur"
					v-model.number="blur"
					type="range"
					min="0"
					max="24"
					step="1"
					@input="updateEffects"
				/>
			</div>
			<p class="eternal-wallpaper-hint">El oscurecimiento añade una capa oscura. El desenfoque suaviza únicamente el fondo, no los botones ni los textos.</p>
		</div>
		<p class="eternal-wallpaper-hint">Admite PNG, JPG, WebP y GIF (máx. 22 MB). Se verifica el formato real y la resolución. Las imágenes fijas admiten hasta 4096 px por lado y 16 MP; los GIF, hasta 1920 × 1080, 150 fotogramas y 100 MP acumulados. Se guardan localmente, nunca se suben a Internet.</p>
		<p v-if="error" class="eternal-wallpaper-error" role="alert">{{ error }}</p>
		<p v-else-if="notice" class="eternal-wallpaper-success" role="status">{{ notice }}</p>
	</section>
	<section class="eternal-wallpaper-settings">
		<h3>Animación del menú principal</h3>
		<p>Partículas ligeras sobre la biblioteca. Solo se animan en la pantalla principal y puedes desactivarlas.</p>
		<div class="eternal-appearance-selector">
			<label for="eternal-particle-mode">Estilo de partículas</label>
			<select id="eternal-particle-mode" v-model="particleChoice" @change="updateParticleMode">
				<option value="default">Sincronizado</option>
				<option value="none">Desactivadas</option>
				<option value="sakura">Sakura (pétalos)</option>
				<option value="lava">Lava (gotas)</option>
				<option value="otono">Otoño (hojas secas)</option>
				<option value="primavera">Primavera (hojas verdes)</option>
				<option value="navidad">Navidad (copos de nieve)</option>
			</select>
		</div>
		<label class="eternal-particle-motion-override" for="eternal-particle-force-motion">
			<input
				id="eternal-particle-force-motion"
				v-model="forceParticleMotion"
				class="eternal-particle-motion-input"
				type="checkbox"
				@change="updateParticleMotionOverride"
			/>
			<span class="eternal-particle-motion-track" aria-hidden="true"></span>
			<span class="eternal-particle-motion-text">Mostrar partículas aunque Windows tenga activado el movimiento reducido</span>
		</label>
		<p class="eternal-wallpaper-hint">Las opciones manuales no se sobrescriben con la configuración remota. Por defecto se respeta la reducción de movimiento de Windows; puedes permitir estas animaciones solo en Eternal mediante la opción anterior.</p>
	</section>
	<section class="eternal-wallpaper-settings">
		<h3>Panel derecho</h3>
		<p>Ajusta la transparencia de la zona de cuenta, amigos y noticias. Con 100 % el fondo de los paneles y su desenfoque desaparecen, pero los textos siguen visibles.</p>
		<div class="eternal-wallpaper-effects">
			<div class="eternal-wallpaper-effect">
				<div class="eternal-wallpaper-effect-heading">
					<label for="eternal-sidebar-transparency">Transparencia del panel derecho</label>
					<output for="eternal-sidebar-transparency">{{ sidebarTransparency }}%</output>
				</div>
				<input
					id="eternal-sidebar-transparency"
					v-model.number="sidebarTransparency"
					type="range"
					min="0"
					max="100"
					step="1"
					@input="updateSidebarTransparency"
				/>
			</div>
			<p class="eternal-wallpaper-hint">0 % conserva el cristal actual. 100 % muestra el fondo sin oscurecimiento adicional del panel derecho.</p>
		</div>
	</section>
</template>

<style scoped>
/* A real, accessible switch: the native checkbox remains focusable, but
 * its browser-specific appearance cannot clash with the Sakura input styles. */
.eternal-particle-motion-override {
  position: relative;
  display: flex;
  align-items: center;
  gap: .85rem;
  margin-top: 1rem;
  color: var(--color-contrast);
  cursor: pointer;
  line-height: 1.45;
  font-size: .88rem;
}
.eternal-particle-motion-input {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  margin: 0 !important;
  padding: 0 !important;
  opacity: 0 !important;
  clip-path: inset(50%);
  overflow: hidden;
}
.eternal-particle-motion-track {
  position: relative;
  display: block;
  flex: 0 0 48px;
  width: 48px;
  height: 28px;
  box-sizing: border-box;
  border-radius: 99px;
  border: 1px solid rgba(255, 221, 240, .22);
  background: rgba(15, 13, 24, .57);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, .18);
  transition: background-color .16s ease, border-color .16s ease;
}
.eternal-particle-motion-track::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #f5d4e5;
  box-shadow: 0 2px 5px rgba(0, 0, 0, .25);
  transition: transform .16s ease, background-color .16s ease;
}
.eternal-particle-motion-input:checked + .eternal-particle-motion-track {
  background: #e693b9;
  border-color: #f2b7d0;
}
.eternal-particle-motion-input:checked + .eternal-particle-motion-track::after {
  transform: translateX(20px);
  background: #fff;
}
.eternal-particle-motion-input:focus-visible + .eternal-particle-motion-track {
  outline: 2px solid var(--color-brand);
  outline-offset: 3px;
}
.eternal-particle-motion-text { flex: 1 1 auto; min-width: 0; }
@media (prefers-reduced-motion: reduce) {
  .eternal-particle-motion-track,
  .eternal-particle-motion-track::after { transition: none; }
}
@media (forced-colors: active) {
  .eternal-particle-motion-track { border-color: ButtonText; background: Canvas; }
  .eternal-particle-motion-track::after { background: ButtonText; }
  .eternal-particle-motion-input:checked + .eternal-particle-motion-track { border-color: Highlight; background: Highlight; }
  .eternal-particle-motion-input:checked + .eternal-particle-motion-track::after { background: HighlightText; }
}
.eternal-wallpaper-settings {
	margin-top: 1.5rem;
	padding: 1.25rem;
	border: 1px solid var(--brand-gradient-border);
	border-radius: 1rem;
	background: var(--color-raised-bg);
}
.eternal-wallpaper-mode-group { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .55rem; margin-top: .95rem; }
.eternal-wallpaper-mode { min-width: 0; padding: .75rem .5rem; border: 1px solid var(--eternal-glass-outline, rgba(255, 214, 236, .25)); border-radius: 13px; background: var(--color-button-bg); color: var(--color-contrast); font: inherit; font-weight: 600; cursor: pointer; transition: background-color .15s ease, border-color .15s ease; }
.eternal-wallpaper-mode:hover { background: var(--eternal-v3-quiet-hover, var(--color-button-bg-hover)); }
.eternal-wallpaper-mode.is-selected { color: #301827; background: #edabc9; border-color: #f6c7db; box-shadow: inset 0 1px 0 rgba(255,255,255,.43); }
.eternal-wallpaper-mode:focus-visible { outline: 2px solid var(--color-brand); outline-offset: 3px; }
@media (max-width: 520px) { .eternal-wallpaper-mode-group { gap: .3rem; } .eternal-wallpaper-mode { font-size: .82rem; padding: .7rem .2rem; } }
.eternal-appearance-selector { display: flex; flex-direction: column; gap: .45rem; margin-top: .9rem; }
.eternal-appearance-selector label { color: var(--color-contrast); font-size: .86rem; font-weight: 600; }
.eternal-appearance-selector select { width: 100%; max-width: 380px; border: 1px solid var(--brand-gradient-border); background: var(--color-button-bg); color: var(--color-contrast); border-radius: 12px; padding: .65rem .85rem; font: inherit; cursor: pointer; }
.eternal-appearance-selector select:focus-visible { outline: 2px solid var(--color-brand); outline-offset: 3px; }
.eternal-wallpaper-settings h3 {
	margin: 0 0 .5rem;
	font-size: 1.1rem;
	font-weight: 650;
	color: var(--color-contrast);
}
.eternal-wallpaper-settings p { color: var(--color-base); line-height: 1.5; }
.eternal-wallpaper-actions { display: flex; flex-wrap: wrap; gap: .6rem; margin-top: 1rem; }
.eternal-wallpaper-file { display: none; }
.eternal-wallpaper-gallery { width: 100%; list-style: none; margin: 0; padding: 0; display: grid; gap: .4rem; }
.eternal-wallpaper-gallery li { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: .45rem; }
.eternal-wallpaper-gallery .eternal-wallpaper-mode { display: flex; align-items: center; gap: .6rem; text-align: left; }
.eternal-wallpaper-gallery img { width: 64px; height: 40px; object-fit: cover; border-radius: 5px; }
.eternal-wallpaper-gallery span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.eternal-wallpaper-actions button {
	padding: .65rem .9rem;
	border-radius: .7rem;
	cursor: pointer;
	font-weight: 650;
}
.eternal-wallpaper-primary { background: var(--color-brand); color: var(--color-accent-contrast, #26141d); border: 1px solid var(--color-brand); }
.eternal-wallpaper-secondary { background: var(--color-button-bg); color: var(--color-contrast); border: 1px solid var(--color-button-bg-selected); }
.eternal-wallpaper-actions button:disabled { opacity: .5; cursor: not-allowed; }
.eternal-wallpaper-actions button:focus-visible { outline: 2px solid var(--color-brand); outline-offset: 3px; }
.eternal-wallpaper-hint { font-size: .78rem; }
.eternal-wallpaper-effects { display: flex; flex-direction: column; gap: .95rem; margin-top: 1.25rem; }
.eternal-wallpaper-effect { display: flex; flex-direction: column; gap: .4rem; }
.eternal-wallpaper-effect-heading { display: flex; justify-content: space-between; align-items: center; gap: 1rem; }
.eternal-wallpaper-effect-heading label { color: var(--color-contrast); font-size: .9rem; font-weight: 600; }
.eternal-wallpaper-effect-heading output { color: var(--color-brand); font-size: .85rem; font-variant-numeric: tabular-nums; }
.eternal-wallpaper-effect input[type="range"] { width: 100%; accent-color: var(--color-brand); cursor: pointer; }
.eternal-wallpaper-effect input[type="range"]:focus-visible { outline: 2px solid var(--color-brand); outline-offset: 3px; border-radius: .25rem; }
.eternal-wallpaper-error { color: var(--color-red, #f55) !important; }
.eternal-wallpaper-success { color: var(--color-brand) !important; }
</style>
