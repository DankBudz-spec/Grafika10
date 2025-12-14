import tkinter as tk
from tkinter import ttk
import math
import tkinter.messagebox as mb


# --- Математические вспомогательные функции ---

def comb(n, k):
    """Вычисление биномиального коэффициента."""
    if k < 0 or k > n: return 0
    if k == 0 or k == n: return 1
    if k > n // 2: k = n - k

    num = 1
    for i in range(k):
        num = num * (n - i) // (i + 1)
    return num


def bernstein(i, n, t):
    """Полином Бернштейна."""
    return comb(n, i) * (t ** i) * ((1 - t) ** (n - i))


# --- Проекция 3D в 2D ---

def project(x, y, z, width, height, angle_x, angle_y, scale=100):
    """Простая изометрическая проекция для визуализации поверхностей."""
    # Вращение вокруг Y
    rad_y = math.radians(angle_y)
    nx = x * math.cos(rad_y) + z * math.sin(rad_y)
    nz = -x * math.sin(rad_y) + z * math.cos(rad_y)

    # Вращение вокруг X
    rad_x = math.radians(angle_x)
    ny = y * math.cos(rad_x) - nz * math.sin(rad_x)

    # Смещение в центр экрана
    screen_x = width / 2 + nx * scale
    screen_y = height / 2 - ny * scale
    return screen_x, screen_y


# --- Основной класс приложения ---

class LabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа: Кривые и поверхности (Вар 8)")

        self.mode = tk.StringVar(value="Chaikin")
        self.iterations = tk.IntVar(value=3)
        self.show_points = tk.BooleanVar(value=True)
        self.show_grid = tk.BooleanVar(value=True)
        self.rows_var = tk.IntVar(value=4)
        self.cols_var = tk.IntVar(value=4)
        # Параметры вращения для 3D
        self.angle_x = 20
        self.angle_y = -30

        self.setup_ui()

        # Исходные данные
        self.curve_points = [(100, 400), (200, 100), (400, 100), (500, 400), (300, 500)]
        self.surface_grid = self.generate_initial_grid(4, 4)

        self.canvas.bind("<B1-Motion>", self.rotate_view)
        self.redraw()

    def setup_ui(self):
        control_panel = ttk.Frame(self.root, padding="10")
        control_panel.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(control_panel, text="Выберите алгоритм:").pack(anchor=tk.W)
        ttk.Radiobutton(control_panel, text="Кривая Чайкина (п.3)", variable=self.mode, value="Chaikin",
                        command=self.redraw).pack(anchor=tk.W)
        ttk.Radiobutton(control_panel, text="Поверхность Безье (п.4)", variable=self.mode, value="BezierSurf",
                        command=self.redraw).pack(anchor=tk.W)
        ttk.Radiobutton(control_panel, text="Поверхность Ду-Сабина (п.5)", variable=self.mode, value="DooSabin",
                        command=self.redraw).pack(anchor=tk.W)

        ttk.Separator(control_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        # --- Управление размером сетки ---
        ttk.Label(control_panel, text="Размер сетки (Поверхности):").pack(anchor=tk.W)

        frame_dims = ttk.Frame(control_panel)
        frame_dims.pack(fill=tk.X)

        ttk.Label(frame_dims, text="Rows (N):").pack(side=tk.LEFT)
        self.rows_entry = ttk.Entry(frame_dims, width=5, textvariable=self.rows_var)
        self.rows_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(frame_dims, text="Cols (M):").pack(side=tk.LEFT)
        self.cols_entry = ttk.Entry(frame_dims, width=5, textvariable=self.cols_var)
        self.cols_entry.pack(side=tk.LEFT, padx=5)

        # Кнопка для применения изменений
        ttk.Button(control_panel, text="Применить размер", command=self.update_grid_size).pack(fill=tk.X, pady=5)
        ttk.Separator(control_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        ttk.Label(control_panel, text="Итерации / Плотность:").pack(anchor=tk.W)
        self.iter_slider = tk.Scale(control_panel, from_=1, to=8, orient=tk.HORIZONTAL, variable=self.iterations,
                                    command=lambda x: self.redraw())
        self.iter_slider.pack(fill=tk.X)

        ttk.Checkbutton(control_panel, text="Показать контр. точки", variable=self.show_points,
                        command=self.redraw).pack(anchor=tk.W)
        ttk.Checkbutton(control_panel, text="Показать сетку", variable=self.show_grid, command=self.redraw).pack(
            anchor=tk.W)

        ttk.Label(control_panel, text="\n*Для 3D: зажмите ЛКМ на холсте\nи двигайте для вращения").pack(anchor=tk.W)

        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="white", highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    def generate_initial_grid(self, rows, cols):
        """Создает волнообразную сетку для демонстрации поверхностей."""
        grid = []
        for i in range(rows):
            row = []
            for j in range(cols):
                # x, y (высота), z
                x = (j - (cols - 1) / 2)
                z = (i - (rows - 1) / 2)
                y = math.sin(x) * math.cos(z) * 0.5
                row.append([x, y, z])
            grid.append(row)
        return grid

    def update_grid_size(self):
        try:
            rows = self.rows_var.get()
            cols = self.cols_var.get()
            if rows < 2 or cols < 2:
                raise ValueError("Размер не может быть меньше чем 2x2")
            self.surface_grid = self.generate_initial_grid(rows, cols)
            self.redraw()
        except Exception as e:
            mb.showerror("Ошибка", f"Некорректный размер {e}")
    def rotate_view(self, event):
        if self.mode.get() in ["BezierSurf", "DooSabin"]:
            self.angle_y += event.x - (self.last_x if hasattr(self, 'last_x') else event.x)
            self.angle_x += event.y - (self.last_y if hasattr(self, 'last_y') else event.y)
            self.last_x, self.last_y = event.x, event.y
            self.redraw()
        self.last_x, self.last_y = event.x, event.y

    # --- Алгоритмы ---

    def run_chaikin(self, points, iters):
        """Реализация алгоритма Чайкина (угловое отсечение)."""
        for _ in range(iters):
            new_pts = []
            for i in range(len(points) - 1):
                p0 = points[i]
                p1 = points[i + 1]
                # Точки Qi и Ri в пропорции 1/4 и 3/4
                q = (0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1])
                r = (0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1])
                new_pts.extend([q, r])
            points = new_pts
        return points

    def get_bezier_surface_point(self, u, v, grid):
        """Вычисляет точку на поверхности Безье в параметрах u, v."""
        n = len(grid) - 1
        m = len(grid[0]) - 1
        res = [0, 0, 0]
        for i in range(n + 1):
            bu = bernstein(i, n, u)
            for j in range(m + 1):
                bv = bernstein(j, m, v)
                for k in range(3):
                    res[k] += grid[i][j][k] * bu * bv
        return res

    def run_doo_sabin_step(self, grid):
        """Один шаг уточнения Ду-Сабина для регулярной сетки."""
        rows = len(grid)
        cols = len(grid[0])
        new_grid = []

        # Для каждой "грани" (ячейки сетки) создаем 4 новые точки
        for i in range(rows - 1):
            new_rows = [[], []]
            for j in range(cols - 1):
                # 4 вершины грани
                p1 = grid[i][j]
                p2 = grid[i][j + 1]
                p3 = grid[i + 1][j + 1]
                p4 = grid[i + 1][j]

                # Центр грани
                f = [(p1[k] + p2[k] + p3[k] + p4[k]) / 4 for k in range(3)]

                # Середины ребер
                e1 = [(p1[k] + p2[k]) / 2 for k in range(3)]
                e2 = [(p2[k] + p3[k]) / 2 for k in range(3)]
                e3 = [(p3[k] + p4[k]) / 2 for k in range(3)]
                e4 = [(p4[k] + p1[k]) / 2 for k in range(3)]

                # Новые точки грани (среднее между вершиной, серединами ребер и центром)
                v1 = [(p1[k] + e1[k] + e4[k] + f[k]) / 4 for k in range(3)]
                v2 = [(p2[k] + e1[k] + e2[k] + f[k]) / 4 for k in range(3)]
                v3 = [(p3[k] + e2[k] + e3[k] + f[k]) / 4 for k in range(3)]
                v4 = [(p4[k] + e3[k] + e4[k] + f[k]) / 4 for k in range(3)]

                new_rows[0].extend([v1, v2])
                new_rows[1].extend([v4, v3])
            new_grid.extend(new_rows)
        return new_grid

    # --- Визуализация ---

    def redraw(self):
        self.canvas.delete("all")
        m = self.mode.get()
        iters = self.iterations.get()
        w, h = 800, 600

        if m == "Chaikin":
            # Рисуем исходный полигон
            if self.show_grid.get():
                self.canvas.create_line(self.curve_points, fill="gray", dash=(4, 4))

            # Расчет кривой
            refined = self.run_chaikin(self.curve_points, iters)
            self.canvas.create_line(refined, fill="blue", width=2)

            if self.show_points.get():
                for x, y in self.curve_points:
                    self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")

        elif m == "BezierSurf":
            # Вычисляем сетку точек поверхности
            steps = iters * 3
            plot_points = []
            for i in range(steps + 1):
                row = []
                u = i / steps
                for j in range(steps + 1):
                    v = j / steps
                    p = self.get_bezier_surface_point(u, v, self.surface_grid)
                    row.append(project(*p, w, h, self.angle_x, self.angle_y, 150))
                plot_points.append(row)
            self.draw_surface(plot_points, "blue")
            if self.show_grid.get():
                self.draw_control_grid(self.surface_grid, "red")

        elif m == "DooSabin":
            # Итерационное уточнение
            current_grid = self.surface_grid
            for _ in range(iters // 2 + 1):  # Ограничим итерации для наглядности
                current_grid = self.run_doo_sabin_step(current_grid)

            # Проектируем и рисуем
            plot_points = []
            for r in range(len(current_grid)):
                row = []
                for c in range(len(current_grid[0])):
                    row.append(project(*current_grid[r][c], w, h, self.angle_x, self.angle_y, 150))
                plot_points.append(row)

            self.draw_surface(plot_points, "green")
            if self.show_grid.get():
                self.draw_control_grid(self.surface_grid, "red")

    def draw_surface(self, pts, color):
        """Рисует спроектированную сетку поверхности."""
        for i in range(len(pts)):
            for j in range(len(pts[i])):
                if j + 1 < len(pts[i]):
                    self.canvas.create_line(pts[i][j], pts[i][j + 1], fill=color)
                if i + 1 < len(pts):
                    self.canvas.create_line(pts[i][j], pts[i + 1][j], fill=color)

    def draw_control_grid(self, grid, color):
        """Рисует исходные контрольные точки и линии связи."""
        w, h = 800, 600
        projected = []
        for r in range(len(grid)):
            row = []
            for c in range(len(grid[0])):
                p_2d = project(*grid[r][c], w, h, self.angle_x, self.angle_y, 150)
                row.append(p_2d)
                if self.show_points.get():
                    self.canvas.create_oval(p_2d[0] - 2, p_2d[1] - 2, p_2d[0] + 2, p_2d[1] + 2, fill=color)
            projected.append(row)

        for i in range(len(projected)):
            for j in range(len(projected[i])):
                if j + 1 < len(projected[i]):
                    self.canvas.create_line(projected[i][j], projected[i][j + 1], fill=color, dash=(2, 2))
                if i + 1 < len(projected):
                    self.canvas.create_line(projected[i][j], projected[i + 1][j], fill=color, dash=(2, 2))


if __name__ == "__main__":
    root = tk.Tk()
    app = LabApp(root)
    root.mainloop()