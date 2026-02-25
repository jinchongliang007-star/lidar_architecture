#!/usr/bin/env python3
"""
截图脚本 - 捕获 LiDAR 演示系统的关键界面
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from ui.main_window import MainWindow

# 截图保存目录
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), 'docs', 'images')

def ensure_dir():
    """确保截图目录存在"""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def capture_screenshot(widget, filename):
    """捕获控件截图"""
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    pixmap = widget.grab()
    pixmap.save(filepath, 'PNG')
    print(f'Saved: {filepath}')
    return filepath

def main():
    ensure_dir()

    app = QApplication(sys.argv)
    app.setApplicationName("LiDAR Architecture Demo")

    window = MainWindow()
    window.show()
    window.resize(1400, 900)

    # 等待窗口完全显示
    app.processEvents()

    step = [0]

    def next_step():
        s = step[0]

        if s == 0:
            # 1. 主界面全景 - 默认视角
            print("Capturing: Main interface...")
            capture_screenshot(window, 'main-interface.png')
            step[0] = 1
            QTimer.singleShot(500, next_step)

        elif s == 1:
            # 2. LiDAR 模型特写 - 侧视图
            print("Capturing: LiDAR model (side view)...")
            window.gl_widget.set_preset_view('side')
            step[0] = 2
            QTimer.singleShot(500, next_step)

        elif s == 2:
            capture_screenshot(window, 'lidar-model-side.png')
            step[0] = 3
            QTimer.singleShot(500, next_step)

        elif s == 3:
            # 3. 点云效果 - 透视图
            print("Capturing: Point cloud (perspective view)...")
            window.gl_widget.set_preset_view('perspective')
            step[0] = 4
            QTimer.singleShot(500, next_step)

        elif s == 4:
            capture_screenshot(window, 'point-cloud-perspective.png')
            step[0] = 5
            QTimer.singleShot(500, next_step)

        elif s == 5:
            # 4. 俯视图
            print("Capturing: Top view...")
            window.gl_widget.set_preset_view('top')
            step[0] = 6
            QTimer.singleShot(500, next_step)

        elif s == 6:
            capture_screenshot(window, 'top-view.png')
            step[0] = 7
            QTimer.singleShot(500, next_step)

        elif s == 7:
            # 5. 等轴视图
            print("Capturing: Isometric view...")
            window.gl_widget.set_preset_view('isometric')
            step[0] = 8
            QTimer.singleShot(500, next_step)

        elif s == 8:
            capture_screenshot(window, 'isometric-view.png')
            step[0] = 9
            QTimer.singleShot(500, next_step)

        elif s == 9:
            # 6. 控制面板特写
            print("Capturing: Control panel...")
            control_panel = window.control_panel
            filepath = os.path.join(SCREENSHOT_DIR, 'control-panel.png')
            control_panel.grab().save(filepath, 'PNG')
            print(f'Saved: {filepath}')
            step[0] = 10
            QTimer.singleShot(300, next_step)

        elif s == 10:
            # 7. 正视图
            print("Capturing: Front view...")
            window.gl_widget.set_preset_view('front')
            step[0] = 11
            QTimer.singleShot(500, next_step)

        elif s == 11:
            capture_screenshot(window, 'front-view.png')
            step[0] = 12
            QTimer.singleShot(300, next_step)

        else:
            # 完成
            print("\n" + "="*50)
            print("All screenshots captured successfully!")
            print(f"Location: {SCREENSHOT_DIR}")
            print("="*50)

            # 列出所有截图
            print("\nCaptured files:")
            for f in sorted(os.listdir(SCREENSHOT_DIR)):
                if f.endswith('.png'):
                    print(f"  - {f}")

            app.quit()

    # 延迟开始截图，等待场景渲染
    QTimer.singleShot(1500, next_step)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
