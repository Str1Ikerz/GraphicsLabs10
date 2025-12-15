import tkinter as tk
from tkinter import ttk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class CurveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Алгоритмы построения кривых и поверхностей")
        self.root.geometry("1200x800")

        self.control_points = []
        self.control_grid = []
        self.current_step = 0
        self.subdivisions = 3
        self.current_method = "Квадр_Безье"

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_frame, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)

        method_frame = ttk.LabelFrame(left_frame, text="Метод построения")
        method_frame.pack(fill=tk.X, pady=(0, 10))

        self.method_var = tk.StringVar(value="Квадр_Безье")
        methods = [
            ("Квадратичная Безье", "Квадр_Безье"),
            ("Кубическая Безье", "Куб_Безье"),
            ("Кривая Чайкина", "Чайкин"),
            ("Поверхность Безье", "Пов_Безье"),
            ("Поверхность Ду-Сабина", "Ду_Сабин")
        ]

        for text, value in methods:
            ttk.Radiobutton(method_frame, text=text, variable=self.method_var,
                            value=value, command=self.method_changed).pack(anchor=tk.W)

        points_frame = ttk.LabelFrame(left_frame, text="Управление данными")
        points_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(points_frame, text="Добавить точку (2D)", command=self.add_point_mode).pack(fill=tk.X)
        ttk.Button(points_frame, text="Создать сетку 4x4 (для поверхности)", command=self.create_4x4_grid).pack(fill=tk.X, pady=(5, 0))
        ttk.Button(points_frame, text="Очистить", command=self.clear_all).pack(fill=tk.X, pady=(5, 0))

        params_frame = ttk.LabelFrame(left_frame, text="Параметры")
        params_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(params_frame, text="Кол-во разбиений:").pack(anchor=tk.W)
        self.subdivisions_var = tk.StringVar(value="3")
        ttk.Entry(params_frame, textvariable=self.subdivisions_var).pack(fill=tk.X)

        control_frame = ttk.LabelFrame(left_frame, text="Управление")
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(control_frame, text="Построить", command=self.build_full).pack(fill=tk.X)
        ttk.Button(control_frame, text="След. шаг", command=self.next_step).pack(fill=tk.X, pady=(5, 0))
        ttk.Button(control_frame, text="Сброс", command=self.reset_steps).pack(fill=tk.X, pady=(5, 0))

        info_frame = ttk.LabelFrame(left_frame, text="Инфо")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.info_text = tk.Text(info_frame, height=8)
        self.info_text.pack(fill=tk.BOTH, expand=True)

        self.right_frame = ttk.Frame(main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas_2d = None
        self.plot_3d = None
        self.fig = None
        self.ax = None

        self.update_display_area()

    def method_changed(self):
        self.current_method = self.method_var.get()
        self.reset_steps()
        self.update_display_area()
        self.redraw()

    def update_display_area(self):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        self.canvas_2d = None
        self.plot_3d = None
        self.fig = None
        self.ax = None

        if self.current_method in ["Пов_Безье", "Ду_Сабин"]:
            self.fig = Figure(figsize=(6, 6))
            self.ax = self.fig.add_subplot(111, projection='3d')
            self.plot_3d = FigureCanvasTkAgg(self.fig, self.right_frame)
            self.plot_3d.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            self.canvas_2d = tk.Canvas(self.right_frame, bg="white")
            self.canvas_2d.pack(fill=tk.BOTH, expand=True)
            self.canvas_2d.bind("<Button-1>", self.canvas_click)

    def canvas_click(self, event):
        if self.current_method not in ["Пов_Безье", "Ду_Сабин"]:
            if len(self.control_points) < 10:
                self.control_points.append((event.x, event.y))
                self.reset_steps()
                self.redraw()

    def add_point_mode(self):
        self.info_text.insert(tk.END, "Кликните на холст, чтобы добавить точку\n")
        self.info_text.see(tk.END)

    def create_4x4_grid(self):
        self.control_grid = []
        offset = 100
        for i in range(4):
            row = []
            for j in range(4):
                z = 0
                if (i == 1 and j == 1) or (i == 2 and j == 2):
                    z = 50
                row.append([j * offset + 50, i * offset + 50, z])
            self.control_grid.append(row)
        self.reset_steps()
        self.redraw()
        self.info_text.insert(tk.END, "Создана сетка 4x4 для поверхности\n")
        self.info_text.see(tk.END)

    def clear_all(self):
        self.control_points.clear()
        self.control_grid = []
        self.current_step = 0
        self.redraw()
        self.info_text.delete(1.0, tk.END)

    def get_subdivisions(self):
        try:
            val = int(self.subdivisions_var.get())
            self.subdivisions = max(1, min(10, val))
        except:
            self.subdivisions = 3
            self.subdivisions_var.set("3")

    def build_full(self):
        self.get_subdivisions()
        self.current_step = self.subdivisions
        self.redraw()

    def next_step(self):
        self.get_subdivisions()
        if self.current_step < self.subdivisions:
            self.current_step += 1
        self.redraw()

    def reset_steps(self):
        self.current_step = 0
        self.redraw()

    def quadratic_bezier_point(self, p0, p1, p2, t):
        return (1 - t)**2 * p0 + 2 * (1 - t) * t * p1 + t**2 * p2

    def cubic_bezier_point(self, p0, p1, p2, p3, t):
        return ((1 - t)**3 * p0 +
                3 * (1 - t)**2 * t * p1 +
                3 * (1 - t) * t**2 * p2 +
                t**3 * p3)

    def chaikin_refine(self, points):
        new_pts = []
        for i in range(len(points) - 1):
            p0 = np.array(points[i])
            p1 = np.array(points[i + 1])
            q = 0.75 * p0 + 0.25 * p1
            r = 0.25 * p0 + 0.75 * p1
            if i == 0:
                new_pts.append(tuple(q))
            new_pts.append(tuple(r))
            new_pts.append(tuple(q))
            if i == len(points) - 2:
                new_pts.append(tuple(r))
        return new_pts[1:-1]

    def bernstein(self, n, i, t):
        from math import comb
        return comb(n, i) * (t ** i) * ((1 - t) ** (n - i))

    def bezier_surface_point(self, P, u, v):
        n = len(P) - 1
        m = len(P[0]) - 1
        point = np.array([0.0, 0.0, 0.0])
        for i in range(n + 1):
            for j in range(m + 1):
                Bi = self.bernstein(n, i, u)
                Bj = self.bernstein(m, j, v)
                point += Bi * Bj * np.array(P[i][j])
        return point

    def du_sabin_refine_grid(self, grid):
        """Упрощённое сглаживание для регулярной сетки (аналог субдивизии)"""
        rows, cols = len(grid), len(grid[0])
        new_grid = [[None for _ in range(cols)] for _ in range(rows)]
        for i in range(rows):
            for j in range(cols):
                current = np.array(grid[i][j], dtype=float)
                neighbors = []
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols:
                        neighbors.append(np.array(grid[ni][nj], dtype=float))
                if neighbors:
                    avg_neighbor = np.mean(neighbors, axis=0)
                    new_pt = 0.4 * current + 0.6 * avg_neighbor
                else:
                    new_pt = current
                new_grid[i][j] = new_pt.tolist()
        return new_grid

    def redraw(self):
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"Метод: {self.current_method}\n")
        self.info_text.insert(tk.END, f"Точек: {len(self.control_points)}\n")
        grid_str = f"{len(self.control_grid)}x{len(self.control_grid[0])}" if self.control_grid else "0x0"
        self.info_text.insert(tk.END, f"Сетка: {grid_str}\n")
        self.info_text.insert(tk.END, f"Шаг: {self.current_step}\n")

        if self.current_method in ["Пов_Безье", "Ду_Сабин"]:
            self.redraw_surface()
        else:
            self.redraw_curve()

    def redraw_curve(self):
        if not self.canvas_2d:
            return
        try:
            self.canvas_2d.delete("all")
        except tk.TclError:
            self.canvas_2d = None
            return

        for i, (x, y) in enumerate(self.control_points):
            self.canvas_2d.create_oval(x - 4, y - 4, x + 4, y + 4, fill="red")
            if i > 0:
                x0, y0 = self.control_points[i - 1]
                self.canvas_2d.create_line(x0, y0, x, y, dash=(3, 3), fill="red")

        if self.current_step == 0:
            return

        if self.current_method == "Квадр_Безье" and len(self.control_points) >= 3:
            pts = self.build_quadratic_bezier()
        elif self.current_method == "Куб_Безье" and len(self.control_points) >= 4:
            pts = self.build_cubic_bezier()
        elif self.current_method == "Чайкин" and len(self.control_points) >= 2:
            pts = self.build_chaikin()
        else:
            return

        for i in range(len(pts) - 1):
            self.canvas_2d.create_line(
                pts[i][0], pts[i][1],
                pts[i+1][0], pts[i+1][1],
                fill="blue", width=2
            )

    def build_quadratic_bezier(self):
        pts = []
        for t in np.linspace(0, 1, 100):
            pt = self.quadratic_bezier_point(
                np.array(self.control_points[0]),
                np.array(self.control_points[1]),
                np.array(self.control_points[2]),
                t
            )
            pts.append(pt)
        return pts

    def build_cubic_bezier(self):
        pts = []
        for t in np.linspace(0, 1, 100):
            pt = self.cubic_bezier_point(
                np.array(self.control_points[0]),
                np.array(self.control_points[1]),
                np.array(self.control_points[2]),
                np.array(self.control_points[3]),
                t
            )
            pts.append(pt)
        return pts

    def build_chaikin(self):
        pts = self.control_points.copy()
        for _ in range(self.current_step):
            pts = self.chaikin_refine(pts)
        return pts

    def redraw_surface(self):
        if not self.ax or not self.control_grid or not self.plot_3d:
            return
        try:
            self.ax.clear()
        except tk.TclError:
            return

        grid = [row[:] for row in self.control_grid]

        for _ in range(self.current_step):
            if self.current_method == "Ду_Сабин":
                grid = self.du_sabin_refine_grid(grid)

        if self.current_method == "Пов_Безье":
            u_vals = np.linspace(0, 1, 20)
            v_vals = np.linspace(0, 1, 20)
            X, Y, Z = [], [], []
            for u in u_vals:
                x_row, y_row, z_row = [], [], []
                for v in v_vals:
                    pt = self.bezier_surface_point(self.control_grid, u, v)
                    x_row.append(pt[0])
                    y_row.append(pt[1])
                    z_row.append(pt[2])
                X.append(x_row)
                Y.append(y_row)
                Z.append(z_row)
            self.ax.plot_surface(np.array(X), np.array(Y), np.array(Z), cmap='viridis', alpha=0.8)
        else:
            X = np.array([[p[0] for p in row] for row in grid])
            Y = np.array([[p[1] for p in row] for row in grid])
            Z = np.array([[p[2] for p in row] for row in grid])
            self.ax.plot_wireframe(X, Y, Z, color="blue")

        Xc = np.array([[p[0] for p in row] for row in self.control_grid])
        Yc = np.array([[p[1] for p in row] for row in self.control_grid])
        Zc = np.array([[p[2] for p in row] for row in self.control_grid])
        self.ax.scatter(Xc, Yc, Zc, color="red", s=50)

        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.plot_3d.draw()


def main():
    root = tk.Tk()
    app = CurveApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()