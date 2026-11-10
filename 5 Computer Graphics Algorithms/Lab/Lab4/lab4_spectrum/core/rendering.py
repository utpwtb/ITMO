# 计算球面的绝对光谱、XYZ、两条 RGB 路径、辐亮度及光度亮度。
# 生成图像数组、三个控制点，以及可见像素和整球采样的亮度统计。
import math
import numpy as np
from .geometry import camera_basis, geometry_factors, trace, unit, validate
from .spectral import load_tables
from .color_conversion import (CIE_RGB_TO_XYZ, XYZ_TO_CIE_RGB,
                               scene_rgb, spectrum_to_xyz)


# 计算给定球面点的出射光谱、颜色坐标、积分辐亮度和光度亮度。
def radiance_at(points_mm, p, tables=None):
    tables = tables or load_tables()
    # 几何系数包含 I₀、两个方向余弦、距离平方衰减和 1/π，不包含光谱与反射率。
    factors = geometry_factors(points_mm, p)

    # 保持输入光谱幅值；重建只保持 XYZ，不能在此重新归一化能量。
    spectra = np.array([light.spectrum for light in p.lights])
    # 多光源光谱按几何系数线性叠加，再逐波长乘材料反射率。
    spectral = (factors @ spectra) * np.asarray(p.reflectance)
    xyz = spectrum_to_xyz(spectral, tables)
    # 第一条 RGB 路径对出射光谱积分；第二条直接叠加光源 RGB 再乘 RGB 反射系数。
    kd, lights = scene_rgb(p, tables)
    # 辐亮度为光谱的波长积分；光度亮度为 683·Y，单位为 cd/m²。
    return dict(spectral=spectral, xyz=xyz, rgb1=xyz @ XYZ_TO_CIE_RGB.T,
                rgb2=(factors @ lights) * kd, radiance_w_m2_sr=spectral @ tables.weights,
                luminance_cd_m2=683 * xyz[..., 1])


# 选取正对观察者的点及左右两个可见点，返回其坐标和物理量。
def control_points(p, tables=None):
    front = unit(p.observer() - p.center())
    right = camera_basis(p)[0]
    # 将相机右方向投影到正面点切平面，确定左右控制点方向。
    tangent = unit(right - np.dot(right, front) * front)
    # 限制左右偏转角，使控制点保持在观察者可见的球面范围内。
    angle = min(math.acos(.8), .7 * math.acos(p.radius_mm / np.linalg.norm(p.observer() - p.center())))
    normals = (front, math.cos(angle) * front - math.sin(angle) * tangent,
               math.cos(angle) * front + math.sin(angle) * tangent)
    points = p.center() + p.radius_mm * np.array(normals)
    values, records = radiance_at(points, p, tables), []
    for i, (point, normal) in enumerate(zip(points, normals)):
        row = dict(name=f"P{i+1}", x_mm=float(point[0]), y_mm=float(point[1]), z_mm=float(point[2]),
                   visible=bool(np.dot(normal, p.observer() - point) > 0),
                   radiance_w_m2_sr=float(values["radiance_w_m2_sr"][i]),
                   luminance_cd_m2=float(values["luminance_cd_m2"][i]))
        for name in ("xyz", "rgb1", "rgb2"):
            row.update({f"{name}_{c}": float(v) for c, v in
                        zip("XYZ" if name == "xyz" else "RGB", values[name][i])})
        records.append(row)
    return records


# 将数组最小值和最大值转为便于导出的普通浮点数。
def _extrema(values):
    return dict(minimum=float(values.min()), maximum=float(values.max()))


# 追踪各像素的球面交点并分块计算，汇总控制点与可见区域及整球统计。
def calculate(p):
    validate(p)
    tables = load_tables()
    # 按像素中心采样，列坐标从左向右，行坐标从上向下映射到屏幕毫米坐标。
    x = -p.width_mm / 2 + (np.arange(p.width_px) + .5) * p.width_mm / p.width_px
    y = p.height_mm / 2 - (np.arange(p.height_px) + .5) * p.height_mm / p.height_px
    # mask 表示射线是否命中球体，背景不参与光照和亮度统计。
    mask, points = trace(p, *np.meshgrid(x, y))
    if not np.any(mask):
        raise ValueError("Ни один пиксель не пересекает сферу")
    shape = mask.shape
    # 光谱数组形状为 (图像高,图像宽,41)，颜色数组最后一维为三个通道。
    spectral = np.zeros(shape + (41,), float)
    xyz, rgb1, rgb2 = (np.zeros(shape + (3,), float) for _ in range(3))
    radiance = np.zeros(shape, float)
    ids = np.flatnonzero(mask)

    # 只处理命中球面的像素，每批最多 8192 点，限制中间数组内存。
    for start in range(0, len(ids), 8192):
        chunk = ids[start:start + 8192]
        values = radiance_at(points.reshape(-1, 3)[chunk], p, tables)
        spectral.reshape(-1, 41)[chunk] = values["spectral"]
        for target, key in ((xyz, "xyz"), (rgb1, "rgb1"), (rgb2, "rgb2")):
            target.reshape(-1, 3)[chunk] = values[key]
        radiance.reshape(-1)[chunk] = values["radiance_w_m2_sr"]
    xyz2 = rgb2 @ CIE_RGB_TO_XYZ.T
    # 从两条计算路径的 XYZ 取 Y，并乘最大明视觉光效常数 683。
    luminance1, luminance2 = 683 * xyz[..., 1], 683 * xyz2[..., 1]
    # 仅统计 mask 内的球面像素，排除背景零值。
    statistics = {name: _extrema(v[mask]) | {"mean": float(v[mask].mean())} for name, v in
                  (("radiance_w_m2_sr", radiance), ("luminance_1_cd_m2", luminance1),
                   ("luminance_2_cd_m2", luminance2))}
    statistics["visible_pixel_count"] = int(mask.sum())
    # 用 181 个极角和 360 个方位角另行采样整球，不限于可见面。
    theta, phi = np.meshgrid(np.linspace(0, np.pi, 181),
                            np.linspace(0, 2 * np.pi, 360, endpoint=False), indexing="ij")
    normals = np.stack((np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)), axis=-1)
    sampled = {key: [] for key in ("radiance_w_m2_sr", "luminance_cd_m2")}
    normals = normals.reshape(-1, 3)
    for start in range(0, len(normals), 8192):
        values = radiance_at(p.center() + p.radius_mm * normals[start:start + 8192], p, tables)
        for key in sampled:
            sampled[key].append(values[key])
    # 整球极值是离散采样估计，不是连续球面的严格最值。
    statistics.update({"sphere_sampled_" + key: _extrema(np.concatenate(v)) for key, v in sampled.items()})
    statistics["sphere_sampling"] = "181 polar angles x 360 azimuths, poles included"
    return dict(parameters=p, wavelengths=tables.wavelengths, x=x, y=y, mask=mask, points=points,
                spectral=spectral, xyz=xyz, rgb1=rgb1, rgb2=rgb2, radiance=radiance,
                luminance1=luminance1, luminance2=luminance2,
                statistics=statistics, control_points=control_points(p, tables))
