"""Raccoon Rampage Game - Core Implementation

A strategic puzzle game where the player must trap raccoons by positioning
recycling bins and locking garbage cans on a grid-based board.

This module contains all game logic classes including the game board,
characters (player, raccoons, recycling bins, garbage cans), and movement mechanics.
"""

from __future__ import annotations

from random import shuffle

from pyta_config import pyta_config, python_ta, check_contracts

# Each raccoon moves every this many turns
RACCOON_TURN_FREQUENCY = 20

# Directions dx, dy
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [LEFT, UP, RIGHT, DOWN]


def get_shuffled_directions() -> list[tuple[int, int]]:
    """Return a shuffled copy of DIRECTIONS for randomized movement."""
    to_return = DIRECTIONS[:]
    shuffle(to_return)
    return to_return


def neighbours(x: tuple[int, int]) -> list[tuple[int, int]]:
    """Return the four coordinates adjacent to position x.

    Note: Does not validate whether coordinates are within board boundaries.

    >>> ns = set(neighbours((2, 3)))
    >>> {(2, 2), (2, 4), (1, 3), (3, 3)} == ns
    True
    """
    rslt = []
    for direction in DIRECTIONS:
        rslt.append((x[0] + direction[0], x[1] + direction[1]))
    return rslt


@check_contracts
class GameBoard:
    """A grid-based game board for Raccoon Rampage.

    Public Attributes:
    - ended: whether the game has concluded
    - turns: number of turns elapsed
    - width: board width in tiles
    - height: board height in tiles

    Private Attributes:
    - _player: the player character
    - _characters: dictionary mapping coordinates to character lists

    Representation Invariants:
    - self.turns >= 0
    - self.width > 0
    - self.height > 0
    - No tile contains more than 1 character, except a tile may contain
      both a Raccoon and an open GarbageCan
    - At most one Player exists on the board
    """

    ended: bool
    turns: int
    width: int
    height: int
    _player: Player | None
    _characters: dict[tuple[int, int], list[Character]]

    def __init__(self, w: int, h: int) -> None:
        """Initialize an empty game board with the given dimensions.

        >>> b = GameBoard(3, 3)
        >>> b.width == 3
        True
        >>> b.height == 3
        True
        >>> b.turns == 0
        True
        >>> b.ended
        False
        """

        self.ended = False
        self.turns = 0

        self.width = w
        self.height = h

        self._player = None
        self._characters = {}

    def place_character(self, c: Character) -> None:
        """Register a character on the board at its current position.

        Preconditions:
        - c.board == self
        - self.on_board(c.x, c.y)
        - Character c has not already been placed on this board
        - The tile (c.x, c.y) does not already contain a character, except
          a raccoon can be placed on a tile with an unlocked GarbageCan

        >>> b = GameBoard(3, 2)
        >>> r = Raccoon(b, 1, 1)
        >>> b.at(1, 1)[0] == r
        True
        """
        x_cor = c.x
        y_cor = c.y
        if (x_cor, y_cor) not in self._characters:
            self._characters[(x_cor, y_cor)] = [c]
        else:
            self._characters[(x_cor, y_cor)].append(c)

        if isinstance(c, Player):
            self._player = c

    def at(self, x: int, y: int) -> list[Character]:
        """Return the characters at tile (x, y).

        Returns an empty list if no characters exist at the position or if
        the coordinates are outside the board.

        Note: A tile may contain up to two characters when a raccoon
        climbs into a garbage can.

        >>> b = GameBoard(3, 2)
        >>> r = Raccoon(b, 1, 1)
        >>> b.at(1, 1)[0] == r
        True
        >>> p = Player(b, 0, 1)
        >>> b.at(0, 1)[0] == p
        True
        """
        if (x, y) in self._characters:
            return self._characters[(x, y)]
        return []

    def to_grid(self) -> list[list[str]]:
        """Return the game state as a 2D list of character symbols.

        Symbol key:
        'R' = Raccoon, 'S' = SmartRaccoon, 'P' = Player,
        'C' = closed GarbageCan, 'O' = open GarbageCan,
        'B' = RecyclingBin, '@' = Raccoon in GarbageCan, '-' = Empty tile

        >>> b = GameBoard(3, 2)
        >>> _ = Player(b, 0, 0)
        >>> _ = Raccoon(b, 1, 1)
        >>> _ = GarbageCan(b, 2, 1, True)
        >>> b.to_grid()
        [['P', '-', '-'], ['-', 'R', 'C']]
        """
        final = []
        for y in range(self.height):
            new = []
            for x in range(self.width):
                if len(self.at(x, y)) == 0:
                    symbol = '-'
                elif len(self.at(x, y)) == 1:
                    symbol = self.at(x, y)[0].get_symbol()

                else:
                    symbol = '@'

                new.append(symbol)

            final.append(new)
        return final

    def __str__(self) -> str:
        """Return a string representation of the board state.

        >>> b = GameBoard(3, 2)
        >>> _ = Raccoon(b, 1, 1)
        >>> print(b)
        ---
        -R-
        >>> _ = Player(b, 0, 0)
        >>> _ = GarbageCan(b, 2, 1, False)
        >>> print(b)
        P--
        -RO
        >>> str(b)
        'P--\\n-RO'
        """
        board = self.to_grid()
        return "\n".join("".join(row) for row in board)

    def setup_from_grid(self, grid: str) -> None:
        """Initialize the board from a string representation.

        Symbol key: 'R' = Raccoon, 'P' = Player, 'C' = closed GarbageCan,
        'O' = open GarbageCan, 'B' = RecyclingBin, '@' = Raccoon in GarbageCan,
        '-' = Empty tile

        >>> b = GameBoard(4, 4)
        >>> b.setup_from_grid('P-B-\\n-BRB\\n--BB\\n-C--')
        >>> str(b)
        'P-B-\\n-BRB\\n--BB\\n-C--'
        >>> print(b)
        P-B-
        -BRB
        --BB
        -C--
        """
        lines = grid.split('\n')
        width = len(lines[0])
        height = len(lines)
        self.__init__(width, height)
        y = 0
        for line in lines:
            x = 0
            for char in line:
                if char == 'R':
                    Raccoon(self, x, y)
                elif char == 'S':
                    SmartRaccoon(self, x, y)
                elif char == 'P':
                    Player(self, x, y)
                elif char == 'O':
                    GarbageCan(self, x, y, False)
                elif char == 'C':
                    GarbageCan(self, x, y, True)
                elif char == 'B':
                    RecyclingBin(self, x, y)
                elif char == '@':
                    GarbageCan(self, x, y, False)
                    Raccoon(self, x, y)
                x += 1
            y += 1

    def on_board(self, x: int, y: int) -> bool:
        """Return whether position (x, y) is within board boundaries."""
        return 0 <= x <= self.width - 1 and 0 <= y <= self.height - 1

    def move_character(self, character: Character, x: int, y: int) -> None:
        """Update character's position from current location to (x, y).

        >>> b = GameBoard(4, 4)
        >>> p = Player(b, 0, 0)
        >>> b.move_character(p, 0, 1)
        >>> b._characters[(0, 1)] == [p]
        True
        >>> b._characters[(0, 0)] == []
        True
        """
        old = (character.x, character.y)
        new = (x, y)
        self._characters[(old[0], old[1])] = []
        self._characters[(new[0], new[1])] = [character]
        character.x, character.y = new[0], new[1]

    def move_raccoon(self, character: Character, x: int, y: int) -> None:
        """Update raccoon's position, handling garbage can occupancy.

        >>> b = GameBoard(4, 4)
        >>> p = Raccoon(b, 0, 0)
        >>> bin = GarbageCan(b, 0, 1, False)
        >>> b.move_raccoon(p, 0, 1)
        >>> b._characters[(0, 1)] == [bin, p]
        True
        >>> b._characters[(0, 0)] == []
        True
        """
        old = (character.x, character.y)
        new = (x, y)
        self._characters[(old[0], old[1])] = []

        changed = False
        if len(self._characters[(new[0], new[1])]) > 0:
            if self._characters[(new[0], new[1])][0].get_symbol() == 'O':
                self._characters[(new[0], new[1])].append(character)
                changed = True

        if not changed:
            self._characters[(new[0], new[1])] = [character]
        character.x, character.y = new[0], new[1]

    def give_turns(self) -> None:
        """Execute one turn for all active characters.

        The Player takes their turn first, then the turn counter increments.
        Other TurnTakers receive turns every RACCOON_TURN_FREQUENCY turns.
        Checks if game has ended after all turns complete.

        Precondition: self._player is not None

        >>> b = GameBoard(4, 3)
        >>> p = Player(b, 0, 0)
        >>> r = Raccoon(b, 1, 1)
        >>> b.turns
        0
        >>> for _ in range(RACCOON_TURN_FREQUENCY - 1):
        ...     b.give_turns()
        >>> b.turns == RACCOON_TURN_FREQUENCY - 1
        True
        >>> (r.x, r.y) == (1, 1)
        True
        >>> (p.x, p.y) == (0, 0)
        True
        >>> p.record_event(RIGHT)
        >>> b.give_turns()
        >>> (r.x, r.y) != (1, 1)
        True
        >>> (p.x, p.y) == (1, 0)
        True
        """
        self._player.take_turn()
        self.turns += 1

        if self.turns % RACCOON_TURN_FREQUENCY == 0:
            for loc in list(self._characters.keys()):
                if len(self._characters[loc]) > 0:
                    character = self._characters[loc][0]
                    self._give_turns_helper(character)

        self.check_game_ended()

    def _give_turns_helper(self, character: Character) -> None:
        """Helper method to process a character's turn if applicable.

        >>> b = GameBoard(4, 3)
        >>> p = Player(b, 0, 0)
        >>> r = Raccoon(b, 1, 1)
        >>> r.inside_can = False
        >>> initial_pos = (r.x, r.y)
        >>> b._give_turns_helper(r)
        >>> (r.x, r.y) != initial_pos
        True
        """
        if isinstance(character, Raccoon):
            if not character.inside_can:
                character.take_turn()

    def handle_event(self, event: tuple[int, int]) -> None:
        """Record a user input event for the Player to process on their next turn.

        Preconditions:
        - event in DIRECTIONS
        """
        self._player.record_event(event)

    def check_game_ended(self) -> int | None:
        """Determine if the game has ended and calculate the score.

        Game ends when all raccoons are either inside a can or trapped.
        Score = (trapped raccoons * 10) + adjacent_bin_score

        Returns the score if game ended, None otherwise.

        >>> b = GameBoard(3, 2)
        >>> _ = Raccoon(b, 1, 0)
        >>> _ = Player(b, 0, 0)
        >>> _ = RecyclingBin(b, 1, 1)
        >>> b.check_game_ended() is None
        True
        >>> b.ended
        False
        >>> _ = RecyclingBin(b, 2, 0)
        >>> b.check_game_ended()
        11
        >>> b.ended
        True
        """
        trapped = 0
        end = True

        for raccoon in self._get_raccoons():
            if raccoon.check_trapped():
                trapped += 1
            else:
                end = False

        if end:
            self.ended = True
            return (10 * trapped) + self.adjacent_bin_score()

        self.ended = False
        return None

    def _get_raccoons(self) -> list:
        """Return a list of all raccoons on the board.
        >>> b = GameBoard(3, 3)
        >>> r1 = Raccoon(b, 0, 0)
        >>> r2 = Raccoon(b, 1, 1)
        >>> r3 = Raccoon(b, 2, 2)
        >>> p = Player(b, 1, 0)  # Player is not a raccoon
        >>> b._get_raccoons() == [r1, r2, r3]
        True
        """
        return [
            ch for loc in self._characters
            for ch in self._characters[loc]
            if ch.get_symbol() in {'R', 'S'}]

    def adjacent_bin_score(self) -> int:
        """Return the size of the largest cluster of adjacent recycling bins.

        Bins are adjacent when directly beside each other horizontally or vertically.

        >>> b = GameBoard(3, 3)
        >>> _ = RecyclingBin(b, 1, 1)
        >>> _ = RecyclingBin(b, 0, 0)
        >>> _ = RecyclingBin(b, 2, 2)
        >>> print(b)
        B--
        -B-
        --B
        >>> b.adjacent_bin_score()
        1
        >>> _ = RecyclingBin(b, 2, 1)
        >>> print(b)
        B--
        -BB
        --B
        >>> b.adjacent_bin_score()
        3
        >>> _ = RecyclingBin(b, 0, 1)
        >>> print(b)
        B--
        BBB
        --B
        >>> b.adjacent_bin_score()
        5
        """
        visited = set()
        largest_cluster = 0

        for loc in self._characters:
            for ch in self._characters[loc]:
                if isinstance(ch, RecyclingBin) and loc not in visited:
                    # Found a new cluster, count its size
                    cluster_size = self._explore_cluster(loc, visited)
                    largest_cluster = max(largest_cluster, cluster_size)

        return largest_cluster

    def _explore_cluster(self, start: tuple[int, int], visited: set) -> int:
        """Use depth-first search to find all connected recycling bins.

        Returns the size of the cluster starting from the given position.

        >>> b = GameBoard(3, 3)
        >>> _ = RecyclingBin(b, 0, 0)
        >>> _ = RecyclingBin(b, 0, 1)
        >>> _ = RecyclingBin(b, 1, 1)
        >>> visited = set()
        >>> b._explore_cluster((0, 0), visited)
        3
        >>> assert visited == {(0, 0), (0, 1), (1, 1)}
        """
        stack = [start]
        visited.add(start)
        cluster_size = 0

        while stack:
            x, y = stack.pop()
            cluster_size += 1

            for dx, dy in DIRECTIONS:
                new_loc = (x + dx, y + dy)
                if (new_loc in self._characters and new_loc not in visited
                        and any(isinstance(ch, RecyclingBin) for ch in self._characters[new_loc])):
                    visited.add(new_loc)
                    stack.append(new_loc)

        return cluster_size


@check_contracts
class Character:
    """Base class for all game characters with position and board association.

    Attributes:
    - board: the game board this character occupies
    - x: x-coordinate position
    - y: y-coordinate position

    Representation Invariants:
    - self.board.on_board(x, y)
    - self is registered on self.board
    """
    board: GameBoard
    x: int
    y: int

    def __init__(self, board: GameBoard, x: int, y: int) -> None:
        """Initialize character at position (x, y) on the given board.

        Preconditions:
        - board.on_board(x, y)
        - If self is a Player, no other players exist on board
        - Tile (x, y) does not contain a character, except a raccoon
          can be placed on a tile with an unlocked GarbageCan
        """
        self.board = board
        self.x, self.y = x, y
        self.board.place_character(self)

    def move(self, direction: tuple[int, int]) -> bool:
        """Attempt to move this character in the specified direction.

        Returns True if move was successful, False otherwise.
        Movement rules are defined by each subclass.
        """
        raise NotImplementedError

    def get_symbol(self) -> str:
        """Return the single-character symbol representing this character."""
        raise NotImplementedError


@check_contracts
class TurnTaker(Character):
    """A character that can take autonomous turns in the game."""

    def take_turn(self) -> None:
        """Execute one turn for this character."""
        raise NotImplementedError


@check_contracts
class RecyclingBin(Character):
    """A recycling bin that can be pushed by the player.

    >>> rb = RecyclingBin(GameBoard(4, 4), 2, 1)
    >>> rb.x, rb.y
    (2, 1)
    """

    def move(self, direction: tuple[int, int]) -> bool:
        """Move this bin in the specified direction if possible.

        If the target tile contains another RecyclingBin, push it recursively.
        Returns False if blocked or out of bounds.

        Preconditions:
        - direction in DIRECTIONS

        >>> b = GameBoard(4, 2)
        >>> rb = RecyclingBin(b, 0, 0)
        >>> rb.move(UP)
        False
        >>> rb.move(DOWN)
        True
        >>> b.at(0, 1) == [rb]
        True
        """
        tile = (self.x + direction[0], self.y + direction[1])

        if not self.board.on_board(tile[0], tile[1]):
            return False

        elif self.board.at(tile[0], tile[1]) == []:
            self.board.move_character(self, tile[0], tile[1])
            return True

        elif self.board.at(tile[0], tile[1])[0].get_symbol() == 'B':
            second_rbin = self.board.at(tile[0], tile[1])[0]
            if second_rbin.move((direction[0], direction[1])):
                self.board.move_character(self, tile[0], tile[1])
                return True
            return False

        return False

    def get_symbol(self) -> str:
        """Return 'B' representing a RecyclingBin."""
        return 'B'


@check_contracts
class Player(TurnTaker):
    """The player-controlled character.

    Attributes:
    - _last_event: The last recorded directional input, or None

    >>> b = GameBoard(3, 1)
    >>> p = Player(b, 0, 0)
    >>> p.record_event(RIGHT)
    >>> p.take_turn()
    >>> (p.x, p.y) == (1, 0)
    True
    >>> g = GarbageCan(b, 0, 0, False)
    >>> p.move(LEFT)
    True
    >>> g.locked
    True
    """

    _last_event: tuple[int, int] | None

    def __init__(self, b: GameBoard, x: int, y: int) -> None:
        """Initialize player at position (x, y) on board b.

        Preconditions:
        - Consistent with Character.__init__ preconditions
        """
        TurnTaker.__init__(self, b, x, y)
        self._last_event = None

    def record_event(self, direction: tuple[int, int]) -> None:
        """Record a directional input to be processed on next turn.

        Preconditions:
        - direction in DIRECTIONS
        """
        self._last_event = direction

    def take_turn(self) -> None:
        """Process the last recorded user input."""
        if self._last_event is not None:
            self.move(self._last_event)
            self._last_event = None

    def move(self, direction: tuple[int, int]) -> bool:
        """Move the player in the specified direction if possible.

        Movement rules:
        - Empty tile: Move to it
        - RecyclingBin: Push it and move if successful
        - Open GarbageCan: Lock it (player doesn't move)
        - Raccoon/locked can/out of bounds: Cannot move

        Preconditions:
        - direction in DIRECTIONS

        >>> b = GameBoard(4, 2)
        >>> p = Player(b, 0, 0)
        >>> p.move(UP)
        False
        >>> p.move(DOWN)
        True
        >>> b.at(0, 1) == [p]
        True
        >>> _ = RecyclingBin(b, 1, 1)
        >>> p.move(RIGHT)
        True
        >>> b.at(1, 1) == [p]
        True
        """
        tile = (self.x + direction[0], self.y + direction[1])

        if not self.board.on_board(tile[0], tile[1]):
            return False

        elif self.board.at(tile[0], tile[1]) == []:
            self.board.move_character(self, tile[0], tile[1])
            return True

        elif self.board.at(tile[0], tile[1])[0].get_symbol() == 'B':
            r_bin = self.board.at(tile[0], tile[1])[0]
            if r_bin.move((direction[0], direction[1])):
                self.board.move_character(self, tile[0], tile[1])
                return True
            else:
                return False

        elif self.board.at(tile[0], tile[1])[0].get_symbol() == 'O':
            can = self.board.at(tile[0], tile[1])[0]
            can.locked = True
            return True

        return False

    def get_symbol(self) -> str:
        """Return 'P' representing the Player."""
        return 'P'


@check_contracts
class Raccoon(TurnTaker):
    """A raccoon that moves randomly and can hide in garbage cans.

    Attributes:
    - inside_can: whether this raccoon is currently inside a garbage can

    Representation Invariants:
    - inside_can is True iff this raccoon is on the same tile as an open GarbageCan

    >>> r = Raccoon(GameBoard(11, 11), 5, 10)
    >>> r.x, r.y
    (5, 10)
    >>> r.inside_can
    False
    """
    inside_can: bool

    def __init__(self, b: GameBoard, x: int, y: int) -> None:
        """Initialize raccoon at position (x, y) on board b.

        Preconditions:
        - Consistent with Character.__init__ preconditions

        >>> b = GameBoard(5, 5)
        >>> r = Raccoon(b, 4, 3)
        >>> r.x == 4 and r.y == 3
        True
        >>> r.board is b
        True
        """
        TurnTaker.__init__(self, b, x, y)
        self.inside_can = False

    def check_trapped(self) -> bool:
        """Return whether this raccoon is completely surrounded and cannot move.

        A raccoon is trapped when all four adjacent tiles are blocked by
        bins, other raccoons, the player, or board edges.

        >>> b = GameBoard(3, 3)
        >>> r = Raccoon(b, 2, 1)
        >>> _ = Raccoon(b, 2, 2)
        >>> _ = Player(b, 2, 0)
        >>> r.check_trapped()
        False
        >>> _ = RecyclingBin(b, 1, 1)
        >>> r.check_trapped()
        True
        """
        old = (self.x, self.y)

        for direction in DIRECTIONS:
            new = (old[0] + direction[0], old[1] + direction[1])
            if self.board.on_board(new[0], new[1]):
                if self.board.at(new[0], new[1]) == []:
                    return False
                if self.board.at(new[0], new[1])[0].get_symbol() == 'O':
                    return False

        return True

    def move(self, direction: tuple[int, int]) -> bool:
        """Move the raccoon in the specified direction if possible.

        Movement rules:
        - Empty tile: Move to it
        - Locked GarbageCan: Unlock it (doesn't move)
        - Open GarbageCan: Climb inside (2 characters on one tile)
        - Player/RecyclingBin/other Raccoon/out of bounds: Cannot move

        Preconditions:
        - direction in DIRECTIONS

        >>> b = GameBoard(4, 2)
        >>> r = Raccoon(b, 0, 0)
        >>> r.move(UP)
        False
        >>> r.move(DOWN)
        True
        >>> b.at(0, 1) == [r]
        True
        >>> g = GarbageCan(b, 1, 1, True)
        >>> r.move(RIGHT)
        True
        >>> r.x, r.y
        (0, 1)
        >>> not g.locked
        True
        >>> r.move(RIGHT)
        True
        >>> r.inside_can
        True
        >>> len(b.at(1, 1)) == 2
        True
        """
        tile = (self.x + direction[0], self.y + direction[1])

        if not self.board.on_board(tile[0], tile[1]):
            return False

        elif self.board.at(tile[0], tile[1]) == []:
            self.board.move_character(self, tile[0], tile[1])
            return True

        elif self.board.at(tile[0], tile[1])[0].get_symbol() == 'C':
            can = self.board.at(tile[0], tile[1])[0]
            can.locked = False
            return True

        elif self.board.at(tile[0], tile[1])[0].get_symbol() == 'O':
            self.board.move_raccoon(self, tile[0], tile[1])
            self.inside_can = True
            return True

        return False

    def take_turn(self) -> None:
        """Move the raccoon in a random available direction.

        Raccoons inside cans or trapped raccoons don't move.

        >>> b = GameBoard(3, 4)
        >>> r1 = Raccoon(b, 0, 0)
        >>> r1.take_turn()
        >>> (r1.x, r1.y) in [(0, 1), (1, 0)]
        True
        >>> r2 = Raccoon(b, 2, 1)
        >>> _ = RecyclingBin(b, 2, 0)
        >>> _ = RecyclingBin(b, 1, 1)
        >>> _ = RecyclingBin(b, 2, 2)
        >>> r2.take_turn()
        >>> r2.x, r2.y
        (2, 1)
        """
        if not self.inside_can and not self.check_trapped():
            moved = False
            directions = get_shuffled_directions()
            n = 0
            while not moved:
                random_direction = directions[n]
                moved = self.move(random_direction)
                n += 1

    def get_symbol(self) -> str:
        """Return '@' if inside a garbage can, 'R' otherwise."""
        if self.inside_can:
            return '@'
        return 'R'


@check_contracts
class SmartRaccoon(Raccoon):
    """A raccoon that intelligently moves toward visible garbage cans.

    Moves like a regular Raccoon, but prioritizes moving toward the closest
    GarbageCan in its line of sight.

    >>> b = GameBoard(8, 1)
    >>> s = SmartRaccoon(b, 4, 0)
    >>> s.x, s.y
    (4, 0)
    >>> s.inside_can
    False
    """

    def take_turn(self) -> None:
        """Move toward the closest visible garbage can, or randomly if none visible.

        Line of sight: Can see GarbageCans through the Player, but not through
        other raccoons, RecyclingBins, or GarbageCans. Prioritizes DIRECTIONS
        order for ties.

        >>> b = GameBoard(8, 2)
        >>> s = SmartRaccoon(b, 4, 0)
        >>> _ = GarbageCan(b, 3, 1, False)
        >>> _ = GarbageCan(b, 0, 0, False)
        >>> _ = GarbageCan(b, 7, 0, False)
        >>> s.take_turn()
        >>> s.x
        5
        >>> s.take_turn()
        >>> s.x
        6
        """
        if not self.inside_can and not self.check_trapped():
            cans_in_sight = self._get_nearby_garbage_cans()

            if cans_in_sight == []:
                moved = False
                directions = get_shuffled_directions()
                n = 0
                while not moved:
                    random_direction = directions[n]
                    moved = self.move(random_direction)
                    n += 1
            else:
                self._take_turn_helper(cans_in_sight)

    def _take_turn_helper(self, cans_in_sight: list[GarbageCan]) -> None:
        """Move toward the closest garbage can(s), prioritizing DIRECTIONS order for ties."""
        closest_cans = self._find_closest_cans(cans_in_sight)
        if len(closest_cans) == 1:
            closest_can = closest_cans[0]
            direction = self._get_direction_of_can(closest_can)
            self.move(direction)
        else:
            directions = []
            for can in closest_cans:
                directions.append(self._get_direction_of_can(can))

            for d in DIRECTIONS:
                if d in directions:
                    self.move(d)
                    break

    def _get_direction_of_can(self, can: GarbageCan) -> tuple[int, int]:
        """Return the direction to move toward the specified garbage can.

        >>> b = GameBoard(6, 6)
        >>> s = SmartRaccoon(b, 2, 2)
        >>> a = GarbageCan(b, 2, 0, False)
        >>> d = GarbageCan(b, 5, 2, False)
        >>> p = Player(b, 4, 2)
        >>> c = GarbageCan(b, 2, 5, False)
        >>> s._get_direction_of_can(a) == UP
        True
        >>> s._get_direction_of_can(d) == RIGHT
        True
        >>> s._get_direction_of_can(c) == DOWN
        True
        """
        if self.x == can.x:
            difference = self.y - can.y
            if difference > 0:
                return UP
            else:
                return DOWN

        elif self.y == can.y:
            difference = self.x - can.x
            if difference > 0:
                return LEFT
            else:
                return RIGHT
        return UP

    def _find_closest_cans(self, cans_in_sight: list[GarbageCan]) -> list[GarbageCan]:
        """Return the garbage can(s) closest to this raccoon.

        >>> b = GameBoard(6, 6)
        >>> s = SmartRaccoon(b, 2, 2)
        >>> a = GarbageCan(b, 2, 0, False)
        >>> d = GarbageCan(b, 5, 2, False)
        >>> p = Player(b, 4, 2)
        >>> c = GarbageCan(b, 2, 5, False)
        >>> cans_in_sight = s._get_nearby_garbage_cans()
        >>> s._find_closest_cans(cans_in_sight) == [a]
        True
        """
        if len(cans_in_sight) == 1:
            return [cans_in_sight[0]]

        else:
            distances = []
            for can in cans_in_sight:
                if can.x == self.x:
                    distance = abs(can.y - self.y)
                    distances.append(distance)
                elif can.y == self.y:
                    distance = abs(can.x - self.x)
                    distances.append(distance)

            min_distance = min(distances)
            closest_cans = []
            for i in range(len(distances)):
                if distances[i] == min_distance:
                    closest_cans.append(cans_in_sight[i])

        return closest_cans

    def _get_nearby_garbage_cans(self) -> list[GarbageCan]:
        """Return all garbage cans visible in the raccoon's line of sight.

        >>> b = GameBoard(6, 6)
        >>> s = SmartRaccoon(b, 2, 2)
        >>> a = GarbageCan(b, 2, 0, False)
        >>> d = GarbageCan(b, 5, 2, False)
        >>> p = Player(b, 4, 2)
        >>> c = GarbageCan(b, 2, 5, False)
        >>> s._get_nearby_garbage_cans() == [a, d, c]
        True
        """
        cans_in_sight = []
        for direction in DIRECTIONS:
            cans_in_sight.extend(self._get_cans_one_dir((self.x, self.y), direction))

        return cans_in_sight

    def _get_cans_one_dir(self, curr_tile: tuple[int, int], direction: tuple[int, int]) -> list[GarbageCan]:
        """Recursively search for garbage cans in the specified direction.

        Returns the first garbage can found, or empty list if blocked or out of bounds.

        >>> b = GameBoard(6, 6)
        >>> s = SmartRaccoon(b, 2, 2)
        >>> a = GarbageCan(b, 2, 0, False)
        >>> d = GarbageCan(b, 5, 2, False)
        >>> p = Player(b, 4, 2)
        >>> c = GarbageCan(b, 2, 5, False)
        >>> s._get_cans_one_dir((2, 2), UP) == [a]
        True
        """
        item = self.board.at(curr_tile[0] + direction[0], curr_tile[1] + direction[1])
        if len(item) == 1:
            ch = item[0]
            if isinstance(ch, GarbageCan):
                return [ch]
            elif not isinstance(ch, Player):
                return []

        new_curr_tile = (curr_tile[0] + direction[0], curr_tile[1] + direction[1])

        if self.board.on_board(new_curr_tile[0], new_curr_tile[1]):
            return self._get_cans_one_dir(new_curr_tile, direction)
        else:
            return []

    def get_symbol(self) -> str:
        """Return '@' if inside a garbage can, 'S' otherwise."""
        if self.inside_can:
            return '@'
        return 'S'


@check_contracts
class GarbageCan(Character):
    """A garbage can that raccoons can hide in.

    Attributes:
    - locked: whether this can is locked (closed)

    >>> b = GameBoard(2, 2)
    >>> g = GarbageCan(b, 0, 0, False)
    >>> g.x, g.y
    (0, 0)
    >>> g.locked
    False
    """
    locked: bool

    def __init__(self, b: GameBoard, x: int, y: int, locked: bool) -> None:
        """Initialize garbage can at position (x, y) with specified lock state.

        Preconditions:
        - Consistent with Character.__init__ preconditions
        """
        Character.__init__(self, b, x, y)
        self.locked = locked

    def get_symbol(self) -> str:
        """Return 'C' for closed (locked) or 'O' for open (unlocked)."""
        if self.locked:
            return 'C'
        return 'O'

    def move(self, direction: tuple[int, int]) -> bool:
        """Garbage cans cannot move."""
        return False


if __name__ == '__main__':
    import doctest

    doctest.testmod()

    check_pyta = True  # set to False if you don't want to run pyTA
    if check_pyta:
        python_ta.check_all(config=pyta_config)
