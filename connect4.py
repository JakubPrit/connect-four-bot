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
GameState = tp.Tuple[tp.List[tp.List[int]], tp.List[int], int]


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
    def __init__(self, game: 'Game', tile_size: int = 100, tile_bg_color: str = "#909090",
                 outline_color: str = "white", window_bg_color: str = "#909090",
                 player_colors: tp.Optional[tp.List[str]] = None):
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
        """

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
        self.DEFAULT_PLAYER_COLORS = ['red', 'yellow', 'blue', 'purple', 'green',
                                      'cyan', 'maroon', 'pink', 'darkgreen', 'black']

        self.game = game
        self.n_cols = game.n_cols
        self.n_rows = game.n_rows
        self.tile_size = tile_size
        self.board_width = self.tile_size * game.n_cols - self.TILE_OUTLINE_WIDTH
        self.board_height = self.tile_size * game.n_rows - self.TILE_OUTLINE_WIDTH
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

        self.board_frame: tk.Frame
        self.board_canvas: tk.Canvas
        self.state_label = tk.Label(self.root_frame, text="Initializing...",
                                    font="TkDefaultFont 20 bold", bg=self.window_bg_color)
        self.state_label.pack(expand=True)

        self._draw_board()
        self.root.bind("<Configure>", self._resize_window)

    def _resize_window(self, event: tk.Event):
        if event.widget == self.root:
            self.window_width = event.width
            self.window_height = event.height
            self.root_frame.config(width=self.window_width, height=self.window_height)
            horizontal_margin = 2 * self.BOARD_MARGIN
            vertical_margin = 2 * self.BOARD_MARGIN + self.BOARD_TOP_EXTRA_MARGIN
            self.tile_size = min(int(event.width / horizontal_margin) // self.n_cols,
                                 int(event.height / vertical_margin) // self.n_rows)
            self.board_width = self.tile_size * self.n_cols - self.TILE_OUTLINE_WIDTH
            self.board_height = self.tile_size * self.n_rows - self.TILE_OUTLINE_WIDTH
            self.redraw_board()

    def redraw_board(self) -> None:
        """ Redraw the whole board.
            Note: _draw_board() has to be called at least once before this,
            it is done in __init__.
        """

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

    def update_tile(self, row: int, col: int) -> None:
        """ Update the tile at the given row and column according to the game state.

        Args:
            row (int): The row of the tile to update.
            col (int): The column of the tile to update.
        """

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
        """ Set the text of the state label and color it according to the player.

        Args:
            text (str): The text to set.
            player (int): The id of the player to color the text with.
        """

        self.state_label.config(text=text, foreground=self.player_color[player])

    def disable_board(self):
        """ Disable placing new tiles on the board by unbinding the tile click event. """

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
        """ Place a tile in the given column and update the game and gui states.

        Args:
            col (int): The column to place the tile in.

        Returns:
            TurnResult: The result of the turn (win, draw, ok, invalid).
        """

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
        """ Check if the given player has won the game by placing a tile in the given position.

        Args:
            row (int): The row of the placed tile.
            col (int): The column of the placed tile.
            player (int): The id of the player that placed the tile.

        Returns:
            bool: True if the player has won, False otherwise.
        """

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
        """ Check if the game has ended in a draw. """

        return self.total_moves == self.n_cols * self.n_rows


class Game(BaseGame):
    """ The main class for the Connect 4 game. """

    def __init__(self, n_cols: int = 7, n_rows: int = 6, n_connect: int = 4, n_players: int = 2,
                 bots: tp.Dict[int, tp.Type['Bot']] = {}, game_state: tp.Optional[GameState] = None,
                 **gui_kwargs):
        """ Initialize the game and start the GUI.

        Args:
            n_cols (int, optional): The number of columns in the game board. Defaults to 7.
            n_rows (int, optional): The number of rows in the game board. Defaults to 6.
            n_connect (int, optional): The number of tiles a player needs to connect to win.
                    Defaults to 4.
            n_players (int, optional): The number of players in the game. Defaults to 2.
            bots (tp.Dict[int, tp.Type[Bot]], optional): A dictionary mapping player ids to
                    bot classes. Defaults to {} for no bots.
            game_state (tp.Optional[GameState], optional):
                    The state of the game to start from. Defaults to None for a new game.
                    The tuple should contain the board, heights, and the player turn.
                    The board should be a list of rows (from top to bottom), each row being
                    a list of integers (from left to right) representing the player id
                    of the tile in that position (0 for empty). The heights should be a list
                    of integers representing the height of each column (from left to right).
                    The player turn should be the id of the player whose turn it is.
            **gui_kwargs: Additional keyword arguments to pass to the GUI constructor.
                    See GUI class.
        """

        super().__init__(n_cols, n_rows, n_connect, n_players)
        self.bots = bots
        self.gui = GUI(self, **gui_kwargs)
        if game_state is not None:
            self.board, self.heights, self.player_turn = game_state
            self.total_moves = sum(height for height in self.heights)
            self.player_turn -= 1
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
        self.gui.set_state_label("Player {}'s turn".format(self.player_turn), self.player_turn)

    def game_win(self, player: int) -> TurnResult.WIN:
        """ Handle the game being won by a player.

        Args:
            player (int): The id of the player that won.

        Returns:
            TurnResult.WIN: The result of the game.
        """

        self.gui.set_state_label("Player {} won!".format(player), player)
        self.end_game()
        return TurnResult.WIN

    def game_draw(self) -> TurnResult.DRAW:
        """ Handle the game ending in a draw.

        Returns:
            TurnResult.DRAW: The result of the game.
        """

        self.gui.set_state_label("It's a draw!", NO_PLAYER)
        self.end_game()
        return TurnResult.DRAW

    def end_game(self) -> None:
        """ End the game by disabling the board. """

        self.gui.disable_board()


class BotSimulationGame(BaseGame):
    """ A modified version of the game that allows for simulating
        moves without affecting the actual game state. """

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
    """ Base class for all bots. """

    @classmethod
    def make_move(cls, game: BaseGame) -> None:
        """ Make a bot move in the game. Prints the time taken to compute the move
            in milliseconds to stdout. The actual move is computed and made in the
            _make_move method that has to be implemented by the bot subclass.

        Args:
            game (BaseGame): The game instance to make a move in.
        """

        start_time = time_ns()
        cls._make_move(game)
        print("Real time elapsed while computing bot move:", (time_ns() - start_time) / 1e6, "ms")

    @classmethod
    @abstractmethod
    def _make_move(cls, game: BaseGame) -> None:
        pass


class RandomBot(Bot):
    """ A bot that makes random valid moves. """

    @classmethod
    def _make_move(cls, game: BaseGame) -> None:
        while not game.place(randint(0, game.n_cols - 1)):
            pass


class AlphaBetaNegamaxBot(Bot):
    """ A bot that uses the Alpha-Beta Pruning Negamax algorithm to make moves. """

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
        _, col = cls._explore(test_game, cls.DEPTH)
        assert col != -1
        del test_game
        game.place(col)

    @classmethod
    def _explore(cls, simulation: 'BotSimulationGame', depth: int,
                alpha: tp.Optional[Num] = None,
                beta: tp.Optional[Num] = None) -> tp.Tuple[Num, int]:
        """ Recursively explore the game tree using the Alpha-Beta Pruning Negamax algorithm.

        Args:
            simulation (BotSimulationGame): An instance of the game to explore.
            depth (int): The depth of the search tree to explore.
            alpha (tp.Optional[Num], optional): Internal parameter for alpha-beta pruning.
                    Defaults to None for the default value of DEFAULT_ALPHA.
            beta (tp.Optional[Num], optional): Internal parameter for alpha-beta pruning.
                    Defaults to None for the default value of DEFAULT_BETA.

        Returns:
            tp.Tuple[Num, int]: The score of the best move found and the column of the move.
        """

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
                # The search window is empty, prune the search
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
                score = - cls._explore(simulation, depth - 1, -beta, -alpha)[0]
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


class NPlayerAlphaBetaBot(Bot):
    """ A bot that uses the Alpha-Beta Pruning modified Minimax algorithm to make moves.
        This bot is able to play in games with more than 2 players. """

    DEPTH = 11
    DEFAULT_ALPHA = -float('inf')
    DEFAULT_BETA = float('inf')

    @classmethod
    def _make_move(cls, game: BaseGame) -> None:
        test_game = BotSimulationGame(game.n_cols, game.n_rows, game.n_connect, game.n_players)
        test_game.board = [row.copy() for row in game.board]
        test_game.heights = game.heights.copy()
        test_game.player_turn = game.player_turn
        test_game.total_moves = game.total_moves
        _, _, col = cls.explore(test_game, cls.DEPTH)
        assert col != -1
        del test_game
        game.place(col)

    @classmethod
    def explore(cls, simulation: 'BotSimulationGame', depth: int,
                alpha: tp.Optional[Num] = None,
                beta: tp.Optional[Num] = None) -> tp.Tuple[Num, int, int]:
        """ Recursively explore the game tree using the Alpha-Beta Pruning
            modified Minimax algorithm.

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
            alpha = cls.DEFAULT_ALPHA
            beta = cls.DEFAULT_BETA
        assert alpha < beta

        if depth == 0:
            return 0, 0, -1

        current_turn = simulation.player_turn

        score_if_win = simulation.n_cols * simulation.n_rows - simulation.total_moves
        for col in range(simulation.n_cols):
            outcome = simulation.place(col)
            if outcome == TurnResult.INVALID:
                continue
            simulation.unplace(col)
            simulation.player_turn = current_turn
            if outcome == TurnResult.WIN:
                # The game is won by this move
                return score_if_win, current_turn, col
            elif outcome == TurnResult.DRAW:
                # If a move immediately leads to a draw, it has to be the only possible move
                return 0, 0, col

        best_possible_score = score_if_win - simulation.n_players
        if best_possible_score < beta:
            beta = best_possible_score # No need to search for moves with impossibly high scores
            if alpha >= beta:
                # The search window is empty, prune the search
                return beta, 0, -1

        best_score, best_player, best_col = -float('inf'), 0, -1
        for offset in range((simulation.n_cols + 1) // 2):
            left = (simulation.n_cols - 1) // 2 - offset
            right = (simulation.n_cols + 1) // 2 + offset
            for col in ([left, right] if right < simulation.n_cols else [left]):
                outcome = simulation.place(col)
                if outcome == TurnResult.INVALID:
                    continue
                assert outcome == TurnResult.OK
                score, player, _ = cls.explore(simulation, depth - 1, -beta, -alpha)
                if player != current_turn:
                    score = -score
                simulation.unplace(col)
                simulation.player_turn = current_turn
                if score > best_score:
                    best_score, bets_player, best_col = score, player, col
                alpha = max(alpha, score)
                if score >= beta:
                    # Found a move better than the highest score we are looking for
                    return abs(score), player, col
                if alpha >= beta:
                    # The search window is empty
                    assert False # Should never happen, we should have returned already
        return abs(best_score), best_player, best_col


class DeeperAlphaBetaNegamaxBot(AlphaBetaNegamaxBot):
    DEPTH = 13


#############################################################
#                          TESTING                          #
#############################################################


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

    board = [
        [0, 0, 0, 2, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 2, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 2, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0]
    ]
    heights = [0, 0, 0, 6, 1, 0, 0]
    turn = 2
    # Game(bots={1:AlphaBetaNegamaxBot, 2:NPlayerAlphaBetaBot}, game_state=(board, heights, turn)) #ok
    Game(bots={1:AlphaBetaNegamaxBot, 2:AlphaBetaNegamaxBot}, game_state=(board, heights, turn)) #bad, idk why
    # Game(bots={1:AlphaBetaNegamaxBot, 2:NPlayerAlphaBetaBot}, n_connect=4)
    # Game(n_players=3, n_connect=3)