#!/usr/bin/env python3
import ctypes
import os
import sys
from pathlib import Path


GLFW_OPENGL_API = 0x00030001
GLFW_OPENGL_CORE_PROFILE = 0x00032001

GLFW_CLIENT_API = 0x00022001
GLFW_CONTEXT_VERSION_MAJOR = 0x00022002
GLFW_CONTEXT_VERSION_MINOR = 0x00022003
GLFW_OPENGL_FORWARD_COMPAT = 0x00022006
GLFW_OPENGL_PROFILE = 0x00022008
GLFW_SCALE_TO_MONITOR = 0x0002200C

GLFW_RED_BITS = 0x00021001
GLFW_GREEN_BITS = 0x00021002
GLFW_BLUE_BITS = 0x00021003
GLFW_ALPHA_BITS = 0x00021004
GLFW_FLOATBUFFER = 0x00021011

GLFW_RESIZABLE = 0x00020003
GLFW_VISIBLE = 0x00020004

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


configure_pyglfw_library()

# Import glfw before imgui_bundle so pyglfw resolves with PYGLFW_LIBRARY.
import glfw  # type: ignore
import OpenGL.GL as gl
from imgui_bundle import imgui
from imgui_bundle.python_backends.glfw_backend import GlfwRenderer


def check_shader(shader: int, stage: str) -> None:
    ok = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
    if ok == gl.GL_TRUE:
        return

    log = gl.glGetShaderInfoLog(shader)
    if isinstance(log, bytes):
        log = log.decode("utf-8", errors="replace")
    raise RuntimeError(f"Failed to compile {stage}: {log}")


def check_program(program: int) -> None:
    ok = gl.glGetProgramiv(program, gl.GL_LINK_STATUS)
    if ok == gl.GL_TRUE:
        return

    log = gl.glGetProgramInfoLog(program)
    if isinstance(log, bytes):
        log = log.decode("utf-8", errors="replace")
    raise RuntimeError(f"Failed to link program: {log}")


def make_program() -> int:
    vertex_source = """
        #version 330 core
        layout(location = 0) in vec2 inPos;
        layout(location = 1) in vec3 inColor;
        out vec3 vColor;

        void main() {
            vColor = inColor;
            gl_Position = vec4(inPos, 0.0, 1.0);
        }
    """

    fragment_source = """
        #version 330 core
        in vec3 vColor;
        out vec4 outColor;
        uniform float gain;

        void main() {
            outColor = vec4(vColor * gain, 1.0);
        }
    """

    vert = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    gl.glShaderSource(vert, vertex_source)
    gl.glCompileShader(vert)
    check_shader(vert, "vertex shader")

    frag = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    gl.glShaderSource(frag, fragment_source)
    gl.glCompileShader(frag)
    check_shader(frag, "fragment shader")

    program = gl.glCreateProgram()
    gl.glAttachShader(program, vert)
    gl.glAttachShader(program, frag)
    gl.glLinkProgram(program)
    check_program(program)

    gl.glDeleteShader(vert)
    gl.glDeleteShader(frag)

    return program


def set_buffer_hints(r: int, g: int, b: int, a: int, float_buffer: bool) -> None:
    glfw.window_hint(GLFW_RED_BITS, r)
    glfw.window_hint(GLFW_GREEN_BITS, g)
    glfw.window_hint(GLFW_BLUE_BITS, b)
    glfw.window_hint(GLFW_ALPHA_BITS, a)
    glfw.window_hint(GLFW_FLOATBUFFER, glfw.TRUE if float_buffer else glfw.FALSE)


def create_window_with_fallbacks():
    title = "tev + imgui_bundle HDR repro"

    set_buffer_hints(16, 16, 16, 16, True)
    window = glfw.create_window(960, 540, title, None, None)

    if not window:
        set_buffer_hints(10, 10, 10, 2, False)
        window = glfw.create_window(960, 540, title, None, None)

    if not window:
        set_buffer_hints(8, 8, 8, 8, False)
        window = glfw.create_window(960, 540, title, None, None)

    return window


def _safe_glfw_call(name: str, default):
    fn = getattr(glfw, name, None)
    if fn is None:
        return default
    try:
        return fn()
    except Exception:
        return default


def main() -> int:
    def on_error(code: int, desc: str) -> None:
        print(f"GLFW error {code}: {desc}", file=sys.stderr)

    glfw.set_error_callback(on_error)

    if hasattr(glfw, "init_hint"):
        glfw.init_hint(GLFW_WAYLAND_COLOR_MANAGEMENT, glfw.TRUE)

    if not glfw.init():
        print("glfw.init() failed", file=sys.stderr)
        return 1

    imgui.create_context()

    try:
        glfw.window_hint(GLFW_CLIENT_API, GLFW_OPENGL_API)
        glfw.window_hint(GLFW_CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(GLFW_OPENGL_FORWARD_COMPAT, glfw.TRUE)
        glfw.window_hint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)

        glfw.window_hint(GLFW_VISIBLE, glfw.TRUE)
        glfw.window_hint(GLFW_RESIZABLE, glfw.TRUE)
        glfw.window_hint(GLFW_SCALE_TO_MONITOR, glfw.TRUE)

        window = create_window_with_fallbacks()
        if not window:
            print("glfw.create_window failed after float/10-bit/8-bit fallbacks", file=sys.stderr)
            return 2

        try:
            glfw.make_context_current(window)
            glfw.swap_interval(1)

            impl = GlfwRenderer(window)
            program = make_program()
            gain_loc = gl.glGetUniformLocation(program, "gain")

            triangle = (ctypes.c_float * 15)(
                0.0,
                0.72,
                1.0,
                1.0,
                1.0,
                -0.8,
                -0.75,
                1.0,
                0.2,
                0.2,
                0.8,
                -0.75,
                0.2,
                1.0,
                0.2,
            )

            vao = gl.glGenVertexArrays(1)
            vbo = gl.glGenBuffers(1)

            gl.glBindVertexArray(vao)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(triangle), triangle, gl.GL_STATIC_DRAW)

            stride = 5 * ctypes.sizeof(ctypes.c_float)
            gl.glEnableVertexAttribArray(0)
            gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, stride, ctypes.c_void_p(0))

            gl.glEnableVertexAttribArray(1)
            gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, stride, ctypes.c_void_p(2 * ctypes.sizeof(ctypes.c_float)))

            gl.glBindVertexArray(0)

            platform = _safe_glfw_call("get_platform", "<unavailable>")
            transfer = _safe_glfw_call("get_window_transfer", "<unavailable>")
            primaries = _safe_glfw_call("get_window_primaries", "<unavailable>")
            print(f"GLFW platform: {platform}")
            print(f"PYGLFW_LIBRARY={os.environ.get('PYGLFW_LIBRARY', '<unset>')}")
            print(f"Window transfer: {transfer}")
            print(f"Window primaries: {primaries}")

            gain = 4.0
            try:
                while not glfw.window_should_close(window):
                    glfw.poll_events()
                    impl.process_inputs()

                    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
                        glfw.set_window_should_close(window, glfw.TRUE)

                    if glfw.get_key(window, glfw.KEY_EQUAL) == glfw.PRESS or glfw.get_key(window, glfw.KEY_KP_ADD) == glfw.PRESS:
                        gain *= 1.01
                    if glfw.get_key(window, glfw.KEY_MINUS) == glfw.PRESS or glfw.get_key(window, glfw.KEY_KP_SUBTRACT) == glfw.PRESS:
                        gain /= 1.01

                    imgui.new_frame()
                    imgui.begin("HDR Controls")
                    imgui.text("+/- or keypad +/- changes gain")
                    _, gain = imgui.slider_float("Gain", gain, 0.1, 16.0)
                    imgui.text(f"PYGLFW_LIBRARY={os.environ.get('PYGLFW_LIBRARY', '<unset>')}")
                    imgui.text(f"Red bits: {glfw.get_window_attrib(window, GLFW_RED_BITS)}")
                    imgui.end()

                    fbw, fbh = glfw.get_framebuffer_size(window)
                    gl.glViewport(0, 0, fbw, fbh)
                    gl.glClearColor(0.03, 0.03, 0.03, 1.0)
                    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

                    gl.glUseProgram(program)
                    gl.glUniform1f(gain_loc, gain)
                    gl.glBindVertexArray(vao)
                    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)
                    gl.glBindVertexArray(0)
                    gl.glUseProgram(0)

                    imgui.render()
                    impl.render(imgui.get_draw_data())
                    glfw.swap_buffers(window)
            finally:
                impl.shutdown()
                gl.glDeleteBuffers(1, [vbo])
                gl.glDeleteVertexArrays(1, [vao])
                gl.glDeleteProgram(program)
        finally:
            glfw.destroy_window(window)
    finally:
        imgui.destroy_context()
        glfw.terminate()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
