# LiDAR 教学演示系统 - 复现提示词

本文档包含复现整个项目所需的关键提示词和技术要点。

---

## 项目概述

### 一句话描述
创建一个 Python 桌面应用程序，用于教学演示机械旋转式激光雷达的内部结构、工作原理和点云生成过程。

### 核心功能
1. LiDAR 3D 模型可视化（外壳、电机、激光单元）
2. 旋转动画模拟
3. 射线碰撞检测（射线-AABB、射线-圆柱）
4. 环境模拟（车辆、墙壁）
5. 实时点云生成和渲染
6. 参数可调的控制面板

---

## 技术栈

```
- GUI 框架: PyQt5
- 3D 渲染: PyOpenGL
- 数学计算: NumPy
- 动画计时: QTimer
```

---

## 项目结构提示词

```
创建以下项目结构：

lidar_architecture/
├── main.py                      # 程序入口
├── requirements.txt             # PyQt5, PyOpenGL, numpy
├── ui/
│   ├── __init__.py
│   ├── main_window.py           # 主窗口，左侧OpenGL+右侧控制面板
│   └── control_panel.py         # 参数滑块、复选框、视角按钮
├── opengl/
│   ├── __init__.py
│   ├── gl_widget.py             # QOpenGLWidget，渲染循环60fps
│   ├── scene.py                 # 场景管理，点云生成
│   ├── camera.py                # 球坐标系相机，预设视角
│   └── environment.py           # 环境、射线碰撞检测
└── core/
    └── __init__.py
```

---

## 模块实现提示词

### 1. 主入口 (main.py)

```
使用 PyQt5 创建应用程序入口：
- QApplication 初始化
- 创建 MainWindow 并显示
- 窗口标题："机械旋转式激光雷达动画演示系统"
- 最小尺寸 1200x800
```

### 2. 主窗口 (ui/main_window.py)

```
创建主窗口布局：
- 使用 QSplitter 水平分割
- 左侧：GLWidget（OpenGL 渲染区域）
- 右侧：ControlPanel（控制面板，最大宽度 300px）
- 状态栏显示 FPS 和旋转角度
- 连接控制面板信号到 OpenGL 控件

样式要求：
- 浅灰色背景 #f0f0f0
- QGroupBox 有边框和圆角
- 按钮悬停有颜色变化
```

### 3. 控制面板 (ui/control_panel.py)

```
创建控制面板，包含：

扫描参数组：
- 转速滑块 (1-20 RPM，默认 10)
- 激光线数滑块 (1-64，默认 16)
- 垂直视场角滑块 (10-45°，默认 30°)

显示控制组：
- 复选框：外壳和旋转头、电机传动、激光单元、激光束、点云、环境模型

视角预设组：
- 按钮：俯视图、正视图、侧视图、透视图、等轴视图、重置视角

使用 pyqtSignal 发送参数变更信号
```

### 4. OpenGL 控件 (opengl/gl_widget.py)

```
创建 QOpenGLWidget 子类：

initializeGL：
- 背景色 (0.15, 0.15, 0.18)
- 启用深度测试 GL_LEQUAL
- 启用混合 GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
- 启用光照 GL_LIGHT0

resizeGL：
- 设置视口
- 调用 camera.apply_projection()

paintGL：
- 清除颜色和深度缓冲
- 应用相机视图
- 渲染场景

动画：
- QTimer 16ms (~60fps)
- 计算帧率 FPS

鼠标交互：
- 左键拖拽旋转视角
- 滚轮缩放
```

### 5. 相机 (opengl/camera.py)

```
球坐标系相机：
- distance: 到目标点距离 (2.0-20.0)
- azimuth: 水平角度
- elevation: 垂直角度 (-89° to 89°)
- target: 观察目标点

方法：
- get_position(): 计算相机位置
- apply_view(): 调用 gluLookAt()
- apply_projection(): 调用 gluPerspective()
- rotate(dx, dy): 鼠标拖拽旋转
- zoom(delta): 滚轮缩放
- set_preset_view(name): 预设视角
  - top: (90°, 0°, 6)
  - front: (0°, 0°, 8)
  - side: (90°, 0°, 8)
  - perspective: (45°, 30°, 8)
  - isometric: (45°, 35°, 10)

平滑过渡：
- target_distance, target_azimuth, target_elevation
- smooth_factor = 0.1
```

### 6. 场景 (opengl/scene.py)

```
场景管理类：

参数：
- rotation_angle: 当前旋转角度
- rotation_speed: 转速 RPM
- laser_lines: 激光线数
- vertical_fov: 垂直视场角
- visible_components: 可见性字典
- environment: Environment 实例
- point_cloud_data: 点云数据列表

渲染方法：
- _draw_ground_grid(): 地面网格
- _draw_axes(): XYZ 坐标轴（红绿蓝）
- _draw_lidar_body(): 底座圆柱、主体圆柱
- _draw_rotating_head(): 旋转头（随角度旋转）
- _draw_motor(): 电机、齿轮、轴承
- _draw_laser_unit(): 发射器阵列（红色）、接收器阵列（绿色）
- _draw_laser_beams(): 激光束线条
- _draw_point_cloud(): 点云点

LiDAR 模型尺寸：
- 底座：半径 0.6，高度 0.3
- 主体：半径 0.5，高度 1.2
- 旋转头：半径 0.4，高度 0.4
- 位置：Y 轴 -1.5 到 0.6

更新逻辑：
- angle_per_second = rotation_speed * 6.0
- 每 2 帧更新一次点云
```

### 7. 环境与碰撞检测 (opengl/environment.py)

```
射线类 Ray：
- origin: 起点 np.array
- direction: 方向（自动归一化）

Box 类（长方体）：
- center, size
- ray_intersect(ray): Slab 方法
  - 遍历 X, Y, Z 三个轴
  - 计算 tmin, tmax
  - 返回 (是否相交, 距离)

Cylinder 类（圆柱）：
- center, radius, height, axis
- ray_intersect(ray): 二次方程法
  - 解方程 at² + bt + c = 0
  - 检查高度限制
  - 返回 (是否相交, 距离)

Vehicle 类（车辆）：
- 组合：车身 Box + 车顶 Box + 4个车轮 Cylinder
- 位置：前方 4 米
- 尺寸：长 4m × 宽 1.8m × 高 1.2m
- 颜色：蓝色 (0.2, 0.4, 0.8)

Wall 类（墙壁）：
- Box 几何体
- 位置：前方 7 米
- 尺寸：厚 0.2m × 高 4m × 宽 10m
- 颜色：灰色 (0.6, 0.6, 0.6)

Environment 类：
- vehicle, wall, ground_y
- ray_cast(origin, direction, max_distance):
  - 检测车辆、墙壁、地面
  - 返回最近碰撞点和对象类型
```

### 8. 点云生成算法

```python
def generate_point_cloud(self):
    lidar_origin = np.array([0.35, 0.4, 0])
    horizontal_resolution = 1.0  # 度

    for h_angle in range(0, 360, 1):
        h_rad = radians(h_angle)
        for i in range(self.laser_lines):
            # 垂直角度均匀分布
            v_angle = -fov/2 + fov * i / (lines - 1)
            v_rad = radians(v_angle)

            # 计算方向向量
            dx = cos(v_rad) * cos(h_rad)
            dy = sin(v_rad)
            dz = cos(v_rad) * sin(h_rad)

            # 射线检测
            hit_point, dist, obj = environment.ray_cast(origin, direction)
            if hit_point:
                point_cloud.append((x, y, z, obj_type))
```

### 9. 点云着色

```
根据碰撞对象类型：
- vehicle: 蓝色 (0.2, 0.5, 1.0)
- wall: 黄色 (1.0, 0.8, 0.2)
- ground: 绿色 (0.2, 0.8, 0.3)

渲染：
- glDisable(GL_LIGHTING)
- glPointSize(3.0)
- glBegin(GL_POINTS)
```

---

## 关键算法提示词

### 射线-AABB 相交（Slab 方法）

```
算法原理：将 AABB 看作三个无限 Slab 的交集

for i in [0, 1, 2]:  # X, Y, Z
    if direction[i] == 0:
        # 射线平行于该轴
        if origin[i] outside slab: return false
    else:
        t1 = (min[i] - origin[i]) / direction[i]
        t2 = (max[i] - origin[i]) / direction[i]
        if t1 > t2: swap(t1, t2)
        tmin = max(tmin, t1)
        tmax = min(tmax, t2)
        if tmin > tmax: return false

return tmin if tmin >= 0 else tmax
```

### 射线-圆柱相交

```
圆柱方程: x² + z² = r²
射线: P(t) = origin + t * direction

代入得到二次方程：
a = dx² + dz²
b = 2 * (ox*dx + oz*dz)
c = ox² + oz² - r²

discriminant = b² - 4ac
if discriminant < 0: 无交点

t1 = (-b - sqrt(d)) / (2a)
t2 = (-b + sqrt(d)) / (2a)

检查高度限制：base_y <= hit_y <= top_y
```

---

## 运行和测试

### 安装依赖

```bash
pip install PyQt5 PyOpenGL numpy
```

### 运行程序

```bash
python main.py
```

### 验证清单

- [ ] 窗口正常显示，左侧 3D 视图，右侧控制面板
- [ ] LiDAR 模型正确渲染
- [ ] 旋转动画流畅（60fps）
- [ ] 鼠标拖拽旋转视角
- [ ] 滚轮缩放
- [ ] 参数滑块响应
- [ ] 复选框控制显示
- [ ] 预设视角按钮工作
- [ ] 点云正确生成（蓝色车辆、黄色墙壁、绿色地面）

---

## 快捷键

| 键 | 功能 |
|----|------|
| R | 重置视角 |
| 1 | 俯视图 |
| 2 | 正视图 |
| 3 | 侧视图 |
| 4 | 透视图 |
| 5 | 等轴视图 |
| ESC | 退出 |

---

## 截图生成

```bash
python capture_screenshots.py
```

截图保存到 `docs/images/`

---

## 文档生成

### Markdown → HTML

```bash
python convert_to_html.py
```

### HTML → PDF

```bash
# 启动服务器
cd docs && python -m http.server 8888

# 浏览器打开，Cmd+P 打印为 PDF
# http://localhost:8888/textbook/lidar-teaching-material.html
```

---

## 完整复现流程

```
1. 创建项目结构和 requirements.txt
2. 实现 main.py 入口
3. 实现 ui/main_window.py 主窗口
4. 实现 ui/control_panel.py 控制面板
5. 实现 opengl/gl_widget.py OpenGL 控件
6. 实现 opengl/camera.py 相机
7. 实现 opengl/environment.py 环境和碰撞
8. 实现 opengl/scene.py 场景渲染
9. 运行测试
10. 截图
11. 生成文档
```

---

*本文档可用于指导 AI 助手复现整个项目*
