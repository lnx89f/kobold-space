{ lib, stdenvNoCC, python3, makeWrapper, glib, gsettings-desktop-schemas,
  niri, noctalia, swaybg }:
stdenvNoCC.mkDerivation {
  pname = "kobold-space-installer";
  version = "1.1.0";
  src = lib.cleanSourceWith {
    src = ../.;
    filter = path: type:
      lib.cleanSourceFilter path type
      && !(lib.hasSuffix ".pyc" path)
      && builtins.baseNameOf path != "__pycache__";
  };
  nativeBuildInputs = [ makeWrapper ];
  dontBuild = true;
  installPhase = ''
    runHook preInstall
    mkdir -p $out/share/kobold-space $out/bin
    cp -R . $out/share/kobold-space/
    makeWrapper ${python3}/bin/python3 $out/bin/kobold-space-install \
      --add-flags "$out/share/kobold-space/install.py --profile nixos" \
      --prefix PATH : ${lib.makeBinPath [ niri noctalia swaybg glib ]} \
      --prefix XDG_DATA_DIRS : ${glib.getSchemaDataDirPath gsettings-desktop-schemas}
    runHook postInstall
  '';
  meta = {
    description = "Kobold Space visual preset installer for NixOS";
    mainProgram = "kobold-space-install";
    platforms = lib.platforms.linux;
  };
}
