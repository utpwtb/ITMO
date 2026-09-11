from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Circle
from PIL import Image


@dataclass(frozen=True)
class LabParameters:

    width_mm: float = 1000.0
    height_mm: float = 1000.0
    width_px: int = 600
    height_px: int = 600
    source_x_mm: float = 200.0
    source_y_mm: float = -150.0
    source_z_mm: float = 800.0
    intensity_w_sr: float = 100.0
    circle_x_mm: float = 0.0
    circle_y_mm: float = 0.0
    circle_radius_mm: float = 400.0


@dataclass
class CalculationResult:

    parameters: LabParameters
    x_mm: np.ndarray
    y_mm: np.ndarray
    irradiance_w_m2: np.ndarray
    mask: np.ndarray
    normalized_u8: np.ndarray
    section_x_mm: np.ndarray
    section_e_w_m2: np.ndarray
    reference_points: Dict[str, Tuple[float, float, float]]
    minimum_w_m2: float
    maximum_w_m2: float
    mean_w_m2: float
    analytical_minimum_w_m2: float
    analytical_maximum_w_m2: float


def validate_parameters(p: LabParameters) -> None:

    errors = []
    if not 100.0 <= p.width_mm <= 10000.0:
        errors.append("W должно находиться в диапазоне 100...10000 мм")
    if not 100.0 <= p.height_mm <= 10000.0:
        errors.append("H должно находиться в диапазоне 100...10000 мм")
    if not 200 <= p.width_px <= 800:
        errors.append("Wres должно находиться в диапазоне 200...800 пикселей")
    if not 200 <= p.height_px <= 800:
        errors.append("Hres должно находиться в диапазоне 200...800 пикселей")
    if not -10000.0 <= p.source_x_mm <= 10000.0:
        errors.append("xL должно находиться в диапазоне -10000...10000 мм")
    if not -10000.0 <= p.source_y_mm <= 10000.0:
        errors.append("yL должно находиться в диапазоне -10000...10000 мм")
    if not 100.0 <= p.source_z_mm <= 10000.0:
        errors.append("zL должно находиться в диапазоне 100...10000 мм")
    if not 0.01 <= p.intensity_w_sr <= 10000.0:
        errors.append("I0 должно находиться в диапазоне 0.01...10000 Вт/ср")
    if p.circle_radius_mm <= 0.0:
        errors.append("Радиус окружности должен быть положительным")

    pixel_x = p.width_mm / p.width_px
    pixel_y = p.height_mm / p.height_px
    if not math.isclose(pixel_x, pixel_y, rel_tol=1e-9, abs_tol=1e-12):
        errors.append(
            "Пиксели должны быть квадратными: W/Wres должно равняться H/Hres"
        )

    if abs(p.circle_x_mm) + p.circle_radius_mm > p.width_mm / 2.0:
        errors.append("Окружность выходит за границы изображения по оси X")
    if abs(p.circle_y_mm) + p.circle_radius_mm > p.height_mm / 2.0:
        errors.append("Окружность выходит за границы изображения по оси Y")

    if errors:
        raise ValueError("\n".join(errors))


def irradiance_at(
    x_mm: np.ndarray | float,
    y_mm: np.ndarray | float,
    p: LabParameters,
) -> np.ndarray | float:

    dx_m = (np.asarray(x_mm) - p.source_x_mm) / 1000.0
    dy_m = (np.asarray(y_mm) - p.source_y_mm) / 1000.0
    z_m = p.source_z_mm / 1000.0
    distance_squared_m2 = dx_m * dx_m + dy_m * dy_m + z_m * z_m
    value = p.intensity_w_sr * z_m * z_m / (distance_squared_m2**2)
    if np.ndim(value) == 0:
        return float(value)
    return value


def reference_points(p: LabParameters) -> Dict[str, Tuple[float, float, float]]:

    coordinates = {
        "Центр C": (p.circle_x_mm, p.circle_y_mm),
        "C + R по X": (p.circle_x_mm + p.circle_radius_mm, p.circle_y_mm),
        "C - R по X": (p.circle_x_mm - p.circle_radius_mm, p.circle_y_mm),
        "C + R по Y": (p.circle_x_mm, p.circle_y_mm + p.circle_radius_mm),
        "C - R по Y": (p.circle_x_mm, p.circle_y_mm - p.circle_radius_mm),
    }
    return {
        name: (x, y, irradiance_at(x, y, p))
        for name, (x, y) in coordinates.items()
    }


def analytical_extrema(p: LabParameters) -> Tuple[float, float]:

    centre_to_projection_mm = math.hypot(
        p.source_x_mm - p.circle_x_mm,
        p.source_y_mm - p.circle_y_mm,
    )
    nearest_rho_mm = max(0.0, centre_to_projection_mm - p.circle_radius_mm)
    farthest_rho_mm = centre_to_projection_mm + p.circle_radius_mm

    z_m = p.source_z_mm / 1000.0

    def radial_value(rho_mm: float) -> float:
        rho_m = rho_mm / 1000.0
        return p.intensity_w_sr * z_m * z_m / (rho_m * rho_m + z_m * z_m) ** 2

    return radial_value(farthest_rho_mm), radial_value(nearest_rho_mm)


def calculate(p: LabParameters) -> CalculationResult:

    validate_parameters(p)

    dx_mm = p.width_mm / p.width_px
    dy_mm = p.height_mm / p.height_px
    x_mm = -p.width_mm / 2.0 + (np.arange(p.width_px) + 0.5) * dx_mm
    y_mm = -p.height_mm / 2.0 + (np.arange(p.height_px) + 0.5) * dy_mm
    grid_x_mm, grid_y_mm = np.meshgrid(x_mm, y_mm)

    mask = (
        (grid_x_mm - p.circle_x_mm) ** 2
        + (grid_y_mm - p.circle_y_mm) ** 2
        <= p.circle_radius_mm**2
    )
    if not np.any(mask):
        raise ValueError("Внутри окружности не оказалось ни одного центра пикселя")

    irradiance = irradiance_at(grid_x_mm, grid_y_mm, p)
    values_inside = irradiance[mask]
    minimum = float(np.min(values_inside))
    maximum = float(np.max(values_inside))
    mean = float(np.mean(values_inside))

    normalized = np.zeros(irradiance.shape, dtype=np.uint8)
    normalized[mask] = np.rint(255.0 * values_inside / maximum).astype(np.uint8)

    section_x = np.linspace(
        p.circle_x_mm - p.circle_radius_mm,
        p.circle_x_mm + p.circle_radius_mm,
        1201,
    )
    section_e = np.asarray(
        irradiance_at(section_x, np.full(section_x.shape, p.circle_y_mm), p)
    )

    continuous_minimum, continuous_maximum = analytical_extrema(p)
    return CalculationResult(
        parameters=p,
        x_mm=x_mm,
        y_mm=y_mm,
        irradiance_w_m2=irradiance,
        mask=mask,
        normalized_u8=normalized,
        section_x_mm=section_x,
        section_e_w_m2=section_e,
        reference_points=reference_points(p),
        minimum_w_m2=minimum,
        maximum_w_m2=maximum,
        mean_w_m2=mean,
        analytical_minimum_w_m2=continuous_minimum,
        analytical_maximum_w_m2=continuous_maximum,
    )


def draw_map(figure: Figure, result: CalculationResult) -> None:
    p = result.parameters
    figure.clear()
    axis = figure.add_subplot(111)
    display_values = np.where(result.mask, result.irradiance_w_m2, np.nan)
    image = axis.imshow(
        display_values,
        origin="lower",
        extent=(-p.width_mm / 2, p.width_mm / 2, -p.height_mm / 2, p.height_mm / 2),
        cmap="inferno",
        interpolation="nearest",
        aspect="equal",
    )
    axis.add_patch(
        Circle(
            (p.circle_x_mm, p.circle_y_mm),
            p.circle_radius_mm,
            fill=False,
            edgecolor="cyan",
            linewidth=1.2,
            label="Граница области расчёта",
        )
    )
    axis.scatter(
        [p.source_x_mm],
        [p.source_y_mm],
        marker="x",
        s=55,
        linewidths=1.7,
        color="deepskyblue",
        label="Проекция источника",
    )
    axis.set_title("Распределение энергетической освещённости")
    axis.set_xlabel("x, мм")
    axis.set_ylabel("y, мм")
    axis.grid(alpha=0.18)
    axis.legend(loc="upper right", fontsize=8)
    colorbar = figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    colorbar.set_label("E, Вт/м²")
    figure.tight_layout()


def draw_section(figure: Figure, result: CalculationResult) -> None:
    p = result.parameters
    figure.clear()
    axis = figure.add_subplot(111)
    axis.plot(result.section_x_mm, result.section_e_w_m2, color="#1f4e79", linewidth=2)
    axis.axvline(p.circle_x_mm, color="gray", linestyle="--", linewidth=1)
    axis.set_title(f"Сечение через центр окружности: y = {p.circle_y_mm:g} мм")
    axis.set_xlabel("x, мм")
    axis.set_ylabel("E, Вт/м²")
    axis.grid(True, alpha=0.3)
    figure.tight_layout()


def save_results(result: CalculationResult, output_directory: Path) -> Dict[str, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "normalized": output_directory / "illumination_normalized.png",
        "map": output_directory / "illumination_map.png",
        "section": output_directory / "center_section.png",
        "points": output_directory / "five_points.csv",
        "json": output_directory / "results.json",
    }

    Image.fromarray(result.normalized_u8, mode="L").save(paths["normalized"])

    map_figure = Figure(figsize=(7.2, 6.0), dpi=150)
    draw_map(map_figure, result)
    map_figure.savefig(paths["map"], dpi=180, bbox_inches="tight")

    section_figure = Figure(figsize=(7.2, 4.5), dpi=150)
    draw_section(section_figure, result)
    section_figure.savefig(paths["section"], dpi=180, bbox_inches="tight")

    with paths["points"].open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream, delimiter=";")
        writer.writerow(["Точка", "x, мм", "y, мм", "E, Вт/м²"])
        for name, (x_mm, y_mm, value) in result.reference_points.items():
            writer.writerow([name, f"{x_mm:.6f}", f"{y_mm:.6f}", f"{value:.9f}"])

    serializable = {
        "parameters": asdict(result.parameters),
        "statistics_on_pixel_grid_w_m2": {
            "minimum": result.minimum_w_m2,
            "maximum": result.maximum_w_m2,
            "mean": result.mean_w_m2,
        },
        "analytical_extrema_w_m2": {
            "minimum": result.analytical_minimum_w_m2,
            "maximum": result.analytical_maximum_w_m2,
        },
        "reference_points": {
            name: {"x_mm": x, "y_mm": y, "irradiance_w_m2": value}
            for name, (x, y, value) in result.reference_points.items()
        },
        "normalization": "G = round(255 * E / E_max) inside the circle; G = 0 outside",
    }
    paths["json"].write_text(
        json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return paths


def result_summary(result: CalculationResult) -> str:

    rows = [
        "Статистика по центрам пикселей внутри окружности:",
        f"E_min  = {result.minimum_w_m2:.6f} Вт/м²",
        f"E_max  = {result.maximum_w_m2:.6f} Вт/м²",
        f"E_mean = {result.mean_w_m2:.6f} Вт/м²",
        "",
        "Точные значения в пяти контрольных точках:",
    ]
    for name, (x_mm, y_mm, value) in result.reference_points.items():
        rows.append(f"{name:12s}: ({x_mm:8.2f}, {y_mm:8.2f}) мм -> {value:.6f} Вт/м²")
    return "\n".join(rows)


def run_gui(initial: LabParameters) -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    root = tk.Tk()
    root.title("ЛР 1 — освещённость от ламбертовского точечного источника")
    root.geometry("1380x820")
    root.minsize(1120, 700)

    main = ttk.Frame(root, padding=10)
    main.pack(fill=tk.BOTH, expand=True)
    main.columnconfigure(1, weight=1)
    main.rowconfigure(0, weight=1)

    controls = ttk.LabelFrame(main, text="Параметры", padding=10)
    controls.grid(row=0, column=0, sticky="nsw", padx=(0, 10))

    field_specs = [
        ("width_mm", "W, мм", initial.width_mm),
        ("height_mm", "H, мм", initial.height_mm),
        ("width_px", "Wres, пикс.", initial.width_px),
        ("height_px", "Hres, пикс.", initial.height_px),
        ("source_x_mm", "xL, мм", initial.source_x_mm),
        ("source_y_mm", "yL, мм", initial.source_y_mm),
        ("source_z_mm", "zL, мм", initial.source_z_mm),
        ("intensity_w_sr", "I0, Вт/ср", initial.intensity_w_sr),
        ("circle_x_mm", "xC, мм", initial.circle_x_mm),
        ("circle_y_mm", "yC, мм", initial.circle_y_mm),
        ("circle_radius_mm", "R, мм", initial.circle_radius_mm),
    ]
    variables: Dict[str, tk.StringVar] = {}
    for row, (key, label, value) in enumerate(field_specs):
        ttk.Label(controls, text=label).grid(row=row, column=0, sticky="w", pady=3)
        variable = tk.StringVar(value=str(value))
        variables[key] = variable
        ttk.Entry(controls, textvariable=variable, width=18).grid(
            row=row, column=1, sticky="ew", padx=(8, 0), pady=3
        )

    ttk.Separator(controls).grid(
        row=len(field_specs), column=0, columnspan=2, sticky="ew", pady=10
    )
    ttk.Label(
        controls,
        text="Условие квадратных пикселей:\nW/Wres = H/Hres",
        foreground="#555555",
        justify="left",
    ).grid(row=len(field_specs) + 1, column=0, columnspan=2, sticky="w")

    output_text = tk.Text(controls, width=43, height=19, wrap="none", font=("Consolas", 9))
    output_text.grid(row=len(field_specs) + 5, column=0, columnspan=2, sticky="nsew", pady=(10, 0))

    plot_frame = ttk.Frame(main)
    plot_frame.grid(row=0, column=1, sticky="nsew")
    plot_frame.columnconfigure(0, weight=1)
    plot_frame.rowconfigure(0, weight=1)

    figure = Figure(figsize=(10, 7), dpi=100)
    canvas = FigureCanvasTkAgg(figure, master=plot_frame)
    canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    current_result: CalculationResult | None = None

    def read_parameters() -> LabParameters:
        return LabParameters(
            width_mm=float(variables["width_mm"].get()),
            height_mm=float(variables["height_mm"].get()),
            width_px=int(variables["width_px"].get()),
            height_px=int(variables["height_px"].get()),
            source_x_mm=float(variables["source_x_mm"].get()),
            source_y_mm=float(variables["source_y_mm"].get()),
            source_z_mm=float(variables["source_z_mm"].get()),
            intensity_w_sr=float(variables["intensity_w_sr"].get()),
            circle_x_mm=float(variables["circle_x_mm"].get()),
            circle_y_mm=float(variables["circle_y_mm"].get()),
            circle_radius_mm=float(variables["circle_radius_mm"].get()),
        )

    def update_plots(result: CalculationResult) -> None:
        figure.clear()
        map_axis = figure.add_subplot(121)
        section_axis = figure.add_subplot(122)
        p = result.parameters
        display_values = np.where(result.mask, result.irradiance_w_m2, np.nan)
        image = map_axis.imshow(
            display_values,
            origin="lower",
            extent=(-p.width_mm / 2, p.width_mm / 2, -p.height_mm / 2, p.height_mm / 2),
            cmap="inferno",
            interpolation="nearest",
            aspect="equal",
        )
        map_axis.add_patch(
            Circle(
                (p.circle_x_mm, p.circle_y_mm),
                p.circle_radius_mm,
                fill=False,
                edgecolor="cyan",
                linewidth=1.0,
            )
        )
        map_axis.scatter([p.source_x_mm], [p.source_y_mm], marker="x", color="cyan")
        map_axis.set_title("Распределение E")
        map_axis.set_xlabel("x, мм")
        map_axis.set_ylabel("y, мм")
        figure.colorbar(image, ax=map_axis, fraction=0.046, pad=0.04).set_label("Вт/м²")

        section_axis.plot(result.section_x_mm, result.section_e_w_m2, color="#1f4e79")
        section_axis.axvline(p.circle_x_mm, color="gray", linestyle="--", linewidth=1)
        section_axis.set_title(f"Сечение y = {p.circle_y_mm:g} мм")
        section_axis.set_xlabel("x, мм")
        section_axis.set_ylabel("E, Вт/м²")
        section_axis.grid(alpha=0.3)
        figure.tight_layout()
        canvas.draw_idle()

    def calculate_from_form() -> None:
        nonlocal current_result
        try:
            current_result = calculate(read_parameters())
        except (ValueError, TypeError) as error:
            messagebox.showerror("Ошибка параметров", str(error))
            return
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, result_summary(current_result))
        update_plots(current_result)

    def save_from_form() -> None:
        if current_result is None:
            messagebox.showwarning("Нет результатов", "Сначала выполните расчёт")
            return
        chosen = filedialog.askdirectory(title="Выберите папку для сохранения результатов")
        if not chosen:
            return
        paths = save_results(current_result, Path(chosen))
        messagebox.showinfo(
            "Результаты сохранены",
            "Сохранены файлы:\n" + "\n".join(str(path) for path in paths.values()),
        )

    ttk.Button(controls, text="Рассчитать", command=calculate_from_form).grid(
        row=len(field_specs) + 2, column=0, columnspan=2, sticky="ew", pady=(10, 3)
    )
    ttk.Button(controls, text="Сохранить результаты", command=save_from_form).grid(
        row=len(field_specs) + 3, column=0, columnspan=2, sticky="ew", pady=3
    )
    ttk.Button(controls, text="Выход", command=root.destroy).grid(
        row=len(field_specs) + 4, column=0, columnspan=2, sticky="ew", pady=3
    )

    calculate_from_form()
    root.mainloop()


def build_parser() -> argparse.ArgumentParser:
    defaults = LabParameters()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-gui", action="store_true", help="run calculation without GUI")
    parser.add_argument("--output", type=Path, default=Path("results"))
    parser.add_argument("--width", type=float, default=defaults.width_mm)
    parser.add_argument("--height", type=float, default=defaults.height_mm)
    parser.add_argument("--width-px", type=int, default=defaults.width_px)
    parser.add_argument("--height-px", type=int, default=defaults.height_px)
    parser.add_argument("--source-x", type=float, default=defaults.source_x_mm)
    parser.add_argument("--source-y", type=float, default=defaults.source_y_mm)
    parser.add_argument("--source-z", type=float, default=defaults.source_z_mm)
    parser.add_argument("--intensity", type=float, default=defaults.intensity_w_sr)
    parser.add_argument("--circle-x", type=float, default=defaults.circle_x_mm)
    parser.add_argument("--circle-y", type=float, default=defaults.circle_y_mm)
    parser.add_argument("--radius", type=float, default=defaults.circle_radius_mm)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    parameters = LabParameters(
        width_mm=args.width,
        height_mm=args.height,
        width_px=args.width_px,
        height_px=args.height_px,
        source_x_mm=args.source_x,
        source_y_mm=args.source_y,
        source_z_mm=args.source_z,
        intensity_w_sr=args.intensity,
        circle_x_mm=args.circle_x,
        circle_y_mm=args.circle_y,
        circle_radius_mm=args.radius,
    )

    if args.no_gui:
        result = calculate(parameters)
        paths = save_results(result, args.output)
        print(result_summary(result))
        print("\nСохранённые файлы:")
        for path in paths.values():
            print(path)
    else:
        run_gui(parameters)


if __name__ == "__main__":
    main()
