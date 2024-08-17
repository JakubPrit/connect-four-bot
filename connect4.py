import tkinter as tk


class GUI:
    def __init__(self, n_cols=7, n_rows=6):
        self.n_cols = n_cols
        self.n_rows = n_rows

        self.tile_width = 50
        self.tile_height = 50
        self.board_width = self.tile_width * n_cols
        self.board_height = self.tile_height * n_rows

        self.root = tk.Tk()
        self.root.title("Connect 4")
        # self.root.geometry("{}x{}".format(self.board_width, self.board_height))
        self.root.minsize(self.board_width, self.board_height)

        self.label=tk.Label(self.root, text="Ready")
        self.label.pack()

        self.canvas = tk.Canvas(self.root, width=self.board_width, height=self.board_height)
        self.canvas.pack()

        self.draw_board()

        self.root.bind("<Configure>", self.resize_window)
        self.root.mainloop()

    def resize_window(self, event: tk.Event):
        if event.widget == self.root:
            self.board_width = event.width
            self.board_height = event.height
            self.tile_width = self.board_width // self.n_cols
            self.tile_height = self.board_height // self.n_rows
            self.label.config(text="{}x{}".format(self.board_width, self.board_height))
            # self.canvas.config(width=self.board_width, height=self.board_height)
            self.canvas.delete("all")
            self.draw_board()

    def draw_board(self):
        for i in range(self.n_cols):
            for j in range(self.n_rows):
                self.canvas.create_rectangle(i * self.tile_width, j * self.tile_height,
                                             (i + 1) * self.tile_width, (j + 1) * self.tile_height,
                                             fill="gray", outline="black")


if __name__ == "__main__":
    GUI()