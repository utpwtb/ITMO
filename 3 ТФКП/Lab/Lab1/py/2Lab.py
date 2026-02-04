import numpy as np
import matplotlib.pyplot as plt

E = np.e

def sample_area(e=E, n_theta=1200, n_r=900, r_max=5_000.0):
    theta = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    r = e * np.exp(np.linspace(np.log(1.0001), np.log(r_max / e), n_r))
    R, T = np.meshgrid(r, theta, indexing="ij")
    return (R * np.exp(1j * T)).ravel()


def sample_boundary(e=E, n=2400):
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False) + 1e-4
    return e * np.exp(1j * theta)


def step1(z):
    return z / E


def step2(z1):
    return 1.0 / z1


def step3(z2):
    return 1j * (1 + z2) / (1 - z2)


def step4(z3):
    root = np.sqrt(z3 * z3 - 1)
    z4a = z3 + root
    z4b = z3 - root
    return np.where(np.abs(z4a) >= np.abs(z4b), z4a, z4b)


def step5(z4):
    return 1 + z4


def step6(z5):
    return np.sqrt(z5)


def transform_chain(z):
    z1 = step1(z)
    z2 = step2(z1)
    z3 = step3(z2)
    z4 = step4(z3)
    z5 = step5(z4)
    w = step6(z5)
    return [z, z1, z2, z3, z4, z5, w]


def build_chain(samples, pole_tol=1e-8):
    chain = transform_chain(samples)
    clean_chain = []
    for stage in chain:
        m = np.isfinite(stage.real) & np.isfinite(stage.imag)
        clean_chain.append(stage[m])
    return clean_chain


area_chain = build_chain(sample_area())
boundary_chain = build_chain(sample_boundary())

titles = [
    r"$D_1:\ |z|>e$",
    r"$z_1 = z/e$",
    r"$z_2 = 1/z_1$",
    r"$z_3 = i\frac{1+z_2}{1-z_2}$",
    r"$z_4 = z_3 + \sqrt{z_3^2-1}$",
    r"$z_5 = 1 + z_4$",
    r"$w = \sqrt{z_5}$ (D2)",
]

def plot_stage(ax, area_pts, boundary_pts, title):
    ax.scatter(area_pts.real, area_pts.imag, s=0.1, alpha=0.35, color="#3B82F6")
    ax.plot(boundary_pts.real, boundary_pts.imag, color="white", linewidth=0.8, alpha=1.0)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_aspect("equal", "box")
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_title(title)

for area_pts, boundary_pts, title in zip(area_chain, boundary_chain, titles):
    fig, ax = plt.subplots(figsize=(5, 5))
    plot_stage(ax, area_pts, boundary_pts, title)
    plt.tight_layout()

plt.show()