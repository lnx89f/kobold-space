"""Verify NixOS portability, backup behavior and failure before user writes."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('preset_install', ROOT / 'install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class NixOSProfileTests(unittest.TestCase):
    def test_portable_settings_without_exported_plugin_or_monitor_geometry(self):
        text = installer.render_settings('nixos', Path('/home/alice'), 'DP-2')
        settings = tomllib.loads(text)
        self.assertNotIn('@HOME@', text)
        self.assertNotIn('/home/kobold', text)
        self.assertNotIn('config_version', settings)
        self.assertNotIn('lockscreen_widgets', settings)
        self.assertNotIn('plugins', settings)
        self.assertNotIn('type', settings['widget']['workspaces'])
        self.assertEqual(settings['theme']['custom_palette'], 'kobold-matrix')
        self.assertEqual(settings['theme']['templates']['community_ids'], [])
        self.assertTrue(settings['wallpaper']['default']['path'].startswith('/home/alice/'))

    def test_fedora_export_still_keeps_its_plugin_and_monitor_selection(self):
        settings = tomllib.loads(installer.render_settings('fedora', Path('/home/alice'), 'DP-2'))
        self.assertEqual(settings['config_version'], 14)
        self.assertEqual(settings['plugins']['enabled'], ['kobold/itaiopolis-weather'])
        self.assertIn('DP-2', settings['wallpaper']['monitors'])

    def test_install_into_temporary_home_preserves_backup_and_mutable_files(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            old_files = {
                '.config/noctalia/config.toml': '[theme]\nmode = "light"\n',
                '.local/state/noctalia/settings.toml': '[theme]\nsource = "builtin"\n',
                '.config/environment.d/60-hackerman.conf': 'QT_QPA_PLATFORMTHEME=gtk3\n',
                '.config/niri/config.kdl': '// previous Niri config\n',
            }
            for name, text in old_files.items():
                dest = home / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(text)

            def fake_run(command, **kwargs):
                return subprocess.CompletedProcess(command, 0, stdout="'old-value'\n", stderr='')

            with patch.object(installer.Path, 'home', return_value=home), \
                 patch.object(installer.os, 'geteuid', return_value=1000), \
                 patch.object(installer.shutil, 'which', side_effect=lambda name: '/test/bin/' + name), \
                 patch.object(installer.subprocess, 'run', side_effect=fake_run), \
                 patch.dict(installer.os.environ, {}, clear=True), \
                 patch('sys.argv', ['install.py', '--profile', 'nixos', '--output', 'DP-2']):
                installer.main()

            backup, = (home / '.local/share/theme-backups').iterdir()
            for name, text in old_files.items():
                self.assertEqual((backup / name).read_text(), text)
            self.assertEqual((home / '.local/state/noctalia/settings.toml').read_text(), '')
            self.assertFalse((home / '.config/noctalia/config.toml').is_symlink())
            self.assertNotIn('gtk3', (home / '.config/environment.d/60-hackerman.conf').read_text())
            config = (home / '.config/niri/config.kdl').read_text()
            self.assertIn('cosmos-overview.kdl', config)
            self.assertIn('output "DP-2"', config)
            cosmos = (home / '.config/niri/cosmos-overview.kdl').read_text()
            self.assertNotIn('@HOME@', cosmos)
            self.assertNotIn('/home/kobold', cosmos)
            self.assertIn('opacity 0.0', cosmos)
            self.assertIn('background-color "transparent"', cosmos)
            self.assertEqual((home / '.local/share/backgrounds/niri/cosmos-minimal-pixel.png').read_bytes(),
                             (ROOT / 'assets/cosmos-minimal-pixel.png').read_bytes())
            self.assertEqual((home / '.local/share/backgrounds/niri/sol-noturno.png').read_bytes(),
                             (ROOT / 'assets/sol-noturno.png').read_bytes())
            self.assertFalse((home / '.local/share/noctalia/plugins/workspaces-outline').exists())
            changes = json.loads((backup / 'changes.json').read_text())
            self.assertIn('.local/state/noctalia/settings.toml', [c['path'] for c in changes])

    def test_validation_failure_does_not_write_user_files(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            with patch.object(installer.Path, 'home', return_value=home), \
                 patch.object(installer, 'validate_configs', side_effect=subprocess.CalledProcessError(1, 'niri')), \
                 patch('sys.argv', ['install.py', '--profile', 'nixos']):
                with self.assertRaises(subprocess.CalledProcessError):
                    installer.main()
            self.assertEqual(list(home.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
