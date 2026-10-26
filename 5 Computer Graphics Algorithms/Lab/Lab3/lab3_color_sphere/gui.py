"""Сгруппированные параметры слева и спектральные результаты справа."""
import json
import queue
import threading
import tkinter as tk
from dataclasses import asdict, replace
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .color_conversion import CIE_RGB_TO_XYZ
from .geometry import validate
from .rendering import calculate, save_results
from .spectral import (apply_spectra_csv, default_parameters, load_parameters,
                       load_tables, parameters_from_dict, spectra_csv)


class SphereApp(ttk.Frame):
    """表单与已计算结果分开保存，仅按钮调用数值算法。"""
    SPECTRA = {"D65": "d65", "Красный": "red", "Синий": "blue",
               "Чёрное тело 6500 К": "black_body_6500", "Табличный": None}
    MATERIALS = ("Из таблицы по умолчанию", "Постоянное отражение", "Своя таблица")
    MODELS = {"По рисунку — cos²/π": "reference_diagram", "Закон Ламберта — cos/π": "lambert"}

    def __init__(self, master, initial=None):
        super().__init__(master, padding=8)
        self.pack(fill="both", expand=True)
        master.title("ЛР 3 — Спектральный и RGB расчёт")
        master.geometry("1380x920")
        master.minsize(1000, 680)
        self.tables = load_tables()
        self.variables, self.light_variables = {}, {}
        self.material_kind = tk.StringVar(value=self.MATERIALS[0])
        self.material_constant = tk.StringVar(value="0.5")
        self.light_spectrum = tk.StringVar(value="D65")
        self.model_label = tk.StringVar(value=next(iter(self.MODELS)))
        self.status = tk.StringVar(value="Задайте параметры и нажмите «Рассчитать».")
        self.resolution = tk.StringVar()
        self.results, self.lights = {}, []
        self.selected_light = None
        self.busy = self.updating = self.dirty = self._closed = False
        self._completed = queue.SimpleQueue()
        self._build()
        self.set_scene(initial if initial is not None else default_parameters("white"))
        self._poll_id = self.after(60, self._poll)
        self.bind("<Destroy>", self._destroyed, add="+")

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        panes = ttk.Panedwindow(self, orient="horizontal")
        panes.grid(row=0, column=0, sticky="nsew")
        self.left = left = ttk.Frame(panes, width=390)
        right = ttk.Frame(panes, padding=(8, 0, 0, 0))
        panes.add(left, weight=0)
        panes.add(right, weight=1)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)
        self.input_tabs = ttk.Notebook(left)
        self.input_tabs.grid(row=0, column=0, sticky="nsew")
        scene_tab, advanced = ttk.Frame(self.input_tabs), ttk.Frame(self.input_tabs)
        self.input_tabs.add(scene_tab, text="Параметры сцены")
        self.input_tabs.add(advanced, text="Дополнительно JSON")
        scroll = tk.Canvas(scene_tab, highlightthickness=0, width=380)
        bar = ttk.Scrollbar(scene_tab, orient="vertical", command=scroll.yview)
        scroll.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        scroll.pack(side="left", fill="both", expand=True)
        controls = ttk.Frame(scroll, padding=5)
        window = scroll.create_window((0, 0), window=controls, anchor="nw")
        controls.bind("<Configure>", lambda event: scroll.configure(scrollregion=scroll.bbox("all")))
        scroll.bind("<Configure>", lambda event: scroll.itemconfigure(window, width=event.width))
        self.master.bind("<MouseWheel>", lambda event: scroll.yview_scroll(
            -int(event.delta / 120), "units") if str(event.widget).startswith(str(controls)) else None, add="+")
        geometry = self._group(controls, "Геометрия экрана и сферы")
        for key, label in (("width_mm", "Ширина W, мм"), ("height_mm", "Высота H, мм"),
            ("width_px", "Разрешение Wres"), ("center_x_mm", "Центр xC, мм"),
            ("center_y_mm", "Центр yC, мм"), ("center_z_mm", "Центр zC, мм"), ("radius_mm", "Радиус, мм")):
            self._field(geometry, key, label)
        ttk.Label(geometry, textvariable=self.resolution).grid(
            row=geometry.grid_size()[1], column=0, columnspan=2, sticky="w", pady=3)
        observer = self._group(controls, "Наблюдатель и проекция")
        for key, label in (("observer_z_mm", "Наблюдатель zO, мм"), ("direction_x", "Направление dx"),
            ("direction_y", "Направление dy"), ("direction_z", "Направление dz"),
            ("screen_z_mm", "Экран z, мм"), ("screen_distance_mm", "Расстояние f, мм")):
            self._field(observer, key, label)
        ttk.Label(observer, text="Пустое f: расстояние определяется по z экрана.", wraplength=335).grid(
            row=6, column=0, columnspan=2, sticky="w", pady=3)
        ttk.Button(observer, text="Пример: вид снизу (+Z)", command=lambda: self.guard(self.below)).grid(
            row=7, column=0, columnspan=2, sticky="ew")
        sources = self._group(controls, "Точечные источники света")
        self.lights_tree = ttk.Treeview(sources, columns=("position", "intensity"), height=3, selectmode="browse")
        for key, label, width in (("#0", "Свет", 45), ("position", "Координаты, мм", 175),
                                  ("intensity", "I₀, Вт/ср", 75)):
            self.lights_tree.heading(key, text=label)
            self.lights_tree.column(key, width=width, stretch=key != "#0")
        self.lights_tree.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.lights_tree.bind("<<TreeviewSelect>>", self._select_light)
        self._light_fields(sources, 1, (("x_mm", "xL, мм"), ("y_mm", "yL, мм"), ("z_mm", "zL, мм")))
        self._light_fields(sources, 2, (("intensity_w_sr", "I₀, Вт/ср"),))
        self._light_fields(sources, 3, (("axis_x", "Ось ax"), ("axis_y", "Ось ay"), ("axis_z", "Ось az")))
        ttk.Label(sources, text="Спектр источника").grid(row=4, column=0, sticky="w")
        combo = ttk.Combobox(sources, textvariable=self.light_spectrum, values=list(self.SPECTRA),
                             state="readonly", width=21)
        combo.grid(row=4, column=1, sticky="ew", pady=3)
        combo.bind("<<ComboboxSelected>>", lambda event: self.mark_dirty())
        buttons = ttk.Frame(sources)
        buttons.grid(row=5, column=0, columnspan=2, sticky="ew", pady=3)
        for label, action in (("Добавить", self.add_light), ("Удалить", self.delete_light), ("Применить", self.commit_light)):
            ttk.Button(buttons, text=label, command=lambda fn=action: self.guard(fn)).pack(side="left", expand=True, fill="x")
        material = self._group(controls, "Отражающий спектр сферы")
        combo = ttk.Combobox(material, textvariable=self.material_kind, values=self.MATERIALS, state="readonly")
        combo.grid(row=0, column=0, columnspan=2, sticky="ew")
        combo.bind("<<ComboboxSelected>>", lambda event: self.mark_dirty())
        ttk.Label(material, text="Постоянный kᵈ, 0…1").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(material, textvariable=self.material_constant, width=12).grid(row=1, column=1, sticky="ew")
        self.material_constant.trace_add("write", self.mark_dirty)
        ttk.Button(material, text="Таблица 41 длины волны…", command=lambda: self.guard(self.spectra_dialog)).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=3)
        combo = ttk.Combobox(material, textvariable=self.model_label, values=list(self.MODELS), state="readonly")
        combo.grid(row=3, column=0, columnspan=2, sticky="ew")
        combo.bind("<<ComboboxSelected>>", lambda event: self.mark_dirty())
        ttk.Label(advanced, text="Нажмите «Применить JSON», чтобы перенести изменения в форму.",
                  padding=6, wraplength=345).pack(fill="x")
        self.json_text = self._editor(advanced)
        row = ttk.Frame(advanced, padding=4)
        row.pack(fill="x")
        ttk.Button(row, text="Из формы", command=lambda: self.guard(self.sync_json)).pack(side="left")
        ttk.Button(row, text="Применить JSON", command=lambda: self.guard(self.apply_json)).pack(side="left")
        actions = ttk.Frame(left, padding=(0, 6, 0, 0))
        actions.grid(row=1, column=0, sticky="ew")
        self.action_buttons = []
        for i, (label, action) in enumerate((("Загрузить JSON", self.load_json), ("Сохранить JSON", self.save_json),
                                            ("Рассчитать", self.compute), ("Сохранить результаты", self.save))):
            button = ttk.Button(actions, text=label, command=lambda fn=action: self.guard(fn))
            button.grid(row=i // 2, column=i % 2, sticky="ew", padx=2, pady=2)
            self.action_buttons.append(button)
        for column in (0, 1):
            actions.columnconfigure(column, weight=1)
        self.compute_button = self.action_buttons[2]
        self.progress = ttk.Progressbar(left, mode="indeterminate")
        self.progress.grid(row=2, column=0, sticky="ew", pady=4)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        ttk.Label(right, text="Результаты расчёта", font=("TkDefaultFont", 12, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 7))
        self.result_tabs = ttk.Notebook(right)
        self.result_tabs.grid(row=1, column=0, sticky="nsew")
        frames = [ttk.Frame(self.result_tabs) for _ in range(4)]
        for frame, label in zip(frames, ("Цветные изображения", "Тоны серого", "Спектральные кривые", "Абсолютная яркость")):
            self.result_tabs.add(frame, text=label)
        for name, frame in zip(("rgb", "gray", "spectra"), frames):
            figure = Figure(figsize=(8, 6), dpi=100, layout="constrained")
            canvas = FigureCanvasTkAgg(figure, master=frame)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            setattr(self, name + "_figure", figure)
            setattr(self, name + "_canvas", canvas)
        numbers = frames[3]
        ttk.Label(numbers, text="Точки вычислены непосредственно по формулам.\n"
                  "Lₑ — Вт/(м²·ср), Lᵥ — кд/м². Фон исключён из экстремумов.", padding=8).pack(fill="x")
        columns = ("point", "position", "radiance", "lv1", "lv2")
        self.points_tree = ttk.Treeview(numbers, columns=columns, show="headings", height=9)
        for key, label, width in zip(columns, ("Точка", "Координаты, мм", "Lₑ", "Lᵥ₁", "Lᵥ₂"),
                                     (55, 165, 105, 110, 110)):
            self.points_tree.heading(key, text=label)
            self.points_tree.column(key, width=width, minwidth=45, anchor="center")
        self.points_tree.pack(fill="both", expand=True, padx=8)
        self.numbers_text = tk.Text(numbers, height=11, wrap="word", font=("Consolas", 10))
        self.numbers_text.pack(fill="x", padx=8, pady=8)
        self.numbers_text.configure(state="disabled")
        self.result_tabs.bind("<<NotebookTabChanged>>", lambda event: self.refresh_results())
        self.status_label = ttk.Label(self, textvariable=self.status, padding=(0, 7, 0, 0), wraplength=1280)
        self.status_label.grid(row=1, column=0, sticky="ew")
        self.bind("<Configure>", lambda event: self.status_label.configure(wraplength=max(600, self.winfo_width()-20)))
        self.refresh_results()

    @staticmethod
    def _group(parent, title):
        group = ttk.LabelFrame(parent, text=title, padding=6)
        group.pack(fill="x", pady=(0, 6))
        group.columnconfigure(1, weight=1)
        return group

    def _field(self, parent, key, label):
        row = parent.grid_size()[1]
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
        variable = self.variables[key] = tk.StringVar()
        ttk.Entry(parent, textvariable=variable, width=15).grid(row=row, column=1, sticky="ew", pady=2)
        variable.trace_add("write", self.mark_dirty)

    def _light_fields(self, parent, row, fields):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=3)
        for column, (key, label) in enumerate(fields):
            frame.columnconfigure(column, weight=1)
            ttk.Label(frame, text=label).grid(row=0, column=column, sticky="w")
            variable = self.light_variables[key] = tk.StringVar()
            ttk.Entry(frame, textvariable=variable, width=10).grid(row=1, column=column, sticky="ew", padx=1)
            variable.trace_add("write", self.mark_dirty)

    @staticmethod
    def _editor(parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        text = tk.Text(frame, width=1, font=("Consolas", 10), wrap="none", undo=True)
        vertical = ttk.Scrollbar(frame, command=text.yview)
        horizontal = ttk.Scrollbar(frame, orient="horizontal", command=text.xview)
        text.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        vertical.pack(side="right", fill="y")
        horizontal.pack(side="bottom", fill="x")
        text.pack(fill="both", expand=True)
        return text

    def mark_dirty(self, *_):
        if self.updating:
            return
        self.dirty = True
        try:
            width, height = (float(self.variables[k].get()) for k in ("width_mm", "height_mm"))
            pixels = int(self.variables["width_px"].get())
            self.resolution.set(f"Авторазрешение: {pixels} × {round(pixels * height / width)} пикселей")
        except (ValueError, KeyError, ZeroDivisionError, OverflowError):
            self.resolution.set("Авторазрешение: проверьте W, H и Wres")
        if not self.busy:
            self.status.set("Параметры изменены. Нажмите «Рассчитать». " +
                            ("Показаны предыдущие результаты." if self.results else ""))

    def guard(self, action):
        if self.busy:
            messagebox.showinfo("Расчёт", "Дождитесь завершения расчёта.")
            return
        try:
            return action()
        except (ValueError, TypeError, OSError, KeyError) as error:
            messagebox.showerror("Ошибка параметров", str(error))

    def _spectrum_name(self, values):
        for label, key in self.SPECTRA.items():
            if key is not None and np.array_equal(values, self.tables.spectra[key]):
                return label
        return "Табличный"

    def _refresh_lights(self):
        self.lights_tree.delete(*self.lights_tree.get_children())
        for index, light in enumerate(self.lights):
            self.lights_tree.insert("", "end", iid=str(index), text=f"L{index+1}",
                values=(f"{light.x_mm:g}, {light.y_mm:g}, {light.z_mm:g}", f"{light.intensity_w_sr:g}"))
        if self.selected_light is not None:
            self.lights_tree.selection_set(str(self.selected_light))

    def _show_light(self, index):
        before, self.updating = self.updating, True
        self.selected_light = index
        light = self.lights[index]
        for key, variable in self.light_variables.items():
            value = light.axis["xyz".index(key[-1])] if key.startswith("axis_") else getattr(light, key)
            variable.set(str(value))
        self.light_spectrum.set(self._spectrum_name(light.spectrum))
        self.updating = before

    def commit_light(self):
        if self.selected_light is None:
            return
        values = {key: float(variable.get()) for key, variable in self.light_variables.items()}
        axis = tuple(values.pop("axis_" + name) for name in "xyz")
        light = self.lights[self.selected_light]
        key = self.SPECTRA[self.light_spectrum.get()]
        spectrum = tuple(self.tables.spectra[key]) if key is not None else light.spectrum
        changed = self.lights[self.selected_light] = replace(light, **values, axis=axis, spectrum=spectrum)
        if self.lights_tree.exists(str(self.selected_light)):
            self.lights_tree.item(str(self.selected_light), values=(
                f"{changed.x_mm:g}, {changed.y_mm:g}, {changed.z_mm:g}", f"{changed.intensity_w_sr:g}"))

    def _select_light(self, event=None):
        selected = self.lights_tree.selection()
        if self.updating or self.busy or not selected or int(selected[0]) == self.selected_light:
            return
        try:
            self.commit_light()
            self._show_light(int(selected[0]))
        except (ValueError, TypeError) as error:
            self.lights_tree.selection_set(str(self.selected_light))
            messagebox.showerror("Источник света", "Проверьте числовые поля источника.\n" + str(error))

    def add_light(self):
        self.commit_light()
        self.lights.append(replace(self.lights[self.selected_light], x_mm=0))
        self.selected_light = len(self.lights)-1
        self._refresh_lights()
        self._show_light(self.selected_light)
        self.mark_dirty()

    def delete_light(self):
        if len(self.lights) == 1:
            raise ValueError("Необходимо оставить хотя бы один источник.")
        self.lights.pop(self.selected_light)
        self.selected_light = min(self.selected_light, len(self.lights)-1)
        self._refresh_lights()
        self._show_light(self.selected_light)
        self.mark_dirty()

    def set_scene(self, scene):
        validate(scene)
        self.updating = True
        self.scene, self.lights = scene, list(scene.lights)
        self.reflectance = tuple(scene.reflectance)
        for key, variable in self.variables.items():
            value = scene.direction["xyz".index(key[-1])] if key.startswith("direction_") else getattr(scene, key)
            variable.set("" if value is None else str(value))
        self.model_label.set(next(label for label, key in self.MODELS.items() if key == scene.model))
        if np.array_equal(scene.reflectance, self.tables.reflectance):
            self.material_kind.set(self.MATERIALS[0])
        elif np.all(np.asarray(scene.reflectance) == scene.reflectance[0]):
            self.material_kind.set(self.MATERIALS[1])
            self.material_constant.set(str(scene.reflectance[0]))
        else:
            self.material_kind.set(self.MATERIALS[2])
        self.selected_light = 0
        self._refresh_lights()
        self._show_light(0)
        self.json_text.delete("1.0", "end")
        self.json_text.insert("1.0", json.dumps(asdict(scene), ensure_ascii=False, indent=2))
        self.updating = False
        self.mark_dirty()

    def read_scene(self):
        self.commit_light()
        values = {}
        for key, variable in self.variables.items():
            value = variable.get().strip()
            values[key] = (None if not value else float(value)) if key == "screen_distance_mm" else (
                int(value) if key == "width_px" else float(value))
        direction = tuple(values.pop("direction_" + name) for name in "xyz")
        kind = self.material_kind.get()
        reflectance = (tuple(self.tables.reflectance) if kind == self.MATERIALS[0] else
                       (float(self.material_constant.get()),) * 41 if kind == self.MATERIALS[1] else self.reflectance)
        scene = replace(self.scene, **values, direction=direction, lights=tuple(self.lights),
                        reflectance=reflectance, model=self.MODELS[self.model_label.get()])
        validate(scene)
        return scene

    def below(self):
        p = self.read_scene()
        self.set_scene(replace(p, width_mm=2000, height_mm=2000, observer_z_mm=-2500,
            direction=(0, 0, 1), screen_z_mm=2000, screen_distance_mm=None,
            lights=tuple(replace(light, z_mm=-abs(light.z_mm), axis=(0, 0, 1)) for light in p.lights)))

    def sync_json(self):
        scene = self.read_scene()
        self.json_text.delete("1.0", "end")
        self.json_text.insert("1.0", json.dumps(asdict(scene), ensure_ascii=False, indent=2))

    def apply_json(self):
        self.set_scene(parameters_from_dict(json.loads(self.json_text.get("1.0", "end"))))

    def load_json(self, path=None):
        path = path or filedialog.askopenfilename(title="Загрузить сцену", filetypes=[("Сцена JSON", "*.json")])
        if path:
            self.set_scene(load_parameters(path))

    def save_json(self, path=None):
        scene = self.read_scene()
        path = path or filedialog.asksaveasfilename(title="Сохранить сцену", defaultextension=".json",
                                                   filetypes=[("Сцена JSON", "*.json")])
        if path:
            Path(path).write_text(json.dumps(asdict(scene), ensure_ascii=False, indent=2), encoding="utf-8")
            self.sync_json()

    def apply_spectra(self, text):
        self.set_scene(apply_spectra_csv(self.read_scene(), text))

    def spectra_dialog(self):
        scene = self.read_scene()
        window = tk.Toplevel(self)
        window.title("Таблица спектров — 380…780 нм, шаг 10 нм")
        window.geometry("780x680")
        ttk.Label(window, text="Столбцы: wavelength_nm, reflectance, light_1, light_2, …\n"
                  "41 строка. Отражение 0…1, излучение — относительная форма.", padding=8).pack(fill="x")
        text = self._editor(window)
        text.insert("1.0", spectra_csv(scene))
        buttons = ttk.Frame(window, padding=6)
        buttons.pack(fill="x")
        def apply():
            self.apply_spectra(text.get("1.0", "end"))
            window.destroy()
        def load():
            path = filedialog.askopenfilename(parent=window, filetypes=[("Таблица CSV", "*.csv")])
            if path:
                text.delete("1.0", "end")
                text.insert("1.0", Path(path).read_text(encoding="utf-8-sig"))
        def save():
            value = text.get("1.0", "end")
            apply_spectra_csv(scene, value)
            path = filedialog.asksaveasfilename(parent=window, defaultextension=".csv",
                                               filetypes=[("Таблица CSV", "*.csv")])
            if path:
                Path(path).write_text(value, encoding="utf-8-sig")
        for label, action in (("Загрузить CSV", load), ("Сохранить CSV", save), ("Применить", apply)):
            ttk.Button(buttons, text=label, command=lambda fn=action: self.guard(fn)).pack(side="left", padx=3)

    def _busy(self, busy):
        self.busy = busy
        if busy:
            def descendants(parent):
                for widget in parent.winfo_children():
                    yield widget
                    yield from descendants(widget)
            self._states = []
            for widget in descendants(self.left):
                if isinstance(widget, (ttk.Entry, ttk.Combobox, ttk.Button, tk.Text)):
                    self._states.append((widget, widget.cget("state")))
                    widget.configure(state="disabled")
            self.progress.start(12)
        else:
            for widget, state in self._states:
                widget.configure(state=state)
            self.progress.stop()

    def compute(self):
        if self.busy:
            return
        try:
            scene = self.read_scene()
        except (ValueError, TypeError, KeyError) as error:
            self.status.set("Ошибка параметров. Предыдущие результаты сохранены.")
            messagebox.showerror("Ошибка параметров", str(error))
            return
        self.scene = scene
        self.sync_json()
        self.dirty = False
        self._busy(True)
        self.status.set("Выполняется спектральный и RGB расчёт…")
        def worker():
            try:
                values = {"scene": calculate(scene)}
                self._completed.put((values, None))
            except Exception as error:
                self._completed.put((None, error))
        threading.Thread(target=worker, daemon=True).start()

    def _poll(self):
        if self._closed:
            return
        try:
            results, error = self._completed.get_nowait()
        except queue.Empty:
            pass
        else:
            self._busy(False)
            if error:
                self.status.set("Расчёт не выполнен. Показаны предыдущие результаты.")
                messagebox.showerror("Ошибка расчёта", str(error))
            else:
                self.results = results
                self.refresh_results()
                self.status.set("Расчёт завершён. " + ("Параметры изменены — нажмите «Рассчитать» снова."
                    if self.dirty else "Изображения и абсолютные значения обновлены."))
        self._poll_id = self.after(60, self._poll)

    def _draw_images(self, figure, gray=False):
        figure.clear()
        if not self.results:
            ax = figure.add_subplot(111)
            ax.text(.5, .5, "Результаты появятся после расчёта", ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()
            return
        for row, result in enumerate(self.results.values()):
            for column, image in enumerate(result["grays"] if gray else result["images"]):
                ax = figure.add_subplot(len(self.results), 2, row*2+column+1)
                p = result["parameters"]
                ax.imshow(image, cmap="gray" if gray else None, vmin=0, vmax=255,
                          extent=(-p.width_mm/2, p.width_mm/2, -p.height_mm/2, p.height_mm/2), interpolation="nearest")
                path = "спектральный расчёт" if column == 0 else "RGB расчёт"
                ax.set_title(f"image_{column+1}\n{path}", fontsize=10)
                ax.set(xlabel="x экрана, мм", ylabel="y экрана, мм")

    def _draw_spectra(self):
        figure = self.spectra_figure
        figure.clear()
        if not self.results:
            ax = figure.add_subplot(111)
            ax.text(.5, .5, "Спектры появятся после расчёта", ha="center", transform=ax.transAxes)
            ax.set_axis_off()
            return
        source_ax, material_ax = figure.subplots(2, 1)
        colors = {"D65": "dimgray", "Красный": "firebrick", "Синий": "royalblue",
                  "Чёрное тело 6500 К": "darkorange"}
        for result in self.results.values():
            for index, light in enumerate(result["parameters"].lights):
                values = np.asarray(light.spectrum)
                source_ax.plot(self.tables.wavelengths, values / values.max(),
                               color=colors.get(self._spectrum_name(light.spectrum)),
                               label=f"L{index+1} · {self._spectrum_name(light.spectrum)}")
        sample = next(iter(self.results.values()))
        material_ax.plot(self.tables.wavelengths, sample["parameters"].reflectance,
                         color="forestgreen", label="Отражение kᵈ(λ)")
        source_ax.set(title="Спектры источников", ylabel="Относительная форма")
        material_ax.set(title="Спектр отражения сферы", xlabel="Длина волны, нм", ylabel="Коэффициент отражения", ylim=(0, 1))
        for ax in (source_ax, material_ax):
            ax.grid(alpha=.25)
            ax.legend(fontsize=8)
            ax.set_xlim(380, 780)

    def _show_numbers(self):
        self.points_tree.delete(*self.points_tree.get_children())
        lines = []
        for result in self.results.values():
            for point in result["control_points"]:
                rgb2 = np.array([point["rgb2_" + c] for c in "RGB"])
                lv2 = float(683 * (CIE_RGB_TO_XYZ @ rgb2)[1])
                self.points_tree.insert("", "end", values=(point["name"],
                    f"({point['x_mm']:.1f}, {point['y_mm']:.1f}, {point['z_mm']:.1f})",
                    f"{point['radiance_w_m2_sr']:.8g}", f"{point['luminance_cd_m2']:.8g}", f"{lv2:.8g}"))
            for key, title in (("radiance_w_m2_sr", "Lₑ, Вт/(м²·ср)"),
                               ("luminance_1_cd_m2", "Lᵥ₁, кд/м²"), ("luminance_2_cd_m2", "Lᵥ₂, кд/м²")):
                stats = result["statistics"][key]
                lines.append(f"  {title}: минимум {stats['minimum']:.8g}, максимум {stats['maximum']:.8g}")
            difference = result["comparison"]
            lines.append(f"  Разность RGB: средняя {difference['monitor_mae_8bit']:.6g}, "
                         f"максимальная {difference['monitor_max_difference_8bit']} из 255")
        self.numbers_text.configure(state="normal")
        self.numbers_text.delete("1.0", "end")
        self.numbers_text.insert("1.0", "\n".join(lines))
        self.numbers_text.configure(state="disabled")

    def refresh_results(self):
        # 视图切换只重绘缓存，绝不调用 calculate。
        self._draw_images(self.rgb_figure)
        self._draw_images(self.gray_figure, gray=True)
        self._draw_spectra()
        self._show_numbers()
        for canvas in (self.rgb_canvas, self.gray_canvas, self.spectra_canvas):
            canvas.draw_idle()

    def export_results(self, directory):
        if not self.results:
            raise ValueError("Сначала выполните расчёт.")
        directory = Path(directory)
        save_results(self.results["scene"], directory)

    def save(self):
        if not self.results:
            raise ValueError("Сначала выполните расчёт.")
        if self.dirty:
            messagebox.showinfo("Сохранение", "Сохраняются показанные результаты предыдущего расчёта.\n"
                               "Для новых параметров сначала нажмите «Рассчитать».")
        directory = filedialog.askdirectory(title="Папка результатов")
        if directory:
            self.export_results(directory)
            messagebox.showinfo("Сохранено", "Изображения, три точки и абсолютные массивы сохранены.")

    def _destroyed(self, event):
        if event.widget is self:
            self._closed = True
            if hasattr(self, "_poll_id"):
                self.after_cancel(self._poll_id)


def launch_gui(initial=None):
    root = tk.Tk()
    SphereApp(root, initial)
    root.mainloop()
