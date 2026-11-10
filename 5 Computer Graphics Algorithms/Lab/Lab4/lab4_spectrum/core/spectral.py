# 管理 380～780 nm、间隔 10 nm 的 41 通道光谱，提供颜色表、积分权重与默认场景。
# 从本包 data 目录读取 CIE 1931 匹配函数及 D65 光谱，路径不依赖当前工作目录。
import csv
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path
import numpy as np
from .geometry import Parameters, require

BASE = Path(__file__).resolve().parent
# 网格包含两端点，共 41 个波长，所有光谱必须使用相同采样顺序。
WAVELENGTHS = np.arange(380.0, 781.0, 10.0)


# 保存波长、XYZ 颜色匹配函数、D65 光谱和梯形积分权重。
@dataclass(frozen=True)
class ColorTables:
    wavelengths: np.ndarray
    cmf: np.ndarray
    d65: np.ndarray
    weights: np.ndarray

    # 将波长积分权重乘入 XYZ 匹配函数，供矩阵乘法完成积分。
    @property
    def weighted_cmf(self):
        # weights[:,None] 将 (41,) 变为 (41,1)，给三个匹配函数施加相同积分权重。
        return self.cmf * self.weights[:, None]


# 读取并校验光谱 CSV，构造颜色表并缓存，避免重复读取磁盘。
@lru_cache(maxsize=1)
def load_tables():
    # 读取指定 CSV 数值列，检查波长网格、有限性和非负性。
    def read(name, columns):
        with (BASE / "data" / name).open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        # 数据必须恰好对应 380、390、…、780 nm，不隐式插值缺失波长。
        require(np.array_equal([float(r["wavelength_nm"]) for r in rows], WAVELENGTHS),
                name + ": требуется 380..780 нм с шагом 10 нм")
        values = np.array([[float(r[c]) for c in columns] for r in rows])
        require(np.all(np.isfinite(values)) and np.all(values >= 0), name + ": неверные значения")
        return values
    cmf = read("cie_xyz_1931.csv", ("x_bar", "y_bar", "z_bar"))
    sources = read("light_spectra.csv", ("d65",))
    require(np.any(sources > 0), "Нулевой спектр источника")
    # 梯形积分的内部样本权重为步长 10 nm，两端减半为 5 nm。
    weights = np.full(41, 10.0)
    weights[[0, -1]] = 5.0
    return ColorTables(WAVELENGTHS.copy(), cmf, sources[:, 0], weights)


# 按梯形积分将原始非负光谱归一为单位面积，分离光谱形状与强度。
def normalize_spd(spectrum, tables=None):
    tables = tables or load_tables()
    values = np.asarray(spectrum, float)
    # 先按峰值缩放改善数值尺度，再除以加权积分，使 Σ S[j]·w[j]=1。
    values = values / np.max(values)
    return values / np.dot(values, tables.weights)


# 为所有默认光源设置归一化 D65 光谱，返回白球实验初始场景。
def default_parameters():
    # 该归一化用于默认原始光谱，RGB 重建后的光谱不调用它。
    spectrum = tuple(normalize_spd(load_tables().d65))
    lights = tuple(replace(light, spectrum=spectrum) for light in Parameters().lights)
    return Parameters(lights=lights)
