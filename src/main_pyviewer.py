#!/usr/bin/env python3
import os

import numpy as np

from wl_hdr import configure_pyglfw_library, GLFW_WAYLAND_COLOR_MANAGEMENT
configure_pyglfw_library()

import glfw  # type: ignore
from imgui_bundle import imgui
from pyviewer.docking_viewer import DockingViewer, dockable  # type: ignore[import-not-found]


def _make_test_image(height: int = 512, width: int = 512) -> np.ndarray:
    l1 = np.linspace(0.0, 1.0, max(height, width), dtype=np.float32)
    l2 = np.linspace(1.0, 0.0, max(height, width), dtype=np.float32)

    grad_r = l1.reshape(-1, 1) * l1.reshape(1, -1)
    grad_g = l1.reshape(-1, 1) * l2.reshape(1, -1)
    grad_b = l2.reshape(-1, 1) * l1.reshape(1, -1)

    img = np.stack((grad_r, grad_b, grad_g), axis=-1)
    return img[:height, :width, :]


def _safe_glfw_call(name: str, default):
    fn = getattr(glfw, name, None)
    if fn is None:
        return default
    try:
        return fn()
    except Exception:
        return default


TEST_IMAGE = _make_test_image()


class WaylandHDRViewer(DockingViewer):
    def setup_state(self):
        self.gain = 4.0
        self.auto_gain = False
        self.max_gain = 16.0

        self.platform = _safe_glfw_call("get_platform", "<unavailable>")
        self.transfer = _safe_glfw_call("get_window_transfer", "<unavailable>")
        self.primaries = _safe_glfw_call("get_window_primaries", "<unavailable>")

        print(f"GLFW platform: {self.platform}")
        print(f"PYGLFW_LIBRARY={os.environ.get('PYGLFW_LIBRARY', '<unset>')}")
        print(f"Window transfer: {self.transfer}")
        print(f"Window primaries: {self.primaries}")

    def compute(self):
        if self.auto_gain:
            self.gain = min(self.gain * 1.0005, self.max_gain)
        self.update_image(img_hwc=TEST_IMAGE * self.gain)

    @dockable
    def toolbar(self):
        imgui.text("DockingViewer HDR test pattern")
        imgui.text("Use gain > 1.0 to probe headroom")

        changed, self.gain = imgui.slider_float("Gain", self.gain, 0.1, self.max_gain)
        if changed and self.gain < 0.1:
            self.gain = 0.1
        self.auto_gain = imgui.checkbox("Auto gain", self.auto_gain)[1]

        imgui.separator()
        imgui.text(f"PYGLFW_LIBRARY={os.environ.get('PYGLFW_LIBRARY', '<unset>')}")
        imgui.text(f"Platform: {self.platform}")
        imgui.text(f"Transfer: {self.transfer}")
        imgui.text(f"Primaries: {self.primaries}")

        if self.window:
            red_bits = glfw.get_window_attrib(self.window, glfw.RED_BITS)
            green_bits = glfw.get_window_attrib(self.window, glfw.GREEN_BITS)
            blue_bits = glfw.get_window_attrib(self.window, glfw.BLUE_BITS)
            imgui.text(f"Framebuffer bits: R{red_bits} G{green_bits} B{blue_bits}")


def main() -> int:
    if hasattr(glfw, "init_hint"):
        glfw.init_hint(GLFW_WAYLAND_COLOR_MANAGEMENT, glfw.TRUE)

    WaylandHDRViewer("Wayland HDR DockingViewer repro", normalize=False)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
