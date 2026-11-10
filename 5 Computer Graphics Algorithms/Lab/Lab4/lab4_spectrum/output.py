# 绘制光谱图、整理文字摘要，并导出 PNG、CSV、JSON 及保存绝对浮点数据的 NPZ。
import csv
import json
from dataclasses import asdict
from pathlib import Path
import numpy as np
from PIL import Image
from .core.spectral import load_tables


# 绘制各光源的原谱与重建谱，以及白球反射率曲线，返回图形对象。
def spectral_figure(data):
    from matplotlib.figure import Figure
    figure = Figure(figsize=(9, 5), layout="constrained")
    ax, material = figure.subplots(1, 2)
    for i, (original, recovered) in enumerate(zip(data["original_spd"], data["recovered"])):
        # 实线表示原谱，虚线表示 RGB 重建谱，使用相同的 41 点波长网格。
        ax.plot(load_tables().wavelengths, original, label=f"L{i+1}: original")
        ax.plot(load_tables().wavelengths, recovered, "--", label=f"L{i+1}: RGB reconstruction")
    ax.set(xlabel="Wavelength, nm", ylabel="Spectral factor, 1/nm", title="Light spectra")
    ax.legend(fontsize=8)
    # 白球的原始与重建反射率均为 1，因此材料曲线重合。
    material.plot(load_tables().wavelengths, np.ones(41), label="Original / reconstructed")
    material.set(xlabel="Wavelength, nm", ylabel="Reflectance", ylim=(0, 1.1), title="White sphere: kd = 1")
    material.legend(fontsize=8)
    return figure


# 将控制点亮度、采样极值、光谱误差和三图差异整理为界面显示文本。
def summary(data):
    r = data["result"]
    lines = ["Белая сфера. Максимумы/минимумы — дискретные оценки."]
    for point in r["control_points"]:
        lines.append(f"{point['name']}: Lₑ={point['radiance_w_m2_sr']:.9g} W/(m² sr), "
                     f"Lᵥ={point['luminance_cd_m2']:.9g} cd/m²")
    for key in ("radiance_w_m2_sr", "luminance_1_cd_m2", "sphere_sampled_radiance_w_m2_sr",
                "sphere_sampled_luminance_cd_m2"):
        lines.append(f"{key}: {r['statistics'][key]}")
    for i, metric in enumerate(data["spectrum_metrics"]):
        lines.append(f"L{i+1}: {metric}")
    lines.append("Сравнение при одинаковом белом материале: " + str(data["comparison"]))
    return "\n".join(lines)


# 将当前已计算的结果保存到指定目录，并返回导出的元数据。
def save(data, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    # 保存统一显示增益后的三张 8 位图片；绝对数值另存到 NPZ。
    for name, image in zip(("image_A", "image_1", "image_2"), data["images"]):
        Image.fromarray(image).save(directory / (name + ".png"))
    t, r = load_tables(), data["result"]
    rows = []
    # 逐波长记录各光源的原始值、重建值和差值。
    for j, wavelength in enumerate(t.wavelengths):
        row = {"wavelength_nm": int(wavelength), "kd_original": 1, "kd_reconstructed": 1}
        for i, (original, recovered) in enumerate(zip(data["original_spd"], data["recovered"])):
            row.update({f"light_{i+1}_original": original[j], f"light_{i+1}_reconstructed": recovered[j],
                        f"light_{i+1}_error": recovered[j]-original[j]})
        rows.append(row)
    for name, records in (("spectra_comparison.csv", rows), ("three_points.csv", r["control_points"])):
        with (directory / name).open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=records[0])
            writer.writeheader()
            writer.writerows(records)
    # 保留光谱立方体、XYZ、RGB、亮度及 mask，避免只保存 PNG 丢失物理量。
    np.savez_compressed(directory / "absolute_data.npz", spectral_A=r["spectral"],
        xyz_A=r["xyz"], rgb_A=r["rgb1"], mask=r["mask"], wavelengths_nm=t.wavelengths,
        radiance_A=r["radiance"], luminance_A=r["luminance1"],
        recovered_spd=data["recovered"], input_rgb=data["input_rgb"])
    # 记录场景输入、物理单位、算法来源和显示约定，便于复现实验。
    metadata = dict(parameters=asdict(data["scene"]), input_rgb=data["input_rgb"].tolist(),
        method="lecture 4 pp.37-42: C a = M RGB, basis = CIE x_bar,y_bar,z_bar",
        material="white Lambertian, kd(lambda)=1, RGB kd=(1,1,1)",
        units={"spectral_A":"W/(m^2 sr nm)", "radiance_A":"W/(m^2 sr)",
               "luminance_A":"cd/m^2 = 683Y", "rgb_A":"absolute signed CIE RGB 1931"},
        comparison=data["comparison"], spectrum_metrics=data["spectrum_metrics"],
        control_points=r["control_points"], statistics=r["statistics"], shared_gain=data["shared_gain"],
        comparison_policy="same white sphere, input I0 scale, textbook Lambert model and shared exposure",
        theory_sources={"reconstruction":"mis_lect04_11.pdf pp.37-42, 3281.pdf printed p.66 Fig.4.6",
                        "lambert":"3281.pdf printed p.47 eq.(3.4.5.1)",
                        "CIE_RGB_TO_XYZ":"3281.pdf printed p.70",
                        "display":"3281.pdf p.77 sRGB matrix, mis_lect05_11.pdf pp.43-46 gamma 2.2"},
        monitor_policy="textbook XYZ->linear sRGB matrix, shared maximum, clip [0,1], gamma 1/2.2, round 255",
        energy_policy="Original SPD has unit integral. Reconstruction is NOT renormalized: XYZ only is constrained.",
        # 实际重建强度为输入 I₀ 乘以重建谱积分；重建谱不强制单位积分。
        reconstructed_intensity_w_sr=[light.intensity_w_sr * metric["integral"]
                                       for light, metric in zip(data["scene"].lights, data["spectrum_metrics"])],
        original_lab3_material="green, retained separately in reference_lab3, not a controlled comparison")
    (directory / "results.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    spectral_figure(data).savefig(directory / "spectra_comparison.png", dpi=150)
    return metadata
