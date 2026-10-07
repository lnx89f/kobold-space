#!/usr/bin/env python3
"""Install the desktop preset into the current user's home, with backups."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parent

def render_settings(profile, home, output):
    template = ('nixos/config/noctalia.toml.in' if profile == 'nixos'
                else 'config/noctalia/settings.toml.in')
    text = (ROOT / template).read_text().replace('@HOME@', str(home)).replace('eDP-1', output)
    tomllib.loads(text)
    return text

def validate_configs(home, output, settings):
    # Both configs are checked before replacing any user files.
    with tempfile.TemporaryDirectory(prefix='kobold-niri-check-') as td:
        staged = Path(td)
        for source in sorted((ROOT / 'config/niri').glob('*.kdl')):
            text = source.read_text().replace('@HOME@', str(home)).replace('eDP-1', output)
            (staged / source.name).write_text(text)
        if shutil.which('niri'):
            subprocess.run(['niri', 'validate', '--config', str(staged / 'config.kdl')], check=True)
        (staged / 'noctalia.toml').write_text(settings)
        if shutil.which('noctalia'):
            subprocess.run(['noctalia', 'config', 'validate', str(staged / 'noctalia.toml')], check=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='Verify files without installing')
    parser.add_argument('--output', default='eDP-1', help='Niri display connector name')
    parser.add_argument('--profile', choices=['fedora', 'nixos'], default='fedora',
                        help='Use the exported Fedora preset or the portable NixOS v5 profile')
    args = parser.parse_args()
    for name, expected in json.loads((ROOT / 'checksums.json').read_text()).items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise SystemExit('Checksum mismatch: ' + name)
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', args.output):
        raise SystemExit('Invalid display connector name')
    home = Path.home()
    settings = render_settings(args.profile, home, args.output)
    validate_configs(home, args.output, settings)
    if args.dry_run:
        print('Preset integrity verified; available config validators passed. No settings changed.')
        return
    if hasattr(os, 'geteuid') and os.geteuid() == 0:
        raise SystemExit('Run the visual installer as your desktop user, without sudo.')
    for binary in ['niri', 'noctalia', 'swaybg']:
        if not shutil.which(binary):
            raise SystemExit('Install required application first: ' + binary)
    backup = home / '.local/share/theme-backups' / datetime.datetime.now().strftime('before-kobold-preset-%Y%m%d-%H%M%S-%f')
    backup.mkdir(parents=True)
    changes = []

    def install_file(source, dest, text=None):
        relative = dest.relative_to(home)
        existed = dest.exists() or dest.is_symlink()
        if existed:
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dest, saved, follow_symlinks=False)
        changes.append({'path': str(relative), 'existed': existed})
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_symlink():
            dest.unlink()
        if text is None:
            shutil.copy2(source, dest)
        else:
            dest.write_text(text)

    # Install icon files before selecting them. Archive contains both the dark
    # variant and the base theme required by its relative symlinks.
    with tempfile.TemporaryDirectory(prefix='kobold-icons-') as td:
        with tarfile.open(ROOT / 'assets/papirus-dark-black.tar.gz') as archive:
            archive.extractall(td, filter='data')
        for name in ['Papirus', 'Papirus-Dark']:
            dest = home / '.local/share/icons' / name
            if dest.is_symlink():
                raise SystemExit('Refusing to replace symlinked icon directory: ' + str(dest))
            existed = dest.exists()
            if existed:
                saved = backup / dest.relative_to(home)
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dest), str(saved))
            changes.append({'path': str(dest.relative_to(home)), 'existed': existed})
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(Path(td) / name, dest, symlinks=True)

    with tempfile.TemporaryDirectory(prefix='kobold-gtk-') as td:
        with tarfile.open(ROOT / 'assets/orchis-green-dark.tar.gz') as archive:
            archive.extractall(td, filter='data')
        dest = home / '.local/share/themes/Orchis-Green-Dark'
        if dest.is_symlink():
            raise SystemExit('Refusing to replace symlinked theme directory: ' + str(dest))
        existed = dest.exists()
        if existed:
            saved = backup / dest.relative_to(home)
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dest), str(saved))
        changes.append({'path': str(dest.relative_to(home)), 'existed': existed})
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(Path(td) / 'Orchis-Green-Dark', dest, symlinks=True)

    # The exported widget uses Noctalia plugin API 24. On NixOS use the
    # native workspace widget so an older native v5 package can be used.
    for source in ([] if args.profile == 'nixos' else (ROOT / 'plugins').rglob('*')):
        if source.is_file():
            install_file(source, home / '.local/share/noctalia/plugins' / source.relative_to(ROOT / 'plugins'))

    for source in sorted((ROOT / 'config').rglob('*')):
        if not source.is_file() or source.name.endswith('.in'):
            continue
        relative = source.relative_to(ROOT / 'config')
        if args.profile == 'nixos' and relative.parts[0] == 'environment.d':
            continue
        text = source.read_text().replace('@HOME@', str(home)).replace('eDP-1', args.output) if relative.parts[0] == 'niri' else None
        install_file(source, home / '.config' / relative, text)
    wallpaper = home / '.local/share/backgrounds/kobold/kobold-wallpaper.png'
    install_file(ROOT / 'assets/kobold-wallpaper.png', wallpaper)
    overview_wallpaper = home / '.local/share/backgrounds/niri/cosmos-minimal-pixel.png'
    install_file(ROOT / 'assets/cosmos-minimal-pixel.png', overview_wallpaper)
    current_overview = json.loads((ROOT / 'preset.json').read_text())['overview_wallpaper']
    if current_overview != 'cosmos-minimal-pixel.png':
        install_file(ROOT / 'assets' / current_overview,
                     home / '.local/share/backgrounds/niri' / current_overview)
    if args.profile == 'nixos':
        # Noctalia's declared config and mutable GUI state are separate layers.
        # Reset previous GUI overrides with a backup so they do not mask this
        # preset; do not symlink the writable state into the Nix store.
        install_file(None, home / '.config/noctalia/config.toml', settings)
        install_file(None, home / '.local/state/noctalia/settings.toml', '')
        fedora_env = home / '.config/environment.d/60-hackerman.conf'
        if fedora_env.exists():
            install_file(None, fedora_env, '# Qt integration is managed by the NixOS qt module.\n')
    else:
        install_file(None, home / '.local/state/noctalia/settings.toml', settings)
    community = ROOT / 'state/noctalia/community-templates'
    if community.exists():
        for source in community.rglob('*'):
            if source.is_file():
                install_file(source, home / '.local/state/noctalia/community-templates' / source.relative_to(community))
    btop = home / '.config/btop/btop.conf'
    text = btop.read_text() if btop.exists() else ''
    if re.search(r'^color_theme\s*=', text, re.M):
        text = re.sub(r'^color_theme\s*=.*$', 'color_theme = "noctalia"', text, flags=re.M)
    else:
        text += '\ncolor_theme = "noctalia"\n'
    install_file(None, btop, text)
    (backup / 'changes.json').write_text(json.dumps(changes, indent=2))
    if shutil.which('gsettings'):
        previous = {}
        for key, value in [('icon-theme', 'Papirus-Dark'), ('gtk-theme', 'Orchis-Green-Dark'), ('color-scheme', 'prefer-dark')]:
            result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', key], capture_output=True, text=True)
            previous[key] = result.stdout.strip()
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', key, value], check=True)
        (backup / 'gsettings.json').write_text(json.dumps(previous, indent=2))
    subprocess.run(['noctalia', 'config', 'validate'], check=True)
    # Reload only if there is an active desktop session; otherwise configs apply
    # at the next login.
    if os.environ.get('NIRI_SOCKET'):
        subprocess.run(['noctalia', 'msg', 'config-reload'], check=True)
        subprocess.run(['noctalia', 'msg', 'templates-apply'], check=True)
        subprocess.run(['noctalia', 'msg', 'wallpaper-set', str(wallpaper)], check=True)
        subprocess.run(['niri', 'msg', 'action', 'spawn', '--', 'swaybg', '-i', str(overview_wallpaper), '-m', 'fill'], check=True)
    print('Preset installed. Backup:', backup)
    print('Reopen apps or log in again to refresh all icons and Qt settings.')

if __name__ == '__main__':
    main()
