{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = with pkgs; [
    cmake
    ninja
    pkg-config
    gcc
    gdb
    git

    # OpenGL and diagnostics
    libglvnd
    mesa
    mesa-demos

    # Wayland stack
    wayland
    wayland-scanner
    wayland-protocols
    libxkbcommon

    # X11 headers/libs needed when GLFW builds X11 backend too
    xorg.libX11
    xorg.libXrandr
    xorg.libXinerama
    xorg.libXcursor
    xorg.libXi
    xorg.libXext

    # Used by GLFW portal/file-dialog integration in this fork
    dbus
    libffi
  ];

  shellHook = ''
    export CMAKE_GENERATOR=Ninja
    export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
      pkgs.libglvnd
      pkgs.wayland
      pkgs.libxkbcommon
      pkgs.xorg.libX11
      pkgs.xorg.libXrandr
      pkgs.xorg.libXinerama
      pkgs.xorg.libXcursor
      pkgs.xorg.libXi
      pkgs.xorg.libXext
    ]}:$LD_LIBRARY_PATH
  '';
}
