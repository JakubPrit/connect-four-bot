import tkinter as tk


class GUI:
    def __init__(self, n_cols=7, n_rows=6,
                 tile_bg_color="gray", tile_outline_color="white",
                 tile_size=50, tile_padding=5, tile_outline_width=2):
        self.n_cols = n_cols
        self.n_rows = n_rows
        self.tile_size = tile_size
        self.tile_padding = tile_padding
        self.tile_outline_width = tile_outline_width
        self.board_width = self.tile_size * n_cols
        self.board_height = self.tile_size * n_rows

        self.root = tk.Tk()
        self.root.title("Connect 4")
        self.root.geometry("{}x{}".format(self.board_width, self.board_height))
        self.root.minsize(self.board_width, self.board_height)

        self.tile_bg_color = tile_bg_color
        self.tile_outline_color = tile_outline_color

        self.create_board()
        self.root.bind("<Configure>", self.resize_window)

        self.root.mainloop()

    def resize_window(self, event: tk.Event):
        if event.widget == self.root:
            self.tile_size = min(event.width // self.n_cols,
                                 event.height // self.n_rows)
            self.board_width = self.tile_size * self.n_cols
            self.board_height = self.tile_size * self.n_rows
            self.board_canvas.delete("all")
            self.create_board()

    def create_board(self):
        self.board_canvas = tk.Canvas(self.root, width=self.board_width, height=self.board_height)
        self.board_canvas.config(width=self.board_width, height=self.board_height)
        self.board_canvas.place(anchor="center", relx=0.5, rely=0.5)

        for i in range(self.n_cols):
            for j in range(self.n_rows):
                self.board_canvas.create_rectangle(i * self.tile_size, j * self.tile_size,
                                                   (i + 1) * self.tile_size, (j + 1) * self.tile_size,
                                                   fill=self.tile_bg_color, outline=self.tile_outline_color)
        self.draw_circle(3, 3, "red")
        self.draw_circle(4, 3, "yellow")


    def draw_circle(self, col, row, color):
        x0 = col * self.tile_size + self.tile_padding
        y0 = row * self.tile_size + self.tile_padding
        x1 = (col + 1) * self.tile_size - self.tile_padding
        y1 = (row + 1) * self.tile_size - self.tile_padding
        self.board_canvas.create_oval(x0, y0, x1, y1, fill=color)


if __name__ == "__main__":
    GUI()