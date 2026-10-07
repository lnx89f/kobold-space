#!/usr/bin/env bash
set -euo pipefail
test -f /usr/share/wayland-sessions/niri.desktop
sudo python3 - <<'PY'
from pathlib import Path
import configparser,shutil,datetime
state=Path('/var/lib/sddm/state.conf')
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
cfg=configparser.ConfigParser()
cfg.optionxform=str
if state.exists():
    cfg.read(state)
    shutil.copy2(state,str(state)+'.backup-'+stamp)
if not cfg.has_section('Last'): cfg.add_section('Last')
cfg.set('Last','Session','/usr/share/wayland-sessions/niri.desktop')
state.parent.mkdir(parents=True,exist_ok=True)
with state.open('w') as f: cfg.write(f)
print('Sessão selecionada no SDDM: Niri. Noctalia inicia pela configuração do Niri.')
PY
