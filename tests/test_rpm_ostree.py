"""Verifica planejamento offline, reconciliação e recusa de base incompatível."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('rpm_plan', Path(__file__).resolve().parents[1] / 'scripts/aplicar-rpm-ostree.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class PlanTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {'base': 'fedora:fedora/44/x86_64/sericea',
                         'install': ['niri', 'btop'], 'override_remove': ['foot'], 'override_replace': []}

    def test_joint_transaction(self):
        self.assertEqual(module.plan(self.manifest), ['rpm-ostree', 'override', 'remove', 'foot', '--install=niri', '--install=btop'])

    def test_existing_declarations_are_skipped(self):
        state = {'origin': self.manifest['base'], 'requested-packages': ['niri', 'btop', 'extra'], 'requested-base-removals': ['foot']}
        self.assertEqual(module.plan(self.manifest, state), [])

    def test_partial_state_installs_only_missing(self):
        state = {'origin': self.manifest['base'], 'requested-packages': ['niri'], 'requested-base-removals': ['foot']}
        self.assertEqual(module.plan(self.manifest, state), ['rpm-ostree', 'install', '--idempotent', '--allow-inactive', 'btop'])

    def test_incompatible_base_and_replacements_fail(self):
        with self.assertRaises(ValueError):
            module.plan(self.manifest, {'origin': 'other'})
        self.manifest['override_replace'] = ['replacement.rpm']
        with self.assertRaises(ValueError):
            module.plan(self.manifest)
