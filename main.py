import tkinter as tk
from tkinter import ttk
import numpy as np

class GeometricCurvesLab:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная №13: Построение кривых")
        self.root.geometry("1020x720")

        self.control_pts = []
        self.current_method = "Безье2"
        self.subdiv_steps = 0
        self.max_steps = 5

        self.show_control = True
        self.show_refined = True

        self.build_ui()

    def build_ui(self):
        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_panel = ttk.Frame(main, width=280)
        main.add(left_panel)

        right_panel = ttk.Frame(main)
        main.add(right_panel)

        method_group = ttk.LabelFrame(left_panel, text="Метод построения")
        method_group.pack(fill=tk.X, pady=(0, 10))

        self.method_var = tk.StringVar(value="Безье2")
        methods = [
            ("Квадратичная кривая Безье", "Безье2"),
            ("Кубическая кривая Безье", "Безье3"),
            ("Кривая Чайкина", "Чайкин")
        ]
        for txt, val in methods:
            ttk.Radiobutton(method_group, text=txt, variable=self.method_var,
                            value=val, command=self.on_method_change).pack(anchor=tk.W, padx=5, pady=2)

        pts_group = ttk.LabelFrame(left_panel, text="Точки")
        pts_group.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(pts_group, text="Добавить точку (клик по холсту)", command=self.enable_add_mode).pack(fill=tk.X, pady=2)
        ttk.Button(pts_group, text="Очистить всё", command=self.clear_all).pack(fill=tk.X, pady=2)

        param_group = ttk.LabelFrame(left_panel, text="Параметры")
        param_group.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(param_group, text="Макс. шагов:").pack(anchor=tk.W, padx=5)
        self.steps_var = tk.StringVar(value="5")
        steps_entry = ttk.Entry(param_group, textvariable=self.steps_var, width=8)
        steps_entry.pack(pady=2)

        build_group = ttk.LabelFrame(left_panel, text="Построение")
        build_group.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(build_group, text="Построить полностью", command=self.build_full).pack(fill=tk.X, pady=2)
        ttk.Button(build_group, text="Следующий шаг", command=self.next_step).pack(fill=tk.X, pady=2)
        ttk.Button(build_group, text="Сбросить шаги", command=self.reset_steps).pack(fill=tk.X, pady=2)

        view_group = ttk.LabelFrame(left_panel, text="Отображение")
        view_group.pack(fill=tk.X, pady=(0, 10))
        self.show_control_var = tk.BooleanVar(value=True)
        self.show_refined_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(view_group, text="Исходные точки", variable=self.show_control_var, command=self.redraw).pack(anchor=tk.W, padx=5)
        ttk.Checkbutton(view_group, text="Промежуточные точки", variable=self.show_refined_var, command=self.redraw).pack(anchor=tk.W, padx=5)

        info_group = ttk.LabelFrame(left_panel, text="Информация")
        info_group.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.info_display = tk.Text(info_group, height=8, font=("Consolas", 9))
        self.info_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(right_panel, bg="white", width=700, height=700)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.update_info()
        self.redraw()

    def on_method_change(self):
        self.current_method = self.method_var.get()
        self.reset_steps()
        self.update_info()

    def enable_add_mode(self):
        self.info_display.insert(tk.END, "Кликните на холсте для добавления точки.\n")
        self.info_display.see(tk.END)

    def clear_all(self):
        self.control_pts.clear()
        self.subdiv_steps = 0
        self.redraw()
        self.update_info()

    def on_canvas_click(self, event):
        if len(self.control_pts) >= 20:
            return
        self.control_pts.append((event.x, event.y))
        self.reset_steps()
        self.redraw()
        self.update_info()

    def get_max_steps(self):
        try:
            val = int(self.steps_var.get())
            self.max_steps = max(1, min(10, val))
        except ValueError:
            self.max_steps = 5
            self.steps_var.set("5")

    def build_full(self):
        self.get_max_steps()
        self.subdiv_steps = self.max_steps
        self.redraw()

    def next_step(self):
        self.get_max_steps()
        if self.subdiv_steps < self.max_steps:
            self.subdiv_steps += 1
        self.redraw()

    def reset_steps(self):
        self.subdiv_steps = 0
        self.redraw()

    def update_info(self):
        self.info_display.delete(1.0, tk.END)
        self.info_display.insert(tk.END, f"Метод: {self.current_method}\n")
        self.info_display.insert(tk.END, f"Точек: {len(self.control_pts)}\n")
        self.info_display.insert(tk.END, f"Тек. шаг: {self.subdiv_steps}\n")
        self.info_display.insert(tk.END, f"Макс. шагов: {self.max_steps}\n\n")
        if self.control_pts:
            self.info_display.insert(tk.END, "Контрольные точки:\n")
            for i, (x, y) in enumerate(self.control_pts):
                self.info_display.insert(tk.END, f"  {i}: ({x}, {y})\n")

    def redraw(self):
        self.canvas.delete("all")
        if not self.control_pts:
            return

        if self.show_control_var.get():
            for x, y in self.control_pts:
                self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="darkred", outline="black")
            for i in range(len(self.control_pts) - 1):
                x1, y1 = self.control_pts[i]
                x2, y2 = self.control_pts[i+1]
                self.canvas.create_line(x1, y1, x2, y2, fill="gray", dash=(3, 2))

        if self.current_method == "Безье2" and len(self.control_pts) >= 3:
            self.draw_quadratic_bezier()
        elif self.current_method == "Безье3" and len(self.control_pts) >= 4:
            self.draw_cubic_bezier()
        elif self.current_method == "Чайкин" and len(self.control_pts) >= 2:
            self.draw_chaikin_curve()

    def draw_quadratic_bezier(self):
        curve = []
        for i in range(len(self.control_pts) - 2):
            p0 = np.array(self.control_pts[i])
            p1 = np.array(self.control_pts[i+1])
            p2 = np.array(self.control_pts[i+2])
            for t in np.linspace(0, 1, 50):
                pt = (1-t)**2 * p0 + 2*(1-t)*t * p1 + t**2 * p2
                curve.append(tuple(pt))

        for i in range(len(curve)-1):
            self.canvas.create_line(curve[i], curve[i+1], fill="blue", width=2)

        if self.show_refined_var.get() and self.subdiv_steps > 0:
            for i in range(len(self.control_pts) - 2):
                p0 = np.array(self.control_pts[i])
                p1 = np.array(self.control_pts[i+1])
                p2 = np.array(self.control_pts[i+2])
                t_val = 0.5
                pt = (1-t_val)**2 * p0 + 2*(1-t_val)*t_val * p1 + t_val**2 * p2
                x, y = pt
                self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="green")

    def de_casteljau_step(self, pts, t):
        n = len(pts)
        if n == 1:
            return pts[0]
        new_pts = []
        for i in range(n - 1):
            p0 = np.array(pts[i])
            p1 = np.array(pts[i+1])
            pt = (1 - t) * p0 + t * p1
            new_pts.append(tuple(pt))
        return self.de_casteljau_step(new_pts, t)

    def draw_cubic_bezier(self):
        if len(self.control_pts) < 4:
            return
        curve = []
        for i in range(len(self.control_pts) - 3):
            segment = self.control_pts[i:i+4]
            for t in np.linspace(0, 1, 60):
                pt = self.de_casteljau_step(segment, t)
                curve.append(pt)

        for i in range(len(curve)-1):
            self.canvas.create_line(curve[i], curve[i+1], fill="navy", width=2)

        if self.show_refined_var.get() and self.subdiv_steps > 0:
            t_vals = [0.0, 0.5, 1.0]
            for i in range(len(self.control_pts) - 3):
                segment = self.control_pts[i:i+4]
                for t in t_vals:
                    self._draw_de_casteljau_intermediate(segment, t, depth=self.subdiv_steps)

    def _draw_de_casteljau_intermediate(self, pts, t, depth):
        if depth <= 0 or len(pts) <= 1:
            return
        new_pts = []
        for i in range(len(pts) - 1):
            p0 = np.array(pts[i])
            p1 = np.array(pts[i+1])
            pt = (1 - t) * p0 + t * p1
            new_pts.append(tuple(pt))
            if self.show_refined_var.get():
                x, y = pt
                self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="orange")
        self._draw_de_casteljau_intermediate(new_pts, t, depth - 1)

    def chaikin_refine(self, pts):
        if len(pts) < 2:
            return pts
        refined = []
        for i in range(len(pts) - 1):
            p0 = np.array(pts[i])
            p1 = np.array(pts[i+1])
            q = 0.75 * p0 + 0.25 * p1
            r = 0.25 * p0 + 0.75 * p1
            refined.extend([tuple(q), tuple(r)])
        return refined

    def draw_chaikin_curve(self):
        current = self.control_pts[:]
        for _ in range(self.subdiv_steps):
            current = self.chaikin_refine(current)
            if not current:
                break

        for i in range(len(current) - 1):
            self.canvas.create_line(current[i], current[i+1], fill="purple", width=2)

        # Промежуточные вершины
        if self.show_refined_var.get():
            for x, y in current:
                self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="limegreen")

if __name__ == "__main__":
    root = tk.Tk()
    app = GeometricCurvesLab(root)
    root.mainloop()