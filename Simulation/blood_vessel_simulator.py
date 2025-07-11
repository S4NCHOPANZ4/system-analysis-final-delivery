import tkinter as tk
from tkinter import filedialog, Toplevel, Label, Button, messagebox
from PIL import Image, ImageTk
import random
import math
import csv
import os

GRID_SIZE = 60
CELL_SIZE = 10
P0 = 100
RESISTANCE = 1
EXPLOSION_RADIUS = 2

PROPAGATION_CHANCE = 0.3
ANEURYSM_THRESHOLD = 5
ANEURYSM_EXPLODE_NEIGHBORS = 2
ANEURYSM_CURE_NEIGHBORS = 4
REVIVE_DEAD_NEIGHBORS = 1


def classify_pixel(value):
    if value < 90:
        return "A"
    elif value < 130:
        return "V"
    elif 130 <= value < 140:
        return "G"
    else:
        return "T"


class ImageLoaderPopup:
    def __init__(self, master, on_done_callback):
        self.popup = Toplevel(master)
        self.popup.title("Load Image and Convert to Grid")
        self.popup.geometry("400x450")
        self.on_done_callback = on_done_callback

        self.image_label = Label(self.popup, text="No image loaded")
        self.image_label.pack(pady=10)

        Button(self.popup, text="Load Image", command=self.load_image).pack()
        Button(self.popup, text="Use This Image", command=self.confirm_image).pack(pady=10)

        self.grid_data = None
        self.tk_img = None

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if not path:
            return

        try:
            img = Image.open(path).convert("L")
            img = img.resize((GRID_SIZE, GRID_SIZE))

            self.grid_data = [
                [classify_pixel(img.getpixel((x, y))) for x in range(GRID_SIZE)]
                for y in range(GRID_SIZE)
            ]

            preview = img.resize((GRID_SIZE * 4, GRID_SIZE * 4))
            self.tk_img = ImageTk.PhotoImage(preview)
            self.image_label.config(image=self.tk_img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def confirm_image(self):
        if self.grid_data:
            self.popup.destroy()
            self.on_done_callback(self.grid_data)
        else:
            messagebox.showwarning("No Image", "Please load an image before continuing.")


class BloodVesselSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Blood Vessel Simulation")

        self.edit_mode = True
        self.current_tool = "V"

        self.canvas = tk.Canvas(root, width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE)
        self.canvas.pack()

        self.grid = [["T" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.pressure = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        self.iteration = 0
        self.history = []  # Guardar datos por paso

        self.create_toolbar(root)
        self.canvas.bind("<Button-1>", self.handle_click)
        self.draw_grid()
        self.show_image_loader()

    def show_image_loader(self):
        self.root.update_idletasks()
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        width = self.root.winfo_width()
        popup = ImageLoaderPopup(self.root, self.apply_image_grid)
        popup.popup.geometry(f"+{x + width + 20}+{y}")

    def apply_image_grid(self, new_grid):
        self.grid = [row[:GRID_SIZE] + ["T"] * (GRID_SIZE - len(row)) for row in new_grid]
        self.draw_grid()

    def create_toolbar(self, root):
        frame = tk.Frame(root)
        frame.pack(pady=5)

        tools = [
            ("Artery", "A"),
            ("Vessel", "V"),
            ("Aneurysm", "X"),
            ("Dead", "D"),
            ("Empty", "T"),
            ("Glomerulus", "G"),
        ]
        for label, code in tools:
            btn = tk.Button(frame, text=label, command=lambda c=code: self.set_tool(c))
            btn.pack(side="left")

        self.btn_start = tk.Button(frame, text="Start Simulation", command=self.start_simulation)
        self.btn_start.pack(side="left", padx=10)

        self.btn_step = tk.Button(frame, text="Step", command=self.step, state="disabled")
        self.btn_step.pack(side="left")

        self.btn_reset = tk.Button(frame, text="Reset", command=self.reset_simulation)
        self.btn_reset.pack(side="left", padx=10)

        self.btn_save = tk.Button(frame, text="Save CSV Results", command=self.save_to_csv)
        self.btn_save.pack(side="left", padx=10)

        self.btn_load_image = tk.Button(frame, text="Load New Image", command=self.show_image_loader)
        self.btn_load_image.pack(side="left", padx=10)

    def set_tool(self, tool_code):
        self.current_tool = tool_code

    def start_simulation(self):
        self.edit_mode = False
        self.btn_start.config(state="disabled")
        self.btn_step.config(state="normal")

    def reset_simulation(self):
        self.grid = [["T" for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.pressure = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.iteration = 0
        self.history = []
        self.edit_mode = True
        self.btn_start.config(state="normal")
        self.btn_step.config(state="disabled")
        self.draw_grid()

    def handle_click(self, event):
        if not self.edit_mode:
            return
        i, j = event.y // CELL_SIZE, event.x // CELL_SIZE
        if 0 <= i < GRID_SIZE and 0 <= j < GRID_SIZE:
            self.grid[i][j] = self.current_tool
            if self.current_tool == "A":
                self.pressure[i][j] = P0
            elif self.current_tool != "V":
                self.pressure[i][j] = 0
            self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                cell = self.grid[i][j]
                x0, y0 = j * CELL_SIZE, i * CELL_SIZE
                x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE

                color = "white"
                if cell == "A":
                    color = "red"
                elif cell == "V":
                    neighbors = sum(
                        1 for ni, nj in self.neighbors_all(i, j)
                        if self.grid[ni][nj] in ["V", "A"]
                    )
                    r = g = int(255 * (1 - neighbors / 8))
                    b = 255
                    color = f"#{r:02x}{g:02x}{b:02x}"
                elif cell == "X":
                    color = "#ff6600"
                elif cell == "D":
                    color = "black"
                elif cell == "G":
                    color = "#00cc00"
                elif cell == "GF":
                    color = "#999900"

                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="gray")

    def neighbors_all(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    yield nx, ny

    def neighbors_xy(self, x, y):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                yield nx, ny

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def step(self):
        self.iteration += 1
        new_vessels = set()
        aneurysms_to_explode = []
        aneurysms_cured = 0

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.grid[i][j] == "A":
                    for ni, nj in self.neighbors_xy(i, j):
                        if self.grid[ni][nj] in ["T", "D"]:
                            self.grid[ni][nj] = "V"

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.grid[i][j] == "V":
                    cardinal = sum(1 for ni, nj in self.neighbors_xy(i, j) if self.grid[ni][nj] in ["V", "A"])
                    total = sum(1 for ni, nj in self.neighbors_all(i, j) if self.grid[ni][nj] in ["V", "A"])

                    if cardinal == 0:
                        self.grid[i][j] = "D"
                    elif total >= ANEURYSM_THRESHOLD:
                        self.grid[i][j] = "X"

                    for ni, nj in self.neighbors_xy(i, j):
                        if self.grid[ni][nj] == "T" and random.random() < PROPAGATION_CHANCE:
                            new_vessels.add((ni, nj))

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.grid[i][j] == "X":
                    x_neigh = sum(1 for ni, nj in self.neighbors_xy(i, j) if self.grid[ni][nj] == "X")
                    v_neigh = sum(1 for ni, nj in self.neighbors_xy(i, j) if self.grid[ni][nj] == "V")
                    if x_neigh >= ANEURYSM_EXPLODE_NEIGHBORS:
                        aneurysms_to_explode.append((i, j))
                    elif v_neigh < ANEURYSM_CURE_NEIGHBORS:
                        self.grid[i][j] = "V"
                        aneurysms_cured += 1

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.grid[i][j] == "D":
                    alive = sum(1 for ni, nj in self.neighbors_xy(i, j) if self.grid[ni][nj] in ["V", "A"])
                    if alive >= REVIVE_DEAD_NEIGHBORS:
                        self.grid[i][j] = "V"

        for i, j in new_vessels:
            self.grid[i][j] = "V"

        for cx, cy in aneurysms_to_explode:
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    if self.grid[i][j] == "V" and self.distance(i, j, cx, cy) <= EXPLOSION_RADIUS:
                        self.grid[i][j] = "T"
            self.grid[cx][cy] = "T"

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.grid[i][j] in ["G", "GF"]:
                    vessels = sum(1 for ni, nj in self.neighbors_all(i, j) if self.grid[ni][nj] == "V")
                    arteries = sum(1 for ni, nj in self.neighbors_all(i, j) if self.grid[ni][nj] == "A")
                    if vessels >= 3 or arteries >= 1:
                        self.grid[i][j] = "G"
                    else:
                        self.grid[i][j] = "GF"

        self.record_current_data(aneurysms_cured, len(aneurysms_to_explode))
        self.draw_grid()

    def record_current_data(self, aneurysms_cured, aneurysms_exploded):
        count = lambda val: sum(cell == val for row in self.grid for cell in row)
        data = {
            "iteration": self.iteration,
            "glomeruli_active": count("G"),
            "glomeruli_failed": count("GF"),
            "vessels": count("V"),
            "dead_vessels": count("D"),
            "aneurysms_cured": aneurysms_cured,
            "aneurysms_exploded": aneurysms_exploded,
        }
        self.history.append(data)

    def save_to_csv(self):
        if not self.history:
            messagebox.showinfo("No Data", "No data to sve.")
            return
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, "simulation_log.csv")
        try:
            with open(file_path, "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=list(self.history[0].keys()))
                writer.writeheader()
                writer.writerows(self.history)
            messagebox.showinfo("Success", "Results saved to simulation_log.csv")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BloodVesselSimulation(root)
    root.mainloop()
