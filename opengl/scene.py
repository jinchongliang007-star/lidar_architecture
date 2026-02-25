"""
场景管理类 - 管理和渲染所有3D对象
"""

from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np

from opengl.environment import Environment


class Scene:
    """场景管理类"""

    def __init__(self):
        # 场景参数
        self.rotation_angle = 0.0  # 当前旋转角度
        self.rotation_speed = 10.0  # 转速 (RPM)
        self.laser_lines = 16  # 激光线数
        self.vertical_fov = 30.0  # 垂直视场角

        # 可见性控制
        self.visible_components = {
            'body': True,
            'motor': True,
            'laser_unit': True,
            'laser_beam': True,
            'point_cloud': True,
            'environment': True,
        }

        # 环境模型
        self.environment = Environment()

        # 点云数据
        self.point_cloud_data = []
        self.point_cloud_update_counter = 0
        self.point_cloud_update_interval = 2  # 每2帧更新一次点云
        self.generate_point_cloud()

        # 颜色定义
        self.colors = {
            'body': (0.3, 0.3, 0.35, 1.0),
            'motor': (0.4, 0.4, 0.45, 1.0),
            'laser_emitter': (0.8, 0.2, 0.2, 1.0),
            'laser_receiver': (0.2, 0.6, 0.2, 1.0),
            'laser_beam': (1.0, 0.0, 0.0, 1.0),
            'point_cloud': (0.0, 1.0, 0.5, 1.0),
        }

    def generate_point_cloud(self):
        """根据LiDAR参数和环境碰撞生成点云数据"""
        self.point_cloud_data = []

        # LiDAR位置（在原点上方）
        lidar_origin = np.array([0.35, 0.4, 0])  # 发射器位置

        # 水平扫描分辨率（度）
        horizontal_resolution = 1.0  # 每度一个点

        # 遍历所有水平角度（360度）
        for h_angle in np.arange(0, 360, horizontal_resolution):
            h_rad = math.radians(h_angle)

            # 遍历所有激光线
            for i in range(self.laser_lines):
                # 计算垂直角度
                v_angle = -self.vertical_fov / 2 + self.vertical_fov * i / max(1, self.laser_lines - 1)
                v_rad = math.radians(v_angle)

                # 计算射线方向
                # 水平角度决定XZ平面方向，垂直角度决定Y方向
                dx = math.cos(v_rad) * math.cos(h_rad)
                dy = math.sin(v_rad)
                dz = math.cos(v_rad) * math.sin(h_rad)

                direction = np.array([dx, dy, dz])

                # 发射射线
                hit_point, distance, hit_object = self.environment.ray_cast(lidar_origin, direction)

                if hit_point is not None:
                    self.point_cloud_data.append((
                        hit_point[0],
                        hit_point[1],
                        hit_point[2],
                        hit_object  # 保存碰撞对象类型用于着色
                    ))

    def generate_mock_point_cloud(self):
        """兼容旧接口"""
        self.generate_point_cloud()

    def update(self, dt):
        """更新场景状态"""
        # 计算旋转角度增量
        # RPM -> 度/秒: RPM * 360 / 60 = RPM * 6
        angle_per_second = self.rotation_speed * 6.0
        self.rotation_angle += angle_per_second * dt
        self.rotation_angle %= 360.0

        # 定期更新点云（为了性能，不是每帧都更新）
        self.point_cloud_update_counter += 1
        if self.point_cloud_update_counter >= self.point_cloud_update_interval:
            self.point_cloud_update_counter = 0
            self.generate_point_cloud()

    def render(self):
        """渲染整个场景"""
        # 绘制地面网格
        self._draw_ground_grid()

        # 绘制坐标轴
        self._draw_axes()

        # 渲染环境模型（车辆、墙壁等）
        if self.visible_components.get('environment', True):
            self.environment.render()

        # 绘制LiDAR主体（底部不旋转）
        if self.visible_components['body']:
            self._draw_lidar_body()

        # 绘制电机（底部不旋转）
        if self.visible_components['motor']:
            self._draw_motor()

        # 旋转部分
        glPushMatrix()
        glRotatef(self.rotation_angle, 0, 1, 0)

        # 绘制旋转头
        if self.visible_components['body']:
            self._draw_rotating_head()

        # 绘制激光单元
        if self.visible_components['laser_unit']:
            self._draw_laser_unit()

        # 绘制激光束
        if self.visible_components['laser_beam']:
            self._draw_laser_beams()

        glPopMatrix()

        # 绘制点云（不随LiDAR旋转）
        if self.visible_components['point_cloud']:
            self._draw_point_cloud()

    def _draw_ground_grid(self):
        """绘制地面网格"""
        glDisable(GL_LIGHTING)
        glColor4f(0.3, 0.3, 0.3, 0.5)
        glLineWidth(1.0)

        glBegin(GL_LINES)
        grid_size = 10
        for i in range(-grid_size, grid_size + 1):
            glVertex3f(i, -2.0, -grid_size)
            glVertex3f(i, -2.0, grid_size)
            glVertex3f(-grid_size, -2.0, i)
            glVertex3f(grid_size, -2.0, i)
        glEnd()

        glEnable(GL_LIGHTING)

    def _draw_axes(self):
        """绘制坐标轴"""
        glDisable(GL_LIGHTING)
        glLineWidth(2.0)

        glBegin(GL_LINES)
        # X轴 - 红色
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(2, 0, 0)
        # Y轴 - 绿色
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 2, 0)
        # Z轴 - 蓝色
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 2)
        glEnd()

        glEnable(GL_LIGHTING)
        glLineWidth(1.0)

    def _draw_lidar_body(self):
        """绘制LiDAR外壳"""
        glColor4fv(self.colors['body'])

        # 底座圆柱
        glPushMatrix()
        glTranslatef(0, -1.5, 0)
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quadric, 0.6, 0.6, 0.3, 32, 1)
        gluDeleteQuadric(quadric)
        glPopMatrix()

        # 底座圆盘
        glPushMatrix()
        glTranslatef(0, -1.2, 0)
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        glRotatef(-90, 1, 0, 0)
        gluDisk(quadric, 0, 0.6, 32, 1)
        gluDeleteQuadric(quadric)
        glPopMatrix()

        # 主体圆柱
        glPushMatrix()
        glTranslatef(0, -1.2, 0)
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quadric, 0.5, 0.5, 1.2, 32, 1)
        gluDeleteQuadric(quadric)
        glPopMatrix()

    def _draw_rotating_head(self):
        """绘制旋转头"""
        glColor4fv(self.colors['body'])

        # 旋转头圆柱
        glPushMatrix()
        glTranslatef(0, 0.2, 0)
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quadric, 0.4, 0.4, 0.4, 32, 1)
        gluDeleteQuadric(quadric)
        glPopMatrix()

        # 旋转头顶部圆盘
        glPushMatrix()
        glTranslatef(0, 0.6, 0)
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        glRotatef(-90, 1, 0, 0)
        gluDisk(quadric, 0, 0.4, 32, 1)
        gluDeleteQuadric(quadric)
        glPopMatrix()

    def _draw_motor(self):
        """绘制电机和传动机构"""
        # 电机主体
        glColor4fv(self.colors['motor'])
        glPushMatrix()
        glTranslatef(0, -0.8, 0)
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quadric, 0.25, 0.25, 0.5, 24, 1)
        gluDeleteQuadric(quadric)
        glPopMatrix()

        # 齿轮（简化为带齿圆盘）
        glColor4f(0.5, 0.5, 0.5, 1.0)
        glPushMatrix()
        glTranslatef(0, -0.3, 0)
        self._draw_gear(0.3, 0.1, 16)
        glPopMatrix()

        # 轴承
        glColor4f(0.6, 0.6, 0.6, 1.0)
        glPushMatrix()
        glTranslatef(0, 0.0, 0)
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        glRotatef(-90, 1, 0, 0)
        gluDisk(quadric, 0.05, 0.15, 24, 1)
        gluDeleteQuadric(quadric)
        glPopMatrix()

    def _draw_gear(self, radius, height, teeth):
        """绘制简化齿轮"""
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)

        # 齿轮主体
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quadric, radius, radius, height, teeth * 2, 1)
        gluDisk(quadric, 0, radius, teeth * 2, 1)
        glTranslatef(0, 0, height)
        gluDisk(quadric, 0, radius, teeth * 2, 1)
        glPopMatrix()

        gluDeleteQuadric(quadric)

    def _draw_laser_unit(self):
        """绘制激光发射/接收单元"""
        # 发射器阵列（红色）
        glColor4fv(self.colors['laser_emitter'])
        for i in range(self.laser_lines):
            angle = -self.vertical_fov / 2 + self.vertical_fov * i / max(1, self.laser_lines - 1)
            angle_rad = math.radians(angle)

            glPushMatrix()
            glTranslatef(0.35, 0.4, 0)
            glRotatef(angle, 0, 0, 1)

            # 小圆柱表示发射器
            quadric = gluNewQuadric()
            gluQuadricNormals(quadric, GLU_SMOOTH)
            glRotatef(-90, 1, 0, 0)
            gluCylinder(quadric, 0.02, 0.02, 0.1, 8, 1)
            gluDeleteQuadric(quadric)
            glPopMatrix()

        # 接收器阵列（绿色）
        glColor4fv(self.colors['laser_receiver'])
        for i in range(self.laser_lines):
            angle = -self.vertical_fov / 2 + self.vertical_fov * i / max(1, self.laser_lines - 1)
            angle_rad = math.radians(angle)

            glPushMatrix()
            glTranslatef(-0.35, 0.4, 0)
            glRotatef(angle, 0, 0, 1)

            # 小圆柱表示接收器
            quadric = gluNewQuadric()
            gluQuadricNormals(quadric, GLU_SMOOTH)
            glRotatef(-90, 1, 0, 0)
            gluCylinder(quadric, 0.025, 0.025, 0.08, 8, 1)
            gluDeleteQuadric(quadric)
            glPopMatrix()

        # 电路板（扁平长方体）
        glColor4f(0.2, 0.4, 0.2, 1.0)
        glPushMatrix()
        glTranslatef(0, 0.35, 0)
        self._draw_box(0.3, 0.02, 0.15)
        glPopMatrix()

    def _draw_box(self, width, height, depth):
        """绘制长方体"""
        w, h, d = width / 2, height / 2, depth / 2

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

    def _draw_laser_beams(self):
        """绘制激光束"""
        glDisable(GL_LIGHTING)
        glLineWidth(2.0)

        beam_length = 5.0

        for i in range(self.laser_lines):
            # 根据距离计算颜色渐变
            t = i / max(1, self.laser_lines - 1)
            r = 1.0
            g = 0.2 + t * 0.3
            b = 0.0
            glColor4f(r, g, b, 0.8)

            angle = -self.vertical_fov / 2 + self.vertical_fov * i / max(1, self.laser_lines - 1)
            angle_rad = math.radians(angle)

            # 发射点
            start_x = 0.35 + 0.1 * math.cos(angle_rad)
            start_y = 0.4 + 0.1 * math.sin(angle_rad)
            start_z = 0

            # 终点
            end_x = start_x + beam_length * math.cos(angle_rad)
            end_y = start_y + beam_length * math.sin(angle_rad)
            end_z = start_z

            glBegin(GL_LINES)
            glVertex3f(start_x, start_y, start_z)
            glVertex3f(end_x, end_y, end_z)
            glEnd()

        glEnable(GL_LIGHTING)
        glLineWidth(1.0)

    def _draw_point_cloud(self):
        """绘制点云"""
        glDisable(GL_LIGHTING)
        glPointSize(3.0)

        glBegin(GL_POINTS)

        for point in self.point_cloud_data:
            x, y, z = point[0], point[1], point[2]
            hit_type = point[3] if len(point) > 3 else 'unknown'

            # 根据碰撞对象类型着色
            if hit_type == 'vehicle':
                # 车辆点 - 蓝色系
                glColor4f(0.2, 0.5, 1.0, 0.9)
            elif hit_type == 'wall':
                # 墙壁点 - 黄色系
                glColor4f(1.0, 0.8, 0.2, 0.9)
            elif hit_type == 'ground':
                # 地面点 - 绿色系
                glColor4f(0.2, 0.8, 0.3, 0.9)
            else:
                # 默认 - 根据距离着色
                dist = math.sqrt(x**2 + y**2 + z**2)
                max_dist = 10.0
                t = min(1.0, dist / max_dist)
                r = t
                g = 1.0 - t * 0.5
                b = 0.2
                glColor4f(r, g, b, 0.8)

            glVertex3f(x, y, z)

        glEnd()

        glEnable(GL_LIGHTING)
        glPointSize(1.0)
