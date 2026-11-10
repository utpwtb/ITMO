# 提供实验图形界面：编辑参数、异步计算、查看三图与光谱，并导出当前结果。
import queue
import threading
import tkinter as tk
from dataclasses import replace
from tkinter import filedialog, messagebox, ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from .core.color_conversion import scene_rgb
from .experiment import run, white_scene
from .output import save, spectral_figure, summary


# 管理参数表单、光源列表、结果标签页及后台计算任务的主界面组件。
class App(ttk.Frame):
    # 建立控件和默认场景，并注册定时轮询以接收后台结果。
    def __init__(self, root):
        super().__init__(root, padding=10)
        self.pack(fill="both", expand=True)
        self.data = None
        self.busy = False
        # 后台线程通过队列传回数据，所有 Tk 控件更新均在界面线程完成。
        self.completed = queue.SimpleQueue()
        self.scene = white_scene()
        self.lights = list(self.scene.lights)
        self.colors = list(scene_rgb(self.scene)[1])
        self.fields, self.light_fields = {}, {}
        self.selected = None
        self.status = tk.StringVar(value="Задайте параметры и нажмите «Рассчитать».")
        # 左侧编辑场景和光源参数，右侧显示实验结果。
        panes = ttk.Panedwindow(self, orient="horizontal")
        panes.pack(fill="both", expand=True)
        left, right = ttk.Frame(panes, width=370), ttk.Frame(panes)
        panes.add(left, weight=0)
        panes.add(right, weight=1)
        action_row = ttk.Frame(left, padding=4)
        action_row.pack(side="bottom", fill="x")
        canvas = tk.Canvas(left, width=365, highlightthickness=0)
        bar = ttk.Scrollbar(left, command=canvas.yview)
        canvas.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        form = ttk.Frame(canvas, padding=4)
        window = canvas.create_window((0, 0), window=form, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window, width=e.width))
        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        for title, fields in (
            ("Экран и сфера, мм", (("width_mm", "W"), ("height_mm", "H"), ("width_px", "Wres (Hres по W/H)"),
             ("center_x_mm", "xC"), ("center_y_mm", "yC"), ("center_z_mm", "zC"), ("radius_mm", "Радиус"))),
            ("Наблюдатель и экран", (("observer_z_mm", "zO, мм"), ("screen_z_mm", "z экрана, мм"),
             ("screen_distance_mm", "f, мм (необязательно)"),
             ("direction_x", "Направление dx"), ("direction_y", "dy"), ("direction_z", "dz")))):
            group = ttk.LabelFrame(form, text=title, padding=6)
            group.pack(fill="x", pady=4)
            for key, label in fields:
                value = self.scene.direction["xyz".index(key[-1])] if key.startswith("direction_") else getattr(self.scene, key)
                self.field(group, self.fields, key, label, "" if value is None else value)
        # 使用绝对 CIE RGB 描述光源颜色，并将其与强度 I₀ 分开输入。
        group = ttk.LabelFrame(form, text="Источники: абсолютный CIE RGB", padding=6)
        group.pack(fill="x", pady=4)
        self.source = ttk.Combobox(group, state="readonly")
        self.source.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.source.bind("<<ComboboxSelected>>", self.select_light)
        for key, label in (("x_mm", "xL, мм"), ("y_mm", "yL, мм"), ("z_mm", "zL, мм"),
            ("intensity_w_sr", "I₀ исходный, Вт/ср"), ("axis_x", "Ось ax"), ("axis_y", "ay"), ("axis_z", "az"),
            ("R", "R"), ("G", "G"), ("B", "B")):
            self.field(group, self.light_fields, key, label, 0)
        actions = ttk.Frame(group)
        actions.grid(row=11, column=0, columnspan=2)
        for label, action in (("Применить", self.commit_light), ("Добавить", self.add_light), ("Удалить", self.delete_light)):
            ttk.Button(actions, text=label, command=lambda f=action: self.guard(f)).pack(side="left")
        ttk.Label(form, text="Белая сфера: kd(λ)=1.\nСетка 380–780 нм, шаг 10 нм.", padding=5).pack(fill="x")
        self.compute_button = ttk.Button(action_row, text="Рассчитать", command=lambda: self.guard(self.compute))
        self.compute_button.pack(fill="x", pady=5)
        self.save_button = ttk.Button(action_row, text="Сохранить результаты…", command=lambda: self.guard(self.export))
        self.save_button.pack(fill="x")
        # 结果分为三图对照、光谱与表格、绝对亮度三个标签页。
        self.tabs = ttk.Notebook(right)
        self.tabs.pack(fill="both", expand=True)
        self.image_tab, self.spectra_tab, numbers = (ttk.Frame(self.tabs) for _ in range(3))
        for frame, name in ((self.image_tab, "Изображения A / 1 / 2"), (self.spectra_tab, "Спектрограммы и таблица"), (numbers, "Абсолютная яркость")):
            self.tabs.add(frame, text=name)
        self.numbers = tk.Text(numbers, wrap="word", font=("Consolas", 11), state="disabled")
        self.numbers.pack(fill="both", expand=True)
        self.table = ttk.Treeview(self.spectra_tab, columns=("nm", "original", "recovered", "error"), show="headings", height=7)
        for key, label in zip(self.table["columns"], ("λ, нм", "L1 исходный, 1/нм", "L1 восстановленный", "Разность")):
            self.table.heading(key, text=label)
            self.table.column(key, width=120)
        self.table.pack(side="bottom", fill="x")
        ttk.Label(self, textvariable=self.status, wraplength=1100, padding=4).pack(fill="x")
        self.plot_canvases = []
        self.refresh_sources(0)
        # 每 80 毫秒检查计算队列，与界面的事件循环配合。
        self.poll_id = self.after(80, self.poll)

    # 创建标签和输入框，将对应文本变量登记到指定字典。
    @staticmethod
    def field(parent, store, key, label, value):
        row = parent.grid_size()[1]
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        store[key] = tk.StringVar(value=str(value))
        ttk.Entry(parent, textvariable=store[key], width=19).grid(row=row, column=1, sticky="ew", pady=2)
        parent.columnconfigure(1, weight=1)

    # 执行界面操作，将输入或文件操作错误显示为消息框。
    def guard(self, action):
        try:
            action()
        except (ValueError, OSError, TypeError) as error:
            messagebox.showerror("Ошибка", str(error), parent=self)

    # 更新光源下拉列表，并载入指定光源的参数。
    def refresh_sources(self, index):
        self.source.configure(values=[f"Источник {i+1}" for i in range(len(self.lights))])
        self.source.current(index)
        self.selected = None
        self.select_light()

    # 切换光源前保存当前输入，再显示所选光源的参数与 RGB。
    def select_light(self, event=None):
        index = self.source.current()
        if self.selected is not None:
            try:
                self.commit_light()
            except ValueError as error:
                self.source.current(self.selected)
                messagebox.showerror("Ошибка", str(error), parent=self)
                return
        self.selected = index
        light = self.lights[index]
        values = {k: getattr(light, k) for k in ("x_mm", "y_mm", "z_mm", "intensity_w_sr")}
        values.update(zip(("axis_x", "axis_y", "axis_z"), light.axis))
        values.update(zip("RGB", self.colors[index]))
        for key, value in values.items():
            self.light_fields[key].set(str(value))

    # 校验光源表单，将几何参数和 CIE RGB 分别写回光源及颜色列表。
    def commit_light(self):
        values = {k: float(v.get()) for k, v in self.light_fields.items()}
        if not np.all(np.isfinite(list(values.values()))):
            raise ValueError("Требуются конечные значения источника")
        self.lights[self.selected] = replace(self.lights[self.selected],
            **{k: values[k] for k in ("x_mm", "y_mm", "z_mm", "intensity_w_sr")},
            axis=tuple(values["axis_"+c] for c in "xyz"))
        # RGB 单独保存，计算时交给重建函数，不直接修改原光谱。
        self.colors[self.selected] = np.array([values[c] for c in "RGB"])

    # 保存当前输入，以默认光源为模板新增光源。
    def add_light(self):
        self.commit_light()
        self.lights.append(self.scene.lights[0])
        self.colors.append(scene_rgb(self.scene)[1][0].copy())
        self.refresh_sources(len(self.lights)-1)

    # 删除所选光源并刷新表单，保证至少保留一个光源。
    def delete_light(self):
        if len(self.lights) == 1:
            raise ValueError("Требуется хотя бы один источник")
        del self.lights[self.selected]
        del self.colors[self.selected]
        self.refresh_sources(0)

    # 读取相机、屏幕、球体和光源参数，生成用于计算的新场景。
    def read_scene(self):
        self.commit_light()
        values = {k: float(v.get()) for k, v in self.fields.items()
                  if not k.startswith("direction_") and k != "screen_distance_mm"}
        distance = self.fields["screen_distance_mm"].get().strip()
        values["screen_distance_mm"] = float(distance) if distance else None
        values["width_px"] = int(self.fields["width_px"].get())
        return replace(self.scene, **values, lights=tuple(self.lights),
                       direction=tuple(float(self.fields["direction_"+c].get()) for c in "xyz"))

    # 取得当前输入，在后台运行实验，并暂时禁用计算和导出按钮。
    def compute(self):
        if self.busy:
            return
        scene, colors = self.read_scene(), np.array(self.colors)
        self.busy = True
        self.compute_button.configure(state="disabled")
        self.save_button.configure(state="disabled")
        self.status.set("Вычисление…")
        # 执行数值计算，通过队列传回结果或异常。
        def worker():
            try:
                self.completed.put((run(scene, colors), None))
            except Exception as error:
                self.completed.put((None, error))
        # 使用守护线程避免计算阻塞窗口，结果由定时轮询取回。
        threading.Thread(target=worker, daemon=True).start()

    # 检查后台结果，在界面线程恢复按钮并显示结果或错误。
    def poll(self):
        try:
            data, error = self.completed.get_nowait()
        except queue.Empty:
            pass
        else:
            self.busy = False
            self.compute_button.configure(state="normal")
            self.save_button.configure(state="normal")
            if error:
                self.status.set(str(error))
                messagebox.showerror("Ошибка расчёта", str(error), parent=self)
            else:
                self.data = data
                self.show_results()
                self.status.set("Готово. На экране — рассчитанная сцена. Экспорт сохраняет именно этот результат.")
        # 每 80 毫秒检查计算队列，与界面的事件循环配合。
        self.poll_id = self.after(80, self.poll)

    # 刷新三张对照图、光谱图、第一光源的 41 点表格及亮度摘要。
    def show_results(self):
        for canvas in self.plot_canvases:
            canvas.get_tk_widget().destroy()
        figure = Figure(figsize=(10, 5), layout="constrained")
        for ax, image, name in zip(figure.subplots(1, 3), self.data["images"], ("image_A", "image_1 (recomputed)", "image_2 (recomputed)")):
            ax.imshow(image)
            ax.set_title(name, fontsize=10)
            ax.set_axis_off()
        self.plot_canvases = []
        for parent, fig in ((self.image_tab, figure), (self.spectra_tab, spectral_figure(self.data))):
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            canvas.draw()
            self.plot_canvases.append(canvas)
        self.table.delete(*self.table.get_children())
        # 表格列出第一光源从 380 到 780 nm、间隔 10 nm 的原谱、重建谱及差值。
        for w, original, recovered in zip(range(380, 781, 10), self.data["original_spd"][0], self.data["recovered"][0]):
            self.table.insert("", "end", values=(w, f"{original:.8g}", f"{recovered:.8g}", f"{recovered-original:.5g}"))
        self.numbers.configure(state="normal")
        self.numbers.delete("1.0", "end")
        self.numbers.insert("1.0", summary(self.data))
        self.numbers.configure(state="disabled")

    # 让用户选择目录，保存界面当前展示的那一次计算结果。
    def export(self):
        if self.data is None or self.busy:
            raise ValueError("Сначала выполните расчёт")
        directory = filedialog.askdirectory(parent=self)
        if directory:
            save(self.data, directory)
            self.status.set("Результаты сохранены: " + directory)


# 创建 Tk 主窗口、装入实验界面并进入事件循环。
def launch():
    root = tk.Tk()
    root.title("Лабораторная работа 4 — RGB → спектр")
    root.geometry("1320x850")
    root.minsize(1000, 650)
    App(root)
    root.mainloop()
