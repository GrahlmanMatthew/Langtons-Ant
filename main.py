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
import math
from collections import defaultdict
 
# ── Tunables ─────────────────────────────────────────────────────────────────
WINDOW_W, WINDOW_H = 900, 900
CELL_SIZE          = 4          # pixels per grid cell
TARGET_FPS         = 60
STEPS_PER_FRAME    = 10         # ant moves this many steps each rendered frame
SPEED_STEP         = 5          # how much +/- changes steps-per-frame
MAX_SPF            = 500
MIN_SPF            = 1
 
# Colour palette — dark background, vivid foreground
BG_COLOUR          = (10,  10,  18)
WHITE_CELL         = (230, 230, 255)   # "white" (on) cell
BLACK_CELL         = BG_COLOUR         # "black" (off) cell — same as background
ANT_COLOUR         = (255,  60,  80)
GRID_COLOUR        = (25,   25,  40)
UI_COLOUR          = (180, 180, 220)
ACCENT_COLOUR      = (255, 200,  50)
HIGHWAY_COLOUR     = (80,  200, 255)   # colour flash once highway emerges
 
HIGHWAY_THRESHOLD  = 10_000    # steps at which the highway reliably starts
 
# ── Direction helpers ─────────────────────────────────────────────────────────
# Directions: 0=Up, 1=Right, 2=Down, 3=Left
DIR_DELTA = [(0, -1), (1, 0), (0, 1), (-1, 0)]
 
TURN_RIGHT = 1
TURN_LEFT  = -1
 
 
# ── Ant state ────────────────────────────────────────────────────────────────
class Ant:
    def __init__(self, x: int, y: int):
        self.x   = x
        self.y   = y
        self.dir = 0          # facing Up
        self.steps = 0
 
    def step(self, grid: dict) -> None:
        cell = (self.x, self.y)
        if grid[cell]:                # white cell → turn right, flip black
            self.dir = (self.dir + TURN_RIGHT) % 4
            grid[cell] = False
        else:                         # black cell → turn left, flip white
            self.dir = (self.dir + TURN_LEFT) % 4
            grid[cell] = True
        dx, dy     = DIR_DELTA[self.dir]
        self.x    += dx
        self.y    += dy
        self.steps += 1
 
 
# ── Rendering helpers ─────────────────────────────────────────────────────────
def world_to_screen(wx: int, wy: int, offset_x: int, offset_y: int) -> tuple:
    sx = (wx + offset_x) * CELL_SIZE
    sy = (wy + offset_y) * CELL_SIZE
    return sx, sy
 
 
def draw_grid_lines(surface: pygame.Surface) -> None:
    """Subtle grid — only drawn when cells are large enough to warrant it."""
    if CELL_SIZE < 6:
        return
    for x in range(0, WINDOW_W, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOUR, (x, 0), (x, WINDOW_H))
    for y in range(0, WINDOW_H, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOUR, (0, y), (0, WINDOW_H))
 
 
def draw_cells(surface: pygame.Surface,
               grid: dict,
               offset_x: int,
               offset_y: int,
               steps: int) -> None:
    cols_visible = WINDOW_W // CELL_SIZE + 2
    rows_visible = WINDOW_H // CELL_SIZE + 2
 
    # Choose white-cell tint based on highway phase
    if steps >= HIGHWAY_THRESHOLD:
        t = min(1.0, (steps - HIGHWAY_THRESHOLD) / 2000)
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
        if -CELL_SIZE <= sx < WINDOW_W and -CELL_SIZE <= sy < WINDOW_H:
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
            show_steps: bool) -> None:
    # Step counter
    if show_steps:
        label = font_large.render(f"{steps:,}", True, ACCENT_COLOUR)
        surface.blit(label, (12, 8))
        sub = font_small.render("steps", True, UI_COLOUR)
        surface.blit(sub, (14, 8 + label.get_height()))
 
    # Speed
    speed_txt = font_small.render(
        f"{'⏸  PAUSED' if paused else f'×{spf} steps/frame'}",
        True, UI_COLOUR)
    surface.blit(speed_txt, (12, WINDOW_H - 28))
 
    # Controls hint
    hint = font_small.render(
        "SPACE pause  |  R reset  |  +/− speed  |  S toggle counter  |  ESC quit",
        True, (80, 80, 110))
    surface.blit(hint, (WINDOW_W // 2 - hint.get_width() // 2, WINDOW_H - 22))
 
    # Highway banner
    if steps >= HIGHWAY_THRESHOLD:
        banner_alpha = min(255, int(255 * (steps - HIGHWAY_THRESHOLD) / 500))
        banner = font_small.render("◆  HIGHWAY EMERGED  ◆", True, HIGHWAY_COLOUR)
        banner.set_alpha(banner_alpha)
        surface.blit(banner, (WINDOW_W - banner.get_width() - 12, 12))
 
 
# ── Main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    pygame.init()
    pygame.display.set_caption("Langton's Ant")
    screen  = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock   = pygame.time.Clock()
 
    try:
        font_large = pygame.font.SysFont("monospace", 28, bold=True)
        font_small = pygame.font.SysFont("monospace", 14)
    except Exception:
        font_large = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 18)
 
    # Grid centre in world coords
    grid_cols = WINDOW_W // CELL_SIZE
    grid_rows = WINDOW_H // CELL_SIZE
    offset_x  = grid_cols  // 2
    offset_y  = grid_rows  // 2
 
    def make_ant():
        return Ant(0, 0)
 
    grid    = defaultdict(bool)   # True = white, False (default) = black
    ant     = make_ant()
    paused  = False
    spf     = STEPS_PER_FRAME    # steps per frame
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
                    grid   = defaultdict(bool)
                    ant    = make_ant()
                    paused = False
 
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
        draw_grid_lines(screen)
        draw_cells(screen, grid, offset_x, offset_y, ant.steps)
        draw_ant(screen,  ant,  offset_x, offset_y)
        draw_ui(screen, font_large, font_small,
                ant.steps, spf, paused, show_steps)
 
        pygame.display.flip()
 
    pygame.quit()
    sys.exit()
 
 
if __name__ == "__main__":
    main()