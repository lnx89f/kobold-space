# Kobold Space

Estado declarativo do desktop Fedora Atomic com Niri, Noctalia, paleta Kobold Matrix, ícones Papirus-Dark e wallpapers incluídos no projeto.

- Borda colorida de 1 px com 50% de transparência; cantos com raio de 4 px.
- Escala de 100%; monitor padrão `eDP-1`.
- Wallpaper de sol noturno no fundo do overview, exportado da configuração ativa.
- Workspaces com fundo totalmente transparente, wallpaper do Noctalia invisível e sem sombra no overview; sem retângulos visíveis ao redor dos workspaces.
- Barra transparente de 22 px: overview, clima de Itaiópolis e monitor do sistema à esquerda; mídia, clipboard, bandeja, rede, Bluetooth, brilho, bateria e volume à direita, agrupados em cápsula com borda. Dock habilitado com ocultação automática.
- Botões laterais do mouse navegam entre colunas; cantos ativos desativados. O botão do overview abre a visão geral e sua rolagem troca workspaces.
- Launcher com ícone de menu e painel junto ao ponto de clique; notificações e tela de bloqueio do Noctalia.
- GTK 3/4 e Thunar; Alacritty e Btop; integração GTK para Qt.
- Paleta e configurações exportadas exatamente como estavam no momento do backup, incluindo a opção de fundo preto do Noctalia.

## NixOS

Veja [o guia de NixOS](nixos/README.md): módulo para NixOS 26.05, sem exigir flakes ou Home Manager, com pacotes declarativos e um instalador do visual com backup. O perfil preserva Niri, cosmos, transparência, paleta e temas; adapta Noctalia para o pacote nativo v5 e usa a integração Qt do NixOS.

## Instalação no Fedora

Instale Niri, Noctalia, swaybg, Python 3.12 ou superior, Alacritty, Thunar, Btop. Para os atalhos multimídia: `wpctl`, `playerctl` e `brightnessctl`. Para Qt, instale o plugin de integração GTK 3.

Este preset foi exportado do Noctalia com `config_version = 14`. Versões anteriores que usam configuração JSON precisam de adaptação. O script não instala aplicativos nem precisa de sudo.

```bash
python3 install.py --dry-run
python3 install.py
```

Se o monitor tiver outro nome, consulte `niri msg outputs` e use:

```bash
python3 install.py --output DP-1
```

O instalador substitui os arquivos de configuração incluídos neste preset e faz backup em `~/.local/share/theme-backups/before-kobold-preset-*`. O backup contém os arquivos anteriores, `changes.json` com os caminhos alterados e `gsettings.json` com as opções anteriores. Para restaurar, recoloque os arquivos do backup nos caminhos relativos à sua pasta pessoal e restaure as opções indicadas em `gsettings.json`.

Reabra os aplicativos depois de instalar. Para a integração Qt, entre novamente na sessão. O preto já está aplicado aos ícones incluídos; não precisa de `papirus-folders`.

O `swaybg` exibe o sol noturno em uma camada dedicada ao backdrop do Niri. A seleção de wallpaper do Noctalia é preservada, mas sua camada fica com opacidade zero. O fundo dos workspaces é transparente e `workspace-shadow` fica desativado. Abra o overview com `Super+O`. Os cantos das janelas continuam com raio de 4 px; o Niri 26.04 não oferece arredondamento dos próprios workspaces.

## Preset de apps Flatpak

Lista exportada da instalação atual: Firefox, Proton VPN, Snes9x, Steam, Fragments e Red (`com.ktechpit.red`), todos do Flathub. Os IDs estão em `flatpak-apps.txt`. Inclui apenas os IDs dos apps, sem dados ou contas. A instalação dos apps é separada do visual:

```bash
bash instalar-flatpaks.sh --dry-run
bash instalar-flatpaks.sh
# Para instalar apenas para seu usuário:
bash instalar-flatpaks.sh --user
```

O padrão é `--system`, como na máquina de origem, e pode pedir autenticação do sistema. O script adiciona o Flathub se necessário e instala os apps ausentes. Não fixa versões. No NixOS, habilite `services.flatpak.enable = true;` antes de executar.

## Firefox e outros aplicativos

`extras/firefox/hackerman.css` personaliza apenas a interface do Firefox. Para instalar, copie para a pasta `chrome` do perfil, acrescente `@import url("hackerman.css");` no início de `userChrome.css` e habilite `toolkit.legacyUserProfileCustomizations.stylesheets` em `about:config`. Reinicie o Firefox. A instalação automática não altera perfis do navegador.

Os templates comunitários selecionados no Noctalia são incluídos em `state/`. O tema do Telegram precisa ser selecionado dentro do aplicativo; o do Codex também depende da seleção do tema personalizado. Aplicativos com aparência própria podem exigir ajustes adicionais.

## Repositório

```bash
git clone https://github.com/lnx89f/kobold-space.git
cd kobold-space
python3 install.py --dry-run
python3 install.py
```

O pacote inclui Orchis-Green-Dark e o widget local Workspaces Outline (API 24 do Noctalia), e o plugin de clima de Itaiópolis (ativo), além das configurações atuais de barra e cores.

`checksums.json` verifica a integridade dos arquivos exportados. Se editar o preset, atualize os hashes antes de instalar. O pacote dos ícones está comprimido para preservar links simbólicos e facilitar a publicação.

## Origem dos recursos

- [Hackerman / Omarchy](https://github.com/omacom/omarchy/tree/quattro/themes/hackerman): paleta de cores adaptada para o Noctalia.
- [lnx89f/kobold-bluefin](https://github.com/lnx89f/kobold-bluefin): `system_files/usr/share/backgrounds/kobold/kobold-wallpaper.png`.
- [Papirus](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme/tree/20250501): versão 20250501; variante Dark oficial e pastas pretas. As licenças do projeto estão em `licenses/`.
- [Orchis](https://github.com/vinceliuice/Orchis-theme): variante Green Dark; licença em `licenses/orchis-COPYING`.
- Templates gerados e comunitários do Noctalia, exportados da instalação local.
- `assets/cosmos-minimal-pixel.png`: gerado com a ferramenta integrada de imagens da OpenAI; prompt: cosmos minimalista pixel art, fundo preto, cinco pequenas galáxias distantes e estrelas esparsas.

Cada recurso de terceiros mantém a licença de seu projeto de origem. Não se atribui uma licença única ao wallpaper, aos ícones e à paleta. Antes de redistribuir, consulte os respectivos projetos; os créditos acima são preservados neste preset.

O exportador não inclui histórico, credenciais, notificações, clipboard, perfis completos de navegador ou configurações pessoais do Codex.

## Versionamento declarativo local

`config/niri/` e `config/noctalia/settings.toml.in` registram as configurações atuais; `@HOME@` é resolvido pelo instalador. `assets/sol-noturno.png` é o wallpaper ativo do overview, copiado do arquivo local `backup-wallpaper-sol-noturno-20261007-152808.png`. O wallpaper do Noctalia continua separado, com sua camada invisível. Os plugins são versionados sem o cache meteorológico ou o histórico de notificações.

`system/rpm-ostree.json` declara a base `fedora:fedora/44/x86_64/sericea`, 15 pacotes solicitados e os overrides que removem `firefox`, `firefox-langpacks`, `foot` e `rofi`. A captura veio dos arquivos `.origin` dos dois deployments, cujas declarações eram iguais; a consulta ao serviço não estava disponível no ambiente de edição. Não há overrides de substituição nessa captura. A lista registra solicitações, incluindo pacotes que possam estar inativos na base, e não todas as dependências instaladas.

Para revisar o plano e aplicar os pacotes em uma máquina com essa mesma base:

```bash
python3 scripts/aplicar-rpm-ostree.py
python3 scripts/aplicar-rpm-ostree.py --apply
```

O primeiro comando só mostra um plano offline. `--apply` consulta o deployment padrão (inclusive pendente), verifica a base e aplica apenas as solicitações ausentes em uma transação. Não remove pacotes extras nem desfaz overrides fora do manifesto. Exige autenticação normal do rpm-ostree; o reinício é manual. Os RPMs seguem os repositórios da máquina, sem fixação de versão. O perfil NixOS mantém seu módulo próprio; esse manifesto é específico do Fedora Atomic.

Para atualizar o registro depois de alterar o desktop:

```bash
python3 scripts/exportar-estado.py
python3 install.py --dry-run
bash instalar-flatpaks.sh --dry-run
git diff
git add .
git commit -m "config: atualiza estado declarativo do desktop"
```

O exportador atualiza Niri, estado visual do Noctalia, paletas, temas gerados de Alacritty/Btop, plugins locais incluídos, wallpapers, apps Flatpak, manifesto rpm-ostree e hashes. Não executa instalações. Se os deployments divergirem, exige `--origin /ostree/deploy/fedora/deploy/DEPLOYMENT.origin` para escolher explicitamente o estado a versionar. Novas fontes de Flatpak ou tipos de override exigem adaptar o exportador. GTK, módulos NixOS e outros arquivos continuam editáveis diretamente no projeto; depois de editá-los, execute `python3 scripts/exportar-estado.py --checksums-only`.

O histórico local começa com o preset anterior e um commit da captura de 2026-10-07. Como não havia identidade Git configurada, esses commits usam `kobold <kobold@localhost>` apenas na execução do commit, sem alterar sua configuração global. Nenhum push foi realizado.

Validação da captura: Niri e Noctalia aceitaram a configuração. O Noctalia avisou sobre a referência residual `kobold/workspaces-outline:workspaces`, cujo plugin não está habilitado no estado exportado; ela foi preservada como estava no desktop.
