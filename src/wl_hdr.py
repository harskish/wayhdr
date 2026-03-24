import os
from pathlib import Path

#GLFW_OPENGL_API = 0x00030001
#GLFW_OPENGL_CORE_PROFILE = 0x00032001
#GLFW_CLIENT_API = 0x00022001
#GLFW_CONTEXT_VERSION_MAJOR = 0x00022002
#GLFW_CONTEXT_VERSION_MINOR = 0x00022003
#GLFW_OPENGL_FORWARD_COMPAT = 0x00022006
#GLFW_OPENGL_PROFILE = 0x00022008
#GLFW_SCALE_TO_MONITOR = 0x0002200C
#GLFW_RED_BITS = 0x00021001
#GLFW_GREEN_BITS = 0x00021002
#GLFW_BLUE_BITS = 0x00021003
#GLFW_ALPHA_BITS = 0x00021004
#GLFW_RESIZABLE = 0x00020003
#GLFW_VISIBLE = 0x00020004

GLFW_FLOATBUFFER = 0x00021011
GLFW_WAYLAND_COLOR_MANAGEMENT = 0x00026002


def _workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_custom_glfw_candidates() -> list[Path]:
    root = _workspace_root()
    return [
        root / "build" / "external" / "glfw" / "src" / "libglfw.so",
        root / "build" / "external" / "glfw" / "src" / "libglfw.so.3",
        root / "build" / "external" / "glfw" / "src" / "libglfw.so.3.4",
    ]


def configure_pyglfw_library() -> None:
    # Respect explicit pyglfw override first.
    if os.environ.get("PYGLFW_LIBRARY"):
        return

    # Backward-compatible bridge for this repo's previous env var.
    wayhdr_glfw = os.environ.get("WAYHDR_GLFW_LIB")
    if wayhdr_glfw:
        os.environ["PYGLFW_LIBRARY"] = wayhdr_glfw
        return

    for candidate in _default_custom_glfw_candidates():
        if candidate.exists():
            os.environ["PYGLFW_LIBRARY"] = str(candidate)
            return
