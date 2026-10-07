# Kobold Space

Preset do desktop Fedora com Niri, Noctalia, paleta Kobold Matrix, ícones Papirus-Dark com pastas pretas e wallpaper Kobold.

- Borda colorida de 1 px com 50% de transparência; cantos com raio de 4 px.
- Escala de 100%; monitor padrão `eDP-1`.
- Cosmos minimalista em pixel art no fundo do overview: preto, pequenas galáxias distantes e estrelas esparsas.
- Workspaces com fundo totalmente transparente, wallpaper do Noctalia invisível e sem sombra no overview; sem retângulos visíveis ao redor dos workspaces.
- Barra transparente de 22 px, sem padding: botão do overview e launcher à esquerda; mídia, bandeja, rede, Bluetooth, brilho, bateria e volume à direita. Posição segue o padrão do Noctalia.
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

O `swaybg` exibe o cosmos em uma camada dedicada ao backdrop do Niri. A seleção de wallpaper do Noctalia é preservada, mas sua camada fica com opacidade zero. O fundo dos workspaces é transparente e `workspace-shadow` fica desativado. Abra o overview com `Super+O`. Os cantos das janelas continuam com raio de 4 px; o Niri 26.04 não oferece arredondamento dos próprios workspaces.

## Preset de apps Flatpak

Lista exportada da instalação atual: Firefox (`org.mozilla.firefox`), Proton VPN (`com.protonvpn.www`) e Snes9x (`com.snes9x.Snes9x`), todos do Flathub. Inclui apenas os IDs dos apps, sem dados ou contas. A instalação dos apps é separada do visual:

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

O pacote inclui Orchis-Green-Dark e o widget local Workspaces Outline (API 24 do Noctalia), além das configurações atuais de barra e cores.

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
