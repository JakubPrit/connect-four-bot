import tkinter as tk
import typing as tp
import enum


TileState = tp.Literal[0, 1, 2]
Player = tp.Literal[1, 2]
Side = tp.Literal[0, 1, 2, 3]


TOP = 0
BOTTOM = 1
SIDE = LEFT = 2
RIGHT = 3


class GUI:
    def __init__(self, n_cols: int = 7, n_rows: int = 6, tile_size: int = 50, bg_color="gray",
                 outline_color="white", window_bg_color="gray",
                 circle_colors=("red", "yellow")):
        self.n_cols = n_cols
        self.n_rows = n_rows
        self.tile_size = tile_size

        self.board_margins: tp.List[float] = [.15, .05, .05, .05]
        self.board_width = self.tile_size * n_cols
        self.board_height = self.tile_size * n_rows
        self.window_width = int(self.board_width * (1 + 2 * self.board_margins[SIDE]))
        self.window_height = int(self.board_height * (1 + self.board_margins[TOP] + self.board_margins[BOTTOM]))

        self.window_bg_color = window_bg_color
        self.tile_bg_color = bg_color
        self.board_outline_color = outline_color
        self.tile_outline_color = outline_color
        self.board_outline_width = max(3, min(self.board_width, self.board_height) // 100)
        self.tile_outline_width = 2
        self.tile_padding = tile_size // 10

        self.root = tk.Tk()
        self.root.title("Connect 4")
        self.root.geometry("{}x{}".format(self.window_width, self.window_height))
        self.root.minsize(self.window_width, self.window_height)
        self.root_frame = tk.Frame(self.root)
        self.root_frame.pack(fill="both", expand=True)
        self.root_frame.config(bg=self.window_bg_color)

        self.create_board()
        self.root.bind("<Configure>", self.resize_window)

        self.root.mainloop()

    def resize_window(self, event: tk.Event):
        if event.widget == self.root:
            self.window_width = event.width
            self.window_height = event.height
            self.root_frame.config(width=self.window_width, height=self.window_height)
            self.tile_size = min(int(event.width * (1 - 2 * self.board_margins[SIDE])) // self.n_cols,
                                 int(event.height * (1 - self.board_margins[TOP] - self.board_margins[BOTTOM])) // self.n_rows)
            self.board_width = self.tile_size * self.n_cols - 2
            self.board_height = self.tile_size * self.n_rows - 2
            self.board_outline_width = max(3, min(self.board_width, self.board_height) // 100)
            self.tile_outline_width = 2
            self.tile_padding = self.tile_size // 10
            self.board_canvas.delete("all")
            self.board_frame.destroy()
            self.create_board()

    def create_board(self):
        self.board_frame = tk.Frame(self.root_frame, width=self.board_width, height=self.board_height,
                                    highlightcolor=self.board_outline_color,
                                    highlightbackground=self.board_outline_color,
                                    highlightthickness=self.board_outline_width)
        self.board_frame.place(anchor="center", relx=0.5, rely=0.5)
        self.board_canvas = tk.Canvas(self.board_frame, width=self.board_width, height=self.board_height)
        self.board_canvas.pack()

        for i in range(self.n_cols):
            for j in range(self.n_rows):
                self.board_canvas.create_rectangle(i * self.tile_size, j * self.tile_size,
                                                   (i + 1) * self.tile_size, (j + 1) * self.tile_size,
                                                   fill=self.tile_bg_color, outline=self.tile_outline_color,
                                                   tags="tile")
        self.draw_circle(3, 3, "red")
        self.draw_circle(4, 3, "yellow")
        self.board_canvas.tag_bind("tile", "<Button-1>", self.on_tile_click)

    def draw_circle(self, col, row, color):
        x0 = col * self.tile_size + self.tile_padding
        y0 = row * self.tile_size + self.tile_padding
        x1 = (col + 1) * self.tile_size - self.tile_padding
        y1 = (row + 1) * self.tile_size - self.tile_padding
        self.board_canvas.create_oval(x0, y0, x1, y1, fill=color, outline="")

    def on_tile_click(self, event: tk.Event):
        col = event.x // self.tile_size
        row = event.y // self.tile_size
        self.draw_circle(col, row, "red")


if __name__ == "__main__":
    GUI()