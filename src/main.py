#!/usr/bin/env python3
import ctypes
import ctypes.util
import os
import sys

from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_COLOR_BUFFER_BIT,
    GL_COMPILE_STATUS,
    GL_FALSE,
    GL_FLOAT,
    GL_FRAGMENT_SHADER,
    GL_INFO_LOG_LENGTH,
    GL_LINK_STATUS,
    GL_STATIC_DRAW,
    GL_TRIANGLES,
    GL_TRUE,
    GL_VERTEX_SHADER,
    GLfloat,
    glAttachShader,
    glBindBuffer,
    glBindVertexArray,
    glBufferData,
    glClear,
    glClearColor,
    glCompileShader,
    glCreateProgram,
    glCreateShader,
    glDeleteProgram,
    glDeleteShader,
    glDeleteBuffers,
    glDeleteVertexArrays,
    glDrawArrays,
    glEnableVertexAttribArray,
    glGenBuffers,
    glGenVertexArrays,
    glGetProgramInfoLog,
    glGetProgramiv,
    glGetShaderInfoLog,
    glGetShaderiv,
    glGetUniformLocation,
    glLinkProgram,
    glShaderSource,
    glUniform1f,
    glUseProgram,
    glVertexAttribPointer,
    glViewport,
)

# GLFW constants used by this sample.
GLFW_TRUE = 1
GLFW_FALSE = 0

GLFW_PRESS = 1

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

GLFW_KEY_ESCAPE = 256
GLFW_KEY_MINUS = 45
GLFW_KEY_EQUAL = 61
GLFW_KEY_KP_SUBTRACT = 333
GLFW_KEY_KP_ADD = 334


class GlfwError(RuntimeError):
    pass


def _default_glfw_paths() -> list[str]:
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return [
        os.path.join(workspace, "build", "external", "glfw", "src", "libglfw.so"),
        os.path.join(workspace, "build", "external", "glfw", "src", "libglfw.so.3"),
        os.path.join(workspace, "build", "external", "glfw", "src", "libglfw.so.3.4"),
    ]


def load_glfw() -> ctypes.CDLL:
    explicit = os.environ.get("WAYHDR_GLFW_LIB")
    candidates = []
    if explicit:
        candidates.append(explicit)
    candidates.extend(_default_glfw_paths())

    system = ctypes.util.find_library("glfw")
    if system:
        candidates.append(system)

    for path in candidates:
        if not path:
            continue
        if "/" in path and not os.path.exists(path):
            continue
        try:
            return ctypes.CDLL(path)
        except OSError:
            continue

    raise GlfwError(
        "Could not load GLFW shared library. Build shared GLFW from your fork and set WAYHDR_GLFW_LIB=/abs/path/libglfw.so"
    )


def configure_glfw_api(glfw: ctypes.CDLL) -> None:
    win = ctypes.c_void_p

    error_cb_t = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p)
    glfw._error_cb_t = error_cb_t

    glfw.glfwSetErrorCallback.argtypes = [error_cb_t]
    glfw.glfwSetErrorCallback.restype = ctypes.c_void_p

    glfw.glfwInitHint.argtypes = [ctypes.c_int, ctypes.c_int]
    glfw.glfwInitHint.restype = None

    glfw.glfwInit.argtypes = []
    glfw.glfwInit.restype = ctypes.c_int

    glfw.glfwTerminate.argtypes = []
    glfw.glfwTerminate.restype = None

    glfw.glfwWindowHint.argtypes = [ctypes.c_int, ctypes.c_int]
    glfw.glfwWindowHint.restype = None

    glfw.glfwCreateWindow.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    glfw.glfwCreateWindow.restype = win

    glfw.glfwDestroyWindow.argtypes = [win]
    glfw.glfwDestroyWindow.restype = None

    glfw.glfwMakeContextCurrent.argtypes = [win]
    glfw.glfwMakeContextCurrent.restype = None

    glfw.glfwSwapInterval.argtypes = [ctypes.c_int]
    glfw.glfwSwapInterval.restype = None

    glfw.glfwGetPlatform.argtypes = []
    glfw.glfwGetPlatform.restype = ctypes.c_int

    glfw.glfwGetWindowAttrib.argtypes = [win, ctypes.c_int]
    glfw.glfwGetWindowAttrib.restype = ctypes.c_int

    glfw.glfwGetWindowSdrWhiteLevel.argtypes = [win]
    glfw.glfwGetWindowSdrWhiteLevel.restype = ctypes.c_float

    glfw.glfwGetWindowTransfer.argtypes = [win]
    glfw.glfwGetWindowTransfer.restype = ctypes.c_uint32

    glfw.glfwGetWindowPrimaries.argtypes = [win]
    glfw.glfwGetWindowPrimaries.restype = ctypes.c_uint32

    glfw.glfwWindowShouldClose.argtypes = [win]
    glfw.glfwWindowShouldClose.restype = ctypes.c_int

    glfw.glfwSetWindowShouldClose.argtypes = [win, ctypes.c_int]
    glfw.glfwSetWindowShouldClose.restype = None

    glfw.glfwGetKey.argtypes = [win, ctypes.c_int]
    glfw.glfwGetKey.restype = ctypes.c_int

    glfw.glfwGetFramebufferSize.argtypes = [win, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
    glfw.glfwGetFramebufferSize.restype = None

    glfw.glfwSwapBuffers.argtypes = [win]
    glfw.glfwSwapBuffers.restype = None

    glfw.glfwPollEvents.argtypes = []
    glfw.glfwPollEvents.restype = None


ERROR_CB = None


def check_shader(shader: int, stage: str) -> None:
    ok = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if ok == GL_TRUE:
        return

    _ = glGetShaderiv(shader, GL_INFO_LOG_LENGTH)
    log = glGetShaderInfoLog(shader)
    if isinstance(log, bytes):
        log = log.decode("utf-8", errors="replace")
    raise RuntimeError(f"Failed to compile {stage}: {log}")


def check_program(program: int) -> None:
    ok = glGetProgramiv(program, GL_LINK_STATUS)
    if ok == GL_TRUE:
        return

    _ = glGetProgramiv(program, GL_INFO_LOG_LENGTH)
    log = glGetProgramInfoLog(program)
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

    vert = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vert, vertex_source)
    glCompileShader(vert)
    check_shader(vert, "vertex shader")

    frag = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(frag, fragment_source)
    glCompileShader(frag)
    check_shader(frag, "fragment shader")

    program = glCreateProgram()
    glAttachShader(program, vert)
    glAttachShader(program, frag)
    glLinkProgram(program)
    check_program(program)

    glDeleteShader(vert)
    glDeleteShader(frag)

    return program


def set_buffer_hints(glfw: ctypes.CDLL, r: int, g: int, b: int, a: int, float_buffer: bool) -> None:
    glfw.glfwWindowHint(GLFW_RED_BITS, r)
    glfw.glfwWindowHint(GLFW_GREEN_BITS, g)
    glfw.glfwWindowHint(GLFW_BLUE_BITS, b)
    glfw.glfwWindowHint(GLFW_ALPHA_BITS, a)
    glfw.glfwWindowHint(GLFW_FLOATBUFFER, GLFW_TRUE if float_buffer else GLFW_FALSE)


def create_window_with_fallbacks(glfw: ctypes.CDLL):
    title = b"tev pure GLFW HDR repro (python)"

    set_buffer_hints(glfw, 16, 16, 16, 16, True)
    window = glfw.glfwCreateWindow(960, 540, title, None, None)

    if not window:
        set_buffer_hints(glfw, 10, 10, 10, 2, False)
        window = glfw.glfwCreateWindow(960, 540, title, None, None)

    if not window:
        set_buffer_hints(glfw, 8, 8, 8, 8, False)
        window = glfw.glfwCreateWindow(960, 540, title, None, None)

    return window


def main() -> int:
    glfw = load_glfw()
    configure_glfw_api(glfw)

    global ERROR_CB

    @glfw._error_cb_t
    def on_error(code: int, desc: bytes) -> None:
        message = desc.decode("utf-8", errors="replace") if desc else "<null>"
        print(f"GLFW error {code}: {message}", file=sys.stderr)

    ERROR_CB = on_error
    glfw.glfwSetErrorCallback(ERROR_CB)

    glfw.glfwInitHint(GLFW_WAYLAND_COLOR_MANAGEMENT, GLFW_TRUE)

    if not glfw.glfwInit():
        print("glfwInit failed", file=sys.stderr)
        return 1

    try:
        glfw.glfwWindowHint(GLFW_CLIENT_API, GLFW_OPENGL_API)
        glfw.glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)
        glfw.glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GLFW_TRUE)
        glfw.glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)

        glfw.glfwWindowHint(GLFW_VISIBLE, GLFW_TRUE)
        glfw.glfwWindowHint(GLFW_RESIZABLE, GLFW_TRUE)
        glfw.glfwWindowHint(GLFW_SCALE_TO_MONITOR, GLFW_TRUE)

        window = create_window_with_fallbacks(glfw)
        if not window:
            print("glfwCreateWindow failed after float/10-bit/8-bit fallbacks", file=sys.stderr)
            return 2

        try:
            glfw.glfwMakeContextCurrent(window)
            glfw.glfwSwapInterval(1)

            program = make_program()
            gain_loc = glGetUniformLocation(program, "gain")

            triangle = (GLfloat * 15)(
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

            vao = glGenVertexArrays(1)
            vbo = glGenBuffers(1)

            glBindVertexArray(vao)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(triangle), triangle, GL_STATIC_DRAW)

            stride = 5 * ctypes.sizeof(GLfloat)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(2 * ctypes.sizeof(GLfloat)))

            glBindVertexArray(0)

            print(f"GLFW platform: {glfw.glfwGetPlatform()} (Wayland value in this fork is 393219)")
            print(f"Framebuffer red bits: {glfw.glfwGetWindowAttrib(window, GLFW_RED_BITS)}")
            print(f"SDR white level: {glfw.glfwGetWindowSdrWhiteLevel(window)}")
            print(f"Window transfer: {glfw.glfwGetWindowTransfer(window)}")
            print(f"Window primaries: {glfw.glfwGetWindowPrimaries(window)}")

            float_allocated = glfw.glfwGetWindowAttrib(window, GLFW_RED_BITS) >= 16
            print(f"Float framebuffer requested: true, allocated: {'true' if float_allocated else 'false'}")

            gain = 4.0
            try:
                while not glfw.glfwWindowShouldClose(window):
                    if glfw.glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS:
                        glfw.glfwSetWindowShouldClose(window, GLFW_TRUE)

                    if (
                        glfw.glfwGetKey(window, GLFW_KEY_EQUAL) == GLFW_PRESS
                        or glfw.glfwGetKey(window, GLFW_KEY_KP_ADD) == GLFW_PRESS
                    ):
                        gain *= 1.01

                    if (
                        glfw.glfwGetKey(window, GLFW_KEY_MINUS) == GLFW_PRESS
                        or glfw.glfwGetKey(window, GLFW_KEY_KP_SUBTRACT) == GLFW_PRESS
                    ):
                        gain /= 1.01

                    fbw = ctypes.c_int(0)
                    fbh = ctypes.c_int(0)
                    glfw.glfwGetFramebufferSize(window, ctypes.byref(fbw), ctypes.byref(fbh))
                    glViewport(0, 0, fbw.value, fbh.value)

                    glClearColor(0.03, 0.03, 0.03, 1.0)
                    glClear(GL_COLOR_BUFFER_BIT)

                    glUseProgram(program)
                    glUniform1f(gain_loc, gain)
                    glBindVertexArray(vao)
                    glDrawArrays(GL_TRIANGLES, 0, 3)
                    glBindVertexArray(0)
                    glUseProgram(0)

                    glfw.glfwSwapBuffers(window)
                    glfw.glfwPollEvents()
            finally:
                glDeleteBuffers(1, [vbo])
                glDeleteVertexArrays(1, [vao])
                glDeleteProgram(program)
        finally:
            glfw.glfwDestroyWindow(window)
    finally:
        glfw.glfwTerminate()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
