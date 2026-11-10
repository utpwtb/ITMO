"""Independent audit. Writes only under review_tests; never patches production code.

Run with Python 3.12+ and the project requirements. Optional local _deps/_tcl
allow the audit to run with the Codex bundled runtime without changing .venv.
FAIL means a reproduced discrepancy; LIMIT is a documented algorithm limit.
"""
from pathlib import Path
import gc
import hashlib
import json
import os
import sys
import time
import traceback
import warnings
from dataclasses import replace
from unittest.mock import patch
from zipfile import ZipFile
from xml.etree import ElementTree as ET

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
LAB4 = HERE.parent
LAB3 = LAB4.parent / "Lab3"
OUT = HERE / "artifacts"
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(LAB4))
if (HERE / "_deps").exists():
    sys.path.insert(0, str(HERE / "_deps"))
if (HERE / "_tcl").exists():
    os.environ["TCL_LIBRARY"] = str(HERE / "_tcl" / "tcl8.6")
    os.environ["TK_LIBRARY"] = str(HERE / "_tcl" / "tk8.6")
os.environ["MPLCONFIGDIR"] = str(HERE / "_mplconfig")

import numpy as np
from PIL import Image, ImageDraw
from lab4_spectrum.experiment import run, white_scene
from lab4_spectrum.reconstruction import reconstruct
from lab4_spectrum.core.color_conversion import scene_rgb, spectrum_to_rgb, spectrum_to_xyz
from lab4_spectrum.core.geometry import validate, geometry_factors
from lab4_spectrum.core.spectral import load_tables
from lab4_spectrum.core.rendering import radiance_at

RECORDS = []
DETAILS = {}


def record(name, func, category="check"):
    started = time.perf_counter()
    try:
        detail = func()
        status = "PASS"
    except AssertionError as error:
        status, detail = "FAIL", str(error)
    except Exception as error:
        status, detail = "ERROR", traceback.format_exc()
    item = dict(name=name, status=status, category=category, detail=detail,
                seconds=round(time.perf_counter() - started, 4))
    RECORDS.append(item)
    print(f"{status}: {name}", flush=True)


def insist(condition, message):
    assert condition, message


def rejects(func):
    try:
        func()
    except (ValueError, TypeError):
        return "rejected"
    raise AssertionError("Input was accepted")


def production_hashes():
    paths = [*list((LAB4 / "lab4_spectrum").rglob("*")),
             *list((LAB4 / "results").rglob("*")),
             *list((LAB4 / "reference_lab3").rglob("*")),
             *list((LAB4 / "report").rglob("*")),
             LAB4 / "README.md", LAB4 / "requirements.txt"]
    return {str(p.relative_to(LAB4)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file() and "__pycache__" not in p.parts}


def extract_assignments():
    for lab in (LAB3, LAB4):
        doc = lab / f"АКГ_лр{3 if lab == LAB3 else 4}.docx"
        root = ET.fromstring(ZipFile(doc).read("word/document.xml"))
        text = "\n".join("".join(n.text or "" for n in p.iter()
                                  if n.tag.rsplit("}", 1)[-1] == "t")
                         for p in root.findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"))
        (OUT / f"{lab.name}_assignment.txt").write_text(text, encoding="utf-8")


def rgb_inputs():
    tables = load_tables()
    d65 = scene_rgb(white_scene())[1][0]
    for label, value in [
        ("zero", [0, 0, 0]), ("NaN", [np.nan, 1, 1]),
        ("positive infinity", [np.inf, 1, 1]), ("negative infinity", [1, -np.inf, 1]),
        ("empty", []), ("two components", [1, 1]), ("four components", [1, 1, 1, 1]),
        ("nested shape", [[1, 1, 1]]), ("nonnumeric", ["red", 1, 1]),
        ("all negative", [-1, -1, -1]),
    ]:
        record("CIE RGB rejects " + label, lambda v=value: rejects(lambda: reconstruct(v)), "RGB")

    def check_rgb(rgb):
        result = reconstruct(rgb)
        insist(result.shape == (41,) and np.isfinite(result).all() and (result >= 0).all(),
                "Spectrum is not 41 finite nonnegative samples")
        error = np.max(np.abs(spectrum_to_rgb(result) - rgb))
        insist(np.allclose(spectrum_to_rgb(result), rgb, rtol=1e-11, atol=0), f"RGB round-trip error={error}")
        return dict(rgb=np.asarray(rgb).tolist(), max_error=float(error), minimum=float(result.min()))

    record("CIE RGB D65 round trip", lambda: check_rgb(d65), "RGB")
    for scale in (1e-200, 1e-170, 1e-160, 1e-12, 1e12, 1e150, 1e200, 1e300):
        def check_scale(s=scale):
            try:
                return check_rgb(d65*s)
            except ValueError as e:
                raise AssertionError(f"Finite nonzero RGB at scale {s} rejected: {e}")
        record(f"CIE RGB linear scaling {scale:g}", check_scale, "RGB")

    # Each basis curve is already a nonnegative spectrum in the chosen span.
    # z_bar has a negative CIE R component: signed CIE RGB must remain legal.
    for index in range(3):
        record(f"CIE RGB exact nonnegative basis {index}",
               lambda i=index: check_rgb(spectrum_to_rgb(tables.cmf[:, i])), "RGB")
    signed_spd = tables.cmf @ np.array([0.01, 0.01, 1.0])
    record("CIE RGB signed physically valid interior spectrum",
           lambda: check_rgb(spectrum_to_rgb(signed_spd)), "RGB")
    rng = np.random.default_rng(104)
    def seeded_roundtrips():
        worst = 0.0
        for _ in range(250):
            spectrum = tables.cmf @ np.exp(rng.uniform(-4, 4, 3))
            rgb = spectrum_to_rgb(spectrum)
            rebuilt = reconstruct(rgb)
            worst = max(worst, float(np.max(np.abs(spectrum_to_rgb(rebuilt)-rgb))))
            insist(np.allclose(rebuilt, spectrum, rtol=1e-10, atol=1e-10), "Known nonnegative basis combination not recovered")
        return dict(samples=250, worst_absolute_rgb_error=worst)
    record("CIE RGB 250 seeded spectra in reconstruction span", seeded_roundtrips, "RGB")
    # Physical colors can be outside the nonnegative cone of this fixed basis.
    for label, rgb in [("CIE red primary", [1, 0, 0]), ("CIE green primary", [0, 1, 0]),
                       ("CIE blue primary", [0, 0, 1]),
                       ("520 nm sampled spectrum", spectrum_to_rgb(np.eye(41)[14]))]:
        try:
            reconstruct(rgb)
            status = "accepted"
        except ValueError as e:
            status = str(e)
        RECORDS.append(dict(name=label, status="LIMIT", category="RGB", detail=status))
    record("CIE RGB 0-255-like [255,255,255] is an absolute color",
           lambda: check_rgb(np.array([255., 255., 255.])), "RGB")
    def no_boolean():
        return rejects(lambda: reconstruct([True, True, True]))
    record("CIE RGB API rejects booleans", no_boolean, "RGB API")
    def no_complex():
        return rejects(lambda: reconstruct(np.array([1+2j, 1+0j, 1+0j])))
    record("CIE RGB API rejects complex ndarray", no_complex, "RGB API")


def main():
    before = production_hashes()
    extract_assignments()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        rgb_inputs()
    DETAILS["rgb_warnings"] = [str(w.message) for w in caught]
    base = replace(white_scene(), width_px=200)
    for label, changes in [
        ("width below range", dict(width_mm=99)), ("width above range", dict(width_mm=10001)),
        ("height below range", dict(height_mm=99)), ("NaN geometry", dict(radius_mm=np.nan)),
        ("negative radius", dict(radius_mm=-1)), ("zero radius", dict(radius_mm=0)),
        ("resolution below", dict(width_px=199)), ("resolution above", dict(width_px=801)),
        ("fractional resolution", dict(width_px=200.5)), ("bool resolution", dict(width_px=True)),
        ("zero viewing vector", dict(direction=(0, 0, 0))),
        ("sphere outside field", dict(center_x_mm=1000)),
        ("observer inside sphere", dict(observer_z_mm=600)),
        ("sphere behind observer", dict(direction=(0, 0, 1))),
        ("no lights", dict(lights=())),
    ]:
        record("geometry rejects " + label,
               lambda c=changes: rejects(lambda: validate(replace(base, **c))), "geometry")
    for label, changes in [
        ("intensity below", dict(intensity_w_sr=0.009)),
        ("intensity above", dict(intensity_w_sr=10001)),
        ("zero axis", dict(axis=(0, 0, 0))), ("NaN position", dict(x_mm=np.nan)),
        ("inside sphere", dict(x_mm=0, y_mm=0, z_mm=600)),
    ]:
        record("light rejects " + label, lambda c=changes: rejects(lambda: validate(
            replace(base, lights=(replace(base.lights[0], **c),)))), "geometry")
    for value in (0.01, 10000):
        record(f"light accepts I0 boundary {value}",
               lambda v=value: validate(replace(base, lights=(replace(base.lights[0], intensity_w_sr=v),))), "geometry")
    record("material rejects nonwhite in Lab4", lambda: rejects(lambda: run(replace(base, reflectance=(0.5,)*41))), "scene")
    record("RGB count must match light count", lambda: rejects(lambda: run(base, [[1, 1, 1]])), "RGB")
    record("second light invalid RGB is rejected", lambda: rejects(lambda: run(base, [scene_rgb(base)[1][0], [np.nan, 1, 1]])), "RGB")

    data = run(base)
    for scale in (1e-150, 1e100, 1e200, 1e306, 1e308):
        def finite_render(s=scale):
            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter("always")
                try:
                    rendered = run(base, scene_rgb(base)[1] * s)
                except ValueError as e:
                    return dict(rejected_safely=str(e))
            bad = [k for k in ("spectral", "xyz", "rgb1", "radiance", "luminance1")
                   if not np.isfinite(rendered["result"][k]).all()]
            bad_metrics = [key for key,value in rendered["comparison"]["image_2"].items() if not np.isfinite(value)]
            all_warnings = sorted(set(str(w.message) for w in captured))
            DETAILS[f"render_scale_{s:g}"] = dict(nonfinite_arrays=bad, nonfinite_metrics=bad_metrics,
                warnings=all_warnings, shared_gain=rendered["shared_gain"],
                displayed_max=int(rendered["images"][0].max()))
            insist(not bad and not bad_metrics,
                   f"Finite RGB scale {s:g} returned nonfinite results: arrays={bad}, metrics={bad_metrics}; warnings={all_warnings}")
            return DETAILS[f"render_scale_{s:g}"]
        record(f"CIE RGB full rendering finite scale {scale:g}", finite_render, "RGB rendering")
    def default_equivalence():
        insist(np.array_equal(data["images"][0], data["images"][1]) and np.array_equal(data["images"][1], data["images"][2]), "Default white-sphere image mismatch")
        insist(max(m["rgb_max_error"] for m in data["spectrum_metrics"]) < 1e-12, "RGB not preserved")
        return data["spectrum_metrics"]
    record("default metamer preserves RGB and display", default_equivalence, "rendering")
    def analytic():
        l = base.lights[0]
        point = base.center() + np.array([0, 0, base.radius_mm])
        delta = l.position()-point
        direction = delta / np.linalg.norm(delta)
        factor = l.intensity_w_sr * max(-direction@np.array(l.axis), 0) * max(direction[2], 0) / (np.pi * np.sum((delta/1000)**2))
        actual = geometry_factors(point, replace(base, lights=(l,)))[0]
        insist(np.isclose(actual, factor, rtol=1e-13), "Independent Lambertian factor mismatch")
        return dict(expected=float(factor), actual=float(actual))
    record("analytical Lambertian factor and mm to m", analytic, "rendering")
    def absolute_values():
        r = data["result"]
        insist(r["spectral"].dtype == np.float64, "Spectral image not float64")
        insist(np.allclose(r["spectral"]@load_tables().weights, r["radiance"]), "Radiance integral mismatch")
        insist(np.allclose(683*r["xyz"][...,1], r["luminance1"]), "Luminance mismatch")
        insist(len(r["control_points"]) == 3 and all(p["visible"] for p in r["control_points"]), "Missing/hidden control points")
    record("spectral float64 units and three visible points", absolute_values, "rendering")

    rgb = scene_rgb(base)[1]
    rgb[0] *= 2
    edited = run(base, rgb)
    def edited_direct():
        # White material: direct input-RGB path is exactly geometry_factors @ input_rgb.
        point = np.array([[p[k] for k in ("x_mm", "y_mm", "z_mm")]
                          for p in edited["result"]["control_points"]])
        direct = geometry_factors(point, base) @ rgb
        original = radiance_at(point, base)["rgb2"]
        actual = np.array([[p["rgb1_"+c] for c in "RGB"] for p in edited["result"]["control_points"]])
        reconstruction_error = float(np.max(np.abs(direct-actual)))
        insist(np.allclose(actual,direct,rtol=1e-12,atol=1e-12), "Reconstruction does not preserve edited RGB")
        mask = edited["result"]["mask"]
        err = float(np.max(np.abs(edited["result"]["rgb1"][mask] - data["result"]["rgb1"][mask])))
        DETAILS["edited_rgb"] = dict(input_rgb=rgb.tolist(), expected_direct_at_points=direct.tolist(),
            image2_original_at_points=original.tolist(), max_absolute_change=err,
            reconstruction_matches_edited_input_max_error=reconstruction_error,
            reported_comparison=edited["comparison"])
        insist(np.allclose(direct, original, rtol=1e-11, atol=1e-12),
               f"image_2 still uses original-spectrum RGB after input edit; max point error={np.max(np.abs(direct-original)):.8g}")
    record("controlled RGB comparison uses same input as reconstruction", edited_direct, "comparison design")

    # Verify the reported baseline independently at the exact default size.
    original_files = [LAB3 / "lab3_color_sphere/results/white" / f"image_{i}.png" for i in (1,2)]
    def archive_integrity():
        for i, original in enumerate(original_files, 1):
            for p in (LAB4 / f"reference_lab3/image_{i}.png", LAB4 / f"lab4_spectrum/assets/lab3_image_{i}.png"):
                insist(p.read_bytes() == original.read_bytes(), f"Archive differs: {p}")
    record("archived Lab3 images are byte-identical originals", archive_integrity, "comparison")
    default = run(white_scene())
    def original_comparison():
        metrics = []
        for i, p in enumerate(original_files, 1):
            image = np.array(Image.open(p).convert("RGB"))
            current = default["images"][i]
            delta = current.astype(float)-image.astype(float)
            metrics.append(dict(image=i, mae=float(np.abs(delta).mean()), maximum=float(np.abs(delta).max()),
                lab3_channel_spread=int(np.ptp(image.astype(int),axis=-1).max()),
                lab4_channel_spread=int(np.ptp(current.astype(int),axis=-1).max())))
        DETAILS["original_comparison"] = metrics
        insist(all(m["maximum"] == 0 for m in metrics), f"Recomputed image_1/2 differ from actual Lab3 PNGs: {metrics}")
    record("comparison uses original Lab3 PNGs at same resolution", original_comparison, "comparison")
    def saved_default():
        for i, name in enumerate(("image_A", "image_1", "image_2")):
            insist(np.array_equal(default["images"][i], np.asarray(Image.open(LAB4 / f"results/{name}.png"))), f"Stored {name} stale")
    record("stored 600x600 images reproduce current implementation", saved_default, "files")
    def upper_resolution():
        upper = run(replace(base,width_px=800))
        insist(upper["result"]["spectral"].shape==(800,800,41), "Wrong 800px spectral shape")
        insist(all(i.shape==(800,800,3) for i in upper["images"]), "Wrong 800px display shape")
        return dict(visible_pixels=upper["result"]["statistics"]["visible_pixel_count"])
    sheet = Image.new("RGB", (900, 650), "white")
    draw = ImageDraw.Draw(sheet)
    views = [("Lab4 A (default)", default["images"][0]), ("Lab4 1 (recomputed)", default["images"][1]),
             ("Lab4 2 (recomputed)", default["images"][2]), ("Actual Lab3 image_1", np.array(Image.open(original_files[0]))),
             ("Actual Lab3 image_2", np.array(Image.open(original_files[1]))), ("Lab4 A (L1 RGB x2)", edited["images"][0])]
    for i, (label, image) in enumerate(views):
        x, y = (i%3)*300, (i//3)*325
        draw.text((x+8, y+5), label, fill="black")
        sheet.paste(Image.fromarray(image).resize((300,300)), (x,y+25))
    sheet.save(OUT / "comparison_contact_sheet.png")
    del default
    gc.collect()
    record("upper resolution 800x800 end-to-end", upper_resolution, "rendering")

    try:
        from lab4_spectrum.output import save
        from lab4_spectrum.gui import App
        from lab4_spectrum.visualization import comparison_figure, scene_figure
        def export():
            target = OUT / "export_200"
            metadata = save(data, target)
            expected = ["image_A.png", "image_1.png", "image_2.png", "absolute_data.npz", "spectra_comparison.csv",
                        "spectra_comparison.png", "three_points.csv", "results.json"]
            insist(all((target/n).is_file() for n in expected), "Export missing files")
            with np.load(target / "absolute_data.npz") as loaded:
                insist(np.array_equal(loaded["spectral_A"],data["result"]["spectral"]), "NPZ spectral values changed")
            insist(len((target/"spectra_comparison.csv").read_text(encoding="utf-8-sig").splitlines()) == 42, "Not 41 wavelength rows")
            return dict(files=expected, shared_gain=metadata["shared_gain"])
        record("export PNG CSV JSON NPZ with round-trip", export, "export")
        for name, func in [("comparison_figure", comparison_figure), ("scene_figure", scene_figure)]:
            record("visualization API " + name, lambda f=func: f(data).savefig(OUT / (f.__name__ + ".png")), "unused API")
        gui_test(App, base, data)
    except Exception:
        RECORDS.append(dict(name="GUI/export dependency setup", status="ERROR", category="environment", detail=traceback.format_exc()))

    record("existing delivery contains absolute_data.npz",
           lambda: insist((LAB4/"results/absolute_data.npz").is_file(), "README claims NPZ, but results/absolute_data.npz is absent"), "files")
    record("production files unchanged", lambda: insist(before == production_hashes(), "Production hash changed"), "isolation")
    (OUT/"production_hashes.json").write_text(json.dumps(before, indent=2, ensure_ascii=False),encoding="utf-8")
    counts = {s:sum(r["status"]==s for r in RECORDS) for s in ("PASS","FAIL","ERROR","LIMIT")}
    report = dict(python=sys.version, numpy=np.__version__, counts=counts, tests=RECORDS, details=DETAILS)
    (OUT/"audit_results.json").write_text(json.dumps(report, indent=2, ensure_ascii=False,default=str),encoding="utf-8")
    print(json.dumps(counts),flush=True)
    return int(counts["FAIL"]>0 or counts["ERROR"]>0)


def gui_test(App, base, data):
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    messages = []
    errors = []
    root.report_callback_exception = lambda *args: errors.append(str(args))
    app = App(root)
    try:
        with patch("lab4_spectrum.gui.messagebox.showerror", side_effect=lambda *a,**k: messages.append(a)), \
             patch("lab4_spectrum.gui.filedialog.askdirectory", return_value=str(OUT/"gui_export")):
            app.fields["width_px"].set("200")
            for channel in "RGB":
                for text in ("", "abc", "nan", "inf", "-inf", "1e10000"):
                    old = app.light_fields[channel].get()
                    app.light_fields[channel].set(text)
                    record(f"GUI CIE {channel} rejects " + repr(text), lambda: rejects(app.commit_light), "GUI RGB")
                    app.light_fields[channel].set(old)
            record("GUI add/delete light", lambda: gui_light_list(app), "GUI")
            # Compute through the actual worker queue and poll loop.
            app.compute()
            deadline = time.perf_counter()+30
            while app.busy and time.perf_counter()<deadline:
                root.update()
                time.sleep(.01)
            record("GUI asynchronous calculation", lambda: insist(app.data is not None and not app.busy and not errors and not messages,
                   f"busy={app.busy}, callbacks={errors}, dialogs={messages}"), "GUI")
            if app.data is not None:
                record("GUI 41 spectral rows", lambda: insist(len(app.table.get_children())==41,"Wrong table size"), "GUI")
                record("GUI export result", lambda: app.export(), "GUI")
                def original_visible():
                    titles = [ax.get_title() for ax in app.plot_canvases[0].figure.axes]
                    DETAILS["gui_image_titles"] = titles
                    arrays = [np.asarray(image.get_array()) for canvas in app.plot_canvases
                              for ax in canvas.figure.axes for image in ax.images]
                    originals = [np.asarray(Image.open(LAB4/f"reference_lab3/image_{i}.png")) for i in (1,2)]
                    insist(all(any(np.array_equal(old,image) for image in arrays) for old in originals),
                           f"Original Lab3 pixels absent; GUI image titles: {titles}")
                record("GUI includes actual Lab3 images", original_visible, "GUI")
                # Run one edited-CIE-RGB calculation in the real GUI.
                old = float(app.light_fields["R"].get())
                app.light_fields["R"].set(str(old*1.1))
                app.compute()
                deadline = time.perf_counter()+30
                while app.busy and time.perf_counter()<deadline:
                    root.update()
                    time.sleep(.01)
                record("GUI computes edited CIE RGB", lambda: insist(not app.busy and not messages and not errors,
                       f"dialogs={messages}, callbacks={errors}"), "GUI RGB")
                signed = spectrum_to_rgb(load_tables().cmf @ np.array([0.01,0.01,1.0])) * .001
                for channel, value in zip("RGB", signed):
                    app.light_fields[channel].set(str(value))
                app.compute()
                deadline = time.perf_counter()+30
                while app.busy and time.perf_counter()<deadline:
                    root.update()
                    time.sleep(.01)
                record("GUI computes physically valid negative CIE R", lambda: insist(
                    not app.busy and not messages and not errors and app.data["input_rgb"][app.selected,0] < 0,
                    f"dialogs={messages}, callbacks={errors}"), "GUI RGB")
                # Invalid input must be handled in the worker and restore the buttons.
                app.light_fields["R"].set("-1")
                app.compute()
                deadline = time.perf_counter()+30
                while app.busy and time.perf_counter()<deadline:
                    root.update()
                    time.sleep(.01)
                record("GUI handles reconstruction rejection and restores controls", lambda: insist(
                    not app.busy and len(messages)>0 and str(app.compute_button["state"])=="normal" and not errors,
                    f"busy={app.busy}, dialogs={messages}, callbacks={errors}"), "GUI RGB")
    finally:
        app.after_cancel(app.poll_id)
        root.destroy()


def gui_light_list(app):
    n = len(app.lights)
    app.add_light()
    insist(len(app.lights)==n+1 and len(app.colors)==n+1,"Add desynchronized lights/colors")
    app.delete_light()
    insist(len(app.lights)==n and len(app.colors)==n,"Delete desynchronized lights/colors")


if __name__ == "__main__":
    raise SystemExit(main())
