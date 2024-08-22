import tkinter as tk
from tkinter import ttk
import typing as tp
import enum
from abc import abstractmethod
from random import randint
from time import time_ns
from functools import lru_cache


#############################################################
#                     TYPE DEFINITIONS                      #
#############################################################


Side = tp.Literal[0, 1, 2, 3]
Num = tp.Union[int, float]
GameState = tp.Tuple[int, tp.List[int], int]


class TurnResult(enum.Enum):
    INVALID = 0
    WIN = 1
    DRAW = 2
    OK = 3

    def __bool__(self):
        return self != TurnResult.INVALID


#############################################################
#                    GUI IMPLEMENTATION                     #
#############################################################


class GUI:
    WIN_TEXT = "Player {} won!"
    DRAW_TEXT = "It's a draw!"
    TURN_TEXT = "Player {}'s turn"
    BOT_TURN_TEXT = "Player {}'s (BOT) turn"

    DEFAULT_PLAYER_COLORS = ["red", "yellow", "blue", "green", "purple",
                             "cyan", "lime", "magenta", "olive"]
    LABEL_FONT = "TkDefaultFont 20 bold"

    BOARD_TOP_EXTRA_MARGIN = 0.1
    BOARD_MARGIN = 0.05
    TILE_PADDING_RATIO = 0.1
    BOARD_OUTLINE_RATIO = 0.01
    MIN_BOARD_OUTLINE_WIDTH = 3
    TILE_OUTLINE_WIDTH = 2
    MIN_WINDOW_WIDTH = 350
    MIN_WINDOW_HEIGHT = 350

    DARK_MODE = {
        "tile_bg_color": "#303030",
        "outline_color": "black",
        "window_bg_color": "#303030",
        "draw_color": "white",
        "no_player_color": "#484848",
    }

    def __init__(self, game: "Game", tile_size: int = 100, tile_bg_color: str = "#909090",
                 outline_color: str = "white", window_bg_color: str = "#909090",
                 player_colors: tp.Optional[tp.List[str]] = None, draw_color: str = "black",
                 no_player_color: str = "#b7b7b7", window_title: str = "Connect 4"):
        """ Initialize the GUI for the game.

        Args:
            game (Game): The game instance to connect the GUI to.
            tile_size (int, optional): The size of each tile in pixels. Defaults to 100.
            tile_bg_color (str, optional): The background color of the tiles.
                    Defaults to "#909090".
            outline_color (str, optional): The color of all outlines. Defaults to "white".
            window_bg_color (str, optional): The background color of the game window.
                    Defaults to "#909090".
            player_colors (tp.Optional[tp.List[str]], optional): A list of colors to use
                    for each player. Defaults to None for default colors.
            draw_color (str, optional): The color to use for draw label. Defaults to "white".
            no_player_color (str, optional): The color to use for empty tiles.
                    Defaults to "#b7b7b7".
            window_title (str, optional): The title of the game window. Defaults to "Connect 4".
        """

        self.game = game
        self.n_cols = game.n_cols
        self.n_rows = game.n_rows
        self.tile_size = tile_size
        self.board_width = self.tile_size * game.n_cols - GUI.TILE_OUTLINE_WIDTH
        self.board_height = self.tile_size * game.n_rows - GUI.TILE_OUTLINE_WIDTH
        self.window_width = int(self.board_width * (1 + 2 * GUI.BOARD_MARGIN))
        self.window_height = int(self.board_height * (1 + 2 * GUI.BOARD_MARGIN
                                                      + GUI.BOARD_TOP_EXTRA_MARGIN))

        self.window_bg_color = window_bg_color
        self.tile_bg_color = tile_bg_color
        self.board_outline_color = outline_color
        self.tile_outline_color = outline_color
        self.window_title = window_title
        self.no_player_color = no_player_color
        self.draw_color = draw_color
        if player_colors is None:
            self.player_colors = [self.no_player_color, *GUI.DEFAULT_PLAYER_COLORS]
        else:
            self.player_colors = [self.no_player_color, *player_colors]

        self.root = tk.Tk()
        self.root.title(self.window_title)
        self.root.geometry("{}x{}".format(self.window_width, self.window_height))
        self.root.minsize(GUI.MIN_WINDOW_WIDTH, GUI.MIN_WINDOW_HEIGHT)
        self.root_frame = tk.Frame(self.root)
        self.root_frame.pack(fill="both", expand=True)
        self.root_frame.config(bg=self.window_bg_color)

        self.board_frame: tk.Frame
        self.board_canvas: tk.Canvas
        self.state_label = tk.Label(self.root_frame, text="Initializing...",
                                    font=GUI.LABEL_FONT, bg=self.window_bg_color)
        self.state_label.pack(expand=True)

        self._draw_board()
        self.root.bind("<Configure>", self._resize_window)

    def _resize_window(self, event: tk.Event):
        if event.widget == self.root:
            self.window_width = event.width
            self.window_height = event.height
            self.root_frame.config(width=self.window_width, height=self.window_height)
            horizontal_margin = 2 * GUI.BOARD_MARGIN
            vertical_margin = 2 * GUI.BOARD_MARGIN + GUI.BOARD_TOP_EXTRA_MARGIN
            self.tile_size = min(int(event.width / (1 + horizontal_margin)) // self.n_cols,
                                 int(event.height / (1 + vertical_margin)) // self.n_rows)
            self.board_width = self.tile_size * self.n_cols - GUI.TILE_OUTLINE_WIDTH
            self.board_height = self.tile_size * self.n_rows - GUI.TILE_OUTLINE_WIDTH
            self.redraw_board()

    def redraw_board(self) -> None:
        """ Redraw the whole board.
            Note: _draw_board() has to be called at least once before this,
            but that is automatically done in __init__.
        """

        self.board_canvas.delete("all")
        self.board_frame.destroy()
        self._draw_board()

    def _draw_board(self):
        self.board_outline_width = max(GUI.MIN_BOARD_OUTLINE_WIDTH,
                                       min(self.board_width, self.board_height)
                                       * GUI.BOARD_OUTLINE_RATIO // 1)
        self.tile_padding = self.tile_size * GUI.TILE_PADDING_RATIO // 1

        self.board_frame = tk.Frame(self.root_frame, width=self.board_width,
                                    height=self.board_height,
                                    highlightcolor=self.board_outline_color,
                                    highlightbackground=self.board_outline_color,
                                    highlightthickness=self.board_outline_width)
        self.board_frame.place(anchor="center", relx=0.5,
                               rely=0.5 + GUI.BOARD_TOP_EXTRA_MARGIN / 2)
        self.board_canvas = tk.Canvas(self.board_frame, width=self.board_width,
                                      height=self.board_height)
        self.board_canvas.pack()

        self.state_label.place(anchor="center", relx=0.5, rely=GUI.BOARD_TOP_EXTRA_MARGIN / 2)

        board = self.game.get_board()
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                self.board_canvas.create_rectangle(col * self.tile_size, row * self.tile_size,
                                                   (col + 1) * self.tile_size,
                                                   (row + 1) * self.tile_size,
                                                   fill=self.tile_bg_color,
                                                   outline=self.tile_outline_color,
                                                   tags=("tile_part"))
                self._draw_circle(row, col, self.player_colors[board[row][col]])
        self.board_canvas.tag_bind("tile_part", "<Button-1>", self._on_tile_click)
        self.root.update()

    def update_tile(self, row: int, col: int) -> None:
        """ Update the tile at the given row and column according to the game state.

        Args:
            row (int): The row of the tile to update.
            col (int): The column of the tile to update.
        """

        self.board_canvas.delete("circle_{}_{}".format(row, col))
        self._draw_circle(row, col, self.player_colors[self.game.get_tile(row, col)])

    def _draw_circle(self, row, col, color) -> None:
        x0 = col * self.tile_size + self.tile_padding
        y0 = row * self.tile_size + self.tile_padding
        x1 = (col + 1) * self.tile_size - self.tile_padding
        y1 = (row + 1) * self.tile_size - self.tile_padding
        self.board_canvas.create_oval(x0, y0, x1, y1, fill=color, outline="",
                                      tags=("tile_part", "circle_{}_{}".format(row, col)))

    def _on_tile_click(self, event: tk.Event) -> None:
        col = event.x // self.tile_size
        if 0 <= col < self.n_cols and self.game.player_turn not in self.game.bots:
            self.game.place(col)

    def set_state_label(self, text: str, player: int = -1) -> None:
        """ Set the text of the state label and color it according to the player.

        Args:
            text (str): The text to set.
            player (int, optional): The id of the player to color the text with.
                    Defaults to 0 for DRAW_COLOR.
        """

        color = self.draw_color if player == -1 else self.player_colors[player]
        self.state_label.config(text=text, foreground=color)

    def disable_board(self):
        """ Disable placing new tiles on the board by unbinding the tile click event. """

        self.board_canvas.tag_unbind("tile_part", "<Button-1>")


class MainMenu:
    TITLE_TEXT = "Connect 4 Menu"
    CONNECT_TEXT = "Connect"
    SETTINGS_LABEL_TEXT = "Settings"
    GENERAL_SETTINGS_LABEL_TEXT = "General settings"
    UI_SETTINGS_LABEL_TEXT = "UI settings"
    BOT_SETTINGS_LABEL_TEXT = "Bot settings"
    SETTINGS_TEXTS = {
        "n_cols": "Number of columns",
        "n_rows": "Number of rows",
        "n_connect": "Number of tiles to connect",
        "n_players": "Number of players",
        "dark_mode": "Dark mode",
    }
    PLAYER_TEXT = "Player"
    ASSIGNED_BOT_TEXT = "Assigned bot:"
    START_GAME_TEXT = "PLAY"
    BOT_EXPLANATION_TEXT = "The strong solver " \
                           "prioritizes faster wins (or slower losses) The number " \
                           "after the bot name is the maximum depth of the search tree (higher " \
                           "is better but slower)."

    # value = (min, default, max)
    GENERAL_SETTINGS = {
        "n_players": (2, 2, 9),
        "n_connect": (2, 4, 10),
        "n_rows": (2, 6, 10),
        "n_cols": (2, 7, 10),
    }

    INFINITY = 999
    MAX_PLAYERS = GENERAL_SETTINGS["n_players"][2]

    BG_COLOR = "#909090"
    LABEL_FONT = "TkDefaultFont 40 bold"
    SETTINGS_FONT = "TkDefaultFont 10"
    SETTINGS_FONT_BOLD = "TkDefaultFont 10 bold"
    GAME_START_FONT = "TkDefaultFont 20 bold"
    RED = "red"
    YELLOW = "yellow"

    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 600
    MIN_WINDOW_WIDTH = 450
    MIN_WINDOW_HEIGHT = 500
    TITLE_REL_Y = 0.15
    TITLE_SETTINGS_SEP_REL_Y = 0.25
    TITLE_SETTINGS_SEP_REL_WIDTH = 0.8
    SETTINGS_TOP_REL_Y = 0.3
    SETTINGS_BOTTOM_REL_Y = 0.75
    SETTINGS_REL_WIDTH = 0.7
    SETTINGS_PAD_X = 15
    START_GAME_REL_Y = 0.85
    GAME_START_REL_WIDTH = 0.3
    GAME_START_REL_HEIGHT = 0.1
    HORIZONTAL_SEP_PAD_Y = 10
    SETTINGS_GROUP1_COLS = 3
    SETTINGS_GROUP2_COLS = 2

    def __init__(self):
        # Root window widget
        self.root = tk.Tk()
        self.root.title(MainMenu.TITLE_TEXT)
        self.root.geometry("{}x{}".format(MainMenu.WINDOW_WIDTH, MainMenu.WINDOW_HEIGHT))
        self.root.minsize(MainMenu.MIN_WINDOW_WIDTH, MainMenu.MIN_WINDOW_HEIGHT)
        self.root.config(bg=MainMenu.BG_COLOR)

        # Title label
        self.title_frame = tk.Frame(self.root)
        self.title_frame.config(bg=MainMenu.BG_COLOR)
        self.title_frame.place(anchor="center", relx=0.5, rely=MainMenu.TITLE_REL_Y)
        tk.Label(self.title_frame, text=MainMenu.CONNECT_TEXT + " ", font=MainMenu.LABEL_FONT,
                 bg=MainMenu.BG_COLOR, fg=MainMenu.YELLOW).pack(side="left")
        self.title_label_num = tk.Label(self.title_frame, text="4", font=MainMenu.LABEL_FONT,
                                        bg=MainMenu.BG_COLOR, fg=MainMenu.RED)
        self.title_label_num.pack(side="left")

        # Settings
        ## Variables
        self.settings_scale = {}
        self.settings_var: tp.Dict[str, tp.Any] = {}
        for key, (min_val, default_val, max_val) in MainMenu.GENERAL_SETTINGS.items():
            self.settings_var[key] = tk.IntVar(value=default_val)
        self.dark_mode_var = tk.BooleanVar(value=False)
        self.currently_selected_player = tk.StringVar()
        self.currently_selected_bot = tk.StringVar()
        self.assigned_bots: tp.Dict[int, tp.Optional['Bot']] = {}

        ## Styles
        self.scale_style = ttk.Style()
        self.scale_style.configure("TScale", background=MainMenu.BG_COLOR)
        self.toggle_style = ttk.Style()
        self.toggle_style.configure("TCheckbutton", background=MainMenu.BG_COLOR)

        ## Frame
        self.settings_frame = tk.Frame(self.root)
        self.settings_frame.pack(fill="both", expand=True)
        self.settings_frame.config(bg=MainMenu.BG_COLOR, highlightthickness=0)
        settings_rel_height = MainMenu.SETTINGS_BOTTOM_REL_Y - MainMenu.SETTINGS_TOP_REL_Y
        self.settings_frame.place(anchor="nw", rely=MainMenu.SETTINGS_TOP_REL_Y,
                                  relx=(1 - MainMenu.SETTINGS_REL_WIDTH) / 2,
                                  relwidth=MainMenu.SETTINGS_REL_WIDTH,
                                  relheight=settings_rel_height)
        self.settings_frame.grid_columnconfigure(0, weight=1, pad=MainMenu.SETTINGS_PAD_X)
        self.settings_frame.grid_columnconfigure(1, weight=5, pad=MainMenu.SETTINGS_PAD_X)
        self.settings_frame.grid_columnconfigure(2, weight=0, pad=MainMenu.SETTINGS_PAD_X)
        self.settings_frame.grid_columnconfigure(3, weight=0, pad=MainMenu.SETTINGS_PAD_X)
        self.settings_frame.grid_columnconfigure(4, weight=2, pad=MainMenu.SETTINGS_PAD_X)
        self.settings_frame.grid_columnconfigure(5, weight=0, pad=MainMenu.SETTINGS_PAD_X)

        settings_header_rows = 0

        ## Separator between title and settings
        ttk.Separator(self.settings_frame, orient="horizontal"
                      ).grid(row=settings_header_rows, column=0, columnspan=MainMenu.INFINITY,
                             sticky="ew", pady=MainMenu.HORIZONTAL_SEP_PAD_Y)
        settings_header_rows += 1

        ## Label
        tk.Label(self.settings_frame, fg=MainMenu.YELLOW, anchor="center", bg=MainMenu.BG_COLOR,
                 font=MainMenu.SETTINGS_FONT_BOLD, text=MainMenu.SETTINGS_LABEL_TEXT
                 ).grid(row=settings_header_rows, column=0,
                        columnspan=MainMenu.INFINITY, sticky="nsew")
        settings_header_rows += 1
        ttk.Separator(self.settings_frame, orient="horizontal"
                      ).grid(row=settings_header_rows, column=0, columnspan=MainMenu.INFINITY,
                             sticky="ew", pady=MainMenu.HORIZONTAL_SEP_PAD_Y)
        settings_header_rows += 1

        ## General Settings
        row = settings_header_rows
        tk.Label(self.settings_frame, fg=MainMenu.RED, anchor="w", bg=MainMenu.BG_COLOR,
                 font=MainMenu.SETTINGS_FONT_BOLD, text=MainMenu.GENERAL_SETTINGS_LABEL_TEXT
                 ).grid(row=row, column=0, columnspan=MainMenu.SETTINGS_GROUP1_COLS,
                        sticky="nsew")
        row += 1
        for key, (min_val, default_val, max_val) in MainMenu.GENERAL_SETTINGS.items():
            tk.Label(self.settings_frame, anchor="w", text=MainMenu.SETTINGS_TEXTS[key],
                     font=MainMenu.SETTINGS_FONT, bg=MainMenu.BG_COLOR, fg=MainMenu.YELLOW
                     ).grid(row=row, column=0, sticky="nsew")
            self.settings_scale[key] = ttk.Scale(self.settings_frame, from_=min_val, to=max_val,
                                                 orient="horizontal",
                                                 variable=self.settings_var[key],
                                                 command=(lambda val, key=key: # type: ignore
                                                          self._handle_scale(val, key)),
                                                 style="TScale")
            self.settings_scale[key].set(default_val)
            self.settings_scale[key].grid(row=row, column=1, sticky="nsew")
            tk.Label(self.settings_frame, anchor="center", textvariable=self.settings_var[key],
                     font=MainMenu.SETTINGS_FONT_BOLD, bg=MainMenu.BG_COLOR, fg=MainMenu.RED
                     ).grid(row=row, column=2, sticky="nsew")
            row += 1
        general_settings_rows = row - settings_header_rows

        ## Light / Dark mode
        row = settings_header_rows + general_settings_rows
        ttk.Separator(self.settings_frame, orient="horizontal"
                      ).grid(row=row, column=0, sticky="ew", pady=MainMenu.HORIZONTAL_SEP_PAD_Y,
                             columnspan=MainMenu.SETTINGS_GROUP1_COLS)
        row += 1
        tk.Label(self.settings_frame, fg=MainMenu.RED, anchor="w", bg=MainMenu.BG_COLOR,
                 font=MainMenu.SETTINGS_FONT_BOLD, text=MainMenu.UI_SETTINGS_LABEL_TEXT
                 ).grid(row=row, column=0, columnspan=MainMenu.INFINITY, sticky="nsew")
        row += 1
        tk.Label(self.settings_frame, anchor="w", text=MainMenu.SETTINGS_TEXTS["dark_mode"],
                 font=MainMenu.SETTINGS_FONT, bg=MainMenu.BG_COLOR, fg=MainMenu.YELLOW
                 ).grid(row=row, column=0, sticky="nsew")
        ttk.Checkbutton(self.settings_frame, variable=self.dark_mode_var
                        ).grid(row=row, column=1, sticky="nsew")
        row += 1
        group1_rows = row - settings_header_rows

        ## Bots
        row = settings_header_rows
        start_col = MainMenu.SETTINGS_GROUP1_COLS + 1
        tk.Label(self.settings_frame, fg=MainMenu.RED, anchor="w", bg=MainMenu.BG_COLOR,
                 font=MainMenu.SETTINGS_FONT_BOLD, text=MainMenu.BOT_SETTINGS_LABEL_TEXT
                 ).grid(row=row, column=start_col, columnspan=MainMenu.SETTINGS_GROUP2_COLS,
                        sticky="nsew")
        row += 1
        tk.Label(self.settings_frame, anchor="w", text=MainMenu.PLAYER_TEXT,
                 font=MainMenu.SETTINGS_FONT, bg=MainMenu.BG_COLOR, fg=MainMenu.YELLOW
                 ).grid(row=row, column=start_col, sticky="nsew")
        self.player_selector = ttk.OptionMenu(self.settings_frame, self.currently_selected_player,
                                              *range(1, MainMenu.MAX_PLAYERS + 1))
        self.player_selector.grid(row=row, column=start_col + 1, sticky="nsew")
        row += 1
        tk.Label(self.settings_frame, anchor="w", text=MainMenu.ASSIGNED_BOT_TEXT,
                 font=MainMenu.SETTINGS_FONT, bg=MainMenu.BG_COLOR, fg=MainMenu.YELLOW
                 ).grid(row=row, column=start_col, columnspan=MainMenu.SETTINGS_GROUP2_COLS,
                        sticky="nsew")
        row += 1
        self.bot_selector = ttk.OptionMenu(self.settings_frame, self.currently_selected_bot,
                                           list(BOT_OPTIONS.keys())[0], *BOT_OPTIONS.keys(),
                                           command=self._handle_bot_assigment)
        self.bot_selector.grid(row=row, column=start_col, sticky="nsew",
                               columnspan=MainMenu.SETTINGS_GROUP2_COLS)
        row += 1
        tk.Label(self.settings_frame, anchor="w", text=MainMenu.BOT_EXPLANATION_TEXT,
                    font=MainMenu.SETTINGS_FONT, bg=MainMenu.BG_COLOR, fg=MainMenu.RED,
                    wraplength=400 * MainMenu.SETTINGS_REL_WIDTH, justify="left"
                    ).grid(row=row, column=start_col, columnspan=MainMenu.SETTINGS_GROUP2_COLS,
                            sticky="nsew")
        group2_rows = row - settings_header_rows

        ## Separator between general, ui and bot settings
        ttk.Separator(self.settings_frame, orient="vertical"
                      ).grid(row=settings_header_rows, column=MainMenu.SETTINGS_GROUP1_COLS,
                             rowspan=max(group1_rows, group2_rows), sticky="ns")

        ## Separator between settings and start game button
        row = settings_header_rows + max(group1_rows, group2_rows)
        ttk.Separator(self.settings_frame, orient="horizontal"
                      ).grid(row=row, column=0, columnspan=MainMenu.INFINITY,
                             sticky="ew", pady=MainMenu.HORIZONTAL_SEP_PAD_Y)

        # Start button
        tk.Button(self.root, text=MainMenu.START_GAME_TEXT, font=MainMenu.GAME_START_FONT,
                  bg=MainMenu.YELLOW, fg=MainMenu.RED, command=self._start_game
                  ).place(anchor="center", relx=0.5, rely=MainMenu.START_GAME_REL_Y,
                          relwidth=MainMenu.GAME_START_REL_WIDTH,
                          relheight=MainMenu.GAME_START_REL_HEIGHT)

        # Run the main loop
        self.root.mainloop()


    def _start_game(self):
        settings = {key: var.get() for key, var in self.settings_var.items()}
        title = MainMenu.CONNECT_TEXT + " " + str(settings["n_connect"])
        if self.dark_mode_var.get():
            for key, val in GUI.DARK_MODE.items():
                settings[key] = val
        self.root.destroy()
        bots = {player: bot for player, bot in self.assigned_bots.items()
                if bot is not None}
        Game(window_title=title, bots=bots, **settings) # type: ignore

    def _handle_scale(self, val, key):
        int_val = int(float(val))
        self.settings_var[key].set(int_val)
        if key == "n_connect":
            self.title_label_num.config(text=str(int_val))
        elif key in ("n_cols", "n_rows"):
            n_connect = int(float(self.settings_var["n_connect"].get()))
            n_rows = int(float(self.settings_var["n_rows"].get()))
            n_cols = int(float(self.settings_var["n_cols"].get()))
            self.settings_var["n_connect"].set(min(n_connect, max(n_rows, n_cols)))
            self.settings_scale["n_connect"].config(to=max(n_rows, n_cols))
            self.title_label_num.config(text=str(min(n_connect, max(n_rows, n_cols))))

    def _handle_bot_assigment(self, bot_name):
        player = int(self.currently_selected_player.get())
        self.assigned_bots[player] = BOT_OPTIONS[bot_name]


#############################################################
#                    GAME IMPLEMENTATION                    #
#############################################################


def board_to_board_id(board: tp.List[tp.List[int]], n_players: int) -> int:
    """ Convert a game board to a unique integer id.

    Args:
        board (tp.List[tp.List[int]]): The board to convert.
        n_players (int): The number of players in the game.

    Returns:
        int: The unique integer id of the board.
    """

    board_id = 0
    for row in range(len(board) - 1, -1, -1):
        for col in range(len(board[0]) - 1, -1, -1):
            board_id = board_id * (n_players + 1) + board[row][col]
    return board_id


class BaseGame:
    def __init__(self, n_cols: int = 7, n_rows: int = 6, n_connect: int = 4, n_players: int = 2,
                 game_state: tp.Optional[GameState] = None):
        """ Initialize the game.

        Args:
            n_cols (int, optional): The number of columns in the game board. Defaults to 7.
                    Must be at least 2.
            n_rows (int, optional): The number of rows in the game board. Defaults to 6.
                    Must be at least 2.
            n_connect (int, optional): The number of tiles a player needs to connect to win.
                    Defaults to 4. Must be at least 2 and at most max(n_cols, n_rows).
                    Should be greater than 2, unless there are really many players.
            n_players (int, optional): The number of players in the game. Defaults to 2.
            game_state (tp.Optional[GameState], optional):
                    The state of the game to start from. Defaults to None for a new game.
                    The tuple should contain the board id, heights, and the player turn.
                    The board id can be obtained using the board_to_board_id function.
                    The heights should be a list of integers representing the height of each
                    column (from left to right). The player turn should be the id of the player
                    whose turn it is.
        """

        assert n_cols >= 2 and n_rows >= 2 and n_players >= 2
        assert 2 <= n_connect <= max(n_cols, n_rows)

        self.n_cols = n_cols
        self.n_rows = n_rows
        self.n_connect = n_connect
        self.n_players = n_players
        self.heights = [0 for _ in range(n_cols)]
        self.player_turn = 0
        self.total_moves = 0
        self.board_id = 0
        self.player_masked_board_ids = [0] * (n_players + 1)

        position_multipliers = [1] * (n_cols * n_rows)
        for i in range(1, n_cols * n_rows):
            position_multipliers[i] = position_multipliers[i - 1] * (n_players + 1)
        self.position_multipliers = [
            position_multipliers[row * n_cols: (row + 1) * n_cols]
            for row in range(n_rows)
        ]

        if game_state is not None:
            self.board_id, self.heights, self.player_turn = game_state
            self.total_moves = sum(height for height in self.heights)
            board = self.get_board()
            for row in range(n_rows):
                for col in range(n_cols):
                    position_shift = row * n_cols + col
                    self.player_masked_board_ids[board[row][col]] |= 1 << position_shift

    def get_board(self) -> tp.List[tp.List[int]]:
        """ Get the current state of the game board.

        Returns:
            tp.List[tp.List[int]]: The board as a list of rows (from top to bottom),
                    each row being a list of integers (from left to right) representing
                    the player id of the tile in that position (0 for empty).
        """

        board = [[0 for _ in range(self.n_cols)] for _ in range(self.n_rows)]
        board_id = self.board_id
        for row in range(self.n_rows - 1, -1, -1):
            for col in range(self.n_cols - 1, -1, -1):
                board[row][col] = board_id // self.position_multipliers[row][col]
                board_id %= self.position_multipliers[row][col]

        return board


    def get_tile(self, row: int, col: int) -> int:
        """ Get the player id of the tile at the given position.

        Args:
            row (int): The row of the tile.
            col (int): The column of the tile.

        Returns:
            int: The player id of the tile (0 for empty).
        """

        position_multiplier = self.position_multipliers[row][col]
        next_position_multiplier = position_multiplier * (self.n_players + 1)
        return (self.board_id % next_position_multiplier) // position_multiplier


    def place(self, col: int) -> TurnResult:
        """ Place a tile in the given column and update the game state.

        Args:
            col (int): The column to place the tile in.

        Returns:
            TurnResult: The result of the turn (win, draw, ok, invalid).
        """

        row = self.n_rows - self.heights[col] - 1
        if row < 0:
            return TurnResult.INVALID
        self.total_moves += 1
        self.heights[col] += 1
        self.board_id += self.player_turn * self.position_multipliers[row][col]
        self.player_masked_board_ids[self.player_turn] |= 1 << (row * self.n_cols + col)

        if self._check_win(row, col, self.player_turn):
            return self.game_win(self.player_turn)
        elif self._check_draw():
            return self.game_draw()
        else:
            return self._next_turn()

    @abstractmethod
    def _next_turn(self) -> TurnResult.OK:
        pass

    @abstractmethod
    def game_win(self, player: int) -> TurnResult.WIN:
        pass

    @abstractmethod
    def game_draw(self) -> TurnResult.DRAW:
        pass

    def _check_win(self, row: int, col: int, player: int) -> bool:
        """ Check if the given player has won the game by placing a tile in the given position.

        Args:
            row (int): The row of the placed tile.
            col (int): The column of the placed tile.
            player (int): The id of the player that placed the tile.

        Returns:
            bool: True if the player has won, False otherwise.
        """

        # TODO: Optimize this

        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for i in range(1, self.n_connect):
                r = row + i * dr
                c = col + i * dc
                if (0 <= r < self.n_rows and 0 <= c < self.n_cols
                        and self.player_masked_board_ids[player] & (1 << (r * self.n_cols + c))):
                    count += 1
                else:
                    break
            for i in range(1, self.n_connect):
                r = row - i * dr
                c = col - i * dc
                if (0 <= r < self.n_rows and 0 <= c < self.n_cols
                        and self.player_masked_board_ids[player] & (1 << (r * self.n_cols + c))):
                    count += 1
                else:
                    break
            if count >= self.n_connect:
                return True
        return False

    def _check_draw(self) -> bool:
        """ Check if the game has ended in a draw. """

        return self.total_moves == self.n_cols * self.n_rows


class Game(BaseGame):
    """ The main class for the Connect 4 game. """

    def __init__(self, n_cols: int = 7, n_rows: int = 6, n_connect: int = 4, n_players: int = 2,
                 bots: tp.Dict[int, "Bot"] = {}, game_state: tp.Optional[GameState] = None,
                 **gui_kwargs):
        """ Initialize the game and start the GUI.

        Args:
            n_cols (int, optional): The number of columns in the game board. Defaults to 7.
            n_rows (int, optional): The number of rows in the game board. Defaults to 6.
            n_connect (int, optional): The number of tiles a player needs to connect to win.
                    Defaults to 4.
            n_players (int, optional): The number of players in the game. Defaults to 2.
            bots (tp.Dict[int, Bot], optional): A dictionary mapping player ids to
                    bot objects. Defaults to {} for no bots. The same bot can be used
                    for multiple players.
            game_state (tp.Optional[GameState], optional):
                    The state of the game to start from. Defaults to None for a new game.
                    See BaseGame class for details.
            **gui_kwargs: Additional keyword arguments to pass to the GUI constructor.
                    See GUI class.
        """

        super().__init__(n_cols, n_rows, n_connect, n_players)
        self.bots = bots
        for bot in bots.values():
            if isinstance(bot, CachingAlphaBetaBot):
                bot.init_from_game(self)
        self.gui = GUI(self, **gui_kwargs)
        if game_state is not None:
            self.gui.redraw_board()
        self._next_turn()
        self.gui.root.mainloop()

    def place(self, col: int) -> TurnResult:
        """ Place a tile in the given column and update the game state.

        Args:
            col (int): The column to place the tile in.

        Returns:
            TurnResult: The result of the turn (win, draw, ok, invalid).
        """

        res = super().place(col)
        if res:
            self.gui.update_tile(self.n_rows - self.heights[col], col)
        return res

    def _next_turn(self) -> TurnResult.OK:
        """ Internal method to handle updating the turn to the next player.
            Is only called after a valid non-game-ending move.

        Returns:
            TurnResult.OK: The result of the turn (the turn was successful, no win or draw).
        """

        self.player_turn = self.player_turn % self.n_players + 1
        self._update_turn_label()
        if self.player_turn in self.bots:
            self.gui.root.after(10, self.bots[self.player_turn].make_move, self)
        return TurnResult.OK

    def _update_turn_label(self) -> None:
        if self.player_turn not in self.bots:
            text = GUI.TURN_TEXT.format(self.player_turn)
        else:
            text = GUI.BOT_TURN_TEXT.format(self.player_turn)
        self.gui.set_state_label(text, self.player_turn)

    def game_win(self, player: int) -> TurnResult.WIN:
        """ Handle the game being won by a player.

        Args:
            player (int): The id of the player that won.

        Returns:
            TurnResult.WIN: The result of the game.
        """

        self.gui.set_state_label(GUI.WIN_TEXT.format(player), player)
        self.end_game()
        return TurnResult.WIN

    def game_draw(self) -> TurnResult.DRAW:
        """ Handle the game ending in a draw.

        Returns:
            TurnResult.DRAW: The result of the game.
        """

        self.gui.set_state_label(GUI.DRAW_TEXT)
        self.end_game()
        return TurnResult.DRAW

    def end_game(self) -> None:
        """ End the game by disabling the board. """

        self.gui.disable_board()


#############################################################
#                    BOT IMPLEMENTATIONS                    #
#############################################################

class Bot:
    """ Base class for all bots. """

    def make_move(self, game: BaseGame) -> None:
        """ Make a bot move in the game. Prints the time taken to compute the move
            in milliseconds to stdout. The actual move is computed and made in the
            _make_move method that has to be implemented by the bot subclass.

            Args:
                game (BaseGame): The game instance to make a move in.
        """

        start_time = time_ns()
        self._make_move(game)
        print("Real time elapsed while computing bot move:", (time_ns() - start_time) / 1e6, "ms")

    @abstractmethod
    def _make_move(self, game: BaseGame) -> None:
        pass


class RandomBot(Bot):
    """ A bot that makes random valid moves. """

    def _make_move(self, game: BaseGame) -> None:
        while not game.place(randint(0, game.n_cols - 1)):
            pass

class CachingAlphaBetaBot(Bot):
    """ A bot that uses the Alpha-Beta Pruning modified Minimax algorithm to make moves.
        This bot is able to play in games with more than 2 players. It caches some of the
        results of the search to speed up the computation using a least-recently-used cache. """

    def __init__(self, max_depth: int = -1, cache_max_size: int = 5 * 10**6,
                 initial_alpha: Num = -float("inf"), initial_beta: Num = float("inf")):
        """ Create a new bot instance.

            Args:
                max_depth (int, optional): The maximum depth of the search tree to explore.
                        Defaults to -1 for no limit.
                cache_max_size (int, optional): The maximum number of results to cache.
                        Defaults to 5 million. Uses a least-recently-used cache.
                default_alpha (Num, optional): The initial value of alpha for alpha-beta pruning.
                        Defaults to -inf. Use -1 for a weak solver.
                default_beta (Num, optional): The initial value of beta for alpha-beta pruning.
                        Defaults to inf. Use 1 for a weak solver.
        """

        self.max_depth = max_depth
        self.initial_alpha = initial_alpha
        self.initial_beta = initial_beta
        self._explore = lru_cache(maxsize=cache_max_size)(self._explore_unwrapped)

    def init_from_game(self, game: BaseGame) -> None:
        """ Initialize the bot from a game instance.
            Must be called before making any moves. Use again if the bot should play in a new game
            with different parameters (board size, number of players, number of tiles to connect).

            Args:
                game (BaseGame): The game instance to initialize the bot from.
        """

        self.position_multipliers = game.position_multipliers
        self.n_connect = game.n_connect
        self.n_players = game.n_players
        self.n_cols = game.n_cols
        self.n_rows = game.n_rows
        self._explore.cache_clear()

    def make_move(self, game: BaseGame) -> None:
        super().make_move(game)
        print("Cache info:", self._explore.cache_info())

    def _make_move(self, game: BaseGame) -> None:
        self.heights = game.heights
        self.player_turn = game.player_turn
        self.total_moves = game.total_moves
        self.player_masked_board_ids = game.player_masked_board_ids

        remaining_depth = min(self.max_depth, game.n_cols * game.n_rows - game.total_moves)
        _, _, col = self._explore(game.board_id, remaining_depth)

        del self.heights, self.player_turn, self.total_moves, self.player_masked_board_ids
        assert col != -1
        game.place(col)

    def _simulation_place(self, board_id: int, col: int) -> tp.Tuple[int, int]:
        row = self.n_rows - self.heights[col] - 1
        if row < 0:
            return row, board_id
        self.total_moves += 1
        self.heights[col] += 1
        board_id += self.player_turn * self.position_multipliers[row][col]
        self.player_masked_board_ids[self.player_turn] |= 1 << (row * self.n_cols + col)
        self.player_turn = self.player_turn % self.n_players + 1
        return row, board_id

    def _simulation_undo_turn(self, board_id: int, col: int) -> int:
        row = self.n_rows - self.heights[col]
        self.total_moves -= 1
        self.heights[col] -= 1
        self.player_turn = self.player_turn - 1 if self.player_turn > 1 else self.n_players
        board_id -= self.player_turn * self.position_multipliers[row][col]
        self.player_masked_board_ids[self.player_turn] -= 1 << (row * self.n_cols + col)
        return board_id
    
    def _check_win(self, row: int, col: int, player: int) -> bool:
        """ Check if the given player has won the game by placing a tile in the given position.

        Args:
            row (int): The row of the placed tile.
            col (int): The column of the placed tile.
            player (int): The id of the player that placed the tile.

        Returns:
            bool: True if the player has won, False otherwise.
        """

        masked_board_id = self.player_masked_board_ids[player]

        # TODO: Optimize this - profiling shows that this is the most time-consuming function

        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for i in range(1, self.n_connect):
                r = row + i * dr
                c = col + i * dc
                if (0 <= r < self.n_rows and 0 <= c < self.n_cols
                        and masked_board_id & (1 << (r * self.n_cols + c))):
                    count += 1
                else:
                    break
            for i in range(1, self.n_connect):
                r = row - i * dr
                c = col - i * dc
                if (0 <= r < self.n_rows and 0 <= c < self.n_cols
                        and masked_board_id & (1 << (r * self.n_cols + c))):
                    count += 1
                else:
                    break
            if count >= self.n_connect:
                return True
        return False

    def _explore_unwrapped(self, board_id: int, remaining_depth: int,
                alpha: tp.Optional[Num] = None,
                beta: tp.Optional[Num] = None) -> tp.Tuple[Num, int, int]:
        """ Recursively explore the game tree using the Alpha-Beta Pruning
            modified Minimax algorithm. Caches some of the results to speed up computation.

        Args:
            simulation (BotSimulationGame): An instance of the game to explore.
            depth (int): The depth of the search tree to explore.
            alpha (tp.Optional[Num], optional): Internal parameter for alpha-beta pruning.
                    Defaults to None for the default value of DEFAULT_ALPHA.
            beta (tp.Optional[Num], optional): Internal parameter for alpha-beta pruning.
                    Defaults to None for the default value of DEFAULT_BETA.

        Returns:
            tp.Tuple[Num, int, int]: The absolute value of the score of the best move found,
                    the player id that is expected to win (has the returned score) or 0 if a draw
                    is expected or the search was cut off, and the column of the move.
        """

        if alpha is None or beta is None:
            alpha = self.initial_alpha
            beta = self.initial_beta
        assert alpha < beta

        if remaining_depth == 0:
            return 0, 0, -1
        elif remaining_depth == -1:
            remaining_depth = 0 # So it will be -1 again in the nested calls (for proper caching)

        turn_idx = self.total_moves

        n_rows = self.n_rows
        n_cols = self.n_cols
        current_turn = self.player_turn

        score_if_win = n_cols * n_rows - turn_idx
        for col in range(n_cols):
            row, board_id = self._simulation_place(board_id, col)
            if row < 0:
                continue
            is_winning = self._check_win(row, col, current_turn)
            is_last_move = self.total_moves == n_cols * n_rows
            board_id = self._simulation_undo_turn(board_id, col)
            if is_winning:
                # The game is won by this move
                return score_if_win, current_turn, col
            elif is_last_move:
                # If the last move (before filling the board) doesn't win the game, it is a draw
                return 0, 0, col

        best_possible_score = score_if_win - self.n_players
        if best_possible_score < beta:
            beta = best_possible_score # No need to search for moves with impossibly high scores
            if alpha >= beta:
                # The search window is empty, prune the search
                return beta, 0, -1

        best_score, best_player, best_col = -float("inf"), 0, -1
        for offset in range((n_cols + 1) // 2):
            left = (n_cols - 1) // 2 - offset
            right = (n_cols + 1) // 2 + offset
            for col in ([left, right] if right < n_cols else [left]):
                row, board_id = self._simulation_place(board_id, col)
                if row < 0:
                    continue
                score, player, _ = self._explore(board_id, remaining_depth - 1, -beta, -alpha)
                if player != current_turn:
                    score = -score
                board_id = self._simulation_undo_turn(board_id, col)

                if score > best_score:
                    best_score, best_player, best_col = score, player, col
                alpha = max(alpha, score)
                if score >= beta:
                    # Found a move better than the highest score we are looking for
                    return abs(score), player, col
        return abs(best_score), best_player, best_col


BOT_OPTIONS = {
    "none (real player)": None,
    "random placer": RandomBot(),
    "strong solver 13": CachingAlphaBetaBot(max_depth=13),
    "strong solver 15": CachingAlphaBetaBot(max_depth=15),
    "strong solver 16": CachingAlphaBetaBot(max_depth=16),
    "strong solver 17": CachingAlphaBetaBot(max_depth=17),
    "strong solver 18": CachingAlphaBetaBot(max_depth=18),
    "strong solver 19": CachingAlphaBetaBot(max_depth=19),
    "strong solver unlimited": CachingAlphaBetaBot(max_depth=-1),
    "weak solver 13": CachingAlphaBetaBot(max_depth=13, initial_alpha=-1, initial_beta=1),
    "weak solver 15": CachingAlphaBetaBot(max_depth=15, initial_alpha=-1, initial_beta=1),
    "weak solver 17": CachingAlphaBetaBot(max_depth=17, initial_alpha=-1, initial_beta=1),
    "weak solver 18": CachingAlphaBetaBot(max_depth=18, initial_alpha=-1, initial_beta=1),
    "weak solver 19": CachingAlphaBetaBot(max_depth=19, initial_alpha=-1, initial_beta=1),
    "weak solver 20": CachingAlphaBetaBot(max_depth=20, initial_alpha=-1, initial_beta=1),
    "weak solver 21": CachingAlphaBetaBot(max_depth=21, initial_alpha=-1, initial_beta=1),
    "weak solver unlimited": CachingAlphaBetaBot(max_depth=-1, initial_alpha=-1, initial_beta=1),
}


#############################################################
#                          TESTING                          #
#############################################################


if __name__ == "__main__":
    MainMenu()