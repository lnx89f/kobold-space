#!/usr/bin/env bash
set -euo pipefail

scope=--system
dry_run=false
for arg in "$@"; do
    case "$arg" in
        --user|--system) scope="$arg" ;;
        --dry-run) dry_run=true ;;
        *) echo "Uso: bash instalar-flatpaks.sh [--user|--system] [--dry-run]" >&2; exit 2 ;;
    esac
done
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
apps=()
while IFS= read -r app || [[ -n "$app" ]]; do
    [[ -z "$app" || "$app" == \#* ]] && continue
    [[ "$app" =~ ^[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)+$ ]] || { echo "ID inválido: $app" >&2; exit 2; }
    apps+=("$app")
done < "$root/flatpak-apps.txt"
if "$dry_run"; then
    printf 'Destino: %s; origem: flathub\n' "$scope"
    printf '%s\n' "${apps[@]}"
    exit 0
fi
command -v flatpak >/dev/null || { echo "Instale Flatpak antes de executar." >&2; exit 1; }
flatpak remote-add "$scope" --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install "$scope" --noninteractive flathub "${apps[@]}"
