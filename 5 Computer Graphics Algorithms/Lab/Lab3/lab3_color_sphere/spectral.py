"""41 通道光谱、输入表和场景参数，不负责显示颜色。"""
import csv
import io
import json
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path
import numpy as np
from .geometry import Light, Parameters, require, validate

BASE = Path(__file__).resolve().parent
WAVELENGTHS = np.arange(380.0, 781.0, 10.0)


@dataclass(frozen=True)
class ColorTables:
    wavelengths: np.ndarray
    cmf: np.ndarray
    d65: np.ndarray
    weights: np.ndarray
    spectra: dict | None = None
    reflectance: np.ndarray | None = None

    @property
    def weighted_cmf(self):
        return self.cmf * self.weights[:, None]


@lru_cache(maxsize=1)
def load_tables():
    def read(name, columns):
        with (BASE / "data" / name).open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        require(np.array_equal([float(r["wavelength_nm"]) for r in rows], WAVELENGTHS),
                name + ": требуется 380..780 нм с шагом 10 нм")
        values = np.array([[float(r[c]) for c in columns] for r in rows])
        require(np.all(np.isfinite(values)) and np.all(values >= 0), name + ": неверные значения")
        return values
    cmf = read("cie_xyz_1931.csv", ("x_bar", "y_bar", "z_bar"))
    names = ("d65", "red", "blue", "black_body_6500")
    sources = read("light_spectra.csv", names)
    require(np.all(np.any(sources > 0, axis=0)), "Нулевой спектр источника")
    reflectance = read("reflectance.csv", ("reflectance",))[:, 0]
    require(np.all(reflectance <= 1), "Коэффициенты отражения: [0,1]")
    weights = np.full(41, 10.0)
    weights[[0, -1]] = 5.0  # 梯形积分的端点权重，单位 nm。
    return ColorTables(WAVELENGTHS.copy(), cmf, sources[:, 0], weights,
                       dict(zip(names, sources.T)), reflectance)


def normalize_spd(spectrum, tables=None):
    tables = tables or load_tables()
    values = np.asarray(spectrum, float)
    values = values / np.max(values)
    return values / np.dot(values, tables.weights)


def default_parameters(case="white"):
    require(case in ("white", "colored"), "Вариант: white или colored")
    tables = load_tables()
    names = ("d65", "d65") if case == "white" else ("red", "blue")
    lights = tuple(replace(light, spectrum=tuple(tables.spectra[name]))
                   for light, name in zip(Parameters().lights, names))
    return Parameters(lights=lights, reflectance=tuple(tables.reflectance))


def spectra_csv(p):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["wavelength_nm", "reflectance"] + [f"light_{i+1}" for i in range(len(p.lights))])
    writer.writerows([int(w), p.reflectance[j], *[light.spectrum[j] for light in p.lights]]
                     for j, w in enumerate(WAVELENGTHS))
    return stream.getvalue()


def apply_spectra_csv(p, text):
    rows = list(csv.DictReader(io.StringIO(text)))
    require(len(rows) == 41 and np.array_equal([float(r["wavelength_nm"]) for r in rows], WAVELENGTHS),
            "Требуется 41 строка: 380,390,...,780 нм")
    lights = tuple(replace(light, spectrum=tuple(float(r[f"light_{i+1}"]) for r in rows))
                   for i, light in enumerate(p.lights))
    scene = replace(p, reflectance=tuple(float(r["reflectance"]) for r in rows), lights=lights)
    validate(scene)
    return scene


def parameters_from_dict(data):
    require(isinstance(data, dict), "JSON сцены должен быть объектом")
    data = dict(data.get("parameters", data))
    try:
        if "lights" in data:
            require(isinstance(data["lights"], list), "lights должен быть массивом")
            data["lights"] = tuple(Light(**item) for item in data["lights"])
        scene = Parameters(**data)
    except TypeError as error:
        raise ValueError(f"Неверные поля сцены: {error}") from error
    validate(scene)
    return scene


def load_parameters(path):
    return parameters_from_dict(json.loads(Path(path).read_text(encoding="utf-8-sig")))
