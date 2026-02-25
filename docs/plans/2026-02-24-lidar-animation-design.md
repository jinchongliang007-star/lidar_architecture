# 机械旋转式激光雷达动画演示系统 - 设计文档

## 背景

创建一个Python桌面应用程序，用于教学演示机械旋转式激光雷达的内部结构和工作原理。支持展示和交互两种模式。

## 技术选型

- **GUI框架**: PyQt5 - 成熟的跨平台GUI库
- **3D渲染**: PyOpenGL - 高性能3D图形渲染
- **数学计算**: NumPy - 向量和矩阵运算
- **动画计时**: QTimeLine/QTimer - 流畅的动画帧控制

## 系统架构

```
lidar_architecture/
├── main.py                 # 程序入口
├── requirements.txt        # 依赖管理
├── ui/
│   ├── __init__.py
│   ├── main_window.py      # 主窗口
│   └── control_panel.py    # 控制面板组件
├── opengl/
│   ├── __init__.py
│   ├── gl_widget.py        # OpenGL渲染窗口
│   ├── scene.py            # 场景管理器
│   ├── camera.py           # 相机控制
│   ├── models/
│   │   ├── __init__.py
│   │   ├── lidar_body.py   # LiDAR外壳和底座
│   │   ├── motor.py        # 电机和传动机构
│   │   ├── laser_unit.py   # 激光发射/接收单元
│   │   └── laser_beam.py   # 激光束渲染
│   └── effects/
│       ├── __init__.py
│       └── point_cloud.py  # 点云效果
└── core/
    ├── __init__.py
    └── lidar_simulator.py  # 扫描仿真逻辑
```

## 核心模块设计

### 1. 主窗口 (ui/main_window.py)

- 布局：左侧OpenGL视图，右侧控制面板
- 菜单栏：文件（导出截图）、视图、帮助
- 状态栏：显示当前帧率、旋转角度等信息

### 2. OpenGL渲染 (opengl/gl_widget.py)

- 继承QOpenGLWidget
- 实现：initializeGL, resizeGL, paintGL
- 帧率控制：目标60fps

### 3. LiDAR 3D模型

#### 外壳模型 (models/lidar_body.py)
- 圆柱形外壳（半透明可选）
- 顶部旋转头
- 底座和安装接口

#### 电机模型 (models/motor.py)
- 电机主体
- 齿轮传动机构
- 轴承

#### 激光单元 (models/laser_unit.py)
- 激光发射器阵列（垂直排列）
- 接收器阵列
- 电路板示意

#### 激光束 (models/laser_beam.py)
- 发射光线（红色/绿色）
- 反射点标注
- 随旋转动态更新

### 4. 点云效果 (effects/point_cloud.py)

- 模拟环境物体（墙壁、车辆等）
- 根据激光碰撞生成点云
- 颜色编码距离

### 5. 仿真器 (core/lidar_simulator.py)

- 扫描角度计算
- 线束垂直角度分布
- 点云数据生成

### 6. 环境模拟 (opengl/environment.py)

#### 射线类 (Ray)
- 射线起点和方向存储
- 方向自动归一化

#### 几何体基类
- **Box (长方体)**: 射线-AABB相交检测（Slab方法）
- **Cylinder (圆柱)**: 射线-圆柱相交检测（二次方程求解）

#### 环境对象
- **Vehicle (车辆)**: 由车身（长方体）、车顶（长方体）、车轮（圆柱）组成
- **Wall (墙壁)**: 垂直于X轴的平面障碍物

#### 环境管理器 (Environment)
- 管理所有环境对象
- `ray_cast()`: 发射射线并返回最近碰撞点
- 支持与车辆、墙壁、地面的碰撞检测

### 7. 点云生成流程

1. 遍历360°水平角度（分辨率1°）
2. 遍历所有激光线（根据垂直FOV分布）
3. 计算每条射线的方向向量
4. 调用环境ray_cast获取碰撞点
5. 根据碰撞对象类型着色：
   - 车辆: 蓝色
   - 墙壁: 黄色
   - 地面: 绿色

## 交互功能

### 参数控制
| 参数 | 范围 | 默认值 |
|------|------|--------|
| 转速 (RPM) | 1-20 | 10 |
| 线数 | 1-64 | 16 |
| 垂直视场角 | ±1° ~ ±30° | ±15° |
| 探测距离 | 10-200m | 100m |

### 显示控制
- [ ] 显示外壳
- [ ] 显示电机
- [ ] 显示激光束
- [ ] 显示点云
- [ ] 爆炸图模式

### 视角控制
- 鼠标左键拖拽：旋转视角
- 鼠标右键拖拽：平移
- 滚轮：缩放
- 预设视角按钮：俯视、侧视、正视

## 实现步骤

1. **Phase 1: 基础框架**
   - 项目结构和依赖
   - PyQt主窗口
   - OpenGL渲染上下文

2. **Phase 2: 3D模型**
   - LiDAR外壳和底座
   - 电机和传动机构
   - 激光单元阵列

3. **Phase 3: 动画效果**
   - 旋转动画
   - 激光束渲染
   - 点云生成

4. **Phase 4: 交互控制**
   - 控制面板UI
   - 参数绑定
   - 视角控制

5. **Phase 5: 优化完善**
   - 性能优化
   - 细节打磨
   - 文档和注释

## 验证方法

1. 运行 `python main.py` 启动应用
2. 验证3D模型正确渲染
3. 验证旋转动画流畅（60fps）
4. 验证参数调节响应正确
5. 验证视角控制功能
6. 验证点云随扫描生成
7. 验证环境模型（车辆、墙壁）正确显示
8. 验证射线碰撞检测结果（点云落在物体表面）

## 目录结构（已实现）

```
lidar_architecture/
├── main.py                      # 程序入口
├── requirements.txt             # 依赖管理
├── CLAUDE.md                    # Claude Code 指导文档
├── ui/
│   ├── __init__.py
│   ├── main_window.py           # 主窗口
│   └── control_panel.py         # 控制面板
├── opengl/
│   ├── __init__.py
│   ├── gl_widget.py             # OpenGL渲染窗口
│   ├── scene.py                 # 场景管理器（含点云生成）
│   ├── camera.py                # 相机控制
│   ├── environment.py           # 环境模型与碰撞检测
│   └── models/
│       └── __init__.py
├── core/
│   └── __init__.py
└── docs/
    ├── plans/
    │   └── 2026-02-24-lidar-animation-design.md
    ├── images/                   # 截图目录
    └── textbook/                 # 教材目录
        └── lidar-teaching-material.md
```
