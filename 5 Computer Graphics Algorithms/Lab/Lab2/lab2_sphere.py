from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

import numpy as np
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg


@dataclass(frozen=True)
class Light:
    x_mm: float = -650.0
    y_mm: float = 450.0
    z_mm: float = 1700.0
    intensity_w_sr: float = 100.0
    # Unit emission axis in world coordinates; default follows the assignment (-Z).
    axis: tuple[float, float, float] = (0.0, 0.0, -1.0)

    def position(self):
        return np.array([self.x_mm, self.y_mm, self.z_mm], dtype=float)


@dataclass(frozen=True)
class Parameters:
    width_mm: float = 1200.0
    height_mm: float = 1200.0
    width_px: int = 600
    height_px: int = 600
    observer_z_mm: float = 2500.0
    direction: tuple[float, float, float] = (0.0, 0.0, -1.0)
    screen_distance_mm: float = 2500.0
    center_x_mm: float = 0.0
    center_y_mm: float = 0.0
    center_z_mm: float = 600.0
    radius_mm: float = 350.0
    kd: float = 0.20
    ks: float = 0.80
    shininess: float = 80.0
    lights: tuple[Light, ...] = field(default_factory=lambda: (
        Light(), Light(550.0, -250.0, 1600.0, 70.0)))

    def __post_init__(self):
        # Derive the vertical resolution from physical screen dimensions.
        if self.width_mm > 0 and self.height_mm > 0 and self.width_px > 0:
            height_px = max(1, int(round(self.width_px * self.height_mm / self.width_mm)))
        else:
            height_px = 1
        object.__setattr__(self, "height_px", height_px)

    def observer(self):
        return np.array([0.0, 0.0, self.observer_z_mm])

    def center(self):
        return np.array([self.center_x_mm, self.center_y_mm, self.center_z_mm])


def unit(v):
    v = np.asarray(v, dtype=float)
    norm = np.linalg.norm(v, axis=-1, keepdims=True)
    return np.divide(v, norm, out=np.zeros_like(v), where=norm > 1e-14)


def camera_basis(p):
    # 相机坐标系：观察方向为前向，叉积构造屏幕右向与上向；三者均为单位向量。
    forward = unit(p.direction)
    up_hint = np.array([0.0, 1.0, 0.0])
    if abs(np.dot(forward, up_hint)) > 0.99:
        up_hint = np.array([1.0, 0.0, 0.0])
    right = unit(np.cross(forward, up_hint))
    up = unit(np.cross(right, forward))
    return right, up, forward


def validate(p):
    numeric = [p.width_mm, p.height_mm, p.observer_z_mm,
               p.screen_distance_mm, p.center_x_mm, p.center_y_mm,
               p.center_z_mm, p.radius_mm, p.kd, p.ks, p.shininess,
               *p.direction]
    if not all(math.isfinite(x) for x in numeric):
        raise ValueError("Все параметры должны быть конечными числами")
    if not 100 <= p.width_mm <= 10000 or not 100 <= p.height_mm <= 10000:
        raise ValueError("W и H должны быть в диапазоне 100..10000 мм")
    if not isinstance(p.width_px, (int, np.integer)) or not 200 <= p.width_px <= 800:
        raise ValueError("Wres должно быть целым числом 200..800")
    expected_height_px = max(1, int(round(p.width_px * p.height_mm / p.width_mm)))
    if p.height_px != expected_height_px or not 200 <= p.height_px <= 800:
        raise ValueError("Автоматическое Hres должно попадать в диапазон 200..800")
    if abs(p.center_x_mm) > 10000 or abs(p.center_y_mm) > 10000:
        raise ValueError("xC и yC должны быть в диапазоне -10000..10000 мм")
    if not 100 <= p.center_z_mm <= 10000:
        raise ValueError("zC должен быть в диапазоне 100..10000 мм")
    if p.radius_mm <= 0 or p.screen_distance_mm <= 0:
        raise ValueError("Радиус и расстояние до экрана должны быть > 0")
    if np.linalg.norm(p.direction) < 1e-12:
        raise ValueError("Направление наблюдения не может быть нулевым")
    # zO may be above or below the sphere.  The camera only has to stay outside it.
    if np.linalg.norm(p.observer() - p.center()) <= p.radius_mm:
        raise ValueError("Наблюдатель должен находиться вне сферы")
    if p.kd < 0 or p.ks < 0 or p.shininess <= 0:
        raise ValueError("kd, ks >= 0; показатель блеска > 0")
    if not p.lights:
        raise ValueError("Требуется хотя бы один источник")
    for light in p.lights:
        light_values = (light.x_mm, light.y_mm, light.z_mm,
                        light.intensity_w_sr, *light.axis)
        if not all(math.isfinite(x) for x in light_values):
            raise ValueError("Параметры источника должны быть конечными")
        if np.linalg.norm(light.axis) < 1e-12:
            raise ValueError("Направление излучения источника не может быть нулевым")
        if abs(light.x_mm) > 10000 or abs(light.y_mm) > 10000:
            raise ValueError("xL и yL должны быть в диапазоне -10000..10000 мм")
        if not 100 <= light.z_mm <= 10000:
            raise ValueError("zL должен быть в диапазоне 100..10000 мм")
        if not 0.01 <= light.intensity_w_sr <= 10000:
            raise ValueError("I0 должен быть в диапазоне 0.01..10000 Вт/ср")
        if np.linalg.norm(light.position() - p.center()) <= p.radius_mm:
            raise ValueError("Источник должен находиться вне сферы")
    # 球体完整可见的几何判据：球心到视锥四个侧面的有符号距离均不小于半径。
    # 不能只检查投影中心，否则球体边缘可能被裁剪。
    right, up, forward = camera_basis(p)
    rel = p.center() - p.observer()
    depth = np.dot(rel, forward)
    if depth <= p.radius_mm:
        raise ValueError("Сфера должна целиком находиться перед наблюдателем")
    # The screen plane O + f*d must lie beyond the far side of the sphere.
    if p.screen_distance_mm <= depth + p.radius_mm:
        raise ValueError("Экран должен находиться за всей сферой по направлению наблюдения")
    for axis, half_size in ((right, p.width_mm / 2), (up, p.height_mm / 2)):
        slope = half_size / p.screen_distance_mm
        for sign in (-1, 1):
            plane_normal = unit(slope * forward + sign * axis)
            if np.dot(rel, plane_normal) < p.radius_mm - 1e-8:
                raise ValueError(
                    "Сфера не целиком помещается в поле зрения. Увеличьте W/H; "
                    "для стандартного вида снизу используйте экран 2000×2000 мм")


def trace(p, screen_x, screen_y):
    """Return hit mask and closest positive ray-sphere intersections (mm)."""
    right, up, forward = camera_basis(p)
    # 透视投影：从观察者 O 发出穿过每个像素中心的单位射线 d。
    directions = unit(p.screen_distance_mm * forward
                      + np.asarray(screen_x)[..., None] * right
                      + np.asarray(screen_y)[..., None] * up)
    oc = p.observer() - p.center()
    # 将 P=O+t*d 代入 |P-C|²=R²，得 t²+2b*t+c=0。
    # 因为 d 已单位化，二次项系数为 1；判别式采用 b²-c。
    b = np.sum(directions * oc, axis=-1)
    c = np.dot(oc, oc) - p.radius_mm**2
    discriminant = b*b - c
    # 相机已被验证位于球体外，取较小的正根，得到遮挡后真正可见的前表面。
    t = -b - np.sqrt(np.maximum(discriminant, 0))
    mask = (discriminant >= 0) & (t > 0)
    points = p.observer() + t[..., None] * directions
    return mask, points


def radiance_at(points_mm, p):
    """Evaluate radiance toward the observer at surface points, in W/(m2 sr)."""
    points = np.asarray(points_mm, dtype=float)
    # 球面单位法向量 n=(P-C)/R；v 是表面点指向观察者的单位向量。
    n = unit(points - p.center())
    view = unit(p.observer() - points)
    # 出射方向必须位于表面法线的正半球；背面朝观察者的方向不产生出射亮度。
    facing_observer = np.sum(n*view, axis=-1) > 0
    diffuse = np.zeros(points.shape[:-1])
    specular = np.zeros_like(diffuse)
    for light in p.lights:
        to_light = light.position() - points
        # 输入距离为毫米；照明的平方反比项必须使用米，得到 W/m² 的辐照度。
        distance2_m = np.sum((to_light / 1000.0)**2, axis=-1)
        l = unit(to_light)
        # 朗伯点光源：I(θ)=I0*max(a·s,0)，a 是可调单位发射轴，s=-l 是光源到表面的方向。
        # 默认 a=(0,0,-1) 时退化为 max(l_z,0)；截断负值表示光源背向一侧不发光。
        emission_axis = unit(light.axis)
        cos_emission = np.maximum(np.sum((-l) * emission_axis, axis=-1), 0.0)
        # 接收面的余弦定律：cosα=max(n·l,0)，背光面不接收该光源的直接照明。
        cos_incidence = np.maximum(np.sum(n*l, axis=-1), 0.0)
        irradiance = (light.intensity_w_sr * cos_emission * cos_incidence
                      * facing_observer / distance2_m)
        # Blinn–Phong 半程向量 h=(l+v)/|l+v|；n·h 越接近 1，高光越强。
        half_vector = unit(l + view)
        cos_half = np.clip(np.sum(n*half_vector, axis=-1), 0.0, 1.0)
        # 按题目示意图的经验反射模型：f=kd+ks*max(n·h,0)^m，L=Σ(E_i*f_i)。
        # kd、ks 在此按 sr⁻¹ 解释，绝对亮度单位为 W/(m²·sr)，不是灰度或 cd/m²。
        # 这是经验模型，不声称其满足能量守恒，也不另加与题目不同的归一化因子。
        diffuse += irradiance * p.kd
        specular += irradiance * p.ks * cos_half**p.shininess
    return diffuse + specular, diffuse, specular


def control_points(p):
    # 三个控制点由单位法向量定义并直接代入理论公式，不读取最近像素。
    # 默认坐标为 (0,0,950)、(-210,0,880)、(210,0,880) mm。
    right, _, forward = camera_basis(p)
    front = -forward
    normals = (front, -0.6*right + 0.8*front, 0.6*right + 0.8*front)
    records = []
    for name, normal in zip(("P1", "P2", "P3"), normals):
        point = p.center() + p.radius_mm * normal
        total, diffuse, specular = radiance_at(point, p)
        records.append(dict(name=name, x_mm=float(point[0]), y_mm=float(point[1]),
                            z_mm=float(point[2]), radiance_w_m2_sr=float(total),
                            diffuse_w_m2_sr=float(diffuse), specular_w_m2_sr=float(specular),
                            visible=bool(np.dot(normal, p.observer()-point) > 0)))
    return records


def calculate(p):
    validate(p)
    x = -p.width_mm/2 + (np.arange(p.width_px)+0.5)*p.width_mm/p.width_px
    # 使用像素中心采样；PNG 第 0 行对应屏幕上方，绘图同样采用 origin='upper'。
    y = p.height_mm/2 - (np.arange(p.height_px)+0.5)*p.height_mm/p.height_px
    gx, gy = np.meshgrid(x, y)
    mask, points = trace(p, gx, gy)
    if not np.any(mask):
        raise ValueError("Сфера слишком мала: ни один луч не пересекает её")
    total = np.zeros(mask.shape)
    diffuse = np.zeros_like(total)
    specular = np.zeros_like(total)
    total[mask], diffuse[mask], specular[mask] = radiance_at(points[mask], p)
    values = total[mask]
    maximum = float(values.max())
    image = np.zeros(mask.shape, dtype=np.uint8)
    # 八位归一化 G=round(255*L/Lmax)；背景为 0，全黑场景单独处理以避免除零。
    if maximum > 0:
        image[mask] = np.rint(255 * values / maximum).astype(np.uint8)
    # 补充全球面角度采样的极值，与图像可见区域的像素极值分别记录。
    # 采样最大值只是离散估计，不能当作连续球面的精确最大值。
    theta = np.linspace(0, np.pi, 361)
    phi = np.linspace(0, 2*np.pi, 720, endpoint=False)
    t, f = np.meshgrid(theta, phi, indexing="ij")
    normals = np.stack((np.sin(t)*np.cos(f), np.sin(t)*np.sin(f), np.cos(t)), axis=-1)
    surface = p.center() + p.radius_mm * normals
    surface_values, _, _ = radiance_at(surface, p)
    argmax = np.unravel_index(np.argmax(total), total.shape)
    statistics = dict(visible_minimum=float(values.min()), visible_maximum=maximum,
                      visible_mean=float(values.mean()), visible_pixel_count=int(mask.sum()),
                      maximum_point_mm=points[argmax].tolist(),
                      sphere_sampled_minimum=float(surface_values.min()),
                      sphere_sampled_maximum=float(surface_values.max()),
                      sphere_grid="361 polar angles x 720 azimuths, poles included")
    return dict(parameters=p, x=x, y=y, mask=mask, points=points,
                total=total, diffuse=diffuse, specular=specular, image=image,
                statistics=statistics, control_points=control_points(p))


def draw_map(fig, result, normalized=False):
    fig.clear()
    ax = fig.add_subplot(111)
    p = result["parameters"]
    data = result["image"] if normalized else np.where(result["mask"], result["total"], np.nan)
    im = ax.imshow(data, origin="upper", extent=(-p.width_mm/2, p.width_mm/2,
                   -p.height_mm/2, p.height_mm/2), cmap="gray" if normalized else "inferno",
                   interpolation="nearest", vmin=0)
    ax.set(xlabel="x экрана, мм", ylabel="y экрана, мм", title="Яркость сферы — Блинн–Фонг")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04).set_label(
        "G, 0–255" if normalized else "L, Вт/(м²·ср)")
    fig.tight_layout()


def draw_section(fig, result):
    p = result["parameters"]
    right, up, forward = camera_basis(p)
    relative = p.center()-p.observer()
    center_screen_y = p.screen_distance_mm*np.dot(relative, up)/np.dot(relative, forward)
    x = np.linspace(-p.width_mm/2, p.width_mm/2, 2001)
    mask, points = trace(p, x, np.full_like(x, center_screen_y))
    values = [np.full_like(x, np.nan) for _ in range(3)]
    if np.any(mask):
        for array, part in zip(values, radiance_at(points[mask], p)):
            array[mask] = part
    fig.clear()
    ax = fig.add_subplot(111)
    for array, name in zip(values, ("Полная яркость", "Диффузная часть", "Зеркальная часть")):
        ax.plot(x, array, label=name)
    ax.set(xlabel="x экрана, мм", ylabel="L, Вт/(м²·ср)",
           title="Сечение через проекцию центра сферы")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=9)
    fig.tight_layout()


def save_results(result, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    Image.fromarray(result["image"]).save(directory/"sphere_normalized.png")
    Image.fromarray((result["mask"]*255).astype(np.uint8)).save(directory/"sphere_mask.png")
    for name, drawer in (("brightness_map.png", draw_map), ("center_section.png", draw_section)):
        fig = Figure(figsize=(7.2, 5.7 if drawer == draw_map else 4.3))
        FigureCanvasAgg(fig)
        drawer(fig, result)
        fig.savefig(directory/name, dpi=180, bbox_inches="tight")
    with (directory/"three_points.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=result["control_points"][0].keys())
        writer.writeheader()
        writer.writerows(result["control_points"])
    p = result["parameters"]
    (directory/"results.json").write_text(json.dumps(dict(
        parameters=asdict(p), unit="W/(m^2 sr)",
        model="L=sum[I0*cos_emission/distance_m^2*cos_incidence*(kd+ks*cos_half^m)]",
        coefficients_unit="sr^-1; empirical assignment BRDF, no energy-conservation claim",
        normalization="round(255*L/visible_maximum); zero outside; all zero if maximum=0",
        statistics=result["statistics"], control_points=result["control_points"]),
        ensure_ascii=False, indent=2), encoding="utf-8")
    np.savez_compressed(directory/"radiance_data.npz", radiance=result["total"],
                        diffuse=result["diffuse"], specular=result["specular"],
                        mask=result["mask"], points_mm=result["points"],
                        screen_x_mm=result["x"], screen_y_mm=result["y"])


def summary(result):
    s = result["statistics"]
    rows = ["Яркость, Вт/(м²·ср):",
            f"Видимая сфера: min={s['visible_minimum']:.9f}; max={s['visible_maximum']:.9f}",
            f"Вся сфера (сетка): min={s['sphere_sampled_minimum']:.9f}; max={s['sphere_sampled_maximum']:.9f}"]
    for point in result["control_points"]:
        rows.append(f"{point['name']}: ({point['x_mm']:.1f}, {point['y_mm']:.1f}, {point['z_mm']:.1f}) мм; L={point['radiance_w_m2_sr']:.9f}")
    return "\n".join(rows)


def load_parameters(path):
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    data = data.get("parameters", data)
    if "lights" in data:
        data["lights"] = tuple(Light(**light) for light in data["lights"])
    if "direction" in data:
        data["direction"] = tuple(data["direction"])
    return Parameters(**data)


def run_gui(initial):
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    root = tk.Tk()
    root.title("ЛР 2 — яркость сферы от точечных источников")
    root.geometry("1280x900")
    controls = ttk.Frame(root, padding=10)
    controls.pack(side="left", fill="y")
    fields = (("width_mm", "W, мм"), ("height_mm", "H, мм"),
              ("width_px", "Wres"),
              ("observer_z_mm", "zO, мм"), ("screen_distance_mm", "f до экрана, мм"),
              ("center_x_mm", "xC, мм"), ("center_y_mm", "yC, мм"),
              ("center_z_mm", "zC, мм"), ("radius_mm", "Радиус, мм"),
              ("kd", "kd, 1/ср"), ("ks", "ks, 1/ср"), ("shininess", "Показатель блеска"))
    variables = {}
    for row, (key, label) in enumerate(fields):
        ttk.Label(controls, text=label).grid(row=row, column=0, sticky="w")
        variables[key] = tk.StringVar(value=str(getattr(initial, key)))
        ttk.Entry(controls, textvariable=variables[key], width=19).grid(row=row, column=1, pady=2)
    resolution_row = len(fields)
    resolution_label = ttk.Label(controls, text="")
    resolution_label.grid(row=resolution_row, column=0, columnspan=2, sticky="w")

    def refresh_resolution(*_):
        try:
            w_mm = float(variables["width_mm"].get())
            h_mm = float(variables["height_mm"].get())
            w_px = int(variables["width_px"].get())
            h_px = max(1, int(round(w_px * h_mm / w_mm)))
            resolution_label.configure(text=f"Авторазрешение: {w_px} × {h_px} px")
        except (ValueError, ZeroDivisionError):
            resolution_label.configure(text="Авторазрешение: проверьте W, H и Wres")

    for key in ("width_mm", "height_mm", "width_px"):
        variables[key].trace_add("write", refresh_resolution)
    refresh_resolution()
    direction_var = tk.StringVar(value=",".join(map(str, initial.direction)))
    row = resolution_row + 1
    ttk.Label(controls, text="Направление dx,dy,dz").grid(row=row, column=0, sticky="w")
    ttk.Entry(controls, textvariable=direction_var, width=19).grid(row=row, column=1)
    ttk.Label(controls, text="Источники: x y z I0 ax ay az, по одному в строке").grid(
        row=row+1, column=0, columnspan=2, sticky="w", pady=(8, 2))
    lights_text = tk.Text(controls, width=39, height=5)
    lights_text.grid(row=row+2, column=0, columnspan=2)
    lights_text.insert("1.0", "\n".join(
        f"{l.x_mm} {l.y_mm} {l.z_mm} {l.intensity_w_sr} "
        f"{' '.join(map(str, l.axis))}" for l in initial.lights))
    output = tk.Text(controls, width=44, height=11, wrap="word")
    output.grid(row=row+6, column=0, columnspan=2, pady=8)
    fig = Figure(figsize=(8, 6))
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side="right", fill="both", expand=True)
    current = None

    def read_form():
        values = {key: (int(var.get()) if key.endswith("_px") else float(var.get()))
                  for key, var in variables.items()}
        direction = tuple(float(v) for v in direction_var.get().replace(",", " ").split())
        if len(direction) != 3:
            raise ValueError("Направление должно содержать три числа")
        lights = []
        for line in lights_text.get("1.0", "end").splitlines():
            if line.strip():
                parts = [float(v) for v in line.replace(",", " ").split()]
                if len(parts) != 7:
                    raise ValueError("Источник: семь чисел x y z I0 ax ay az")
                lights.append(Light(*parts[:4], axis=tuple(parts[4:])))
        return Parameters(**values, direction=direction, lights=tuple(lights))

    def update():
        nonlocal current
        try:
            computed = calculate(read_form())
        except (ValueError, TypeError) as error:
            messagebox.showerror("Ошибка параметров", str(error))
            return False
        current = computed
        draw_map(fig, current, normalized=True)
        canvas.draw_idle()
        output.delete("1.0", "end")
        output.insert("1.0", summary(current))
        return True

    def save():
        # Read and recalculate to prevent saving stale results after form edits.
        if not update():
            return
        directory = filedialog.askdirectory(title="Папка результатов")
        if directory:
            save_results(current, directory)
            messagebox.showinfo("Сохранено", "Изображения и численные результаты сохранены")

    def apply_below_view_preset():
        # Рабочая геометрия: наблюдатель снизу, сфера между ним и экраном.
        preset = {
            "width_mm": 2000, "height_mm": 2000,
            "observer_z_mm": 0, "screen_distance_mm": 1200,
            "center_x_mm": 0, "center_y_mm": 0,
            "center_z_mm": 600, "radius_mm": 350,
        }
        for key, value in preset.items():
            variables[key].set(str(value))
        direction_var.set("0,0,1")
        update()

    ttk.Button(controls, text="Рассчитать", command=update).grid(row=row+3, column=0, columnspan=2, sticky="ew", pady=6)
    ttk.Button(controls, text="Сохранить результаты", command=save).grid(row=row+4, column=0, columnspan=2, sticky="ew")
    ttk.Button(controls, text="Пример: вид снизу (+Z)",
               command=apply_below_view_preset).grid(
                   row=row+5, column=0, columnspan=2, sticky="ew", pady=(6, 0))
    update()
    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-gui", action="store_true")
    parser.add_argument("--config", type=Path, help="JSON parameters file")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent/"results")
    args = parser.parse_args()
    p = load_parameters(args.config) if args.config else Parameters()
    try:
        if args.no_gui:
            result = calculate(p)
            save_results(result, args.output)
            print(summary(result))
            print(f"Результаты: {args.output.resolve()}")
        else:
            run_gui(p)
    except (ValueError, TypeError, OSError) as error:
        parser.exit(2, f"Ошибка: {error}\n")
    except ImportError as error:
        parser.exit(2, f"GUI requires tkinter and matplotlib. Use --no-gui for headless mode. {error}\n")


if __name__ == "__main__":
    main()
