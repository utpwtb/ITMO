"""实验二的相机、球面求交和光照几何，长度输入为毫米。"""
from dataclasses import dataclass, field
import math
import numpy as np


@dataclass(frozen=True)
class Light:
    x_mm: float = -650.0
    y_mm: float = 450.0
    z_mm: float = 1700.0
    intensity_w_sr: float = 100.0
    axis: tuple = (0.0, 0.0, -1.0)
    spectrum: tuple = (1.0,) * 41

    def position(self):
        return np.array([self.x_mm, self.y_mm, self.z_mm], float)


@dataclass(frozen=True)
class Parameters:
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
    model: str = "reference_diagram"
    reflectance: tuple = field(default_factory=lambda: tuple(
        .08 + .8 * np.exp(-.5 * ((np.arange(380, 781, 10) - 540) / 45) ** 2)))
    lights: tuple = (Light(), Light(550.0, -250.0, 1600.0, 70.0))

    def __post_init__(self):
        try:
            height = round(self.width_px * self.height_mm / self.width_mm)
        except (TypeError, ValueError, ZeroDivisionError, OverflowError):
            height = 0
        object.__setattr__(self, "height_px", height)

    def observer(self):
        return np.array([0.0, 0.0, self.observer_z_mm])

    def center(self):
        return np.array([self.center_x_mm, self.center_y_mm, self.center_z_mm])


def unit(v):
    v = np.asarray(v, float)
    scale = np.max(np.abs(v), axis=-1, keepdims=True)
    v = np.divide(v, scale, out=np.zeros_like(v), where=scale > 0)
    norm = np.linalg.norm(v, axis=-1, keepdims=True)
    return np.divide(v, norm, out=np.zeros_like(v), where=norm > 0)


def camera_basis(p):
    forward = unit(p.direction)
    hint = (1, 0, 0) if abs(forward[1]) > .99 else (0, 1, 0)
    right = unit(np.cross(forward, hint))
    return right, unit(np.cross(right, forward)), forward


def screen_offset_mm(p, forward=None):
    if p.screen_distance_mm is not None:
        return p.screen_distance_mm
    forward = unit(p.direction) if forward is None else forward
    require(abs(forward[2]) >= 1e-12, "Для горизонтального взгляда задайте screen_distance_mm")
    return (p.screen_z_mm - p.observer_z_mm) / forward[2]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _numeric(values, name):
    require(all(not isinstance(v, (bool, np.bool_)) and isinstance(v, (int, float, np.number))
                and math.isfinite(v) for v in values), name + ": требуются конечные числа")


def _vector(values, size, name):
    require(isinstance(values, (tuple, list, np.ndarray)) and np.shape(values) == (size,),
            f"{name}: требуется {size} чисел")
    _numeric(values, name)
    return np.asarray(values, float)


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
    require(math.isclose(p.width_mm / p.width_px, p.height_mm / p.height_px, rel_tol=1e-10, abs_tol=1e-10),
            f"Для квадратных пикселей задайте H={p.height_px * p.width_mm / p.width_px:.10g} мм")
    require(abs(p.center_x_mm) <= 10000 and abs(p.center_y_mm) <= 10000 and 0 <= p.center_z_mm <= 10000,
            "Центр: X,Y ±10000 мм, Z 0..10000 мм")
    require(p.radius_mm > 0, "Радиус должен быть положительным")
    require(p.model in ("reference_diagram", "lambert"), "Модель: reference_diagram или lambert")
    require(np.linalg.norm(_vector(p.direction, 3, "Направление")) > 1e-12, "Нулевое направление")
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
    depth = np.dot(relative, forward)
    require(depth > p.radius_mm and distance > depth + p.radius_mm,
            "Порядок вдоль взгляда: наблюдатель, вся сфера, экран")
    for axis, half_size in ((right, p.width_mm / 2), (up, p.height_mm / 2)):
        for sign in (-1, 1):
            normal = unit(half_size / distance * forward + sign * axis)
            require(np.dot(relative, normal) >= p.radius_mm - 1e-8, "Сфера не целиком в поле зрения")


def trace(p, screen_x, screen_y):
    right, up, forward = camera_basis(p)
    rays = unit(screen_offset_mm(p, forward) * forward + np.asarray(screen_x)[..., None] * right
                + np.asarray(screen_y)[..., None] * up)
    oc = p.observer() - p.center()
    b = np.sum(rays * oc, axis=-1)
    discriminant = b * b - (np.dot(oc, oc) - p.radius_mm ** 2)
    t = -b - np.sqrt(np.maximum(discriminant, 0))
    return (discriminant >= 0) & (t > 0), p.observer() + t[..., None] * rays


def geometry_factors(points_mm, p):
    points = np.asarray(points_mm, float)
    normal = unit(points - p.center())
    factors = []
    for light in p.lights:
        to_light = light.position() - points
        direction = unit(to_light)
        emission = np.maximum(np.sum(-direction * unit(light.axis), axis=-1), 0)
        incidence = np.maximum(np.sum(normal * direction, axis=-1), 0)
        # 题图 E 与 f 各含一次接收余弦，默认保留 cos²/π。距离从毫米转米。
        power = 2 if p.model == "reference_diagram" else 1
        factors.append(light.intensity_w_sr * emission * incidence ** power
                       / (math.pi * np.sum((to_light / 1000) ** 2, axis=-1)))
    return np.stack(factors, axis=-1)
