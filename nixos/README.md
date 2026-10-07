# Kobold Space no NixOS

Este perfil usa **NixOS 26.05**, Niri e o **Noctalia nativo v5** (`pkgs.noctalia`). Não exige flakes nem Home Manager. O módulo declara os programas e a integração do desktop; o comando `kobold-space-install` instala os arquivos visuais editáveis na sua pasta pessoal com backup.

## O que muda em relação ao Fedora

| Parte | Adaptação no NixOS |
| --- | --- |
| Niri e overview | Mesmos atalhos, bordas das janelas de 1 px/50%, cantos de 4 px, cosmos pixel art e workspaces transparentes sem sombra. |
| Noctalia | Configuração TOML portátil em `~/.config/noctalia/config.toml`; alterações pela interface continuam em `~/.local/state/noctalia/settings.toml`. |
| Workspaces na barra | Widget nativo; o plugin exportado exige API 24 e não é ativado neste perfil. |
| Tela de bloqueio | Layout nativo automático; não copia as coordenadas de um monitor 1920×1080 do Fedora. |
| GTK e ícones | Preserva Orchis-Green-Dark e Papirus-Dark com pastas pretas, extraídos dos arquivos incluídos no repo. |
| Qt | Usa o módulo `qt` do NixOS com integração GNOME e Adwaita escuro. Não aplica `QT_QPA_PLATFORMTHEME=gtk3` do Fedora; a aparência Qt pode diferir do GTK. |
| Alacritty e Btop | Preserva os temas exportados e habilita sua geração pelo Noctalia. |
| Codex, Telegram e Firefox | Recursos continuam disponíveis no repo, mas os templates comunitários não são ativados automaticamente pelo perfil NixOS. Firefox segue a instalação manual descrita no README principal. |
| Programas e serviços | Pacotes vêm do nixpkgs do seu sistema; não usa RPM, `dnf`, executáveis do Fedora ou caminhos de `/home/kobold`. |

O arquivo de estado exportado no Fedora tem `config_version = 14` e o Noctalia local era 5.2. O perfil NixOS usa um template próprio, sem esse número de migração nem o plugin com API específica. O pacote `noctalia-shell` v4/Quickshell tem configuração e IPC diferentes e não serve para este preset. O módulo rejeita versões anteriores ao Noctalia 5.

## 1. Colocar o repo junto da configuração NixOS

Para uma configuração tradicional em `/etc/nixos`:

```bash
sudo git clone https://github.com/lnx89f/kobold-space.git /etc/nixos/kobold-space
```

Se sua configuração fica em outro diretório, coloque o checkout junto dela e adapte o caminho do `import`. Mantenha o repo inteiro: o módulo usa os temas, arquivos e imagens das outras pastas.

No seu `configuration.nix`, acrescente o import e habilite o módulo:

```nix
{ config, pkgs, ... }:
{
  imports = [
    ./hardware-configuration.nix
    ./kobold-space/nixos
  ];

  programs.kobold-space.enable = true;

  # Continue usando seus usuários, boot, discos, rede e display manager.
  # Mantenha também o system.stateVersion que seu sistema já usa.
}
```

Mescle esse trecho com a configuração existente. O módulo habilita a sessão Niri, Thunar, dconf, GVfs, UPower, Polkit e o portal GTK; inclui Noctalia, swaybg, Alacritty, Btop, ferramentas multimídia, Xwayland Satellite e fontes. Niri integra os portais e o keyring pelo módulo oficial do NixOS. Noctalia inicia pelo `spawn-at-startup` do preset, sem um segundo serviço de autostart.

O módulo não escolhe display manager. Se você já usa GDM, SDDM ou outro gerenciador de login, selecione **Niri** nele depois do rebuild. Para uma máquina sem gerenciador, é possível iniciar `niri-session` a partir de um TTY após o login.

Se já gerencia Qt de outra forma (por exemplo, Plasma ou qt6ct), use:

```nix
programs.kobold-space.manageQt = false;
```

## 2. Conferir áudio e recursos do hardware

O preset não substitui suas escolhas de áudio, rede, Bluetooth ou gerenciamento de energia. As bibliotecas e ferramentas de áudio não iniciam sozinhas o daemon. Se você ainda não tem áudio configurado, uma configuração PipeWire típica é:

```nix
security.rtkit.enable = true;
services.pipewire = {
  enable = true;
  alsa.enable = true;
  pulse.enable = true;
  wireplumber.enable = true;
};
```

Use uma única pilha de áudio. Se migra de PulseAudio, ajuste sua declaração existente antes de ativar PipeWire.

Os widgets de rede e Bluetooth dependem dos serviços do sistema. Se forem apropriados para sua máquina e ainda não estiverem configurados:

```nix
networking.networkmanager.enable = true;
hardware.bluetooth.enable = true;
# Adicione seu usuário ao grupo networkmanager, preservando seus outros grupos.
```

Noctalia habilita seu próprio agente Polkit no template. Se já tem um agente separado, ajuste `shell.polkit_agent` para `false` em `~/.config/noctalia/config.toml`. Evite iniciar na sessão Niri outra barra, host de tray ou daemon de notificações que dispute os mesmos serviços com o Noctalia. O bloqueio nativo usa PAM `login`, já fornecido pelo NixOS; teste `Super+Alt+L` na sua máquina antes de depender dele.

## 3. Rebuild e instalação do visual

```bash
sudo nixos-rebuild build
sudo nixos-rebuild switch
```

Se você usa uma configuração por flake, continue usando seu comando de rebuild habitual; o módulo também pode ser importado nela, sem adicionar inputs externos.

**Como o usuário do desktop, sem sudo:**

```bash
kobold-space-install --dry-run
kobold-space-install
```

Para outro conector de monitor:

```bash
niri msg outputs
kobold-space-install --dry-run --output DP-1
kobold-space-install --output DP-1
```

O dry-run verifica os hashes e valida os arquivos com Niri e Noctalia disponíveis. A instalação substitui os arquivos do preset e guarda os anteriores em `~/.local/share/theme-backups/before-kobold-preset-*`. **No perfil NixOS, ela também substitui `~/.config/noctalia/config.toml` e limpa o arquivo de overrides `~/.local/state/noctalia/settings.toml`, com backup**, para que escolhas antigas da interface não sobreponham o preset. Outros arquivos TOML na pasta do Noctalia também participam da configuração; revise-os se houver sobreposições.

Se havia uma instalação anterior do perfil Fedora, o arquivo `~/.config/environment.d/60-hackerman.conf` é neutralizado com backup para a integração Qt ficar a cargo do NixOS. Faça logout/login para atualizar o ambiente. Home Manager ou outro gerenciador não deve controlar simultaneamente os mesmos arquivos que este instalador substitui.

Entre na sessão Niri. `Super+Space` abre o launcher; `Super+Return` abre Alacritty; `Super+O` abre o overview; `Super+Alt+L` bloqueia a sessão. Se instalou de dentro de uma sessão ativa, reabra os aplicativos para atualizar GTK/ícones. O fundo do cosmos também fica visível no desktop através dos workspaces transparentes.

## Atualizações e restauração

```bash
sudo git -C /etc/nixos/kobold-space pull --ff-only
sudo nixos-rebuild build
sudo nixos-rebuild switch
# Só reaplique o visual quando quiser substituir suas customizações locais:
kobold-space-install --dry-run
kobold-space-install
```

Um rebuild atualiza programas e o comando de instalação, mas não sobrescreve silenciosamente sua pasta pessoal. Essa separação permite que Noctalia gere `niri/noctalia.kdl` e os temas de aplicativos sem tentar escrever em symlinks somente leitura do `/nix/store`. Para reaplicar exatamente o preset, execute novamente o instalador.

O rollback de uma geração NixOS restaura os pacotes, não os arquivos visuais copiados. Restaure esses arquivos a partir do backup e consulte `changes.json` e `gsettings.json`, conforme o README principal. Preserve seu canal/revisão do nixpkgs para reproduzir as mesmas versões. Se sua versão estável não possui `pkgs.noctalia`, atualize para NixOS 26.05 ou forneça um pacote **nativo v5** compatível pela opção `programs.kobold-space.noctaliaPackage`; não troque por `noctalia-shell` v4.

## Validação e limites

Este repo inclui `nixos/check.nix` para avaliar o módulo com seu nixpkgs e `tests/test_install.py` para testar o perfil e a instalação em uma pasta temporária:

```bash
nix-instantiate --eval --strict --expr 'import ./nixos/check.nix {}'
python3 -m unittest discover -s tests -v
```

Validado em x86_64 com nixpkgs do canal NixOS 26.05, Niri 26.04 e Noctalia 5.0.1: avaliação do módulo, construção do pacote do instalador, dry-run com os binários Nix e quatro testes Python de portabilidade, instalação/backup e falha antes de gravar arquivos. Essa validação foi executada com Nix portátil no Fedora, sem iniciar uma sessão NixOS.

O comportamento de áudio, desbloqueio PAM, aceleração gráfica, suspensão e hotplug depende do hardware e da configuração NixOS da máquina. A avaliação do módulo e a validação dos arquivos não substituem uma sessão gráfica nessa máquina.

Fontes consultadas para a adaptação:

- [Módulo Niri no nixpkgs 26.05](https://github.com/NixOS/nixpkgs/blob/nixos-26.05/nixos/modules/programs/wayland/niri.nix).
- [Noctalia nativo no nixpkgs 26.05](https://github.com/NixOS/nixpkgs/blob/nixos-26.05/pkgs/by-name/no/noctalia/package.nix).
- [Configuração de referência do Noctalia 5.0.1](https://github.com/noctalia-dev/noctalia/blob/v5.0.1/example.toml).
- [Packaging e requisitos do Noctalia](https://github.com/noctalia-dev/noctalia/blob/main/PACKAGING.md).
- [Módulo Qt do NixOS 26.05](https://github.com/NixOS/nixpkgs/blob/nixos-26.05/nixos/modules/config/qt.nix).
