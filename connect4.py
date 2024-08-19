import tkinter as tk
import typing as tp
import enum
from abc import abstractmethod
from random import randint
from time import time_ns


#############################################################
#              TYPE DEFINITIONS AND CONSTANTS               #
#############################################################


Side = tp.Literal[0, 1, 2, 3]
Num = tp.Union[int, float]
class TurnResult(enum.Enum):
    INVALID = 0
    WIN = 1
    DRAW = 2
    OK = 3

    def __bool__(self):
        return self != TurnResult.INVALID


NO_PLAYER = 0


#############################################################
#                    GUI IMPLEMENTATION                     #
#############################################################


class GUI:
    def __init__(self, game: 'Game', n_cols: int, n_rows: int, tile_size: int = 100,
                 tile_bg_color: str = "#909090", outline_color: str = "white",
                 window_bg_color: str = "#909090", player_colors: tp.Optional[tp.List[str]] = None):
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
        self.NO_PLAYER_COLOR = "white"
        self.DEFAULT_PLAYER_COLORS = ['red', 'yellow', 'blue', 'purple', 'green', 'cyan', 'maroon', 'pink', 'black']

        self.game = game
        self.n_cols = n_cols
        self.n_rows = n_rows
        self.tile_size = tile_size
        self.board_width = self.tile_size * n_cols - self.TILE_OUTLINE_WIDTH
        self.board_height = self.tile_size * n_rows - self.TILE_OUTLINE_WIDTH
        self.window_width = int(self.board_width * (1 + 2 * self.BOARD_MARGIN))
        self.window_height = int(self.board_height * (1 + 2 * self.BOARD_MARGIN
                                                      + self.BOARD_TOP_EXTRA_MARGIN))

        self.window_bg_color = window_bg_color
        self.tile_bg_color = tile_bg_color
        self.board_outline_color = outline_color
        self.tile_outline_color = outline_color
        if player_colors is None:
            self.player_color = [self.NO_PLAYER_COLOR, *self.DEFAULT_PLAYER_COLORS]
        else:
            self.player_color = [self.NO_PLAYER_COLOR, *player_colors]

        self.root = tk.Tk()
        self.root.title(self.WINDOW_TITLE)
        self.root.geometry("{}x{}".format(self.window_width, self.window_height))
        self.root.minsize(self.MIN_WINDOW_WIDTH, self.MIN_WINDOW_HEIGHT)
        self.root_frame = tk.Frame(self.root)
        self.root_frame.pack(fill="both", expand=True)
        self.root_frame.config(bg=self.window_bg_color)

        self.state_label = tk.Label(self.root_frame, text="Initializing...", font="TkDefaultFont 20 bold",
                                    bg=self.window_bg_color)
        self.state_label.pack(expand=True)

        self._draw_board()
        self.root.bind("<Configure>", self._resize_window)

    def _resize_window(self, event: tk.Event):
        if event.widget == self.root:
            self.window_width = event.width
            self.window_height = event.height
            self.root_frame.config(width=self.window_width, height=self.window_height)
            self.tile_size = min(int(event.width / (1 + 2 * self.BOARD_MARGIN)) // self.n_cols,
                                 int(event.height / (1 + 2 * self.BOARD_MARGIN
                                                     + self.BOARD_TOP_EXTRA_MARGIN)) // self.n_rows)
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

        self.state_label.place(anchor="center", relx=0.5, rely=self.BOARD_TOP_EXTRA_MARGIN / 2)

        for row in range(self.n_rows):
            for col in range(self.n_cols):
                self.board_canvas.create_rectangle(col * self.tile_size, row * self.tile_size,
                                                   (col + 1) * self.tile_size, (row + 1) * self.tile_size,
                                                   fill=self.tile_bg_color, outline=self.tile_outline_color,
                                                   tags=("tile_part"))
                if self.game.board[row][col] != 0:
                    self._draw_circle(row, col, self.player_color[self.game.board[row][col]])
        self.board_canvas.tag_bind("tile_part", "<Button-1>", self._on_tile_click)
        self.root.update()

    def update_tile(self, row, col):
        self._draw_circle(row, col, self.player_color[self.game.board[row][col]])

    def _draw_circle(self, row, col, color):
        x0 = col * self.tile_size + self.tile_padding
        y0 = row * self.tile_size + self.tile_padding
        x1 = (col + 1) * self.tile_size - self.tile_padding
        y1 = (row + 1) * self.tile_size - self.tile_padding
        self.board_canvas.create_oval(x0, y0, x1, y1, fill=color, outline="", tags=("tile_part"))

    def _on_tile_click(self, event: tk.Event):
        col = event.x // self.tile_size
        if 0 <= col < self.n_cols and self.game.player_turn not in self.game.bots:
            self.game.place(col)

    def set_state_label(self, text: str, player: int):
        self.state_label.config(text=text, foreground=self.player_color[player])

    def disable_board(self):
        self.board_canvas.tag_unbind("tile_part", "<Button-1>")


#############################################################
#                    GAME IMPLEMENTATION                    #
#############################################################


class BaseGame:
    def __init__(self, n_cols: int = 7, n_rows: int = 6, n_connect: int = 4,  n_players: int = 2):
        assert n_cols >= 2 and n_rows >= 2 and n_players >= 2
        assert 2 <= n_connect <= max(n_cols, n_rows)

        self.n_cols = n_cols
        self.n_rows = n_rows
        self.n_connect = n_connect
        self.n_players = n_players
        self.board = [[0 for _ in range(n_cols)] for _ in range(n_rows)]
        self.heights = [0 for _ in range(n_cols)]
        self.player_turn = 0
        self.total_moves = 0

    def place(self, col: int) -> TurnResult:
        row = self.n_rows - self.heights[col] - 1
        if row < 0:
            return TurnResult.INVALID
        self.total_moves += 1
        self.board[row][col] = self.player_turn
        self.heights[col] += 1
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
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for i in range(1, self.n_connect):
                r = row + i * dr
                c = col + i * dc
                if 0 <= r < self.n_rows and 0 <= c < self.n_cols and self.board[r][c] == player:
                    count += 1
                else:
                    break
            for i in range(1, self.n_connect):
                r = row - i * dr
                c = col - i * dc
                if 0 <= r < self.n_rows and 0 <= c < self.n_cols and self.board[r][c] == player:
                    count += 1
                else:
                    break
            if count >= self.n_connect:
                return True
        return False

    def _check_draw(self) -> bool:
        return self.total_moves == self.n_cols * self.n_rows


class Game(BaseGame):
    def __init__(self, n_cols: int = 7, n_rows: int = 6, n_connect: int = 4, n_players: int = 2,
                 bots: tp.Dict[int, tp.Type['Bot']] = {},
                 game_state: tp.Optional[tp.Tuple[tp.List[tp.List[int]], tp.List[int], int]] = None, **gui_kwargs):
        super().__init__(n_cols, n_rows, n_connect, n_players)
        self.bots = bots
        self.gui = GUI(self, n_cols, n_rows, **gui_kwargs)
        if game_state is not None:
            self.board, self.heights, self.player_turn = game_state
            self.total_moves = sum(height for height in self.heights)
            self.player_turn -= 1
            self.gui.redraw_board()
        self._next_turn()
        self.gui.root.mainloop()

    def place(self, col: int) -> TurnResult:
        res = super().place(col)
        self.gui.update_tile(self.n_rows - self.heights[col], col)
        return res

    def _next_turn(self) -> TurnResult.OK:
        self.player_turn = self.player_turn % self.n_players + 1
        self._update_turn_label()
        if self.player_turn in self.bots:
            self.gui.root.after(10, self.bots[self.player_turn].make_move, self)
        return TurnResult.OK

    def _update_turn_label(self):
        self.gui.set_state_label("Player {}'s turn".format(self.player_turn), self.player_turn)

    def game_win(self, player: int) -> TurnResult.WIN:
        self.gui.set_state_label("Player {} won!".format(player), player)
        self.end_game()
        return TurnResult.WIN

    def game_draw(self) -> TurnResult.DRAW:
        self.gui.set_state_label("It's a draw!", NO_PLAYER)
        self.end_game()
        return TurnResult.DRAW

    def end_game(self):
        self.gui.disable_board()


class BotSimulationGame(BaseGame):
    def __init__(self, n_cols: int = 7, n_rows: int = 6, n_connect: int = 4, n_players: int = 2):
        super().__init__(n_cols, n_rows, n_connect, n_players)

    def _next_turn(self) -> TurnResult.OK:
        self.player_turn = self.player_turn % self.n_players + 1
        return TurnResult.OK

    def game_win(self, player: int) -> TurnResult.WIN:
        return TurnResult.WIN
    
    def game_draw(self) -> TurnResult.DRAW:
        return TurnResult.DRAW
    
    def unplace(self, col: int) -> None:
        row = self.n_rows - self.heights[col]
        self.board[row][col] = 0
        self.heights[col] -= 1
        self.total_moves -= 1


#############################################################
#                    BOT IMPLEMENTATIONS                    #
#############################################################

class Bot:
    @classmethod
    def make_move(cls, game: BaseGame) -> None:
        start_time = time_ns()
        cls._make_move(game)
        print("Real time elapsed while computing bot move:", (time_ns() - start_time) / 1e6, "ms")

    @classmethod
    @abstractmethod
    def _make_move(cls, game: BaseGame) -> None:
        pass


class RandomBot(Bot):
    @classmethod
    def _make_move(cls, game: BaseGame) -> None:
        while not game.place(randint(0, game.n_cols - 1)):
            pass


class AlphaBetaNegamaxBot(Bot):
    DEPTH = 11
    DEFAULT_ALPHA = -float('inf')
    DEFAULT_BETA = float('inf')

    @classmethod
    def _make_move(cls, game: BaseGame) -> None:
        if game.n_players != 2:
            raise NotImplementedError("Only 2-player games are supported")

        test_game = BotSimulationGame(game.n_cols, game.n_rows, game.n_connect, game.n_players)
        test_game.board = [row.copy() for row in game.board]
        test_game.heights = game.heights.copy()
        test_game.player_turn = game.player_turn
        test_game.total_moves = game.total_moves
        _, col = cls.explore(test_game, cls.DEPTH)
        assert col != -1
        del test_game
        game.place(col)

    @classmethod
    def explore(cls, simulation: 'BotSimulationGame', depth: int,
                alpha: tp.Optional[Num] = None, beta: tp.Optional[Num] = None) -> tp.Tuple[Num, int]:
        if alpha is None or beta is None:
            alpha = cls.DEFAULT_ALPHA
            beta = cls.DEFAULT_BETA
        assert alpha < beta

        if depth == 0:
            return 0, -1

        current_turn = simulation.player_turn

        for col in range(simulation.n_cols):
            outcome = simulation.place(col)
            if outcome == TurnResult.INVALID:
                continue
            simulation.unplace(col)
            simulation.player_turn = current_turn
            if outcome == TurnResult.WIN:
                # The game is won by this move
                return simulation.n_cols * simulation.n_rows - simulation.total_moves, col
            elif outcome == TurnResult.DRAW:
                # If a move immediately leads to a draw, it has to be the only possible move
                return 0, col

        best_possible_score = (simulation.n_cols * simulation.n_rows
                               - simulation.total_moves - simulation.n_players)
        if best_possible_score < beta:
            beta = best_possible_score # No need to search for moves with impossibly high scores
            if alpha >= beta:
                # The search window is empty
                return beta, -1

        best_score, best_col = -float('inf'), -1
        for offset in range((simulation.n_cols + 1) // 2):
            left = (simulation.n_cols - 1) // 2 - offset
            right = (simulation.n_cols + 1) // 2 + offset
            for col in ([left, right] if right < simulation.n_cols else [left]):
                outcome = simulation.place(col)
                if outcome == TurnResult.INVALID:
                    continue
                assert outcome == TurnResult.OK
                score = - cls.explore(simulation, depth - 1, -beta, -alpha)[0]
                simulation.unplace(col)
                simulation.player_turn = current_turn
                if score > best_score:
                    best_score, best_col = score, col
                alpha = max(alpha, score)
                if score >= beta:
                    # Found a move better than the highest score we are looking for
                    return score, col
                if alpha >= beta:
                    # The search window is empty
                    assert False # Should never happen, we should have returned already
        return best_score, best_col


if __name__ == "__main__":
    # Game(bots={1:BruteForceBot, 2:BruteForceBot})
    # Game()
    board = [
        [0, 1, 2, 2, 1, 1, 0],
        [0, 2, 1, 1, 2, 2, 0],
        [0, 1, 2, 2, 1, 1, 1],
        [0, 2, 1, 1, 2, 2, 2],
        [0, 1, 2, 2, 1, 1, 2],
        [1, 2, 2, 1, 1, 1, 2]
    ]
    heights = [1, 6, 6, 6, 6, 6, 4]
    turn = 2
    # Game(bots={1:AlphaBetaOptimisedBot, 2:AlphaBetaOptimisedBot}, game_state=(board, heights, turn))
    Game(bots={1:AlphaBetaNegamaxBot, 2:AlphaBetaNegamaxBot})