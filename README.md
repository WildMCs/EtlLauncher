# EternalLauncher — Sakura Edition 🌸

**EternalLauncher** es una compilación privada y no oficial de Modrinth App con parches propios. No está afiliada a Rinth, Inc. El repositorio conserva por ahora el nombre histórico `WildMCs/EtlLauncher`.

## Licencia y uso de IA

Los parches y el código propio de EternalLauncher se distribuyen bajo la [GNU General Public License, versión 3 únicamente (GPL-3.0-only)](LICENSE). EternalLauncher se basa en [Modrinth App](https://github.com/modrinth/code/tree/v0.23.5/apps/app), de Rinth, Inc. Los componentes de terceros conservan sus licencias y avisos, y las marcas y recursos de Modrinth están sujetos a sus [condiciones de uso](https://github.com/modrinth/code/blob/v0.23.5/COPYING.md).

Consulta cómo se usó IA durante el desarrollo en [AI-USAGE.md](AI-USAGE.md).

## Identidad

- **Ejecutable/instalador:** `EternalLauncher`.
- **Nombre mostrado dentro del launcher:** **Eternal** (barra superior, bienvenida, pantalla de carga y ajustes).
- **Discord Rich Presence:** identidad de la aplicación **EternalLauncher** y recurso de imagen `eternal_logo`, solo cuando se configura una aplicación propia de Discord (ver abajo).
- **Tema Sakura predeterminado:** cristal rosa con transparencias suaves, barra superior y laterales translúcidos, navegación redondeada y tarjetas ligeras. Conserva el icono personalizado. El modo OLED mantiene la marca rosa pero usa paneles negros.

## Tema Sakura Glass

La apariencia se aplica en cada compilación usando `branding/theme.css`. El selector de Modrinth incorpora **Sakura, OLED, Luz y Sistema**; **Sakura es el valor predeterminado**. Se conserva el enum nativo de Rust: Sakura utiliza un valor OLED compatible para los ajustes del sistema y una clave local para distinguir la apariencia escogida. Esto evita alterar la estructura de Minecraft.

- Fondo Sakura predeterminado integrado en el instalador como WebP (1920 × 1280). Funciona sin Internet y admite fotografía local alternativa.
- Barra superior, navegación izquierda y panel derecho con efecto de cristal rosa, mayor transparencia y reflejos blancos suaves.
- Tarjetas de instancias y «Continuar» translúcidas, con bordes más redondos; botones principales ligeramente más redondeados, conservando sus tamaños, tipografía y funcionamiento. **Sin desenfoque por tarjeta**, para no castigar bibliotecas grandes.
- Compatibilidad con modo claro/oscuro, reducción de transparencia y el ajuste de renderizado avanzado (desactiva el blur).
- Si el desenfoque no está disponible, quedan los colores semitransparentes de respaldo.

Para deshacer este aspecto, basta con revertir los cambios CSS de `branding/theme.css`; no afecta a instancias, mods o partidas. La apariencia definitiva aún debe revisarse en Windows después de que el workflow compile.


## Temas de menús de Eternal

**Sakura**: los cuadros de Ajustes, la creación de instancias, las tarjetas de exploración de Modrinth y la columna de filtros utilizan paneles color ciruela translúcidos, con botones rosados.

**OLED**: esas mismas superficies de menús se pintan en negro o gris muy oscuro. El inicio, las barras del launcher, la imagen de fondo y los acentos de acción siguen siendo Sakura. **Luz** y **Sistema** conservan su comportamiento original. No se introducen nuevos permisos de Windows ni se altera el sistema de instalación de mods.

Para que la apariencia siga siendo segura al actualizar, la nueva capa se aplica con `patches/sakura_themes.py` después de `patches/wallpaper_news_launcher.py`. Sus sustituciones exigen coincidencias únicas y detienen la compilación si el código upstream cambia. Es necesario validar la compilación Windows antes de publicar la siguiente Release.

## Ajustes visuales refinados

El panel izquierdo ahora tiene una **columna de 112 px y una barra Sakura de 88 px**, desplazada 16 px hacia el interior. Los controles redondos de Inicio y perfil caben completos en su borde. Los controles personalizados de la ventana, situados en la esquina superior derecha, y los menús desplegables de cuenta utilizan la misma paleta ciruela/rosa del launcher, incluidos los modos claro y alto contraste.

En **Ajustes → Apariencia → Fondo de Eternal**, puedes elegir **Sincronizado**, **Sakura**, **Personalizado** o **Escritorio de Windows**. En Personalizado puedes agregar varias imágenes o GIF a la vez y cambiar entre los fondos guardados. Los fondos mantienen el límite de **22 MiB** por archivo y los límites de resolución. El ajuste de partículas muestra **Sincronizado** en lugar de «Predeterminado (sincronizado)».

Las partículas se montan desde `branding/particles.vue` mediante Vue Teleport a una capa decorativa sobre Inicio (no dentro de las capas recortables del viewport). No usan observadores temporales ni capturan clics. Se muestran **22 partículas**; la opción Lava utiliza gotas luminosas con caída propia, sin el giro de los pétalos. Por defecto se respeta la reducción de movimiento de Windows, pero el usuario puede activar la casilla **«Mostrar partículas aunque Windows tenga activado el movimiento reducido»** en Ajustes → Apariencia. Esta elección solo afecta a Eternal, se almacena localmente en `eternal.particles.ignore-reduced-motion.v1` y **nunca** reactiva el modo «Desactivadas» ni anula los colores forzados de accesibilidad.

## Fondo personalizado

**Personalizado** tiene una galería local con hasta 12 imágenes JPG, PNG, WebP o GIF animados. Puedes elegir un fondo guardado o quitarlo de la galería. La selección se recupera al reiniciar Eternal.

Las imágenes fijas se reducen localmente a un máximo de 1920×1080 y se comprimen de forma asíncrona. Los fondos fijos y los GIF animados se guardan como archivos Blob en IndexedDB. Eternal también puede abrir los fondos guardados por versiones anteriores. Los archivos se mantienen en el dispositivo y se eliminan al borrar los datos del WebView.

**Escritorio de Windows** usa la imagen que Windows informa como fondo activo. La vista se actualiza cuando vuelves a Eternal o pulsas **Actualizar desde Windows**. Si Windows usa un color sólido o la imagen no cumple los límites y formatos admitidos, Eternal muestra Sakura.

### Validación de imágenes antes de aceptarlas

Tanto los archivos locales como las imágenes obtenidas de `appearance.json` deben pasar la **misma validación**. Límite de **22 MiB** en todos los formatos; extensiones permitidas `.png`, `.jpg`, `.jpeg`, `.webp` y `.gif`. Se comprueba la firma real (bytes del archivo), que coincida con la extensión y con el MIME declarado cuando esté disponible. Los archivos también deben superar la decodificación del WebView.

- **PNG/JPG/WebP estáticos**: hasta 4096 píxeles por lado **y** hasta 16 millones de píxeles en total. WebP animado y PNG animado (APNG) se rechazan para impedir que eludan los límites de fotogramas; para animaciones se admite GIF con los límites siguientes.
- **GIF**: hasta 1920 × 1080, como máximo 150 fotogramas y un máximo acumulado de 100 millones de píxeles de fotogramas. Se valida su estructura, paletas y bloques antes de pedir al navegador que lo abra. La animación se conserva intacta.
- **Fondos remotos**: solo HTTPS y el mismo origen que el archivo `appearance.json`, sin redirecciones. Se valida el flujo de descarga mientras llega (límite real de 22 MiB aunque falte `Content-Length`), formato, dimensiones y decodificación **antes** de aplicar el fondo. Si falla, se muestra Sakura integrado.
- **Seguridad**: estos controles mitigan archivos malformados y problemas de recursos, pero no sustituyen las actualizaciones del motor de imágenes/WebView2, ni garantizan ausencia total de vulnerabilidades.

Ejecuta `node --test` con Node 24 para comprobar la validación de imágenes y los límites de las descargas. GitHub Actions ejecuta estas pruebas en un trabajo separado, incluso cuando la caché permite omitir la compilación.

En **Ajustes → Apariencia → Fondo de Eternal**, dos deslizadores se aplican en tiempo real al fondo predeterminado o al personalizado: **Oscurecimiento** (capa oscura, 0–100 %) y **Desenfoque** (0–24 px, solo sobre la imagen). Reemplazamos el antiguo desvanecimiento por desenfoque. Se conserva el oscurecimiento de instalaciones anteriores; los nuevos ajustes se guardan localmente y persisten al reiniciar.

En esa misma pantalla, el bloque **Panel derecho** permite ajustar la **Transparencia del panel derecho** de 0 a 100 %. Al 0 % conserva la opacidad actual de cuenta, amigos y noticias. Al 100 % elimina sus fondos de cristal y el blur, sin desvanecer los textos; los controles siguen siendo funcionales. El valor se guarda localmente. La barra de navegación izquierda también es un poco más ancha y está desplazada hacia la derecha para que los iconos seleccionados no se recorten.

El archivo de fondo está incluido como `branding/default-sakura.webp.b64` para que GitHub pueda almacenar la imagen sin un plugin adicional; `patches/brand_launcher.py` lo descodifica como `apps/app-frontend/public/eternal-default-sakura.webp` durante la compilación. Para cambiar el fondo integrado en otra versión, sustituye el Base64 por otra imagen WebP.

## Animaciones y opciones sincronizadas

En **Ajustes → Apariencia → Animación del menú principal**, las partículas son opcionales y solo aparecen en la biblioteca de inicio. Se incluyen seis opciones: **Predeterminado (sincronizado)**, **Sakura**, **Lava**, **Otoño**, **Primavera**, **Navidad**, además de **Desactivadas**. Son 18 partículas decorativas CSS; no contienen scripts remotos, no interceptan clics y se desactivan automáticamente cuando el sistema pide reducir el movimiento.

Los modos **Predeterminado** del fondo y de las partículas leen al iniciar el launcher, una única vez, el archivo público `appearance.json` del mismo dominio que `branding/news-config.json`. Con la URL configurada actualmente, es `https://new.etlservers.moe/appearance.json`. El archivo en GitHub es `public-news/appearance.json` y Cloudflare Pages lo publica junto con las noticias. No hay comprobaciones periódicas: los cambios remotos entran al **volver a abrir Eternal**.

Ejemplo de configuración pública:

```json
{
  "version": 1,
  "wallpaper": "/wallpapers/default.webp",
  "particles": "sakura"
}
```

Para usar la ilustración remota, sube `public-news/wallpapers/default.webp` a GitHub; Pages la publicará en `https://new.etlservers.moe/wallpapers/default.webp`. La ruta puede apuntar a JPG, PNG, WebP o GIF del **mismo dominio HTTPS**. Si `wallpaper` queda vacío, la URL falla o no hay conexión, usa el Sakura integrado como respaldo. Si la persona elige **Sakura** o **Personalizado**, el fondo remoto deja de tener prioridad; si escoge una animación concreta o **Desactivadas**, la animación remota también deja de tener prioridad. Son dos opciones independientes y locales.

Valores admitidos en `particles`: `"sakura"`, `"lava"`, `"otono"`, `"primavera"`, `"navidad"` o `"none"`. Se consulta únicamente JSON pequeño (máximo 4 KB) por HTTPS; los enlaces de fondo quedan restringidos al mismo origen, sin HTML, JavaScript ni acceso al sistema de archivos.

En **Ajustes → Apariencia**, el selector de colores muestra **Sakura**, **OLED**, **Luz** y **Sincronizar con el sistema**. En una instalación nueva y durante la migración desde la antigua edición de cristal rosa se prefiere Sakura. En OLED se conservan el fondo, la marca y los botones rosa de Eternal, pero los menús de Ajustes, creación de instancias y exploración de modpacks utilizan superficies negras. La selección local se guarda en `eternal.theme.choice.v1`; el backend nativo de Modrinth continúa recibiendo únicamente temas admitidos por su enum, y la sincronización de cuenta representa Sakura mediante OLED.

## Noticias remotas (sin actualizar el ejecutable)

El panel lateral carga noticias desde un archivo JSON público por HTTPS. Consulta al abrir y cada 15 minutos mientras esté abierto; permite actualización manual. Guarda un caché local con las últimas noticias válidas. Sin URL configurada, sin conexión o sin datos en caché, aparece la bienvenida incluida en el instalador.

### Publicarlo con Cloudflare Pages

1. Crea un proyecto **Cloudflare Pages** conectado a este repositorio privado de GitHub (el sitio publicado será público).
2. Selecciona la rama `main`, **sin comando de compilación**, y establece **`public-news` como directorio de salida**. El archivo `public-news/_headers` configura CORS y un tiempo corto de caché.
3. Abre la URL generada por Pages, por ejemplo `https://TU-PROYECTO.pages.dev/news.json`, y verifica que responde con JSON válido. También puedes utilizar un dominio personalizado propio.
4. Edita **`branding/news-config.json`** y pega la URL pública completa en el campo `url`. Compila **una vez**; el parche permite ese origen HTTPS en la política CSP de Tauri.
5. Para publicar noticias futuras, **solo edita `public-news/news.json`**. Cloudflare Pages publicará el JSON y los EternalLauncher instalados recibirán los cambios en su próxima consulta; no necesitan recompilarse.

Formato del archivo: `{ "version": 1, "updated_at": "AAAA-MM-DD", "items": [{ "id": "novedad", "title": "Título", "body": "Contenido de texto", "date": "AAAA-MM-DD", "url": "https://enlace-opcional" }] }`.

Las noticias se muestran como texto plano, con un máximo de cinco entradas. La descarga se cancela al superar 100 000 bytes y usa HTTPS sin cookies ni redirecciones. Cada enlace muestra el dominio que se abrirá. Si la URL queda vacía o no hay acceso a Internet, Eternal usa las últimas noticias guardadas o la bienvenida integrada.

## Rendimiento del workflow

El workflow conserva la optimización anterior que **salta versiones de Modrinth ya compiladas**, y ahora también:

- Conserva las descargas de **pnpm** mediante `actions/cache@v4`.
- Reutiliza compilaciones de dependencias **Rust/Cargo** mediante `Swatinem/rust-cache@v2`.
- Escribe en el **resumen de GitHub Actions** el tiempo real de instalación de pnpm y compilación Tauri/NSIS, además del acierto de caché pnpm.

La primera compilación que crea las cachés puede tardar lo mismo o más. Las mejoras reales deben comprobarse en la segunda ejecución comparable. No se ha medido todavía un tiempo de referencia confiable ni se garantiza una reducción concreta.

## Cambios de interfaz y privacidad

- Oculta la entrada de **Modrinth Hosting** del menú lateral. Mantiene las APIs necesarias para instalaciones, descargas y funciones online; **no** modifica el servicio de pago ni elimina todo el código de Hosting.
- Sustituye el panel lateral de noticias por la **bienvenida editable a la primera versión**. No realiza peticiones para cargar noticias en ese panel.
- Oculta publicidad y la opción de suscripción Modrinth+ del menú de perfil.
- Desactiva el actualizador oficial para no sustituir la versión personalizada.
- Desactiva la inicialización de Sentry y fuerza la telemetría opcional a OFF. Las conexiones necesarias con Modrinth/Minecraft siguen funcionando.

## Personalizar la bienvenida

Edita **`branding/welcome.json`** (texto del encabezado, título, descripción, lista de características y mensaje final). La próxima compilación incorporará los cambios. El componente visual está en `branding/welcome-sidebar.vue`; no necesitas modificar los archivos descargados de Modrinth.

## Discord Rich Presence — EternalLauncher

El parche ya incorpora el **Application ID** público `1269391023797436426` para las compilaciones nuevas. También puedes sustituirlo más adelante mediante la variable de GitHub Actions `ETERNAL_DISCORD_CLIENT_ID`, sin editar el parche.

Mensajes personalizados:

- **Sin jugar:** `Ausente (｡-ω-) zzZ` y `Disfrutando de un descansito 🌸`.
- **Jugando a una instancia:** `Jugando: {nombre de la instancia}` y `¡De aventura! (ง •̀ω•́)ง`.
- **Logo (tooltip):** `EternalLauncher 🌸`.

Discord muestra el **nombre de aplicación** registrado en el Developer Portal: debe llamarse **EternalLauncher**. En **Rich Presence / Art Assets**, sube el [logo de 512 px](branding/icons/512.png) con la clave exacta `eternal_logo`. El recurso puede tardar en aparecer en Discord. [Discord Developer Portal](https://discord.com/developers/applications)

No hace falta un bot, un token ni abrir puertos. La opción Discord Rich Presence sigue siendo configurable desde **Privacidad**, y necesitarás reiniciar el launcher tras cambiarla. Aún falta comprobar el resultado visual en una compilación real.

## Construir

### Plantilla de iconos

El [PNG maestro](public-news/IconApp/Modrith_rosita_fresita.png) conserva la resolución original y la transparencia. La carpeta [`branding/icons/`](branding/icons/) contiene PNG cuadrados de 16, 24, 32, 40, 48, 64, 96, 128, 256 y 512 px. El launcher y el instalador de Windows usan [`EternalLauncher.ico`](branding/icons/EternalLauncher.ico), que reúne los tamaños de 16 a 256 px.

Para regenerar los archivos desde la raíz del repositorio, instala Pillow y ejecuta el generador. Cada tamaño se calcula desde el maestro y se guarda con compresión sin pérdida.

```powershell
python -m pip install Pillow
python branding/generate_icons.py
```

El generador también acepta otro PNG como argumento y `--output` para exportar a una carpeta distinta. Para actualizar el logo del proyecto, guarda el nuevo maestro, regenera `branding/icons/` e incluye ambos cambios en la siguiente compilación.

### Instalar en Windows

Descarga el instalador NSIS de Windows x64 de la Release que te compartieron. Compara su SHA-256 con `SHA256SUMS.txt` y ejecuta el instalador. Lee la política de privacidad en español y pulsa **Leído** para continuar. El asistente incluye el texto original de la licencia GPLv3. Una vez instalado, abre **EternalLauncher** desde Inicio. El instalador usa una carpeta de aplicación propia y guarda los datos del launcher en `%APPDATA%\com.eternal.launcher`. La compilación de desarrollo local usa un perfil aparte.

### Generar el instalador con GitHub Actions

1. Abre **Actions → Build EternalLauncher (experimental) → Run workflow**.
2. Descarga el artefacto `EternalLauncher-vX.Y.Z-windows-x64` cuando termine correctamente.
3. Extrae el instalador `.exe` y haz una copia de seguridad de las instancias antes de instalar.

Las compilaciones manuales y las de `main` usan `MODRINTH_TAG` y `MODRINTH_COMMIT`, fijados en `.github/workflows/build.yml`. Cada seis horas, el workflow comprueba la última versión estable de Modrinth y compila el commit correspondiente si no hay una compilación en caché. Para actualizar la base de Eternal, cambia el tag y el SHA después de revisar que los parches se apliquen y probar el instalador. Las publicaciones manuales desde `main` registran el commit exacto de Modrinth y el commit de Eternal.

## Publicar una Release privada

En **Run workflow**, marca **Publish a private GitHub Release after the build succeeds** para publicar el instalador y su comprobación SHA-256 en https://github.com/WildMCs/EtlLauncher/releases. Las publicaciones se marcan como versiones experimentales; las automáticas no publican Releases por sí solas.

### Archivos para GitHub

Incluye `.github/workflows/build.yml`, `.gitignore`, `README.md`, `branding/`, `patches/`, `public-news/` y `tests/`. Esto incluye los archivos nuevos del fondo de Windows y cualquier eliminación intencional en `public-news/`. Los scripts de desarrollo de esta máquina viven en `scripts/` y Git los ignora. Publica el instalador y su SHA-256 como archivos de la Release. El acceso a una Release de un repositorio privado depende de los permisos de acceso al repositorio.

## Estructura

- `.github/workflows/build.yml`: descarga el código oficial, aplica los parches, genera los iconos y compila NSIS.
- `patches/patch_launcher.py`: nombre del ejecutable, anuncios y actualizador.
- `patches/brand_launcher.py`: marca interna Eternal, iconos, colores y promoción del perfil.
- `patches/eternal_features.py`: Hosting en navegación, bienvenida editable y Discord Rich Presence.
- `patches/privacy_launcher.py`: privacidad de la compilación.
- `branding/icons/` y `branding/generate_icons.py`: iconos listos para usar y generador de la plantilla.
- `branding/theme.css`: tema Sakura Glass (CSS únicamente, sin motor de temas).
- `branding/welcome.json`, `branding/welcome-sidebar.vue` y `branding/news-config.json`: bienvenida y noticias remotas.
- `public-news/news.json` y `public-news/_headers`: archivos listos para publicar en Cloudflare Pages.
- `branding/wallpaper.ts`, `branding/wallpaper-settings.vue`: selección y persistencia local del fondo.
- `patches/wallpaper_news_launcher.py`: añade la opción de fondo a Apariencia y configura el origen HTTPS de noticias.

## Avisos y compatibilidad

- El instalador usa el identificador `com.eternal.launcher` y un perfil propio. Los archivos `.mrpack` se pueden importar desde el launcher. La instalación evita registrar las asociaciones de archivos y enlaces de Modrinth en Windows.
- No hay firma comercial: Windows podría advertir sobre aplicaciones desconocidas.
- EternalLauncher es una distribución independiente. Para redistribuir el instalador, conserva los avisos de licencia y ofrece el código fuente correspondiente al binario, incluyendo el commit base y los parches. Verifica los derechos de redistribución del icono, las imágenes y cualquier recurso de marca incluido. [Licencia del launcher base](https://github.com/modrinth/code/blob/e30eb38e77566cbca6502dad93142d5ba892cd87/apps/app/LICENSE) · [Pautas de marcas de Modrinth](https://github.com/modrinth/code/blob/e30eb38e77566cbca6502dad93142d5ba892cd87/COPYING.md)
- Las nuevas personalizaciones requieren verificar una compilación y su aspecto en Windows antes de considerarlas estables.


## Pulido visual específico de Eternal (v4.4)

El paso guardado `patches/ui_polish.py` se ejecuta después de los temas y **antes** de compilar: identifica los botones de Detener de las tarjetas de instancias (también las variantes antiguas), el recuadro de Añadir skin y las páginas de perfil de usuario. Si alguna estructura cambia en Modrinth, la compilación se detiene antes de publicar un instalador parcialmente modificado.

- **Detener** conserva su comportamiento original, con degradado rojo y un borde rojo oscuro propio; los demás botones mantienen su apariencia.
- La opción de **mostrar partículas con movimiento reducido** tiene un switch accesible con indicador de enfoque visible y la misma preferencia local de siempre.
- **Skins** muestra bordes rosas de selección y enfoque dentro de la tarjeta, para que la lista virtualizada no los recorte.
- **Perfiles de usuario** conserva las insignias y organizaciones en la barra derecha y muestra también la sección habitual de cuenta, amigos y noticias. No altera las rutas ni los datos de perfil.

Cambios únicamente de frontend/CSS; se deben validar visualmente en Windows después de que GitHub Actions complete la compilación.
## Política de privacidad

**Versión del 23 de noviembre de 2026.** Esta política describe cómo funciona esta distribución de EternalLauncher para Windows, una compilación independiente basada en Modrinth App.

- **Cuenta de Minecraft.** Eternal abre el formulario de Microsoft en una ventana web para iniciar sesión. El flujo del launcher recibe un código OAuth y obtiene las credenciales de sesión necesarias para consultar el perfil, comprobar el acceso a Minecraft y renovar la sesión. Eternal no solicita ni guarda tu contraseña de Microsoft. Los tokens de acceso y renovación se guardan en la base SQLite local `app.db` sin cifrado propio del launcher. Protege esa carpeta y sus copias de seguridad. La cuenta opcional de Modrinth usa su propio flujo y sus propios tokens. [Inicio de sesión de Minecraft](https://support.modrinth.com/en/articles/9038231-minecraft-sign-in-issues) · [Privacidad de Microsoft](https://www.microsoft.com/es-es/privacy/privacystatement) · [Privacidad de Modrinth](https://modrinth.com/legal/privacy/)
- **Datos locales.** Los perfiles, partidas, ajustes, credenciales de sesión, registros de diagnóstico y fondos se conservan en el equipo. Las imágenes de tu galería y del escritorio de Windows se procesan localmente. El parche de Eternal desactiva la analítica opcional y los reportes de errores de Sentry. Si compartes un diagnóstico por tu cuenta, revisa su contenido y evita adjuntar `app.db`, sus respaldos o cualquier token.
- **Conexiones externas.** Microsoft, Xbox, Minecraft y Modrinth reciben las peticiones necesarias para el inicio de sesión, el catálogo, las descargas y otras funciones en línea que uses. El servidor de noticias y apariencia recibe las solicitudes de esos archivos, con datos de conexión como la dirección IP. Si activas Discord Rich Presence, Discord puede mostrar tu actividad y el nombre de la instancia. Puedes desactivar esa integración en **Ajustes → Privacidad**. [Privacidad de Discord](https://discord.com/privacy)
- **Control y eliminación.** Desde el launcher puedes quitar tus cuentas guardadas y eliminar fondos de tu galería. También puedes revisar y revocar permisos en tu cuenta de Microsoft. Para borrar el perfil local completo, cierra Eternal, respalda las partidas que quieras conservar y elimina `%APPDATA%\com.eternal.launcher` y `%LOCALAPPDATA%\com.eternal.launcher`. La segunda carpeta incluye el almacenamiento del WebView y puede contener respaldos de la base en `Backups\app-db`. [Permisos de la cuenta Microsoft](https://account.live.com/consent/Manage)
- **Contacto y cambios.** Para consultas de privacidad, contacta al responsable de la distribución de EternalLauncher por el canal por el que recibiste el instalador. Los cambios de esta política se publicarán en este README. Para datos que administra un servicio externo, consulta su propia política y sus canales de soporte.
