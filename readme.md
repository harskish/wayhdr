# GLFW
- https://github.com/Tom94/glfw/commits/tev-rebased/
- https://github.com/wjakob/glfw/commits/master/

## Build
```
cmake -S . -B build -DBUILD_SHARED_LIBS=ON
cmake --build build -j
WAYHDR_GLFW_LIB=build/external/glfw/src/libglfw.so python3 src/main.py
PYGLFW_LIBRARY=build/external/glfw/src/libglfw.so python src/main_imgui_bundle.py
```
