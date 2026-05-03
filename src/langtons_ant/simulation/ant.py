from collections import defaultdict

from langtons_ant.config.constants import (
    DIR_DELTA,
    HIGHWAY_CYCLES,
    HIGHWAY_PERIOD,
    TURN_LEFT,
    TURN_RIGHT,
    UP,
)


class Ant:
    def __init__(self, x: int, y: int, direction: int = UP) -> None:
        self.x = x
        self.y = y
        self.direction = direction
        self.steps = 0
        self.highway = False
        self._hw_step = 0
        self._buf_size = HIGHWAY_PERIOD * (HIGHWAY_CYCLES + 1)
        self._history: list[tuple[int, int]] = []

    @property
    def highway_step(self) -> int:
        return self._hw_step

    def step(self, grid: defaultdict) -> None:
        cell = (self.x, self.y)
        if grid[cell]:
            self.direction = (self.direction + TURN_RIGHT) % 4
            grid[cell] = False
        else:
            self.direction = (self.direction + TURN_LEFT) % 4
            grid[cell] = True
        dx, dy = DIR_DELTA[self.direction]
        self.x += dx
        self.y += dy
        self.steps += 1

        if not self.highway:
            self._history.append((self.x, self.y))
            if len(self._history) > self._buf_size:
                self._history.pop(0)
            self._detect_highway()

    def _detect_highway(self) -> None:
        # Confirm the highway by verifying that the ant's displacement over exactly one
        # period is identical for HIGHWAY_CYCLES consecutive periods. During the chaotic
        # phase the per-period displacement is erratic; on the highway it is constant.
        needed = HIGHWAY_PERIOD * HIGHWAY_CYCLES
        if len(self._history) < needed + HIGHWAY_PERIOD:
            return

        displacements: list[tuple[int, int]] = []
        h = self._history
        n = len(h)
        for i in range(HIGHWAY_CYCLES):
            start = n - needed + i * HIGHWAY_PERIOD - HIGHWAY_PERIOD
            end = start + HIGHWAY_PERIOD
            if start < 0:
                return
            displacements.append((h[end][0] - h[start][0], h[end][1] - h[start][1]))

        first = displacements[0]
        if first != (0, 0) and all(d == first for d in displacements):
            self.highway = True
            self._hw_step = self.steps
