# LiDAR 快速参考手册

## 核心概念速查

### LiDAR 基本原理

```
距离 = (光速 × 飞行时间) / 2

其中：
- 光速 c ≈ 3 × 10^8 m/s
- 飞行时间：激光发射到接收的时间间隔
```

### 关键参数定义

| 参数 | 英文 | 说明 | 典型值 |
|------|------|------|--------|
| RPM | Rotations Per Minute | 每分钟旋转圈数 | 5-20 |
| 线数 | Laser Lines | 垂直方向激光器数量 | 16/32/64 |
| 垂直 FOV | Vertical Field of View | 垂直扫描范围 | ±15°~±30° |
| 水平分辨率 | Horizontal Resolution | 水平角度分辨率 | 0.1°~0.4° |
| 探测距离 | Detection Range | 最大有效距离 | 100-200m |

---

## 关键公式

### 坐标转换

**球坐标 → 直角坐标**：

```python
# 已知：距离 d，水平角 h，垂直角 v
x = d * cos(v) * cos(h)
y = d * sin(v)
z = d * cos(v) * sin(h)
```

**直角坐标 → 球坐标**：

```python
# 已知：直角坐标 (x, y, z)
d = sqrt(x² + y² + z²)
h = atan2(z, x)
v = atan2(y, sqrt(x² + z²))
```

### 分辨率计算

```python
# 水平分辨率
horizontal_resolution = 360 / points_per_rotation

# 垂直分辨率
vertical_resolution = vertical_fov / (laser_lines - 1)

# 点云密度（点/秒）
point_density = horizontal_points * laser_lines * rpm / 60
```

### 角度与弧度转换

```python
import math

# 角度 → 弧度
radians = math.radians(degrees)

# 弧度 → 角度
degrees = math.degrees(radians)

# RPM → 度/秒
degrees_per_second = rpm * 6.0
```

---

## 碰撞检测算法

### 射线-AABB 相交（Slab 方法）

```python
def ray_aabb_intersect(ray_origin, ray_dir, box_min, box_max):
    """
    射线与轴对齐包围盒相交检测

    返回：(是否相交, 相交参数t)
    """
    tmin, tmax = -float('inf'), float('inf')

    for i in range(3):  # X, Y, Z 三个轴
        if abs(ray_dir[i]) < 1e-8:
            if ray_origin[i] < box_min[i] or ray_origin[i] > box_max[i]:
                return False, float('inf')
        else:
            t1 = (box_min[i] - ray_origin[i]) / ray_dir[i]
            t2 = (box_max[i] - ray_origin[i]) / ray_dir[i]
            if t1 > t2:
                t1, t2 = t2, t1
            tmin = max(tmin, t1)
            tmax = min(tmax, t2)
            if tmin > tmax:
                return False, float('inf')

    t = tmin if tmin >= 0 else tmax
    return True, t
```

### 射线-平面相交

```python
def ray_plane_intersect(ray_origin, ray_dir, plane_point, plane_normal):
    """
    射线与平面相交检测

    参数：
        ray_origin: 射线起点
        ray_dir: 射线方向（需归一化）
        plane_point: 平面上一点
        plane_normal: 平面法向量（需归一化）

    返回：(是否相交, 相交参数t, 交点)
    """
    denom = np.dot(plane_normal, ray_dir)
    if abs(denom) < 1e-8:
        return False, float('inf'), None  # 射线与平面平行

    t = np.dot(plane_point - ray_origin, plane_normal) / denom
    if t < 0:
        return False, float('inf'), None  # 交点在射线反向

    hit_point = ray_origin + t * ray_dir
    return True, t, hit_point
```

### 射线-圆柱相交

```python
def ray_cylinder_intersect(ray_origin, ray_dir, cylinder_center, radius, height):
    """
    射线与Y轴对齐圆柱相交检测

    圆柱方程：x² + z² = r²
    """
    ox = ray_origin[0] - cylinder_center[0]
    oz = ray_origin[2] - cylinder_center[2]
    dx, dz = ray_dir[0], ray_dir[2]

    # 二次方程系数
    a = dx*dx + dz*dz
    b = 2 * (ox*dx + oz*dz)
    c = ox*ox + oz*oz - radius*radius

    discriminant = b*b - 4*a*c
    if discriminant < 0:
        return False, float('inf')

    sqrt_disc = math.sqrt(discriminant)
    t1 = (-b - sqrt_disc) / (2*a)
    t2 = (-b + sqrt_disc) / (2*a)

    # 检查高度限制和取正解
    for t in [t1, t2]:
        if t >= 0:
            y = ray_origin[1] + t * ray_dir[1]
            if cylinder_center[1] <= y <= cylinder_center[1] + height:
                return True, t

    return False, float('inf')
```

---

## OpenGL 常用代码片段

### 初始化设置

```python
from OpenGL.GL import *
from OpenGL.GLU import *

def initializeGL():
    # 背景颜色
    glClearColor(0.15, 0.15, 0.18, 1.0)

    # 深度测试
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)

    # 混合（透明度）
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # 光照
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 10.0, 5.0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
```

### 绘制基本形状

```python
def draw_cylinder(radius, height, slices=32):
    """绘制圆柱体"""
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quadric, radius, radius, height, slices, 1)
    glPopMatrix()
    gluDeleteQuadric(quadric)

def draw_sphere(radius, slices=32, stacks=32):
    """绘制球体"""
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluSphere(quadric, radius, slices, stacks)
    gluDeleteQuadric(quadric)

def draw_box(width, height, depth):
    """绘制长方体"""
    w, h, d = width/2, height/2, depth/2
    glBegin(GL_QUADS)
    # 前面
    glNormal3f(0, 0, 1)
    glVertex3f(-w, -h, d); glVertex3f(w, -h, d)
    glVertex3f(w, h, d); glVertex3f(-w, h, d)
    # 后面
    glNormal3f(0, 0, -1)
    glVertex3f(-w, -h, -d); glVertex3f(-w, h, -d)
    glVertex3f(w, h, -d); glVertex3f(w, -h, -d)
    # 其他面...
    glEnd()
```

### 点云绘制

```python
def draw_point_cloud(points, colors):
    """绘制点云

    参数：
        points: [(x, y, z), ...]
        colors: [(r, g, b, a), ...] 或按类型的颜色映射
    """
    glDisable(GL_LIGHTING)
    glPointSize(3.0)

    glBegin(GL_POINTS)
    for i, point in enumerate(points):
        if isinstance(colors, dict):
            # 按类型着色
            color = colors.get(point[3], (0.5, 0.5, 0.5, 1.0))
        else:
            color = colors[i]
        glColor4fv(color)
        glVertex3f(point[0], point[1], point[2])
    glEnd()

    glEnable(GL_LIGHTING)
```

### 相机设置

```python
def setup_camera(fov=45, aspect=16/9, near=0.1, far=100):
    """设置透视投影"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fov, aspect, near, far)
    glMatrixMode(GL_MODELVIEW)

def look_at(eye, target, up):
    """设置视图矩阵"""
    glLoadIdentity()
    gluLookAt(
        eye[0], eye[1], eye[2],
        target[0], target[1], target[2],
        up[0], up[1], up[2]
    )
```

---

## PyQt5 常用代码片段

### 创建滑块控件

```python
from PyQt5.QtWidgets import QSlider, QLabel, QVBoxLayout

def create_slider(name, min_val, max_val, default, callback):
    """创建带标签的滑块"""
    layout = QVBoxLayout()

    label = QLabel(f"{name}: {default}")
    slider = QSlider(Qt.Horizontal)
    slider.setMinimum(min_val)
    slider.setMaximum(max_val)
    slider.setValue(default)

    def on_change(val):
        label.setText(f"{name}: {val}")
        callback(val)

    slider.valueChanged.connect(on_change)

    layout.addWidget(label)
    layout.addWidget(slider)
    return layout, slider
```

### 定时器动画

```python
from PyQt5.QtCore import QTimer

class AnimationWidget:
    def __init__(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 FPS
        self.last_time = time.time()

    def update_animation(self):
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        # 更新动画状态
        self.rotation_angle += self.rpm * 6.0 * dt

        # 触发重绘
        self.update()
```

---

## 快捷键参考

### 程序控制

| 快捷键 | 功能 |
|--------|------|
| `R` | 重置视角到默认位置 |
| `1` | 切换到俯视图 |
| `2` | 切换到正视图 |
| `3` | 切换到侧视图 |
| `4` | 切换到透视图 |
| `5` | 切换到等轴视图 |
| `ESC` | 退出程序 |
| `Space` | 暂停/继续动画 |

### 鼠标操作

| 操作 | 功能 |
|------|------|
| 左键拖拽 | 旋转视角 |
| 右键拖拽 | 平移视角 |
| 滚轮 | 缩放 |
| 双击 | 重置视角 |

---

## 故障排除

### 常见错误及解决方案

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `ModuleNotFoundError: No module named 'PyQt5'` | 依赖未安装 | `pip install PyQt5` |
| `OpenGL error: invalid operation` | OpenGL 状态错误 | 检查 GL 调用顺序 |
| `glCreateShader failed` | 显卡不支持 | 更新显卡驱动 |
| 程序窗口黑屏 | OpenGL 初始化失败 | 检查 GL 版本支持 |
| 点云不显示 | 碰撞检测失败 | 检查射线方向和范围 |
| 动画卡顿 | 帧率过低 | 减少点云数量或优化渲染 |

### 调试技巧

```python
# 检查 OpenGL 错误
def check_gl_error():
    error = glGetError()
    if error != GL_NO_ERROR:
        print(f"OpenGL Error: {error}")

# 打印点云统计
def print_point_cloud_stats(points):
    print(f"点云数量: {len(points)}")
    if points:
        arr = np.array([p[:3] for p in points])
        print(f"X 范围: [{arr[:,0].min():.2f}, {arr[:,0].max():.2f}]")
        print(f"Y 范围: [{arr[:,1].min():.2f}, {arr[:,1].max():.2f}]")
        print(f"Z 范围: [{arr[:,2].min():.2f}, {arr[:,2].max():.2f}]")
```

---

## 文件结构速查

```
lidar_architecture/
├── main.py                 # 程序入口
├── requirements.txt        # 依赖列表
├── convert_to_html.py      # Markdown 转 HTML
│
├── ui/
│   ├── main_window.py      # 主窗口
│   └── control_panel.py    # 控制面板
│
├── opengl/
│   ├── gl_widget.py        # OpenGL 控件
│   ├── camera.py           # 相机控制
│   ├── scene.py            # 场景管理
│   └── environment.py      # 环境对象
│
└── docs/
    ├── textbook/           # 教材文档
    └── images/             # 图片资源
```

---

## 常用命令

### 环境管理

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 冻结依赖
pip freeze > requirements.txt
```

### 运行和测试

```bash
# 运行主程序
python main.py

# 转换文档
python convert_to_html.py

# 启动本地服务器查看文档
python -m http.server 8000
```

---

*本快速参考手册配套项目：机械旋转式激光雷达教学演示系统*

*最后更新：2026年2月*
