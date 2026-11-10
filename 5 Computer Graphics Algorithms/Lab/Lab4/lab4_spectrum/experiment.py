# 组织白球实验：重建各光源光谱，计算原始与重建场景，生成统一显示的三图和误差。
from dataclasses import replace
import numpy as np
from .core.color_conversion import (CIE_RGB_TO_XYZ, XYZ_TO_LINEAR_SRGB,
                                    scene_rgb, spectrum_to_rgb, monitor_encode)
from .core.geometry import validate
from .core.rendering import calculate
from .core.spectral import default_parameters, load_tables, normalize_spd
from .reconstruction import reconstruct


# 创建使用归一化 D65 光谱、白色漫反射球和默认相机及光源的场景。
def white_scene():
    return default_parameters()


# 接收可选场景和各光源的 CIE RGB，返回渲染数据、三张对照图和光谱误差。
def run(scene=None, light_rgb=None):
    scene = white_scene() if scene is None else scene
    validate(scene)
    # 实验限定白色朗伯球，所有波长的漫反射系数均为 1。
    if not np.allclose(scene.reflectance, 1, rtol=0, atol=1e-12):
        raise ValueError("ЛР4: требуется белый ламбертовский отражатель, kd=1")

    # 原始光谱积分归一到 1，I₀ 保留为原场景的强度尺度；重建谱不再归一化。
    scene = replace(scene, lights=tuple(replace(light, spectrum=tuple(normalize_spd(light.spectrum)))
                                       for light in scene.lights))
    t = load_tables()
    # 未传入光源 RGB 时，从原始光谱计算输入颜色；每个光源对应三个坐标。
    _, original_rgb = scene_rgb(scene)
    rgb = original_rgb if light_rgb is None else np.asarray(light_rgb, float)
    if rgb.shape != (len(scene.lights), 3):
        raise ValueError("Требуется RGB для каждого источника")
    # 重建函数只接收 RGB；再以重建谱建立几何参数相同的场景。
    recovered = np.array([reconstruct(v) for v in rgb])
    rebuilt = replace(scene, lights=tuple(replace(light, spectrum=tuple(s))
                      for light, s in zip(scene.lights, recovered)))
    # 分别渲染原场景与重建场景，用相同白球和照明公式进行比较。
    reference = calculate(scene)
    result = calculate(rebuilt)
    mask = result["mask"]
    # 三条路径依次为：重建谱渲染、原谱渲染、原场景直接 RGB 计算。
    arrays = [result["rgb1"], reference["rgb1"], reference["rgb2"]]
    # 绝对 CIE RGB 先转 XYZ，再转线性 sRGB，之后才进行显示编码。
    linear = [v @ CIE_RGB_TO_XYZ.T @ XYZ_TO_LINEAR_SRGB.T for v in arrays]
    # 三图共用球面有效像素的最大通道设置增益，避免独立缩放掩盖差异。
    maximum = max(float(v[mask].max()) for v in linear)
    gain = 1 / maximum if maximum > 0 else 0
    # 最后才进行 gamma 编码和 8 位量化；绝对计算数组仍为浮点数。
    images = [np.rint(255 * monitor_encode(v * gain)).astype(np.uint8) for v in linear]
    original_spd = np.array([normalize_spd(l.spectrum) for l in scene.lights])
    comparison = {}
    # 仅比较球体 mask 内的绝对 RGB 和显示像素，排除背景。
    for label, value, image in zip(("image_1", "image_2"), arrays[1:], images[1:]):
        difference = images[0][mask].astype(float) - image[mask].astype(float)
        comparison[label] = dict(rgb_absolute_rmse=float(np.sqrt(np.mean(
            (arrays[0][mask] - value[mask]) ** 2))), monitor_mae=float(np.abs(difference).mean()),
            monitor_max=int(np.abs(difference).max()))
    # 记录光谱误差、RGB 回算误差和积分；同色光谱的积分可以不同。
    spectrum_metrics = [dict(rmse=float(np.sqrt(np.mean((s-r)**2))),
                            max_error=float(np.abs(s-r).max()),
                            rgb_max_error=float(np.abs(spectrum_to_rgb(s)-c).max()),
                            integral=float(s @ t.weights))
                        for s, r, c in zip(recovered, original_spd, rgb)]
    return dict(scene=scene, result=result, images=images, original_spd=original_spd,
                recovered=recovered, input_rgb=rgb, spectrum_metrics=spectrum_metrics,
                comparison=comparison, shared_gain=gain)
