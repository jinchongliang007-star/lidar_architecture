"""
环境模型 - 车辆、墙壁等环境对象及其碰撞检测
"""

from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np


class Ray:
    """射线类"""

    def __init__(self, origin, direction):
        """
        origin: 射线起点 (x, y, z)
        direction: 射线方向 (dx, dy, dz)，应该归一化
        """
        self.origin = np.array(origin, dtype=np.float64)
        self.direction = np.array(direction, dtype=np.float64)
        self.direction = self.direction / np.linalg.norm(self.direction)  # 归一化


class Box:
    """长方体几何体"""

    def __init__(self, center, size):
        """
        center: 中心点 (x, y, z)
        size: 尺寸 (width, height, depth)
        """
        self.center = np.array(center, dtype=np.float64)
        self.size = np.array(size, dtype=np.float64)

    def get_bounds(self):
        """获取边界框"""
        half = self.size / 2
        return self.center - half, self.center + half

    def ray_intersect(self, ray):
        """
        射线-长方体相交检测 (Slab方法)
        返回: (是否相交, 相交距离)
        """
        min_bound, max_bound = self.get_bounds()

        tmin = -float('inf')
        tmax = float('inf')

        for i in range(3):
            if abs(ray.direction[i]) < 1e-8:
                # 射线平行于该轴
                if ray.origin[i] < min_bound[i] or ray.origin[i] > max_bound[i]:
                    return False, float('inf')
            else:
                t1 = (min_bound[i] - ray.origin[i]) / ray.direction[i]
                t2 = (max_bound[i] - ray.origin[i]) / ray.direction[i]

                if t1 > t2:
                    t1, t2 = t2, t1

                tmin = max(tmin, t1)
                tmax = min(tmax, t2)

                if tmin > tmax:
                    return False, float('inf')

        if tmax < 0:
            return False, float('inf')

        t = tmin if tmin >= 0 else tmax
        return True, t

    def render(self, color=(0.5, 0.5, 0.5, 0.3)):
        """渲染长方体（半透明）"""
        glPushMatrix()

        glTranslatef(*self.center)

        w, h, d = self.size / 2

        glColor4fv(color)

        glBegin(GL_QUADS)
        # 前面
        glNormal3f(0, 0, 1)
        glVertex3f(-w, -h, d)
        glVertex3f(w, -h, d)
        glVertex3f(w, h, d)
        glVertex3f(-w, h, d)
        # 后面
        glNormal3f(0, 0, -1)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, -h, -d)
        # 上面
        glNormal3f(0, 1, 0)
        glVertex3f(-w, h, -d)
        glVertex3f(-w, h, d)
        glVertex3f(w, h, d)
        glVertex3f(w, h, -d)
        # 下面
        glNormal3f(0, -1, 0)
        glVertex3f(-w, -h, -d)
        glVertex3f(w, -h, -d)
        glVertex3f(w, -h, d)
        glVertex3f(-w, -h, d)
        # 右面
        glNormal3f(1, 0, 0)
        glVertex3f(w, -h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, h, d)
        glVertex3f(w, -h, d)
        # 左面
        glNormal3f(-1, 0, 0)
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, -h, d)
        glVertex3f(-w, h, d)
        glVertex3f(-w, h, -d)
        glEnd()

        glPopMatrix()


class Cylinder:
    """圆柱几何体"""

    def __init__(self, center, radius, height, axis='y'):
        """
        center: 底部中心点 (x, y, z)
        radius: 半径
        height: 高度
        axis: 轴向 ('x', 'y', 'z')
        """
        self.center = np.array(center, dtype=np.float64)
        self.radius = radius
        self.height = height
        self.axis = axis

    def ray_intersect(self, ray):
        """
        射线-圆柱相交检测 (无限长圆柱 + 高度裁剪)
        返回: (是否相交, 相交距离)
        """
        # 将射线转换到圆柱局部坐标系（Y轴为圆柱轴）
        if self.axis == 'y':
            # 圆柱沿Y轴
            ox, oy, oz = ray.origin - self.center
            dx, dy, dz = ray.direction
            base_y = 0
            top_y = self.height
        elif self.axis == 'x':
            # 圆柱沿X轴
            oy, ox, oz = ray.origin - self.center
            dy, dx, dz = ray.direction
            base_y = 0
            top_y = self.height
        else:  # axis == 'z'
            # 圆柱沿Z轴
            ox, oz, oy = ray.origin - self.center
            dx, dz, dy = ray.direction
            base_y = 0
            top_y = self.height

        # 计算与无限圆柱的交点
        # 圆柱方程: x^2 + z^2 = r^2
        # 射线: (ox + t*dx, oy + t*dy, oz + t*dz)
        # 代入: (ox + t*dx)^2 + (oz + t*dz)^2 = r^2
        # 展开: (dx^2 + dz^2)*t^2 + 2*(ox*dx + oz*dz)*t + (ox^2 + oz^2 - r^2) = 0

        a = dx * dx + dz * dz
        b = 2 * (ox * dx + oz * dz)
        c = ox * ox + oz * oz - self.radius * self.radius

        if abs(a) < 1e-8:
            # 射线平行于圆柱轴
            if c > 0:
                return False, float('inf')
            # 射线在圆柱内部，检查高度
            t = -oy / dy if dy != 0 else 0
            if t < 0:
                t = (self.height - oy) / dy if dy != 0 else float('inf')
            hit_y = oy + t * dy
            if 0 <= hit_y <= self.height:
                return True, t
            return False, float('inf')

        discriminant = b * b - 4 * a * c

        if discriminant < 0:
            return False, float('inf')

        sqrt_disc = math.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2 * a)
        t2 = (-b + sqrt_disc) / (2 * a)

        # 检查高度限制
        for t in [t1, t2]:
            if t >= 0:
                hit_y = oy + t * dy
                if base_y <= hit_y <= top_y:
                    return True, t

        # 检查与顶面和底面的交点
        if abs(dy) > 1e-8:
            # 底面
            t_bottom = -oy / dy
            if t_bottom >= 0:
                hit_x = ox + t_bottom * dx
                hit_z = oz + t_bottom * dz
                if hit_x * hit_x + hit_z * hit_z <= self.radius * self.radius:
                    return True, t_bottom

            # 顶面
            t_top = (self.height - oy) / dy
            if t_top >= 0:
                hit_x = ox + t_top * dx
                hit_z = oz + t_top * dz
                if hit_x * hit_x + hit_z * hit_z <= self.radius * self.radius:
                    return True, t_top

        return False, float('inf')

    def render(self, color=(0.3, 0.3, 0.3, 0.5)):
        """渲染圆柱"""
        glPushMatrix()
        glTranslatef(*self.center)

        if self.axis == 'x':
            glRotatef(90, 0, 0, 1)
        elif self.axis == 'z':
            glRotatef(90, 1, 0, 0)

        glColor4fv(color)

        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)

        # 圆柱侧面
        gluCylinder(quadric, self.radius, self.radius, self.height, 32, 1)

        # 底面
        glPushMatrix()
        glRotatef(180, 1, 0, 0)
        gluDisk(quadric, 0, self.radius, 32, 1)
        glPopMatrix()

        # 顶面
        glPushMatrix()
        glTranslatef(0, 0, self.height)
        gluDisk(quadric, 0, self.radius, 32, 1)
        glPopMatrix()

        gluDeleteQuadric(quadric)
        glPopMatrix()


class Vehicle:
    """简化车辆模型"""

    def __init__(self, position=(4.0, 0, 0)):
        """
        position: 车辆中心位置（底部中心）
        """
        self.position = np.array(position, dtype=np.float64)

        # 车辆尺寸参数
        self.body_length = 4.0   # 车身长度
        self.body_width = 1.8    # 车身宽度
        self.body_height = 1.2   # 车身高度

        self.roof_length = 2.5   # 车顶长度
        self.roof_width = 1.6    # 车顶宽度
        self.roof_height = 0.8   # 车顶高度

        self.wheel_radius = 0.35
        self.wheel_width = 0.25

        # 构建几何体
        self.parts = []
        self._build_parts()

    def _build_parts(self):
        """构建车辆的各个部件"""
        # 车身（底部在地面）
        body_center = self.position + np.array([0, self.body_height / 2, 0])
        self.parts.append(Box(body_center, (self.body_length, self.body_height, self.body_width)))

        # 车顶（在车身上方，偏后）
        roof_center = self.position + np.array([
            -0.3,  # 稍微偏后
            self.body_height + self.roof_height / 2,
            0
        ])
        self.parts.append(Box(roof_center, (self.roof_length, self.roof_height, self.roof_width)))

        # 四个车轮
        wheel_positions = [
            (self.body_length / 2 - 0.5, self.wheel_radius, self.body_width / 2 + self.wheel_width / 2),   # 前右
            (self.body_length / 2 - 0.5, self.wheel_radius, -self.body_width / 2 - self.wheel_width / 2),  # 前左
            (-self.body_length / 2 + 0.5, self.wheel_radius, self.body_width / 2 + self.wheel_width / 2),  # 后右
            (-self.body_length / 2 + 0.5, self.wheel_radius, -self.body_width / 2 - self.wheel_width / 2), # 后左
        ]

        for pos in wheel_positions:
            wheel_center = self.position + np.array(pos)
            self.parts.append(Cylinder(wheel_center, self.wheel_radius, self.wheel_width, axis='x'))

    def ray_intersect(self, ray):
        """
        射线与车辆相交检测
        返回: (是否相交, 相交距离)
        """
        min_t = float('inf')
        hit = False

        for part in self.parts:
            is_hit, t = part.ray_intersect(ray)
            if is_hit and t < min_t:
                min_t = t
                hit = True

        return hit, min_t

    def render(self):
        """渲染车辆"""
        # 车身颜色（蓝色）
        body_color = (0.2, 0.4, 0.8, 0.4)

        # 车顶颜色（深蓝色）
        roof_color = (0.15, 0.3, 0.6, 0.4)

        # 车轮颜色（黑色）
        wheel_color = (0.1, 0.1, 0.1, 0.5)

        # 渲染车身
        self.parts[0].render(body_color)

        # 渲染车顶
        self.parts[1].render(roof_color)

        # 渲染车轮
        for part in self.parts[2:]:
            part.render(wheel_color)


class Wall:
    """墙壁"""

    def __init__(self, position=(7.0, 0, 0), width=10, height=4):
        """
        position: 墙壁中心位置
        width: 墙壁宽度（沿Z轴）
        height: 墙壁高度
        墙壁默认垂直于X轴，面向LiDAR
        """
        self.position = np.array(position, dtype=np.float64)
        self.width = width
        self.height = height
        self.thickness = 0.2  # 墙壁厚度

        # 构建几何体
        self.box = Box(
            self.position,
            (self.thickness, self.height, self.width)
        )

    def ray_intersect(self, ray):
        """
        射线与墙壁相交检测
        返回: (是否相交, 相交距离)
        """
        return self.box.ray_intersect(ray)

    def render(self):
        """渲染墙壁"""
        # 墙壁颜色（灰色，半透明）
        wall_color = (0.6, 0.6, 0.6, 0.3)
        self.box.render(wall_color)


class Environment:
    """环境管理类"""

    def __init__(self):
        # 创建车辆（前方4米）
        self.vehicle = Vehicle(position=(4.0, 0, 0))

        # 创建墙壁（前方7米）
        self.wall = Wall(position=(7.0, 2.0, 0), width=10, height=4)

        # 地面
        self.ground_y = 0

        # 可见性
        self.visible = True

    def ray_cast(self, origin, direction, max_distance=20.0):
        """
        发射射线，返回最近碰撞点

        Args:
            origin: 射线起点
            direction: 射线方向
            max_distance: 最大检测距离

        Returns:
            hit_point: 碰撞点坐标，如果没有碰撞返回 None
            distance: 碰撞距离
        """
        ray = Ray(origin, direction)

        min_t = float('inf')
        hit_object = None

        # 检测与车辆的碰撞
        is_hit, t = self.vehicle.ray_intersect(ray)
        if is_hit and t < min_t:
            min_t = t
            hit_object = 'vehicle'

        # 检测与墙壁的碰撞
        is_hit, t = self.wall.ray_intersect(ray)
        if is_hit and t < min_t:
            min_t = t
            hit_object = 'wall'

        # 检测与地面的碰撞
        if ray.direction[1] < 0:  # 射线向下
            t_ground = (self.ground_y - ray.origin[1]) / ray.direction[1]
            if t_ground >= 0 and t_ground < min_t:
                # 检查是否在地面范围内
                hit_x = ray.origin[0] + t_ground * ray.direction[0]
                hit_z = ray.origin[2] + t_ground * ray.direction[2]
                if abs(hit_x) < 15 and abs(hit_z) < 15:
                    min_t = t_ground
                    hit_object = 'ground'

        if min_t < max_distance and hit_object:
            hit_point = ray.origin + min_t * ray.direction
            return hit_point, min_t, hit_object

        return None, float('inf'), None

    def render(self):
        """渲染环境"""
        if not self.visible:
            return

        # 启用混合以渲染半透明物体
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # 禁用深度写入，但保持深度测试
        glDepthMask(GL_FALSE)

        # 渲染车辆
        self.vehicle.render()

        # 渲染墙壁
        self.wall.render()

        # 恢复深度写入
        glDepthMask(GL_TRUE)
