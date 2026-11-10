# 定义光源及场景，校验参数，计算相机基向量、射线球面交点与光照几何系数。
# 位置和长度输入为毫米，在光照距离平方公式中换算为米。
from dataclasses import dataclass
import math
import numpy as np


# 保存光源位置、强度 I₀、发光轴和 41 通道光谱。
@dataclass(frozen=True)
class Light:
    x_mm: float = -650.0
    y_mm: float = 450.0
    z_mm: float = 1700.0
    intensity_w_sr: float = 100.0
    axis: tuple = (0.0, 0.0, -1.0)
    spectrum: tuple = (1.0,) * 41

    # 返回光源的三维浮点坐标，单位为毫米。
    def position(self):
        return np.array([self.x_mm, self.y_mm, self.z_mm], float)


# 保存屏幕、相机、球体、反射率和光源的不可变场景参数。
@dataclass(frozen=True)
class Parameters:
    # 物理尺寸使用毫米，图像尺寸使用像素；默认反射率的 41 个通道均为 1。
    width_mm: float = 1200.0
    height_mm: float = 1200.0
    width_px: int = 600
    height_px: int = 600
    observer_z_mm: float = 2500.0
    direction: tuple = (0.0, 0.0, -1.0)
    screen_z_mm: float = 0.0
    screen_distance_mm: float | None = None
    center_x_mm: float = 0.0
    center_y_mm: float = 0.0
    center_z_mm: float = 600.0
    radius_mm: float = 350.0
    reflectance: tuple = (1.0,) * 41
    lights: tuple = (Light(), Light(550.0, -250.0, 1600.0, 70.0))

    # 依据屏幕比例和图像宽度推算图像高度，使像素保持正方形。
    def __post_init__(self):
        try:
            # 像素高宽比与物理屏幕高宽比一致，避免把球拉伸为椭球。
            height = round(self.width_px * self.height_mm / self.width_mm)
        except (TypeError, ValueError, ZeroDivisionError, OverflowError):
            height = 0
        object.__setattr__(self, "height_px", height)

    # 返回位于 Z 轴上的观察者坐标，单位为毫米。
    def observer(self):
        return np.array([0.0, 0.0, self.observer_z_mm])

    # 返回球心坐标，单位为毫米。
    def center(self):
        return np.array([self.center_x_mm, self.center_y_mm, self.center_z_mm])


# 沿最后一维单位化向量，支持批量输入，零向量保持为零。
def unit(v):
    v = np.asarray(v, float)
    # 先按最大绝对分量缩放再求模长，降低大数平方溢出的风险。
    scale = np.max(np.abs(v), axis=-1, keepdims=True)
    v = np.divide(v, scale, out=np.zeros_like(v), where=scale > 0)
    norm = np.linalg.norm(v, axis=-1, keepdims=True)
    return np.divide(v, norm, out=np.zeros_like(v), where=norm > 0)


# 根据视线方向生成右、上、前三个正交单位向量。
def camera_basis(p):
    forward = unit(p.direction)
    # 视线接近 Y 轴时改用 X 轴作参考，避免叉乘接近零。
    hint = (1, 0, 0) if abs(forward[1]) > .99 else (0, 1, 0)
    right = unit(np.cross(forward, hint))
    return right, unit(np.cross(right, forward)), forward


# 取得屏幕沿视线的距离，未显式设置时由屏幕 Z 坐标推算。
def screen_offset_mm(p, forward=None):
    if p.screen_distance_mm is not None:
        return p.screen_distance_mm
    forward = unit(p.direction) if forward is None else forward
    require(abs(forward[2]) >= 1e-12, "Для горизонтального взгляда задайте screen_distance_mm")
    # 由 O+d·forward 的 Z 分量等于屏幕 Z 坐标，解出沿视线的距离 d。
    return (p.screen_z_mm - p.observer_z_mm) / forward[2]


# 检查条件，不满足时抛出带说明的输入错误。
def require(condition, message):
    if not condition:
        raise ValueError(message)


# 检查所有元素均为有限实数，排除布尔值。
def _numeric(values, name):
    require(all(not isinstance(v, (bool, np.bool_)) and isinstance(v, (int, float, np.number))
                and math.isfinite(v) for v in values), name + ": требуются конечные числа")


# 检查向量长度与元素类型，返回浮点数组。
def _vector(values, size, name):
    require(isinstance(values, (tuple, list, np.ndarray)) and np.shape(values) == (size,),
            f"{name}: требуется {size} чисел")
    _numeric(values, name)
    return np.asarray(values, float)


# 校验尺寸、分辨率、方向、光谱及光源、球体、相机的几何关系。
def validate(p):
    _numeric([p.width_mm, p.height_mm, p.observer_z_mm, p.screen_z_mm,
              p.center_x_mm, p.center_y_mm, p.center_z_mm, p.radius_mm], "Геометрия")
    if p.screen_distance_mm is not None:
        _numeric([p.screen_distance_mm], "Расстояние экрана")
        require(p.screen_distance_mm > 0, "screen_distance_mm должно быть положительным")
    require(100 <= p.width_mm <= 10000 and 100 <= p.height_mm <= 10000, "W,H: 100..10000 мм")
    require(not isinstance(p.width_px, (bool, np.bool_)) and isinstance(p.width_px, (int, np.integer)),
            "Wres должно быть целым числом")
    require(200 <= p.width_px <= 800 and 200 <= p.height_px <= 800, "Wres,Hres: 200..800")
    # 横纵方向的物理尺寸除以像素数应一致，保证正方形像素。
    require(math.isclose(p.width_mm / p.width_px, p.height_mm / p.height_px, rel_tol=1e-10, abs_tol=1e-10),
            f"Для квадратных пикселей задайте H={p.height_px * p.width_mm / p.width_px:.10g} мм")
    require(abs(p.center_x_mm) <= 10000 and abs(p.center_y_mm) <= 10000 and 0 <= p.center_z_mm <= 10000,
            "Центр: X,Y ±10000 мм, Z 0..10000 мм")
    require(p.radius_mm > 0, "Радиус должен быть положительным")
    require(np.linalg.norm(_vector(p.direction, 3, "Направление")) > 1e-12, "Нулевое направление")
    # 反射率和光谱均需 41 个波长样本；反射率限于 [0,1]。
    kd = _vector(p.reflectance, 41, "Отражение")
    require(np.all((kd >= 0) & (kd <= 1)), "Коэффициенты отражения: [0,1]")
    require(isinstance(p.lights, (tuple, list)) and len(p.lights) > 0, "Требуется источник света")
    for light in p.lights:
        require(isinstance(light, Light), "Неверная запись источника")
        _numeric([light.x_mm, light.y_mm, light.z_mm, light.intensity_w_sr], "Источник")
        require(np.all(np.abs(light.position()) <= 10000), "Координаты источника: ±10000 мм")
        require(.01 <= light.intensity_w_sr <= 10000, "I0: 0.01..10000 Вт/ср")
        require(np.linalg.norm(_vector(light.axis, 3, "Ось источника")) > 1e-12, "Нулевая ось")
        spd = _vector(light.spectrum, 41, "Спектр источника")
        require(np.all(spd >= 0) and np.any(spd > 0), "Спектр должен быть неотрицательным и ненулевым")
        require(np.linalg.norm(light.position() - p.center()) > p.radius_mm, "Источник внутри сферы")
    require(np.linalg.norm(p.observer() - p.center()) > p.radius_mm, "Наблюдатель внутри сферы")
    right, up, forward = camera_basis(p)
    distance, relative = screen_offset_mm(p, forward), p.center() - p.observer()
    # 沿视线校验顺序：观察者、整个球体、屏幕。
    depth = np.dot(relative, forward)
    require(depth > p.radius_mm and distance > depth + p.radius_mm,
            "Порядок вдоль взгляда: наблюдатель, вся сфера, экран")
    # 检查球心到四个视锥边界平面的距离，保证球体完全处于视野中。
    for axis, half_size in ((right, p.width_mm / 2), (up, p.height_mm / 2)):
        for sign in (-1, 1):
            normal = unit(half_size / distance * forward + sign * axis)
            require(np.dot(relative, normal) >= p.radius_mm - 1e-8, "Сфера не целиком в поле зрения")


# 向屏幕采样点发射射线，返回球面命中 mask 和交点坐标。
def trace(p, screen_x, screen_y):
    right, up, forward = camera_basis(p)
    # 按屏幕距离及水平、竖直偏移构造射线方向，再归一化。
    rays = unit(screen_offset_mm(p, forward) * forward + np.asarray(screen_x)[..., None] * right
                + np.asarray(screen_y)[..., None] * up)
    # 将射线 O+t·d 代入球方程；d 已单位化，二次项系数为 1。
    oc = p.observer() - p.center()
    b = np.sum(rays * oc, axis=-1)
    # 判别式小于零表示未相交；求根时截到零，避免无效平方根。
    discriminant = b * b - (np.dot(oc, oc) - p.radius_mm ** 2)
    # 选较近的根得到前表面，最终 mask 要求真实相交且 t>0。
    t = -b - np.sqrt(np.maximum(discriminant, 0))
    return (discriminant >= 0) & (t > 0), p.observer() + t[..., None] * rays


# 计算各球面点相对各光源的照明系数，供光谱和 RGB 路径共用。
def geometry_factors(points_mm, p):
    points = np.asarray(points_mm, float)
    # 球面外法线是球心指向表面点的单位向量。
    normal = unit(points - p.center())
    factors = []
    for light in p.lights:
        to_light = light.position() - points
        direction = unit(to_light)
        # 发光余弦为发光轴与光源指向表面点的方向夹角余弦，背向部分置零。
        emission = np.maximum(np.sum(-direction * unit(light.axis), axis=-1), 0)
        # 入射余弦为外法线与表面点指向光源的方向夹角余弦，背光部分置零。
        incidence = np.maximum(np.sum(normal * direction, axis=-1), 0)

        # 朗伯关系 L=kd·E/π：系数为 I₀·发光余弦·入射余弦/(π·r²)，入射余弦只出现一次。
        # to_light/1000 将毫米换成米；反射率 kd 和光谱在渲染模块中乘入。
        factors.append(light.intensity_w_sr * emission * incidence
                       / (math.pi * np.sum((to_light / 1000) ** 2, axis=-1)))
    return np.stack(factors, axis=-1)
