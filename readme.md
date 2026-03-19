## Build
```
cmake -S . -B build -DBUILD_SHARED_LIBS=ON
cmake --build build -j
WAYHDR_GLFW_LIB=build/external/glfw/src/libglfw.so python3 src/main.py
```