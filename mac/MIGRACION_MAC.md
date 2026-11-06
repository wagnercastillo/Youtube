# Mudanza a la Mac mini M4 + producción nocturna automática

Todo lo de Puro Chisme se regenera en la Mac con 3 piezas: **el repo de GitHub** (código, episodios, reglas, skill
nocturna), **puro-chisme-claude.zip** (skills de Claude Code, memoria, configuración) y **puro-chisme-SECRETOS.zip**
(claves). Los videos renderizados no hacen falta: están en YouTube y se pueden volver a renderizar.

## A. En la computadora vieja (Windows)
1. Apaga la VPN. En Git Bash, desde el repo: `python -I mac/exportar_desde_windows.py`
   → crea en el Escritorio `puro-chisme-claude.zip` y `puro-chisme-SECRETOS.zip`.
2. Pasa los dos zips a la Mac **por USB o AirDrop** (el de SECRETOS nunca por correo, chat ni GitHub).
3. `git push` para que el repo esté al día.

## B. En la Mac mini
1. Abre Terminal y clona el repo:
   ```bash
   mkdir -p ~/Documents/GitHub && cd ~/Documents/GitHub
   git clone https://github.com/wagnercastillo/Youtube.git YouTube
   ```
   (si el repo es privado: `brew install gh && gh auth login` primero)
2. Deja los dos zips en `~/Downloads` y corre: `bash ~/Documents/GitHub/YouTube/mac/setup_mac.sh`
   Instala Homebrew, Node, Python 3.12, ffmpeg, Chrome, Claude Code, los entornos `~/.chatterbox-py` y `~/.manim-py`,
   copia skills/memoria/claves, instala los plugins y deja programada la producción nocturna.
3. Inicia sesión en Claude Code: `cd ~/Documents/GitHub/YouTube && claude` (una vez, con tu cuenta).
4. Borra `~/Downloads/puro-chisme-SECRETOS.zip` y vacía la papelera.
5. Ajustes del Sistema → Energía: activa **"Evitar que la Mac entre en reposo automáticamente"** y
   **"Arrancar automáticamente después de un corte de luz"**. Deja la Mac conectada a internet por cable si puedes.
6. Prueba que todo funciona antes de dejarlo solo:
   ```bash
   cd ~/Documents/GitHub/YouTube/episodios/ep09-plaga-del-baile && npx hyperframes check && npm run render
   cd ~/.claude/skills/youtube-uploader/scripts && npx ts-node check-video.ts 56edefRgceM
   ```
   Si la autorización de YouTube venció: `npx ts-node youtube-upload.ts --auth` (abre el navegador).

## C. Lo que cambia en macOS
| Windows | Mac |
|---|---|
| `~/.chatterbox-py/Scripts/python.exe` | `~/.chatterbox-py/bin/python` |
| `~/.manim-py/Scripts/manim.exe` | `~/.manim-py/bin/manim` |
| Chrome en `C:/Program Files/...` | `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"` |
| Bug del `npx` con argumentos acentuados | No existe, pero seguimos usando archivos para descripción y etiquetas |
| statusLine de caveman en PowerShell | No se copia; el plugin caveman funciona sin él |

## D. Producción nocturna
- **Cuándo:** todos los días a las 00:30 (hora de la Mac) launchd ejecuta `mac/nightly/run_nightly.sh`, que corre
  `claude -p "/produccion-nocturna"` sin permisos interactivos.
- **Qué hace** (`.claude/skills/produccion-nocturna/SKILL.md`): elige 3 temas distintos y verificados, produce los 3
  episodios con formatos diferentes, revisa voz/cuadros/volumen, los sube PRIVADOS y programados a las
  12 pm, 4 pm y 8 pm CDMX, hace commit + push y escribe `reportes/AAAA-MM-DD.md`.
- **Control del dueño:**
  - Por la mañana lee `reportes/` (o en GitHub). Los videos siguen privados hasta su hora: si uno no te gusta, en
    YouTube Studio quítale la programación o bórralo antes de las 12 pm.
  - Pausar: `touch ~/Documents/GitHub/YouTube/mac/nightly/PAUSA` · Reanudar: borra ese archivo.
  - Correr ya (prueba): `launchctl start com.purochisme.nocturno` · Logs: `~/Library/Logs/purochisme/`.
  - Desactivar del todo: `launchctl unload ~/Library/LaunchAgents/com.purochisme.nocturno.plist`.
- **Límites a vigilar:**
  - Uso de tu plan de Claude: 3 videos completos por noche es mucho trabajo; si se acaba el límite, la noche queda a
    medias (el reporte lo dirá). Empieza revisando las primeras noches.
  - Créditos de ElevenLabs (voz + música + efectos de 3 videos diarios) y su límite de 10 voces propias.
  - Cuota de la API de YouTube: 10 000 unidades/día; 3 subidas ≈ 5 000. Alcanza.
  - Miniaturas: hasta que el canal tenga "funciones intermedias", la API las rechaza y hay que ponerlas a mano.

## E. Skills de Claude Code
Van todas en `puro-chisme-claude.zip` (copia de `~/.claude/skills`, sin `node_modules` ni claves), entre ellas las que
usa el canal: hyperframes, hyperframes-cli, hyperframes-registry, media-use, manim-skill, threejs-webgl,
lottie-animations, youtube-uploader, viral-video-hooks-retention, viral-video-animated-captions, faceless-youtube-niche-research,
higgsfield-youtube-thumbnail y trabajo-autonomo. La skill `produccion-nocturna` vive en el repo (`.claude/skills/`).
Plugins: caveman, token-optimizer, ponytail, superpowers, claude-code-setup (setup_mac.sh los instala).
