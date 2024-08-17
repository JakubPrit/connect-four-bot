import tkinter as tk
import typing as tp


Player = tp.Literal[1, 2]
Side = tp.Literal[0, 1, 2, 3]


TOP = 0
BOTTOM = 1
SIDE = LEFT = 2
RIGHT = 3


class GUI:
    def __init__(self, n_cols: int = 7, n_rows: int = 6, tile_size: int = 100, bg_color="gray",
                 outline_color="white", window_bg_color="gray", player_colors=("red", "yellow")):
        self.MIN_TILE_SIZE = 50
        self.BOARD_TOP_EXTRA_MARGIN = 0.1
        self.BOARD_MARGIN = 0.05
        self.TILE_PADDING_RATIO = 0.1
        self.BOARD_OUTLINE_RATIO = 0.01
        self.MIN_BOARD_OUTLINE_WIDTH = 3
        self.TILE_OUTLINE_WIDTH = 2
        self.MIN_WINDOW_WIDTH = 350
        self.MIN_WINDOW_HEIGHT = 350
        self.WINDOW_TITLE = "Connect 4"

        self.n_cols = n_cols
        self.n_rows = n_rows
        self.tile_size = tile_size
        self.board_width = self.tile_size * n_cols - self.TILE_OUTLINE_WIDTH
        self.board_height = self.tile_size * n_rows - self.TILE_OUTLINE_WIDTH
        self.window_width = int(self.board_width * (1 + 2 * self.BOARD_MARGIN))
        self.window_height = int(self.board_height * (1 + 2 * self.BOARD_MARGIN
                                                      + self.BOARD_TOP_EXTRA_MARGIN))

        self.window_bg_color = window_bg_color
        self.tile_bg_color = bg_color
        self.board_outline_color = outline_color
        self.tile_outline_color = outline_color

        self.root = tk.Tk()
        self.root.title(self.WINDOW_TITLE)
        self.root.geometry("{}x{}".format(self.window_width, self.window_height))
        self.root.minsize(self.MIN_WINDOW_WIDTH, self.MIN_WINDOW_HEIGHT)
        self.root_frame = tk.Frame(self.root)
        self.root_frame.pack(fill="both", expand=True)
        self.root_frame.config(bg=self.window_bg_color)

        self.state_color = [self.tile_bg_color, *player_colors]
        self.tile_states = [[0 for _ in range(self.n_cols)] for _ in range(self.n_rows)]

        self._draw_board()
        self.root.bind("<Configure>", self._resize_window)

        self.root.mainloop()

    def _resize_window(self, event: tk.Event):
        if event.widget == self.root:
            self.window_width = event.width
            self.window_height = event.height
            self.root_frame.config(width=self.window_width, height=self.window_height)
            self.tile_size = min(int(event.width * (1 - 2 * self.BOARD_MARGIN)) // self.n_cols,
                                 int(event.height * (1 - 2 * self.BOARD_MARGIN
                                                     - self.BOARD_TOP_EXTRA_MARGIN)) // self.n_rows)
            self.board_width = self.tile_size * self.n_cols - self.TILE_OUTLINE_WIDTH
            self.board_height = self.tile_size * self.n_rows - self.TILE_OUTLINE_WIDTH
            self.redraw_board()

    def redraw_board(self):
        self.board_canvas.delete("all")
        self.board_frame.destroy()
        self._draw_board()

    def _draw_board(self):
        self.board_outline_width = max(self.MIN_BOARD_OUTLINE_WIDTH,
                                       min(self.board_width, self.board_height)
                                       * self.BOARD_OUTLINE_RATIO // 1)
        self.tile_padding = self.tile_size * self.TILE_PADDING_RATIO // 1

        self.board_frame = tk.Frame(self.root_frame, width=self.board_width, height=self.board_height,
                                    highlightcolor=self.board_outline_color,
                                    highlightbackground=self.board_outline_color,
                                    highlightthickness=self.board_outline_width)
        self.board_frame.place(anchor="center", relx=0.5, rely=0.5 + self.BOARD_TOP_EXTRA_MARGIN / 2)
        self.board_canvas = tk.Canvas(self.board_frame, width=self.board_width, height=self.board_height)
        self.board_canvas.pack()

        for row in range(self.n_rows):
            for col in range(self.n_cols):
                self.board_canvas.create_rectangle(col * self.tile_size, row * self.tile_size,
                                                   (col + 1) * self.tile_size, (row + 1) * self.tile_size,
                                                   fill=self.tile_bg_color, outline=self.tile_outline_color,
                                                   tags=("tile_part"))
                if self.tile_states[row][col] != 0:
                    self._draw_circle(row, col, self.state_color[self.tile_states[row][col]])
        self.board_canvas.tag_bind("tile_part", "<Button-1>", self._on_tile_click)

    def _draw_circle(self, row, col, color):
        x0 = col * self.tile_size + self.tile_padding
        y0 = row * self.tile_size + self.tile_padding
        x1 = (col + 1) * self.tile_size - self.tile_padding
        y1 = (row + 1) * self.tile_size - self.tile_padding
        self.board_canvas.create_oval(x0, y0, x1, y1, fill=color, outline="", tags=("tile_part"))

    def _on_tile_click(self, event: tk.Event):
        col = event.x // self.tile_size
        row = event.y // self.tile_size
        if 0 <= row < self.n_rows and 0 <= col < self.n_cols:
            self.tile_states[row][col] = 1 - self.tile_states[row][col]
            self.redraw_board()


if __name__ == "__main__":
    GUI()