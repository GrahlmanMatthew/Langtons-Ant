from collections import defaultdict

from langtons_ant.config.constants import DOWN, LEFT, RIGHT, UP
from langtons_ant.simulation.ant import Ant


def _empty_grid() -> defaultdict:
    return defaultdict(bool)


def _white_at(x: int, y: int) -> defaultdict:
    grid = _empty_grid()
    grid[(x, y)] = True
    return grid


def test_step_on_white_cell():
    grid = _white_at(0, 0)
    ant = Ant(0, 0, UP)
    ant.step(grid)
    assert ant.direction == RIGHT
    assert grid[(0, 0)] is False
    assert ant.x == 1
    assert ant.y == 0
    assert ant.steps == 1


def test_step_on_black_cell():
    ant = Ant(0, 0, UP)
    ant.step(_empty_grid())
    assert ant.direction == LEFT
    assert ant.x == -1
    assert ant.y == 0
    assert ant.steps == 1


def test_direction_wraps_left_of_up():
    # Black cell starting UP: turning left from UP wraps to LEFT (3)
    ant = Ant(0, 0, UP)
    ant.step(_empty_grid())
    assert ant.direction == LEFT


def test_direction_wraps_right_of_left():
    # White cell starting LEFT: turning right from LEFT wraps to UP (0)
    ant = Ant(0, 0, LEFT)
    ant.step(_white_at(0, 0))
    assert ant.direction == UP


def test_step_increments_counter():
    ant = Ant(0, 0, UP)
    grid = _empty_grid()
    for i in range(1, 6):
        ant.step(grid)
        assert ant.steps == i


def test_highway_detected():
    # On an empty grid with a fixed direction the highway emerges deterministically.
    ant = Ant(0, 0, UP)
    grid = _empty_grid()
    for _ in range(15_000):
        ant.step(grid)
    assert ant.highway is True
    assert ant.highway_step > 0


def test_highway_step_recorded():
    ant = Ant(0, 0, UP)
    grid = _empty_grid()
    for _ in range(15_000):
        ant.step(grid)
    assert ant.highway_step > 0
    assert ant.highway_step <= ant.steps


def test_cell_flip_is_persistent():
    grid = _empty_grid()
    ant = Ant(0, 0, DOWN)
    ant.step(grid)  # black cell → flipped to white
    assert grid[(0, 0)] is True
