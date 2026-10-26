"""Spectrum → XYZ → CIE RGB，显示时再转换为 sRGB。"""
import numpy as np
from .spectral import load_tables, normalize_spd

XYZ_TO_CIE_RGB = np.array([[2.36461, -.89654, -.46807],
                          [-.51517, 1.42641, .08876], [.00520, -.01441, 1.00920]])
# 原题两矩阵尺度不一致，保留指定逆矩阵，反向由数值求逆保证自洽。
CIE_RGB_TO_XYZ = np.linalg.inv(XYZ_TO_CIE_RGB)
XYZ_TO_LINEAR_SRGB = np.array([[3.2406, -1.5372, -.4986],
                              [-.9689, 1.8758, .0415], [.0557, -.2040, 1.0570]])
LINEAR_SRGB_TO_XYZ = np.linalg.inv(XYZ_TO_LINEAR_SRGB)


def spectrum_to_xyz(spectrum, tables=None):
    return np.asarray(spectrum) @ (tables or load_tables()).weighted_cmf


def spectrum_to_rgb(spectrum, tables=None):
    return spectrum_to_xyz(spectrum, tables) @ XYZ_TO_CIE_RGB.T


def scene_rgb(p, tables=None):
    tables = tables or load_tables()
    white = spectrum_to_rgb(tables.d65, tables)
    if np.any(np.abs(white) < 1e-12):
        raise ValueError("Нулевой канал эталонного D65")
    kd = spectrum_to_rgb(tables.d65 * np.asarray(p.reflectance), tables) / white
    lights = [spectrum_to_rgb(normalize_spd(light.spectrum, tables), tables) for light in p.lights]
    return kd, np.array(lights)


def srgb_encode(linear):
    v = np.clip(np.asarray(linear, float), 0, 1)
    return np.where(v <= .0031308, 12.92 * v, 1.055 * v ** (1 / 2.4) - .055)


def srgb_decode(encoded):
    v = np.clip(np.asarray(encoded, float), 0, 1)
    return np.where(v <= .04045, v / 12.92, ((v + .055) / 1.055) ** 2.4)


def display_images(rgb1, rgb2, mask):
    linear = [(rgb @ CIE_RGB_TO_XYZ.T) @ XYZ_TO_LINEAR_SRGB.T for rgb in (rgb1, rgb2)]
    maximum = max(0.0, *(float(v[mask].max()) for v in linear))
    gain = 1 / maximum if maximum > 0 else 0.0
    images, grays, clipping = [], [], []
    for value in linear:
        scaled = value * gain
        clipping.append(int(np.count_nonzero(np.any((scaled < 0) | (scaled > 1), axis=-1) & mask)))
        image = np.rint(255 * srgb_encode(scaled)).astype(np.uint8)
        image[~mask] = 0
        # 从实际得到的 8 位图反解线性值，再计算灰度。
        gray = np.rint(255 * srgb_encode(srgb_decode(image / 255) @ LINEAR_SRGB_TO_XYZ[1])).astype(np.uint8)
        gray[~mask] = 0
        images.append(image)
        grays.append(gray)
    return images, grays, dict(shared_linear_maximum=maximum, shared_gain=gain,
                              gamut_clipped_pixels_1=clipping[0], gamut_clipped_pixels_2=clipping[1])
