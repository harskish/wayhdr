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

    # Python demo
    python312Packages.python
    python312Packages.uv
    python312Packages.venvShellHook
  ];

  venvDir = "./.venv";
  
  postVenvCreation = ''
    uv pip install imgui-bundle PyOpenGL glfw
  '';

  LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (with pkgs; [
    libglvnd
    zlib
    wayland
    libxkbcommon
    xorg.libX11
    xorg.libXrandr
    xorg.libXinerama
    xorg.libXcursor
    xorg.libXi
    xorg.libXext
    stdenv.cc.cc
  ]);
}
