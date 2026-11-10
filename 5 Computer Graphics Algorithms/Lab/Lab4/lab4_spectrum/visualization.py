"""Comparisons and the assignment scene drawn from the actual experiment data."""
from pathlib import Path

import numpy as np
from matplotlib.figure import Figure
from PIL import Image

from .core.geometry import camera_basis, screen_offset_mm, unit


def comparison_figure(data):
    figure = Figure(figsize=(12, 8), layout="constrained")
    axes = figure.subplots(2, 3)
    for ax, image, title in zip(axes[0], data["images"],
            ("A: reconstructed spectrum", "1: original spectrum", "2: input CIE RGB directly")):
        ax.imshow(image)
        ax.set_title(title, fontsize=10)
        ax.set_axis_off()

    result, reference = data["result"], data["reference"]
    mask = result["mask"]
    rgb_error = np.max(np.abs(result["rgb1"] - data["rgb_direct"]), axis=-1)
    errors = (rgb_error, result["luminance1"] - reference["luminance1"],
              result["radiance"] - reference["radiance"])
    labels = ("max channel |CIE RGB A - 2|", "Luminance A - 1", "Radiance A - 1")
    units = ("absolute CIE RGB", "cd/m²", "W/(m² sr)")
    floors = (1e-8, 1e-6, 1e-10)
    for index, (ax, error, label, unit_label, floor) in enumerate(
            zip(axes[1], errors, labels, units, floors)):
        maximum = float(np.max(np.abs(error[mask])))
        # A fixed numerical floor keeps floating-point noise visually close to zero.
        limit = max(maximum, floor)
        picture = ax.imshow(np.ma.array(error, mask=~mask),
                            cmap="viridis" if index == 0 else "coolwarm",
                            vmin=0 if index == 0 else -limit, vmax=limit)
        ax.set_title(f"{label}\nmax |difference| = {maximum:.4g}", fontsize=10)
        ax.set_axis_off()
        figure.colorbar(picture, ax=ax, shrink=.8, label=unit_label)
    status = ("Same input color as original spectrum" if data["input_matches_original"] else
              "Input color was edited: original-spectrum image 1 is a different-color baseline")
    figure.suptitle("Shared display exposure; absolute differences below\n" + status, fontsize=11)
    return figure


def scene_figure(data):
    figure = Figure(figsize=(13, 7))
    grid = figure.add_gridspec(1, 2, width_ratios=(1.05, 1.25),
                                 left=.04, right=.99, bottom=.14, top=.92, wspace=.1)
    ax = figure.add_subplot(grid[0], projection="3d")
    table_ax = figure.add_subplot(grid[1])
    scene = data["scene"]
    center, observer = scene.center(), scene.observer()
    right, up, forward = camera_basis(scene)
    screen_center = observer + screen_offset_mm(scene, forward) * forward
    corners = np.array([screen_center + x * scene.width_mm / 2 * right
                        + y * scene.height_mm / 2 * up
                        for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    outline = np.vstack((corners, corners[0]))
    ax.plot(*outline.T, color="steelblue", label="Screen W × H")
    for corner in corners:
        ax.plot(*np.stack((observer, corner)).T, color="gray", linestyle=":", alpha=.5)
    azimuth, polar = np.meshgrid(np.linspace(0, 2*np.pi, 32), np.linspace(0, np.pi, 17))
    radius = scene.radius_mm
    sphere = (center[0] + radius*np.sin(polar)*np.cos(azimuth),
              center[1] + radius*np.sin(polar)*np.sin(azimuth),
              center[2] + radius*np.cos(polar))
    ax.plot_wireframe(*sphere, color="gray", alpha=.3, linewidth=.5)
    ax.scatter(*observer, color="black", marker="^", s=45)
    ax.text(*observer, " O")
    ax.scatter(*center, color="gray", s=12)
    ax.text(*center, " C")

    record = data["result"]["control_points"][0]
    point = np.array([record[key] for key in ("x_mm", "y_mm", "z_mm")])
    normal = unit(point-center)
    ax.scatter(*point, color="purple", s=30)
    ax.text(*point, " P1")
    ax.quiver(*point, *normal, length=.6*radius, color="purple", arrow_length_ratio=.18)
    ax.text(*(point+.65*radius*normal), "N")
    for index, light in enumerate(scene.lights):
        position = light.position()
        ax.scatter(*position, color="darkorange", marker="*", s=65)
        ax.text(*position, f" L{index+1}")
        ax.quiver(*position, *unit(light.axis), length=.65*radius,
                  color="darkorange", arrow_length_ratio=.2)
        ax.quiver(*position, *(point-position), color="crimson",
                  arrow_length_ratio=.06, linewidth=.8)
    points = np.vstack((corners, observer, center-radius, center+radius,
                        *[light.position() for light in scene.lights]))
    ax.set_box_aspect(np.maximum(np.ptp(points, axis=0), 1))
    ax.set(xlabel="X, mm", ylabel="Y, mm", zlabel="Z, mm", title="Actual scene and rays to P1")
    ax.tick_params(labelsize=8, pad=0)
    ax.view_init(elev=20, azim=-60)
    ax.legend(loc="lower left", fontsize=8)

    table_ax.set_axis_off()
    fields = ("distance_m", "theta_deg", "sigma_deg", "emitted_intensity_w_sr",
              "irradiance_w_m2", "lambert_factor_w_m2_sr")
    rows = [[row["source"], *[f"{row[key]:.5g}" for key in fields]]
            for row in data["geometry_rows"]]
    height = min(.65, .085*(len(rows)+1))
    table = table_ax.table(cellText=rows,
        colLabels=("Light", "r\nm", "θ\ndeg", "σ\ndeg", "I₀ cosθ\nW/sr", "E\nW/m²", "E/π\nW/(m² sr)"),
        cellLoc="center", bbox=(0, .78-height, 1, height))
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table_ax.set_title("P1: factors from the assignment geometry", fontsize=11)
    table_ax.text(0, .12, "I = I₀ max(cos θ, 0)\n"
                  "E = I max(cos σ, 0) / r²\nL = kd E / π\n"
                  "Table uses the original I₀ scale before spectral factors.\n"
                  "The reconstructed spectrum is applied separately.",
                  transform=table_ax.transAxes, fontsize=10, va="bottom")
    return figure


def lab3_figure(data):
    figure = Figure(figsize=(12, 4.5), layout="constrained")
    assets = Path(__file__).resolve().parent / "assets"
    images = [data["images"][0]]
    for name in ("lab3_image_1.png", "lab3_image_2.png"):
        with Image.open(assets / name) as image:
            images.append(np.array(image.convert("RGB")))
    for ax, image, title in zip(figure.subplots(1, 3), images,
            ("A: current Lab4 scene", "Original Lab3 image_1", "Original Lab3 image_2")):
        ax.imshow(image)
        ax.set_title(title, fontsize=10)
        ax.set_axis_off()
    figure.suptitle("Archived Lab3: green material, two receiver cosines, piecewise sRGB\n"
                   "Different scene/display conditions: differences are not pure reconstruction error",
                   fontsize=11)
    return figure
