#!/usr/bin/env python3
"""Exporta somente configurações selecionadas, sem modificar o desktop."""
import argparse
import configparser
import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

def checksums():
    files = [p for p in ROOT.rglob('*') if p.is_file()
             and not any(part in ('.git', '__pycache__') for part in p.relative_to(ROOT).parts)
             and p.name != 'checksums.json' and not p.name.endswith(('.bak', '.pyc'))]
    data = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    (ROOT / 'checksums.json').write_text(json.dumps(data, indent=2) + '\n')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origin', type=Path, help='Arquivo .origin do deployment desejado')
    parser.add_argument('--checksums-only', action='store_true')
    args = parser.parse_args()
    if args.checksums_only:
        checksums()
        return
    origins = [args.origin] if args.origin else sorted(Path('/ostree/deploy/fedora/deploy').glob('*.origin'))
    if not origins or len({p.read_text() for p in origins}) != 1:
        raise SystemExit('Deployments ausentes ou diferentes: informe --origin CAMINHO explicitamente.')
    origin = configparser.ConfigParser(interpolation=None)
    origin.read_string(origins[0].read_text())
    allowed = {'origin': {'baserefspec'}, 'packages': {'requested'}, 'overrides': {'remove'}}
    for section in origin.sections():
        if section not in allowed or set(origin[section]) - allowed[section]:
            raise SystemExit('Origin contém opções não suportadas; revisar antes de exportar: ' + section)
    packages = sorted(filter(None, origin.get('packages', 'requested', fallback='').split(';')))
    removals = sorted(filter(None, origin.get('overrides', 'remove', fallback='').split(';')))
    manifest = {'base': origin.get('origin', 'baserefspec'), 'install': packages,
                'override_remove': removals, 'override_replace': [],
                'source': 'deployment .origin; declarações iguais em todos os arquivos selecionados'}
    flatpak = subprocess.check_output(['flatpak', 'list', '--app', '--columns=application,origin,installation'], text=True)
    rows = [line.split('\t') for line in flatpak.splitlines() if line]
    if any(len(r) != 3 or r[1:] != ['flathub', 'system'] for r in rows):
        raise SystemExit('Há apps fora de flathub/system; adaptar manifesto antes de exportar.')
    apps = sorted(r[0] for r in rows)
    settings = (HOME / '.local/state/noctalia/settings.toml').read_text()
    tomllib.loads(settings)
    cosmos = (HOME / '.config/niri/cosmos-overview.kdl').read_text()
    match = re.search(r'spawn-at-startup "swaybg" "-i" "([^"]+)"', cosmos)
    shell_wallpaper = Path(tomllib.loads(settings)['wallpaper']['default']['path'])
    overview = Path(match[1]) if match else shell_wallpaper
    if not overview.is_file():
        raise SystemExit('Wallpaper ausente: ' + str(overview))
    shell_wallpaper = Path(tomllib.loads(settings)['wallpaper']['default']['path'])
    if not shell_wallpaper.is_file():
        raise SystemExit('Wallpaper do Noctalia ausente.')
    (ROOT / 'system').mkdir(exist_ok=True)
    (ROOT / 'system/rpm-ostree.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (ROOT / 'flatpak-apps.txt').write_text('\n'.join(apps) + '\n')
    for source in sorted((HOME / '.config/niri').glob('*.kdl')):
        text = source.read_text().replace(str(HOME), '@HOME@').replace('/home/kobold', '@HOME@')
        if source.name == 'cosmos-overview.kdl':
            text = text.replace(str(overview).replace('/home/kobold', '@HOME@').replace(str(HOME), '@HOME@'),
                                '@HOME@/.local/share/backgrounds/niri/sol-noturno.png')
        (ROOT / 'config/niri' / source.name).write_text(text)
    # Preserve selected wallpapers while making their paths portable.
    wallpaper_settings = tomllib.loads(settings)['wallpaper']
    for entry in [wallpaper_settings.get('last', {}), *wallpaper_settings.get('monitors', {}).values()]:
        if entry.get('path') and entry['path'] != str(shell_wallpaper):
            raise SystemExit('Wallpapers diferentes por monitor: adaptar exportação antes de publicar.')
    settings = settings.replace(str(shell_wallpaper), '@HOME@/.local/share/backgrounds/kobold/kobold-wallpaper.png')
    if wallpaper_settings.get('directory'):
        settings = settings.replace(wallpaper_settings['directory'], '@HOME@/.local/share/backgrounds/kobold/')
    (ROOT / 'config/noctalia/settings.toml.in').write_text(settings.replace(str(HOME), '@HOME@').replace('/home/kobold', '@HOME@'))
    for relative in ('noctalia/palettes', 'alacritty/themes', 'btop/themes'):
        shutil.copytree(HOME / '.config' / relative, ROOT / 'config' / relative, dirs_exist_ok=True)
    community_palettes = HOME / '.local/state/noctalia/community-palettes'
    if community_palettes.exists():
        target_palettes = ROOT / 'state/noctalia/community-palettes'
        target_palettes.mkdir(parents=True, exist_ok=True)
        for palette in community_palettes.glob('*.json'):
            shutil.copy2(palette, target_palettes / palette.name)
    for relative in ('gtk-3.0', 'gtk-4.0', 'environment.d'):
        for target in (ROOT / 'config' / relative).rglob('*'):
            source = HOME / '.config' / target.relative_to(ROOT / 'config')
            if target.is_file() and source.is_file():
                shutil.copy2(source, target)
    for name in ('workspaces-outline', 'itaiopolis-weather'):
        shutil.copytree(HOME / '.local/share/noctalia/plugins' / name, ROOT / 'plugins' / name, dirs_exist_ok=True)
    shutil.copy2(overview, ROOT / 'assets/sol-noturno.png')
    shutil.copy2(shell_wallpaper, ROOT / 'assets/kobold-wallpaper.png')
    preset = json.loads((ROOT / 'preset.json').read_text())
    preset['updated'] = datetime.datetime.now().astimezone().isoformat()
    preset['overview_wallpaper'] = 'sol-noturno.png'
    preset['overview_wallpaper_provider'] = 'swaybg' if match else 'noctalia'
    preset['workspace_wallpaper_opacity'] = 0 if match else 1
    preset['flatpak']['apps'] = apps
    preset['rpm_ostree'] = {'manifest': 'system/rpm-ostree.json'}
    preset['noctalia_plugins_enabled'] = tomllib.loads(settings)['plugins']['enabled']
    (ROOT / 'preset.json').write_text(json.dumps(preset, indent=2, ensure_ascii=False) + '\n')
    checksums()
    print('Estado exportado; configurações ativas preservadas. Revise git diff antes de commitar.')

if __name__ == '__main__':
    main()
