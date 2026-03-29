"""Raccoon Rampage - Game Interface

Main game program with pygame-based user interface.
Features customizable board dimensions, character counts, and game speed.
"""
from __future__ import annotations

import sys
from random import random, shuffle

import pygame

from pyta_config import python_ta

# Turn off check contracts to prevent the UI from being too slow to use.
# This MUST run before we import our classes.
python_ta.contracts.ENABLE_CONTRACT_CHECKING = False

import game

# Feel free to modify any of these constant values.

# Game Screen dimensions in pixels
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Dimensions of the game board, in squares.
BOARD_WIDTH = 10
BOARD_HEIGHT = 10

# Number of each type of Character to include in a random game
NUM_RACCOONS = 4
NUM_GARBAGE_CANS = 4
NUM_RECYCLING_BINS = int(BOARD_HEIGHT * BOARD_WIDTH * 0.2)

# Number of milliseconds to wait between iterations of the main game loop.
# This changes the speed of the game. The main player can move at most
# once every LOOP_DELAY milliseconds.
LOOP_DELAY = 100

# Fraction of garbage cans that are to be locked at the start of the game.
FRACTION_LOCKED = 0.1

# Fraction of "smart" raccoons
FRACTION_SMART = 0.5

# Character icons
BACKGROUND_ICON = 'icons/background.png'
GARBAGE_CAN_OPEN_ICON = 'icons/open.png'
GARBAGE_CAN_CLOSED_ICON = 'icons/closed.png'
PERSON_ICON = 'icons/person.png'
SMART_RACCOON_ICON = 'icons/smart.png'
RACCOON_ICON = 'icons/raccoon.png'
RECYCLING_ICON = 'icons/recycling.png'
RACCOON_IN_BIN_ICON = 'icons/raccoon_in_bin.png'


def make_image(icon_file: str, width: int, height: int) -> pygame.surface:
    """Load and scale an image file to the specified dimensions."""
    pic = pygame.image.load(icon_file)
    return pygame.transform.scale(pic, (width, height))


class RaccoonRaiders:
    """Pygame-based user interface for Raccoon Rampage.

    Attributes:
    - width: game board width
    - height: game board height
    - square_size: pixel size of each board square
    - _board: the game board state
    - _screen: pygame display surface
    - _icon_map: character symbol to image mapping
    - _background_tile: background tile image
    - _last_state: cached previous board state for optimization
    """

    width: int
    height: int
    square_size: int
    _board: game.GameBoard
    _screen: pygame.Surface
    _icon_map: dict[str, pygame.Surface]
    _background_tile: pygame.Surface
    _last_state: list[list[str]] | None

    def __init__(self, w: int, h: int, board_string: str = '') -> None:
        """Initialize game with board dimensions w x h.

        If board_string is provided, initializes from that layout.
        Otherwise, generates a random board.
        """
        self._board = game.GameBoard(w, h)

        if board_string:
            self._board.setup_from_grid(board_string)
        else:
            populate_board(self._board,
                           NUM_RACCOONS,
                           NUM_GARBAGE_CANS,
                           NUM_RECYCLING_BINS)

        self.square_size = min(int(SCREEN_WIDTH / w),
                               int(SCREEN_HEIGHT / h))

        self._screen = pygame.display.set_mode((w * self.square_size,
                                                h * self.square_size)
                                               )

        def image_loader(x: str) -> pygame.surface:
            return make_image(x, self.square_size, self.square_size)

        self._background_tile = image_loader(BACKGROUND_ICON)

        self._icon_map = {'R': image_loader(RACCOON_ICON),
                          'S': image_loader(SMART_RACCOON_ICON),
                          'C': image_loader(GARBAGE_CAN_CLOSED_ICON),
                          'O': image_loader(GARBAGE_CAN_OPEN_ICON),
                          '@': image_loader(RACCOON_IN_BIN_ICON),
                          'B': image_loader(RECYCLING_ICON),
                          'P': image_loader(PERSON_ICON)
                          }

        self._last_state = None
        self.height, self.width = self._board.height, self._board.width

    def draw(self) -> None:
        """Render the current board state to the screen and terminal."""
        state = self._board.to_grid()
        changed = self._last_state != state
        if changed:
            print(f'\n{self._board}')
        self._last_state = state

        for x in range(len(state[0])):
            for y in range(len(state)):
                c = state[y][x]
                rectangle = pygame.Rect(x * self.square_size,
                                        y * self.square_size,
                                        self.square_size, self.square_size)
                self._screen.blit(self._background_tile, (x * self.square_size,
                                                          y * self.square_size))
                if c in self._icon_map:
                    self._screen.blit(self._icon_map[c], rectangle)

        pygame.display.flip()

    def play(self) -> None:
        """Run the main game loop."""
        while not self._board.ended:
            pygame.time.wait(LOOP_DELAY)
            self._handle_user_input()

        score = self._board.check_game_ended()
        print(f"Game has ended. Your score is {score}")

        pygame.font.init()
        font = pygame.font.Font(pygame.font.get_default_font(), 36)
        text_surface = font.render(f"Your Score: {score}",
                                   False, (0, 0, 0))
        self._screen.blit(text_surface, dest=(0,
                                              (self.square_size
                                               * self.height) // 2))
        pygame.display.flip()

        while True:
            pygame.time.wait(LOOP_DELAY * 5)
            for event in pygame.event.get():
                if event.type == pygame.constants.QUIT:
                    sys.exit()

    def _handle_user_input(self) -> None:
        """Process user input and update game state."""
        for event in pygame.event.get():
            if event.type == pygame.constants.QUIT:
                sys.exit()
            if event.type == pygame.constants.KEYDOWN:
                dx, dy = None, None
                if event.key == pygame.constants.K_DOWN:
                    dx, dy = 0, 1
                if event.key == pygame.constants.K_LEFT:
                    dx, dy = -1, 0
                if event.key == pygame.constants.K_RIGHT:
                    dx, dy = 1, 0
                if event.key == pygame.constants.K_UP:
                    dx, dy = 0, -1
                if dx is not None:
                    self._board.handle_event((dx, dy))

        self._board.give_turns()
        self.draw()


def populate_board(board: game.GameBoard, num_raccoons: int,
                   num_cans: int, num_bins: int) -> None:
    """Randomly populate the board with characters.

    Places a player at (0, 0) and distributes the specified number of
    raccoons, garbage cans, and recycling bins randomly.

    Precondition:
        - num_raccoons + num_bins + num_cans + 1 <= board size

    >>> b = game.GameBoard(3, 1)
    >>> populate_board(b,1,0,1)
    >>> str(b) in ['PRB', 'PBR', 'PSB', 'PBS']
    True
    """
    game.Player(board, 0, 0)

    availables = []
    for i in range(board.width):
        for j in range(board.height):
            availables.append((i, j))
    availables.remove((0, 0))

    shuffle(availables)

    for _ in range(num_raccoons):
        x, y = availables.pop()
        if random() <= FRACTION_SMART:
            game.SmartRaccoon(board, x, y)
        else:
            game.Raccoon(board, x, y)

    for _ in range(num_cans):
        x, y = availables.pop()
        locked = random() <= FRACTION_LOCKED
        game.GarbageCan(board, x, y, locked)

    for _ in range(num_bins):
        x, y = availables.pop()
        game.RecyclingBin(board, x, y)


if __name__ == '__main__':
    random_game = True
    if random_game:
        rc = RaccoonRaiders(BOARD_WIDTH, BOARD_HEIGHT)
    else:
        game_string = "P-O----S\n---BBB-\n------B-\n-BRBB-O-\n" \
                      "---B-B--\n--O---S-"
        rc = RaccoonRaiders(8, 6, game_string)

    rc.play()
