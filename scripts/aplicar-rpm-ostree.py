#!/usr/bin/env python3
"""Planeja ou aplica os pacotes declarados; não reinicia nem remove extras."""
import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def plan(manifest, deployment=None):
    if manifest['override_replace']:
        raise ValueError('Overrides de substituição exigem suporte explícito a fontes RPM.')
    for name in manifest['install'] + manifest['override_remove']:
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9+_.:-]*', name):
            raise ValueError('Nome de pacote inválido: ' + name)
    installs = manifest['install']
    removals = manifest['override_remove']
    if deployment is not None:
        if deployment.get('origin') != manifest['base']:
            raise ValueError('Base diferente do manifesto; faça a migração explicitamente antes de aplicar.')
        installs = sorted(set(installs) - set(deployment.get('requested-packages', [])))
        removals = sorted(set(removals) - set(deployment.get('requested-base-removals', [])))
    if removals:
        return ['rpm-ostree', 'override', 'remove', *removals,
                *['--install=' + package for package in installs]]
    if installs:
        return ['rpm-ostree', 'install', '--idempotent', '--allow-inactive', *installs]
    return []

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Aplicar ao deployment; padrão só mostra plano offline')
    parser.add_argument('--status-json', type=Path, help='Planejar com uma captura de rpm-ostree status --json')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'system/rpm-ostree.json').read_text())
    deployment = None
    if args.apply or args.status_json:
        status = json.loads(subprocess.check_output(['rpm-ostree', 'status', '--json'], text=True)) if args.apply else json.loads(args.status_json.read_text())
        # O primeiro deployment é o destino padrão, incluindo alterações pendentes.
        deployment = status['deployments'][0]
    command = plan(manifest, deployment)
    print('Base declarada:', manifest['base'])
    print(shlex.join(command) if command else 'Nenhuma alteração necessária.')
    if args.apply and command:
        subprocess.run(command, check=True)
        print('Deployment atualizado. Reinicie manualmente para ativá-lo.')

if __name__ == '__main__':
    main()
