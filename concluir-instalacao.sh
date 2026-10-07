#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
python3 - <<'PY'
import hashlib,json,urllib.request
from pathlib import Path
root=Path.cwd()
checks=json.loads((root/'checksums.json').read_text())
for name,expected in checks.items():
    path=root/name
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==expected:
        continue
    print('Baixando:',name,flush=True)
    url='https://raw.githubusercontent.com/lnx89f/kobold-space/main/'+name
    data=urllib.request.urlopen(url,timeout=120).read()
    if hashlib.sha256(data).hexdigest()!=expected:
        raise SystemExit('Checksum divergente: '+name)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)
PY
python3 install.py --dry-run "$@"
python3 install.py "$@"
