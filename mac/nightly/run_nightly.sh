#!/bin/bash
# Producción nocturna de Puro Chisme en la Mac mini. La lanza launchd (com.purochisme.nocturno.plist) cada noche.
# Pausar: crea el archivo mac/nightly/PAUSA. Logs: ~/Library/Logs/purochisme/AAAA-MM-DD.log
set -u
REPO="$HOME/Documents/GitHub/YouTube"
LOGDIR="$HOME/Library/Logs/purochisme"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/$(date +%F).log"
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"

{
  echo "=== inicio $(date) ==="
  cd "$REPO" || exit 1
  if [ -f mac/nightly/PAUSA ]; then echo "pausado (mac/nightly/PAUSA)"; exit 0; fi
  git pull --ff-only || echo "aviso: git pull falló, sigo con la copia local"
  # caffeinate: la Mac no se duerme mientras corre. Sin permisos interactivos: nadie va a contestar de noche.
  caffeinate -i claude -p "/produccion-nocturna" \
    --dangerously-skip-permissions \
    --output-format text
  echo "=== fin $(date) (código $?) ==="
} >> "$LOG" 2>&1
