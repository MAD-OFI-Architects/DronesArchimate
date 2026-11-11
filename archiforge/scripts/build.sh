#!/usr/bin/env bash
# Construye un dominio hasta terminar (reintenta/reanuda solo). Uso: ./scripts/build.sh "Intervenciones" [vueltas=6] [espera=900]
cd "$(dirname "$0")/.."
exec python -m forge build "$1" --laps "${2:-6}" --wait "${3:-900}"
