#!/usr/bin/env bash
# Limpeza conservadora: mantém SDDM e sua implementação atual com Sway.
set -euo pipefail
case "${1:-}" in
  '') mode=apply ;;
  --dry-run) mode=dry-run ;;
  *) echo 'Uso: bash remover-componentes-sway.sh [--dry-run]' >&2; exit 2 ;;
esac
for binary in niri noctalia alacritty swaybg; do command -v "$binary" >/dev/null; done
niri validate --config "$HOME/.config/niri/config.kdl"
noctalia config validate
python3 - "$mode" <<'PY'
import ast,datetime,json,os,subprocess,sys,tomllib
from pathlib import Path
mode=sys.argv[1]
env=dict(os.environ,LC_ALL='C')
def run(args,**kwargs):
    return subprocess.run(args,env=env,check=True,**kwargs)
config=tomllib.loads(run(['noctalia','config','export','full'],capture_output=True,text=True).stdout)
if not config.get('notification',{}).get('enable_daemon',False):
    raise SystemExit('Ative o daemon de notificações do Noctalia antes de remover Dunst.')
# Falha em qualquer dependência, sem analisar ou ignorar mensagens localizadas.
candidates=['foot','dunst','wlsunset']
installed=[p for p in candidates if subprocess.run(['rpm','-q',p],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0]
if not installed:
    print('Os três pacotes selecionados já estão ausentes.')
    sys.exit(0)
print('Remover somente:',', '.join(installed),flush=True)
run(['rpm','-e','--test',*installed])
status=json.loads(run(['rpm-ostree','status','--json'],capture_output=True,text=True).stdout)
deployments=status['deployments']
booted=next(d for d in deployments if d.get('booted'))
if deployments[0].get('id') != booted.get('id'):
    raise SystemExit('Existe uma implantação pendente. Reinicie antes de executar a limpeza.')
base_commit=booted.get('base-checksum') or booted['checksum']
metadata=run(['ostree','--repo=/ostree/repo','show','--print-metadata-key=rpmostree.rpmdb.pkglist',base_commit],capture_output=True,text=True).stdout
base_names={p[0] for p in ast.literal_eval(metadata)}
outside_base=[p for p in installed if p not in base_names]
if outside_base:
    raise SystemExit('Pacotes fora da imagem base; limpeza interrompida: '+', '.join(outside_base))
base=installed
overlays=[]
print('Confirmados nos metadados da imagem base:', ', '.join(base),flush=True)
print('Fuzzel será preservado: é recomendação do Niri instalada como dependência da camada.',flush=True)
command=['pkexec','/usr/bin/rpm-ostree','override','remove',*base]
run([*command,'--dry-run'])
if mode=='dry-run':
    print('Simulação concluída. Nenhum pacote ou configuração foi alterado.')
    sys.exit(0)
# Foot é o terminal padrão do Sway: use Alacritty na sessão alternativa.
terminal=Path.home()/'.config/sway/config.d/99-terminal-alacritty.conf'
backup=Path.home()/'.local/share/theme-backups'/('before-desktop-cleanup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
backup.mkdir(parents=True)
(backup/'rpm-ostree-status.json').write_text(json.dumps(status,indent=2))
if terminal.exists():
    (backup/'99-terminal-alacritty.conf').write_bytes(terminal.read_bytes())
terminal.parent.mkdir(parents=True,exist_ok=True)
terminal.write_text('# Terminal para a sessão alternativa Sway.\nset $term alacritty\nbindsym $mod+Return exec alacritty\n')
try:
    run(command)
except BaseException:
    saved=backup/'99-terminal-alacritty.conf'
    if saved.exists(): terminal.write_bytes(saved.read_bytes())
    else: terminal.unlink(missing_ok=True)
    raise
(backup/'removed-packages.json').write_text(json.dumps({'base':base,'layered':overlays},indent=2))
print('Backup:',backup)
print('Reinicie para aplicar. SDDM e sua configuração de login automático foram preservados.')
if base: print('Restaurar pacotes da base: pkexec /usr/bin/rpm-ostree override reset '+' '.join(base))
PY
