{pkgs}: {
  deps = [
    pkgs.zip
    pkgs.xorg.libXext
    pkgs.xorg.libX11
    pkgs.xorg.libXrender
  ];
}
