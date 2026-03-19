cmake_minimum_required(VERSION 3.20)
project(hdr_triangle_glfw LANGUAGES C CXX)

option(USE_SYSTEM_GLFW "Use system-installed GLFW instead of bundled submodule" OFF)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(hdr_triangle_glfw
    src/main.cpp
)

if (USE_SYSTEM_GLFW)
    find_package(glfw3 CONFIG REQUIRED)
    target_link_libraries(hdr_triangle_glfw PRIVATE glfw)
else()
    # Assumes tev GLFW fork is vendored at external/glfw
    # Example:
    #   git submodule add <your-fork-url> external/glfw
    set(GLFW_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
    set(GLFW_BUILD_TESTS OFF CACHE BOOL "" FORCE)
    set(GLFW_BUILD_DOCS OFF CACHE BOOL "" FORCE)
    set(GLFW_INSTALL OFF CACHE BOOL "" FORCE)
    set(GLFW_BUILD_INSTALL OFF CACHE BOOL "" FORCE)

    add_subdirectory(external/glfw)
    target_link_libraries(hdr_triangle_glfw PRIVATE glfw)
endif()

find_package(OpenGL REQUIRED)

if (TARGET OpenGL::GL)
    target_link_libraries(hdr_triangle_glfw PRIVATE OpenGL::GL)
elseif (UNIX AND NOT APPLE)
    target_link_libraries(hdr_triangle_glfw PRIVATE GL)
endif()

if (MSVC)
    target_compile_options(hdr_triangle_glfw PRIVATE /W4)
else()
    target_compile_options(hdr_triangle_glfw PRIVATE -Wall -Wextra -Wshadow -Wno-unused-parameter)
endif()
