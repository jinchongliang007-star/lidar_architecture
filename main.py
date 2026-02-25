#!/usr/bin/env python3
"""
机械旋转式激光雷达动画演示系统
Mechanical Rotating LiDAR Animation Demo System
"""

import sys
import os

# 确保项目根目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """程序入口"""
    app = QApplication(sys.argv)
    app.setApplicationName("LiDAR Architecture Demo")
    app.setApplicationVersion("1.0.0")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
