"""
Langton's Ant — Pygame Visualizer
==================================
Controls:
  SPACE       — pause / resume
  R           — reset
  +  /  =     — speed up
  -           — slow down
  S           — toggle step-count display
  ESC / Q     — quit
"""

import pygame
import sys
import random
from collections import defaultdict

# ── Tunables ─────────────────────────────────────────────────────────────────
# Window size is set at runtime from the monitor resolution
CELL_SIZE          = 5          # pixels per grid cell (larger = more zoomed in)
TARGET_FPS         = 60
STEPS_PER_FRAME    = 10         # ant moves this many steps each rendered frame
SPEED_STEP         = 5          # how much +/- changes steps-per-frame
MAX_SPF            = 500
MIN_SPF            = 1

# Random start options on reset
NUM_NOISE_CELLS    = 200        # how many cells to pre-flip randomly
RANDOM_DIRECTIONS  = True       # randomise ant's starting direction too

# Colour palette — dark background, vivid foreground
BG_COLOUR          = (10,  10,  18)
WHITE_CELL         = (230, 230, 255)   # "white" (on) cell
BLACK_CELL         = BG_COLOUR         # "black" (off) cell — same as background
ANT_COLOUR         = (255,  60,  80)
GRID_COLOUR        = (25,   25,  40)
UI_COLOUR          = (180, 180, 220)
ACCENT_COLOUR      = (255, 200,  50)
HIGHWAY_COLOUR     = (80,  200, 255)   # colour flash once highway emerges

# ── Direction helpers ─────────────────────────────────────────────────────────
# Directions: 0=Up, 1=Right, 2=Down, 3=Left
DIR_DELTA = [(0, -1), (1, 0), (0, 1), (-1, 0)]

TURN_RIGHT = 1
TURN_LEFT  = -1


# The highway repeats with an exact period of 104 steps.
# We confirm it by checking that the ant's position 104 steps ago matches
# a consistent offset — repeated across multiple cycles.
HIGHWAY_PERIOD        = 104
HIGHWAY_CYCLES        = 5    # require this many consecutive clean cycles


# ── Ant state ────────────────────────────────────────────────────────────────
class Ant:
    def __init__(self, x: int, y: int, direction: int = 0):
        self.x        = x
        self.y        = y
        self.dir      = direction
        self.steps    = 0
        self.highway  = False
        self._hw_step = 0
        # Ring buffer: store enough history to check HIGHWAY_CYCLES full periods
        self._buf_size = HIGHWAY_PERIOD * (HIGHWAY_CYCLES + 1)
        self._history  = []   # list of (x, y)

    def step(self, grid: dict) -> None:
        cell = (self.x, self.y)
        if grid[cell]:
            self.dir = (self.dir + TURN_RIGHT) % 4
            grid[cell] = False
        else:
            self.dir = (self.dir + TURN_LEFT) % 4
            grid[cell] = True
        dx, dy  = DIR_DELTA[self.dir]
        self.x += dx
        self.y += dy
        self.steps += 1

        if not self.highway:
            self._history.append((self.x, self.y))
            if len(self._history) > self._buf_size:
                self._history.pop(0)
            self._detect_highway()

    def _detect_highway(self) -> None:
        """
        Confirm the highway by verifying that the ant's displacement over
        exactly one period (104 steps) is identical for HIGHWAY_CYCLES
        consecutive periods. During chaotic phase the per-period displacement
        is erratic; on the highway it is perfectly constant.
        """
        needed = HIGHWAY_PERIOD * HIGHWAY_CYCLES
        if len(self._history) < needed + HIGHWAY_PERIOD:
            return

        # Compute displacement vectors for the last HIGHWAY_CYCLES periods
        displacements = []
        h = self._history
        n = len(h)
        for i in range(HIGHWAY_CYCLES):
            start = n - needed + i * HIGHWAY_PERIOD - HIGHWAY_PERIOD
            end   = start + HIGHWAY_PERIOD
            if start < 0:
                return
            dx = h[end][0] - h[start][0]
            dy = h[end][1] - h[start][1]
            displacements.append((dx, dy))

        # All displacement vectors must be identical and non-zero
        first = displacements[0]
        if first == (0, 0):
            return
        if all(d == first for d in displacements):
            self.highway  = True
            self._hw_step = self.steps


# ── Rendering helpers ─────────────────────────────────────────────────────────
def world_to_screen(wx: int, wy: int, offset_x: int, offset_y: int) -> tuple:
    sx = (wx + offset_x) * CELL_SIZE
    sy = (wy + offset_y) * CELL_SIZE
    return sx, sy


def draw_grid_lines(surface: pygame.Surface, window_w: int, window_h: int) -> None:
    """Subtle grid — only drawn when cells are large enough to warrant it."""
    if CELL_SIZE < 6:
        return
    for x in range(0, window_w, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOUR, (x, 0), (x, window_h))
    for y in range(0, window_h, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOUR, (0, y), (0, window_h))


def draw_cells(surface: pygame.Surface,
               grid: dict,
               offset_x: int,
               offset_y: int,
               steps: int,
               highway: bool,
               hw_step: int,
               window_w: int,
               window_h: int) -> None:
    # Choose white-cell tint based on detected highway phase
    if highway:
        t = min(1.0, (steps - hw_step) / 2000)
        r = int(WHITE_CELL[0] * (1 - t) + HIGHWAY_COLOUR[0] * t)
        g = int(WHITE_CELL[1] * (1 - t) + HIGHWAY_COLOUR[1] * t)
        b = int(WHITE_CELL[2] * (1 - t) + HIGHWAY_COLOUR[2] * t)
        cell_colour = (r, g, b)
    else:
        cell_colour = WHITE_CELL

    rect = pygame.Rect(0, 0, CELL_SIZE - 1, CELL_SIZE - 1)
    for (wx, wy), is_white in grid.items():
        if not is_white:
            continue
        sx = (wx + offset_x) * CELL_SIZE
        sy = (wy + offset_y) * CELL_SIZE
        if -CELL_SIZE <= sx < window_w and -CELL_SIZE <= sy < window_h:
            rect.x = sx
            rect.y = sy
            pygame.draw.rect(surface, cell_colour, rect)


def draw_ant(surface: pygame.Surface,
             ant: Ant,
             offset_x: int,
             offset_y: int) -> None:
    sx = (ant.x + offset_x) * CELL_SIZE
    sy = (ant.y + offset_y) * CELL_SIZE
    cx = sx + CELL_SIZE // 2
    cy = sy + CELL_SIZE // 2
    r  = max(2, CELL_SIZE // 2)
    # Outer glow
    glow_surf = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
    for i in range(4, 0, -1):
        alpha = 40 * i
        pygame.draw.circle(glow_surf, (*ANT_COLOUR, alpha),
                           (r * 3, r * 3), r * i)
    surface.blit(glow_surf, (cx - r * 3, cy - r * 3))
    pygame.draw.circle(surface, ANT_COLOUR, (cx, cy), r)


def draw_ui(surface: pygame.Surface,
            font_large: pygame.font.Font,
            font_small: pygame.font.Font,
            steps: int,
            spf: int,
            paused: bool,
            show_steps: bool,
            highway: bool,
            hw_step: int,
            window_w: int,
            window_h: int) -> None:
    # Step counter
    if show_steps:
        label = font_large.render(f"{steps:,}", True, ACCENT_COLOUR)
        surface.blit(label, (12, 8))
        sub = font_small.render("steps", True, UI_COLOUR)
        surface.blit(sub, (14, 8 + label.get_height()))

    # Speed (bottom left)
    if paused:
        speed_txt = font_small.render("⏸  PAUSED", True, UI_COLOUR)
    else:
        speed_txt = font_small.render(f"×{spf} steps/frame", True, UI_COLOUR)
    surface.blit(speed_txt, (12, window_h - 28))

    # Controls hint (bottom centre)
    hint = font_small.render(
        "SPACE pause  |  R reset  |  +/− speed  |  S toggle counter  |  ESC quit",
        True, (80, 80, 110))
    surface.blit(hint, (window_w // 2 - hint.get_width() // 2, window_h - 22))

    # Highway banner (top right) — shown only after actual detection
    if highway:
        banner_alpha = min(255, int(255 * (steps - hw_step) / 500))
        banner = font_small.render("◆  HIGHWAY EMERGED  ◆", True, HIGHWAY_COLOUR)
        banner.set_alpha(banner_alpha)
        surface.blit(banner, (window_w - banner.get_width() - 12, 12))


# ── Main ─────────────────────────────────────────────────────────────────────
def make_random_grid(spread: int) -> defaultdict:
    """Pre-flip a handful of cells near the origin for variety on each reset."""
    grid = defaultdict(bool)
    for _ in range(NUM_NOISE_CELLS):
        x = random.randint(-spread, spread)
        y = random.randint(-spread, spread)
        grid[(x, y)] = True   # flip to white
    return grid


def main() -> None:
    pygame.init()

    # Detect monitor resolution — borderless windowed (no exclusive fullscreen)
    info     = pygame.display.Info()
    WINDOW_W = info.current_w
    WINDOW_H = info.current_h
    screen   = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.NOFRAME)
    pygame.display.set_caption("Langton's Ant")
    clock    = pygame.time.Clock()

    try:
        font_large = pygame.font.SysFont("monospace", 28, bold=True)
        font_small = pygame.font.SysFont("monospace", 14)
    except Exception:
        font_large = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 18)

    # Grid centre offsets (world → screen)
    offset_x = (WINDOW_W // CELL_SIZE) // 2
    offset_y = (WINDOW_H // CELL_SIZE) // 2

    # Noise spread: roughly 1/8 of the visible grid radius
    noise_spread = min(WINDOW_W, WINDOW_H) // (CELL_SIZE * 8)

    def reset():
        grid = make_random_grid(noise_spread)
        direction = random.randint(0, 3) if RANDOM_DIRECTIONS else 0
        ant = Ant(0, 0, direction)
        return grid, ant

    grid, ant  = reset()
    paused     = False
    spf        = STEPS_PER_FRAME
    show_steps = True

    running = True
    while running:
        clock.tick(TARGET_FPS)

        # ── Events ───────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False

                elif event.key == pygame.K_SPACE:
                    paused = not paused

                elif event.key == pygame.K_r:
                    grid, ant = reset()
                    paused    = False

                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS,
                                   pygame.K_KP_PLUS):
                    spf = min(MAX_SPF, spf + SPEED_STEP)

                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    spf = max(MIN_SPF, spf - SPEED_STEP)

                elif event.key == pygame.K_s:
                    show_steps = not show_steps

        # ── Simulation ───────────────────────────────────────────────────────
        if not paused:
            for _ in range(spf):
                ant.step(grid)

        # ── Draw ─────────────────────────────────────────────────────────────
        screen.fill(BG_COLOUR)
        draw_grid_lines(screen, WINDOW_W, WINDOW_H)
        draw_cells(screen, grid, offset_x, offset_y,
                   ant.steps, ant.highway, ant._hw_step, WINDOW_W, WINDOW_H)
        draw_ant(screen, ant, offset_x, offset_y)
        draw_ui(screen, font_large, font_small,
                ant.steps, spf, paused, show_steps,
                ant.highway, ant._hw_step, WINDOW_W, WINDOW_H)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()