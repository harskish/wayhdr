#if !defined(__APPLE__)
#define GL_GLEXT_PROTOTYPES
#endif

#include <GLFW/glfw3.h>

#include <iostream>
#include <stdexcept>
#include <string>

namespace {

void checkShader(GLuint shader, const char* stage) {
    GLint ok = 0;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &ok);
    if (ok == GL_TRUE) {
        return;
    }

    GLint logLen = 0;
    glGetShaderiv(shader, GL_INFO_LOG_LENGTH, &logLen);
    std::string log(static_cast<size_t>(logLen), '\0');
    glGetShaderInfoLog(shader, logLen, nullptr, log.data());

    throw std::runtime_error{std::string{"Failed to compile "} + stage + ": " + log};
}

void checkProgram(GLuint program) {
    GLint ok = 0;
    glGetProgramiv(program, GL_LINK_STATUS, &ok);
    if (ok == GL_TRUE) {
        return;
    }

    GLint logLen = 0;
    glGetProgramiv(program, GL_INFO_LOG_LENGTH, &logLen);
    std::string log(static_cast<size_t>(logLen), '\0');
    glGetProgramInfoLog(program, logLen, nullptr, log.data());

    throw std::runtime_error{"Failed to link program: " + log};
}

GLuint makeProgram() {
    static constexpr const char* kVertexSource = R"(
        #version 330 core
        layout(location = 0) in vec2 inPos;
        layout(location = 1) in vec3 inColor;
        out vec3 vColor;

        void main() {
            vColor = inColor;
            gl_Position = vec4(inPos, 0.0, 1.0);
        }
    )";

    static constexpr const char* kFragmentSource = R"(
        #version 330 core
        in vec3 vColor;
        out vec4 outColor;
        uniform float gain;

        void main() {
            outColor = vec4(vColor * gain, 1.0);
        }
    )";

    const GLuint vert = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vert, 1, &kVertexSource, nullptr);
    glCompileShader(vert);
    checkShader(vert, "vertex shader");

    const GLuint frag = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(frag, 1, &kFragmentSource, nullptr);
    glCompileShader(frag);
    checkShader(frag, "fragment shader");

    const GLuint program = glCreateProgram();
    glAttachShader(program, vert);
    glAttachShader(program, frag);
    glLinkProgram(program);
    checkProgram(program);

    glDeleteShader(vert);
    glDeleteShader(frag);

    return program;
}

} // namespace

int main() {
    glfwSetErrorCallback([](int code, const char* desc) {
        std::cerr << "GLFW error " << code << ": " << desc << "\n";
    });

    // This init hint is specific to tev's GLFW fork and enables Wayland color-management wiring.
    glfwInitHint(GLFW_WAYLAND_COLOR_MANAGEMENT, GLFW_TRUE);

    if (!glfwInit()) {
        std::cerr << "glfwInit failed\n";
        return 1;
    }

    glfwWindowHint(GLFW_CLIENT_API, GLFW_OPENGL_API);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GLFW_TRUE);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    glfwWindowHint(GLFW_VISIBLE, GLFW_TRUE);
    glfwWindowHint(GLFW_RESIZABLE, GLFW_TRUE);
    glfwWindowHint(GLFW_SCALE_TO_MONITOR, GLFW_TRUE);

    auto setBufferHints = [](int r, int g, int b, int a, bool floatBuffer) {
        glfwWindowHint(GLFW_RED_BITS, r);
        glfwWindowHint(GLFW_GREEN_BITS, g);
        glfwWindowHint(GLFW_BLUE_BITS, b);
        glfwWindowHint(GLFW_ALPHA_BITS, a);
#if defined(GLFW_FLOATBUFFER)
        glfwWindowHint(GLFW_FLOATBUFFER, floatBuffer ? GLFW_TRUE : GLFW_FALSE);
#else
        (void)floatBuffer;
#endif
    };

    GLFWwindow* window = nullptr;

    // Match tev/NanoGUI behavior: try float first, then 10-bit, then plain 8-bit.
    setBufferHints(16, 16, 16, 16, true);
    window = glfwCreateWindow(960, 540, "tev pure GLFW HDR repro", nullptr, nullptr);

    if (!window) {
        setBufferHints(10, 10, 10, 2, false);
        window = glfwCreateWindow(960, 540, "tev pure GLFW HDR repro", nullptr, nullptr);
    }

    if (!window) {
        setBufferHints(8, 8, 8, 8, false);
        window = glfwCreateWindow(960, 540, "tev pure GLFW HDR repro", nullptr, nullptr);
    }

    if (!window) {
        std::cerr << "glfwCreateWindow failed after float/10-bit/8-bit fallbacks\n";
        glfwTerminate();
        return 2;
    }

    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);

    const GLuint program = makeProgram();
    const GLint gainLoc = glGetUniformLocation(program, "gain");

    static constexpr float kTriangle[] = {
        // pos.xy     color.rgb
         0.0f,  0.72f, 1.0f, 1.0f, 1.0f,
        -0.8f, -0.75f, 1.0f, 0.2f, 0.2f,
         0.8f, -0.75f, 0.2f, 1.0f, 0.2f,
    };

    GLuint vao = 0;
    GLuint vbo = 0;
    glGenVertexArrays(1, &vao);
    glGenBuffers(1, &vbo);

    glBindVertexArray(vao);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(kTriangle), kTriangle, GL_STATIC_DRAW);

    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), reinterpret_cast<void*>(0));

    glEnableVertexAttribArray(1);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), reinterpret_cast<void*>(2 * sizeof(float)));

    glBindVertexArray(0);

    std::cout << "GLFW platform: " << glfwGetPlatform() << " (Wayland value in this fork is 393219)\n";
    std::cout << "Framebuffer red bits: " << glfwGetWindowAttrib(window, GLFW_RED_BITS) << "\n";
    std::cout << "SDR white level: " << glfwGetWindowSdrWhiteLevel(window) << "\n";
    std::cout << "Window transfer: " << glfwGetWindowTransfer(window) << "\n";
    std::cout << "Window primaries: " << glfwGetWindowPrimaries(window) << "\n";

    const bool floatAllocated = glfwGetWindowAttrib(window, GLFW_RED_BITS) >= 16;
    std::cout << "Float framebuffer requested: true, allocated: "
              << (floatAllocated ? "true" : "false")
              << "\n";

    float gain = 4.0f;

    while (!glfwWindowShouldClose(window)) {
        if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
            glfwSetWindowShouldClose(window, GLFW_TRUE);
        }

        if (glfwGetKey(window, GLFW_KEY_EQUAL) == GLFW_PRESS || glfwGetKey(window, GLFW_KEY_KP_ADD) == GLFW_PRESS) {
            gain *= 1.01f;
        }

        if (glfwGetKey(window, GLFW_KEY_MINUS) == GLFW_PRESS || glfwGetKey(window, GLFW_KEY_KP_SUBTRACT) == GLFW_PRESS) {
            gain /= 1.01f;
        }

        int fbw = 0;
        int fbh = 0;
        glfwGetFramebufferSize(window, &fbw, &fbh);
        glViewport(0, 0, fbw, fbh);

        glClearColor(0.03f, 0.03f, 0.03f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        glUseProgram(program);
        glUniform1f(gainLoc, gain);
        glBindVertexArray(vao);
        glDrawArrays(GL_TRIANGLES, 0, 3);
        glBindVertexArray(0);
        glUseProgram(0);

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    glDeleteBuffers(1, &vbo);
    glDeleteVertexArrays(1, &vao);
    glDeleteProgram(program);

    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}
