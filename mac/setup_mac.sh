#!/bin/bash
# Instala todo en la Mac mini (Apple Silicon). Antes: clona el repo en ~/Documents/GitHub/YouTube y deja en ~/Downloads
# los dos zips que creó exportar_desde_windows.py. Luego:  bash ~/Documents/GitHub/YouTube/mac/setup_mac.sh
set -euo pipefail
REPO="$HOME/Documents/GitHub/YouTube"
DL="$HOME/Downloads"
step() { printf '\n\033[1;33m==> %s\033[0m\n' "$1"; }

step "1/8 Homebrew"
if ! command -v brew >/dev/null; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv)"
  echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> "$HOME/.zprofile"
fi

step "2/8 Herramientas: node, python 3.12, ffmpeg, git, gh, Chrome, librerías de Manim"
brew install node python@3.12 ffmpeg git gh pkg-config cairo pango
brew install --cask google-chrome || true

step "3/8 Claude Code"
command -v claude >/dev/null || curl -fsSL https://claude.ai/install.sh | bash

step "4/8 Entornos de Python (voces y Manim) con las mismas rutas que usa el repo"
PY=/opt/homebrew/bin/python3.12
[ -d "$HOME/.chatterbox-py" ] || $PY -m venv "$HOME/.chatterbox-py"
"$HOME/.chatterbox-py/bin/pip" install -q --upgrade pip numpy soundfile librosa
[ -d "$HOME/.manim-py" ] || $PY -m venv "$HOME/.manim-py"
"$HOME/.manim-py/bin/pip" install -q --upgrade pip "manim==0.22.1"

step "5/8 Skills, memoria y configuración global de Claude Code"
mkdir -p "$HOME/.claude/skills"
TMP=$(mktemp -d)
unzip -q -o "$DL/puro-chisme-claude.zip" -d "$TMP"
cp -R "$TMP/skills/." "$HOME/.claude/skills/"
for f in CLAUDE.md RTK.md; do [ -f "$TMP/global/$f" ] && cp "$TMP/global/$f" "$HOME/.claude/$f"; done
SLUG=$(echo "$REPO" | sed 's#[^A-Za-z0-9]#-#g')          # carpeta de proyecto que usa Claude Code para este repo
mkdir -p "$HOME/.claude/projects/$SLUG/memory"
cp -R "$TMP/memory/." "$HOME/.claude/projects/$SLUG/memory/"
cp "$TMP/plugins.json" "$REPO/mac/plugins.local.json"
echo "settings.json de Windows guardado como referencia en $TMP/global/settings.json (no se copia: tenía rutas de Windows)"

step "6/8 Claves (zip de SECRETOS)"
if [ -f "$DL/puro-chisme-SECRETOS.zip" ]; then
  S=$(mktemp -d); unzip -q -o "$DL/puro-chisme-SECRETOS.zip" -d "$S"
  cp "$S/repo/.env" "$REPO/.env"
  [ -f "$S/repo/research/.env" ] && cp "$S/repo/research/.env" "$REPO/research/.env"
  cp -R "$S/skills/youtube-uploader/." "$HOME/.claude/skills/youtube-uploader/"
  chmod 600 "$REPO/.env" "$REPO/research/.env" "$HOME/.claude/skills/youtube-uploader/scripts/.env" \
    "$HOME/.claude/skills/youtube-uploader/scripts/.youtube-token.json" 2>/dev/null || true
  rm -rf "$S"; echo "Claves copiadas. Borra ahora $DL/puro-chisme-SECRETOS.zip y vacía la papelera."
else
  echo "FALTA $DL/puro-chisme-SECRETOS.zip — sin él no hay voces ni subida a YouTube."
fi

step "7/8 Dependencias del youtube-uploader + prueba"
(cd "$HOME/.claude/skills/youtube-uploader/scripts" && npm install --silent)
npx --yes hyperframes@0.9.17 --version || true

step "8/8 Plugins de Claude Code"
claude plugin marketplace add JuliusBrussee/caveman || true
claude plugin marketplace add alexgreensh/token-optimizer || true
claude plugin marketplace add DietrichGebert/ponytail || true
for p in caveman@caveman token-optimizer@alexgreensh-token-optimizer ponytail@ponytail \
         superpowers@claude-plugins-official claude-code-setup@claude-plugins-official; do
  claude plugin install "$p" || echo "instala a mano dentro de claude: /plugin install $p"
done

step "Automatización nocturna (launchd, 00:30 cada noche)"
sed "s#/Users/USUARIO#$HOME#" "$REPO/mac/nightly/com.purochisme.nocturno.plist" > "$HOME/Library/LaunchAgents/com.purochisme.nocturno.plist"
chmod +x "$REPO/mac/nightly/run_nightly.sh"
launchctl unload "$HOME/Library/LaunchAgents/com.purochisme.nocturno.plist" 2>/dev/null || true
launchctl load "$HOME/Library/LaunchAgents/com.purochisme.nocturno.plist"
rm -rf "$TMP"
echo
echo "LISTO. Falta (a mano): 'claude' una vez para iniciar sesión, y en Ajustes → Energía activar"
echo "'Evitar que la Mac entre en reposo automáticamente' para que corra de noche. Guía: mac/MIGRACION_MAC.md"
