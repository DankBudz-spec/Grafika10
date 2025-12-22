import tkinter as tk
from tkinter import ttk
import math


class CurveLabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Построение кривых по координатам")

        # Данные
        self.points = []
        self.t_param = tk.DoubleVar(value=0.5)
        self.mode = tk.StringVar(value="BezierN")
        self.iterations = tk.IntVar(value=3)
        self.show_steps = tk.BooleanVar(value=True)

        self.setup_ui()

        # Начальные данные для примера
        self.coord_input.insert("1.0", "100, 500\n200, 100\n500, 100\n700, 500")
        self.update_from_text()

    def setup_ui(self):
        # Панель управления (слева)
        ctrl = ttk.Frame(self.root, padding="10")
        ctrl.pack(side=tk.LEFT, fill=tk.Y)

        # 1. Ввод координат
        ttk.Label(ctrl, text="Координаты (X, Y):", font='Arial 10 bold').pack(anchor=tk.W)
        ttk.Label(ctrl, text="по одной паре на строку", foreground="gray", font='Arial 8').pack(anchor=tk.W)

        self.coord_input = tk.Text(ctrl, width=25, height=10)
        self.coord_input.pack(pady=5)

        ttk.Button(ctrl, text="Применить координаты", command=self.update_from_text).pack(fill=tk.X, pady=5)

        ttk.Separator(ctrl, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # 2. Выбор алгоритма
        ttk.Label(ctrl, text="Алгоритм:", font='Arial 10 bold').pack(anchor=tk.W)
        ttk.Radiobutton(ctrl, text="Квадратичная Безье (3т)", variable=self.mode, value="Bezier2",
                        command=self.redraw).pack(anchor=tk.W)
        ttk.Radiobutton(ctrl, text="Кубическая Безье (4т)", variable=self.mode, value="Bezier3",
                        command=self.redraw).pack(anchor=tk.W)
        ttk.Radiobutton(ctrl, text="N-степени Безье", variable=self.mode, value="BezierN", command=self.redraw).pack(
            anchor=tk.W)
        ttk.Radiobutton(ctrl, text="Кривая Чайкина", variable=self.mode, value="Chaikin", command=self.redraw).pack(
            anchor=tk.W)

        ttk.Separator(ctrl, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # 3. Параметры
        ttk.Label(ctrl, text="Параметр t (разбиение):").pack(anchor=tk.W)
        tk.Scale(ctrl, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL,
                 variable=self.t_param, command=lambda x: self.redraw()).pack(fill=tk.X)

        ttk.Label(ctrl, text="Итерации (Чайкин):").pack(anchor=tk.W)
        tk.Scale(ctrl, from_=1, to=6, orient=tk.HORIZONTAL, variable=self.iterations,
                 command=lambda x: self.redraw()).pack(fill=tk.X)

        ttk.Checkbutton(ctrl, text="Показать расчет (шаги)", variable=self.show_steps, command=self.redraw).pack(
            anchor=tk.W, pady=5)

        # Холст (справа)
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    def update_from_text(self):
        """Парсинг текста из поля ввода в список координат"""
        raw_data = self.coord_input.get("1.0", tk.END).strip()
        new_points = []
        try:
            for line in raw_data.split('\n'):
                if not line.strip(): continue
                # Замена запятых на пробелы и разбиение
                parts = line.replace(',', ' ').split()
                if len(parts) >= 2:
                    x, y = float(parts[0]), float(parts[1])
                    new_points.append([x, y])
            self.points = new_points
            self.redraw()
        except ValueError:
            tk.messagebox.showerror("Ошибка", "Неверный формат координат! Используйте: X, Y")

    # --- Алгоритмы ---

    def get_casteljau_layers(self, points, t):
        """Расчет промежуточных вершин (алгоритм де Кастельжо)"""
        layers = [points]
        while len(layers[-1]) > 1:
            prev = layers[-1]
            current = []
            for i in range(len(prev) - 1):
                px = (1 - t) * prev[i][0] + t * prev[i + 1][0]
                py = (1 - t) * prev[i][1] + t * prev[i + 1][1]
                current.append((px, py))
            layers.append(current)
        return layers

    def run_chaikin(self, points, iters):
        pts = points
        for _ in range(iters):
            new_pts = []
            for i in range(len(pts) - 1):
                p0, p1 = pts[i], pts[i + 1]
                new_pts.append(((0.75 * p0[0] + 0.25 * p1[0]), (0.75 * p0[1] + 0.25 * p1[1])))
                new_pts.append(((0.25 * p0[0] + 0.75 * p1[0]), (0.25 * p0[1] + 0.75 * p1[1])))
            pts = new_pts
        return pts

    # --- Отрисовка ---

    def redraw(self):
        self.canvas.delete("all")
        if len(self.points) < 2: return

        mode = self.mode.get()
        t = self.t_param.get()

        # Определяем набор точек для Безье (ограничиваем для 2 и 3 степени)
        if mode == "Bezier2":
            pts = self.points[:3]
        elif mode == "Bezier3":
            pts = self.points[:4]
        else:
            pts = self.points

        # 1. Опорный полигон
        self.canvas.create_line(pts, fill="#dddddd", dash=(2, 2))

        # 2. Отрисовка Безье
        if "Bezier" in mode:
            # Рисуем саму кривую
            curve_pts = []
            for step in range(101):
                curr_t = step / 100
                layer_pts = self.get_casteljau_layers(pts, curr_t)
                curve_pts.append(layer_pts[-1][0])
            self.canvas.create_line(curve_pts, fill="#3498db", width=2)

            # Отрисовка шагов (геометрическое построение для текущего t)
            layers = self.get_casteljau_layers(pts, t)
            if self.show_steps.get():
                colors = ["#e74c3c", "#f1c40f", "#2ecc71", "#9b59b6"]
                for i, layer in enumerate(layers[1:-1]):
                    color = colors[i % len(colors)]
                    self.canvas.create_line(layer, fill=color, width=1)
                    for px, py in layer:
                        self.canvas.create_oval(px - 3, py - 3, px + 3, py + 3, outline=color)

            # Итоговая точка на кривой при данном t
            final_p = layers[-1][0]
            self.canvas.create_oval(final_p[0] - 5, final_p[1] - 5, final_p[0] + 5, final_p[1] + 5, fill="#2980b9")

        # 3. Отрисовка Чайкина
        elif mode == "Chaikin":
            chaikin_pts = self.run_chaikin(self.points, self.iterations.get())
            self.canvas.create_line(chaikin_pts, fill="#27ae60", width=2)

        # 4. Контрольные точки и подписи
        for i, (x, y) in enumerate(self.points):
            self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#2c3e50")
            self.canvas.create_text(x + 12, y - 12, text=f"P{i}({int(x)},{int(y)})", font='Arial 8')


if __name__ == "__main__":
    root = tk.Tk()
    app = CurveLabApp(root)
    root.mainloop()