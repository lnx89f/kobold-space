{ config, lib, pkgs, ... }:
let
  cfg = config.programs.kobold-space;
  installer = pkgs.callPackage ./package.nix {
    niri = config.programs.niri.package;
    noctalia = cfg.noctaliaPackage;
  };
in
{
  options.programs.kobold-space = {
    enable = lib.mkEnableOption "the Kobold Space desktop preset";
    noctaliaPackage = lib.mkPackageOption pkgs "noctalia" { };
    manageQt = lib.mkOption {
      type = lib.types.bool;
      default = true;
      description = "Use NixOS Qt integration with the dark Adwaita style.";
    };
  };

  config = lib.mkIf cfg.enable {
    assertions = [
      {
        assertion = lib.versionAtLeast (cfg.noctaliaPackage.version or "0") "5.0.0";
        message = "Kobold Space needs native Noctalia v5 (pkgs.noctalia), not noctalia-shell v4.";
      }
      {
        assertion = lib.versionAtLeast (config.programs.niri.package.version or "0") "25.05";
        message = "Kobold Space needs Niri 25.05 or later for overview backdrop support.";
      }
    ];

    programs.niri = {
      enable = true;
      useNautilus = lib.mkDefault false;
    };
    programs.thunar.enable = true;
    programs.dconf.enable = true;
    security.polkit.enable = lib.mkDefault true;
    services.gvfs.enable = lib.mkDefault true;
    services.upower.enable = lib.mkDefault true;
    xdg.portal.extraPortals = [ pkgs.xdg-desktop-portal-gtk ];

    environment.systemPackages = with pkgs; [
      installer
      cfg.noctaliaPackage
      alacritty
      btop
      swaybg
      playerctl
      brightnessctl
      pipewire # wpctl is supplied by wireplumber below
      wireplumber
      wl-clipboard
      xwayland-satellite
    ];
    fonts.packages = with pkgs; [ noto-fonts nerd-fonts.jetbrains-mono ];

    # NixOS supplies Qt plugins via its module, rather than a Fedora-specific
    # QT_QPA_PLATFORMTHEME=gtk3 environment.d file.
    qt = lib.mkIf cfg.manageQt {
      enable = lib.mkDefault true;
      platformTheme = lib.mkDefault "gnome";
      style = lib.mkDefault "adwaita-dark";
    };
  };
}
