CELL_SIZE: int = 5

# Colour palette
BG_COLOUR: tuple[int, int, int] = (10, 10, 18)
WHITE_CELL: tuple[int, int, int] = (230, 230, 255)
BLACK_CELL: tuple[int, int, int] = BG_COLOUR
ANT_COLOUR: tuple[int, int, int] = (255, 60, 80)
GRID_COLOUR: tuple[int, int, int] = (25, 25, 40)
UI_COLOUR: tuple[int, int, int] = (180, 180, 220)
ACCENT_COLOUR: tuple[int, int, int] = (255, 200, 50)
HIGHWAY_COLOUR: tuple[int, int, int] = (80, 200, 255)

# Directions: 0=Up 1=Right 2=Down 3=Left
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

DIR_DELTA: list[tuple[int, int]] = [(0, -1), (1, 0), (0, 1), (-1, 0)]
TURN_RIGHT = 1
TURN_LEFT = -1

# Highway detection: the ant's displacement repeats with a period of exactly 104 steps.
# Confirming 5 consecutive identical periods eliminates false positives during the chaotic phase.
HIGHWAY_PERIOD = 104
HIGHWAY_CYCLES = 5
