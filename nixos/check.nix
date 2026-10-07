# Evaluate against the caller's pinned nixpkgs without building a whole OS.
{ pkgs ? import <nixpkgs> { } }:
let
  system = import (pkgs.path + "/nixos/lib/eval-config.nix") {
    system = pkgs.stdenv.hostPlatform.system;
    modules = [
      ./default.nix
      {
        nixpkgs.pkgs = pkgs;
        programs.kobold-space.enable = true;
        system.stateVersion = "26.05";
        fileSystems."/" = { device = "/dev/example"; fsType = "ext4"; };
        boot.loader.grub.enable = false;
      }
    ];
  };
  cfg = system.config;
  failed = builtins.filter (entry: !entry.assertion) cfg.assertions;
in
assert failed == [ ];
assert cfg.programs.niri.enable;
assert cfg.programs.thunar.enable;
assert cfg.services.gvfs.enable;
assert cfg.qt.style == "adwaita-dark";
assert builtins.any (pkg: (pkg.pname or "") == "kobold-space-installer") cfg.environment.systemPackages;
{
  inherit (pkgs.stdenv.hostPlatform) system;
  niriVersion = cfg.programs.niri.package.version;
  noctaliaVersion = cfg.programs.kobold-space.noctaliaPackage.version;
  installer = (pkgs.callPackage ./package.nix {
    niri = cfg.programs.niri.package;
    noctalia = cfg.programs.kobold-space.noctaliaPackage;
  }).drvPath;
  systemDerivation = cfg.system.build.toplevel.drvPath;
  assertionsPassed = true;
}
