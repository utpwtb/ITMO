# 使用三基谱法，将绝对 CIE RGB 1931 重建为 380～780 nm 的 41 通道光谱。
import numpy as np
from .core.color_conversion import CIE_RGB_TO_XYZ
from .core.spectral import load_tables


# 接收三个有限且不全为零的 CIE RGB 坐标，返回保持其颜色的 41 通道非负光谱。
def reconstruct(rgb):

    # 这里的 RGB 是颜色学坐标，不是图像中 0～255 的显示值。
    rgb = np.asarray(rgb, float)
    if rgb.shape != (3,) or not np.all(np.isfinite(rgb)) or np.linalg.norm(rgb) == 0:
        raise ValueError("RGB: требуются три конечных ненулевых координаты CIE RGB")
    tables = load_tables()
    # 取 x̄、ȳ、z̄ 为三个基谱，basis 的形状为 (41,3)。
    basis = tables.cmf
    # 构造 C[i,k] = Σ w[j]·c̄[j,i]·F[j,k]，把三个基谱系数映射为 XYZ。
    matrix = tables.weighted_cmf.T @ basis
    # 先由 XYZ=M·RGB 得到目标颜色，再解 C·a=M·RGB，避免显式求逆。
    coefficients = np.linalg.solve(matrix, CIE_RGB_TO_XYZ @ rgb)
    # 按 S=F·a 合成光谱；重建只约束颜色，不能再强制归一化能量。
    spectrum = basis @ coefficients

    # 基谱组合可能产生负光谱；直接拒绝，裁剪负值会破坏颜色约束。
    if not np.all(np.isfinite(spectrum)) or np.any(spectrum < 0) or not np.any(spectrum > 0):
        raise ValueError("Выбранный базис XYZ даёт отрицательный или нулевой спектр для этого RGB")
    return spectrum
