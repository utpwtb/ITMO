# 提供光谱、XYZ、CIE RGB 1931 与显示用 sRGB 之间的转换，物理计算使用线性浮点数。
import numpy as np
from .spectral import load_tables


# CIE RGB→XYZ 矩阵，与显示用 sRGB 矩阵属于不同颜色空间。
CIE_RGB_TO_XYZ = np.array([[.49, .31, .20],
                          [.17697, .81240, .01063], [0, .01, .99]])
# 由同一矩阵求逆实现 XYZ→CIE RGB；CIE RGB 坐标允许有符号分量。
XYZ_TO_CIE_RGB = np.linalg.inv(CIE_RGB_TO_XYZ)
# 将 XYZ 转为线性 sRGB，gamma 编码留到最后显示时进行。
XYZ_TO_LINEAR_SRGB = np.array([[3.2406, -1.5372, -.4986],
                              [-.9689, 1.8758, .0415], [.0557, -.2040, 1.0570]])


# 将最后一维的 41 通道光谱按颜色匹配函数积分，得到 XYZ。
def spectrum_to_xyz(spectrum, tables=None):
    # 离散积分 XYZ[i]=Σ S[j]·c̄[j,i]·w[j]，积分权重已并入 weighted_cmf。
    return np.asarray(spectrum) @ (tables or load_tables()).weighted_cmf


# 将光谱积分为 XYZ，再转换为绝对 CIE RGB 1931 坐标。
def spectrum_to_rgb(spectrum, tables=None):
    return spectrum_to_xyz(spectrum, tables) @ XYZ_TO_CIE_RGB.T


# 计算材料相对 D65 的 RGB 反射系数和每个光源的 CIE RGB。
def scene_rgb(p, tables=None):
    tables = tables or load_tables()
    white = spectrum_to_rgb(tables.d65, tables)
    if np.any(np.abs(white) < 1e-12):
        raise ValueError("Нулевой канал эталонного D65")
    # 以 D65 照射材料前后的 RGB 比值定义反射系数；白球的比值为 1。
    kd = spectrum_to_rgb(tables.d65 * np.asarray(p.reflectance), tables) / white
    lights = [spectrum_to_rgb(light.spectrum, tables) for light in p.lights]
    return kd, np.array(lights)


# 将线性显示值裁剪到 [0,1]，按 gamma=2.2 编码。
def monitor_encode(linear):

    # 采用讲义的 1/2.2 次幂显示近似；裁剪只用于显示，不改变重建谱。
    return np.clip(np.asarray(linear, float), 0, 1) ** (1 / 2.2)
