#!/usr/bin/env bash
set -euo pipefail
test -f /usr/share/wayland-sessions/niri.desktop
test -f /etc/pam.d/sddm-autologin
login_user=$(id -un)
if [ "$login_user" = root ]; then
    echo 'Execute como seu usuário normal, sem sudo antes do comando.' >&2
    exit 1
fi
sudo python3 - "$login_user" <<'PY'
from pathlib import Path
import datetime,pwd,shutil,sys
user=sys.argv[1]
pwd.getpwnam(user)
dest=Path('/etc/sddm.conf.d/zz-kobold-autologin.conf')
dest.parent.mkdir(parents=True,exist_ok=True)
if dest.exists():
    backup=Path('/var/backups/sddm')
    backup.mkdir(parents=True,exist_ok=True)
    shutil.copy2(dest,backup/('zz-kobold-autologin.conf-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')))
dest.write_text('[Autologin]\nUser='+user+'\nSession=niri.desktop\nRelogin=false\n')
dest.chmod(0o644)
print('Login automático configurado para '+user+' na sessão Niri.')
print('Será aplicado na próxima inicialização ou reinicialização do computador.')
PY
