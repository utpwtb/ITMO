"""两种渲染路径、精确控制点、绝对数组和结果导出。"""
import csv
import json
import math
from dataclasses import asdict
from pathlib import Path
import numpy as np
from PIL import Image
from .geometry import camera_basis, geometry_factors, trace, unit, validate
from .spectral import default_parameters, load_tables, normalize_spd
from .color_conversion import (CIE_RGB_TO_XYZ, XYZ_TO_CIE_RGB, display_images,
                               scene_rgb, spectrum_to_xyz)


def radiance_at(points_mm, p, tables=None):
    tables = tables or load_tables()
    factors = geometry_factors(points_mm, p)
    spectra = np.array([normalize_spd(light.spectrum, tables) for light in p.lights])
    spectral = (factors @ spectra) * np.asarray(p.reflectance)
    xyz = spectrum_to_xyz(spectral, tables)
    kd, lights = scene_rgb(p, tables)
    return dict(spectral=spectral, xyz=xyz, rgb1=xyz @ XYZ_TO_CIE_RGB.T,
                rgb2=(factors @ lights) * kd, radiance_w_m2_sr=spectral @ tables.weights,
                luminance_cd_m2=683 * xyz[..., 1])


def control_points(p, tables=None):
    front = unit(p.observer() - p.center())
    right = camera_basis(p)[0]
    tangent = unit(right - np.dot(right, front) * front)
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


def _extrema(values):
    return dict(minimum=float(values.min()), maximum=float(values.max()))


def calculate(p):
    validate(p)
    tables = load_tables()
    x = -p.width_mm / 2 + (np.arange(p.width_px) + .5) * p.width_mm / p.width_px
    y = p.height_mm / 2 - (np.arange(p.height_px) + .5) * p.height_mm / p.height_px
    mask, points = trace(p, *np.meshgrid(x, y))
    if not np.any(mask):
        raise ValueError("Ни один пиксель не пересекает сферу")
    shape = mask.shape
    spectral = np.zeros(shape + (41,), float)
    xyz, rgb1, rgb2 = (np.zeros(shape + (3,), float) for _ in range(3))
    radiance = np.zeros(shape, float)
    ids = np.flatnonzero(mask)
    # 保留完整光谱立方体，但按块计算中间结果，避免额外大数组。
    for start in range(0, len(ids), 8192):
        chunk = ids[start:start + 8192]
        values = radiance_at(points.reshape(-1, 3)[chunk], p, tables)
        spectral.reshape(-1, 41)[chunk] = values["spectral"]
        for target, key in ((xyz, "xyz"), (rgb1, "rgb1"), (rgb2, "rgb2")):
            target.reshape(-1, 3)[chunk] = values[key]
        radiance.reshape(-1)[chunk] = values["radiance_w_m2_sr"]
    images, grays, exposure = display_images(rgb1, rgb2, mask)
    xyz2 = rgb2 @ CIE_RGB_TO_XYZ.T
    luminance1, luminance2 = 683 * xyz[..., 1], 683 * xyz2[..., 1]
    statistics = {name: _extrema(v[mask]) | {"mean": float(v[mask].mean())} for name, v in
                  (("radiance_w_m2_sr", radiance), ("luminance_1_cd_m2", luminance1),
                   ("luminance_2_cd_m2", luminance2))}
    statistics["visible_pixel_count"] = int(mask.sum())
    theta, phi = np.meshgrid(np.linspace(0, np.pi, 181),
                            np.linspace(0, 2 * np.pi, 360, endpoint=False), indexing="ij")
    normals = np.stack((np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)), axis=-1)
    sampled = {key: [] for key in ("radiance_w_m2_sr", "luminance_cd_m2")}
    normals = normals.reshape(-1, 3)
    for start in range(0, len(normals), 8192):
        values = radiance_at(p.center() + p.radius_mm * normals[start:start + 8192], p, tables)
        for key in sampled:
            sampled[key].append(values[key])
    statistics.update({"sphere_sampled_" + key: _extrema(np.concatenate(v)) for key, v in sampled.items()})
    statistics["sphere_sampling"] = "181 polar angles x 360 azimuths, poles included"
    difference = np.abs(images[0].astype(float) - images[1].astype(float))
    comparison = dict(rgb_absolute_max_difference=float(np.max(np.abs(rgb1[mask] - rgb2[mask]))),
        xyz_absolute_rmse=float(np.sqrt(np.mean((xyz[mask] - xyz2[mask]) ** 2))),
        monitor_mae_8bit=float(difference[mask].mean()),
        monitor_rmse_8bit=float(np.sqrt(np.mean(difference[mask] ** 2))),
        monitor_max_difference_8bit=int(difference[mask].max()),
        monitor_different_pixels=int(np.count_nonzero(np.any(difference > 0, axis=-1) & mask)))
    kd_rgb, lights_rgb = scene_rgb(p, tables)
    return dict(parameters=p, wavelengths=tables.wavelengths, x=x, y=y, mask=mask, points=points,
                spectral=spectral, xyz=xyz, rgb1=rgb1, rgb2=rgb2, radiance=radiance,
                luminance1=luminance1, luminance2=luminance2, images=images, grays=grays,
                statistics=statistics, comparison=comparison, exposure=exposure,
                kd_rgb=kd_rgb, lights_rgb=lights_rgb, control_points=control_points(p, tables))


def save_results(result, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    p = result["parameters"]
    images = result["images"]
    arrays = {f"image_{i+1}.png": v for i, v in enumerate(images)}
    arrays.update({f"image_{i+1}_gray.png": v for i, v in enumerate(result["grays"])})
    for name, value in arrays.items():
        Image.fromarray(value).save(directory / name)
    with (directory / "three_points.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=result["control_points"][0])
        writer.writeheader()
        writer.writerows(result["control_points"])
    metadata = dict(parameters=asdict(p),
        units=dict(spectral="W/(m^2 sr nm)", radiance="W/(m^2 sr)",
                   xyz="unscaled CIE integrals of radiance", cie_rgb="signed CIE RGB coordinates",
                   luminance="cd/m^2 = 683*Y"),
        model_formula="L_lambda=sum(I0*cos_emission*cos_incidence^power/(pi*r_m^2)*normalized_SPD*kd_lambda)",
        incidence_power=2 if p.model == "reference_diagram" else 1,
        spectral_integration="380..780 nm, 10 nm, composite trapezoid, SPD integral normalized to one",
        matrix_policy="assignment XYZ_TO_CIE_RGB, forward matrix is its numerical inverse",
        XYZ_TO_CIE_RGB=XYZ_TO_CIE_RGB.tolist(), CIE_RGB_TO_XYZ=CIE_RGB_TO_XYZ.tolist(),
        monitor_policy="CIE RGB -> XYZ -> linear sRGB, shared gain, gamut clipping, sRGB transfer, round 255",
        grayscale_policy="decode saved RGB PNG sRGB, linear Y, encode sRGB, round 255",
        spectral_storage="float64 full Hres x Wres x 41 cube, zeros outside independent mask",
        kd_rgb=result["kd_rgb"].tolist(), lights_rgb=result["lights_rgb"].tolist())
    metadata.update({key: result[key] for key in ("control_points", "statistics", "comparison", "exposure")})
    (directory / "results.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = dict(wavelengths_nm="wavelengths", spectral_radiance="spectral", xyz1="xyz",
        rgb1="rgb1", rgb2="rgb2", radiance_w_m2_sr="radiance", luminance1_cd_m2="luminance1",
        luminance2_cd_m2="luminance2", mask="mask", points_mm="points", screen_x_mm="x", screen_y_mm="y")
    np.savez_compressed(directory / "radiance_data.npz", **{name: result[key] for name, key in fields.items()})
    return metadata


def summary(result):
    rows = [f"{key}: min={result['statistics'][key]['minimum']:.9g}, "
            f"max={result['statistics'][key]['maximum']:.9g}" for key in
            ("radiance_w_m2_sr", "luminance_1_cd_m2", "luminance_2_cd_m2")]
    rows.append(f"Различие RGB PNG, MAE={result['comparison']['monitor_mae_8bit']:.6g}")
    rows.extend(f"{point['name']}: L={point['radiance_w_m2_sr']:.9g} W/(m² sr), "
                f"Lv={point['luminance_cd_m2']:.9g} cd/m²" for point in result["control_points"])
    return "\n".join(rows)


def run_case(case, directory, p=None):
    result = calculate(default_parameters(case) if p is None else p)
    save_results(result, directory)
    return result
