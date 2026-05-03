import logging
import random
import sys

import pygame

from langtons_ant.config import constants, settings
from langtons_ant.rendering.renderer import draw_ant, draw_cells, draw_grid_lines, draw_ui
from langtons_ant.simulation.ant import Ant
from langtons_ant.simulation.grid import make_random_grid

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def initialize_display() -> tuple[pygame.Surface, int, int, pygame.font.Font, pygame.font.Font]:
    pygame.init()
    window_w, window_h = 1280, 720
    screen = pygame.display.set_mode((window_w, window_h))
    pygame.display.set_caption("Langton's Ant")
    try:
        font_large = pygame.font.SysFont("monospace", 28, bold=True)
        font_small = pygame.font.SysFont("monospace", 14)
    except Exception:
        font_large = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 18)
    return screen, window_w, window_h, font_large, font_small


def make_initial_state(window_w: int, window_h: int) -> dict:
    noise_spread = min(window_w, window_h) // (constants.CELL_SIZE * settings.NOISE_SPREAD_DIVISOR)
    direction = random.randint(0, 3) if settings.RANDOM_DIRECTIONS else constants.UP
    return {
        "ant": Ant(0, 0, direction),
        "grid": make_random_grid(noise_spread, settings.NUM_NOISE_CELLS),
        "spf": settings.STEPS_PER_FRAME,
        "paused": False,
        "show_steps": True,
        "offset_x": (window_w // constants.CELL_SIZE) // 2,
        "offset_y": (window_h // constants.CELL_SIZE) // 2,
        "noise_spread": noise_spread,
    }


def handle_events(state: dict, window_w: int, window_h: int) -> bool:
    """Process all queued events. Returns False when the user requests quit."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type != pygame.KEYDOWN:
            continue
        key = event.key
        if key in (pygame.K_ESCAPE, pygame.K_q):
            return False
        elif key == pygame.K_SPACE:
            state["paused"] = not state["paused"]
        elif key == pygame.K_r:
            state.update(make_initial_state(window_w, window_h))
        elif key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            state["spf"] = min(settings.MAX_SPF, state["spf"] + settings.SPEED_STEP)
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            state["spf"] = max(settings.MIN_SPF, state["spf"] - settings.SPEED_STEP)
        elif key == pygame.K_s:
            state["show_steps"] = not state["show_steps"]
    return True


def update_simulation(state: dict) -> None:
    if state["paused"]:
        return
    ant: Ant = state["ant"]
    grid = state["grid"]
    for _ in range(state["spf"]):
        ant.step(grid)


def render_frame(
    surface: pygame.Surface,
    state: dict,
    font_large: pygame.font.Font,
    font_small: pygame.font.Font,
    window_w: int,
    window_h: int,
) -> None:
    ant: Ant = state["ant"]
    surface.fill(constants.BG_COLOUR)
    draw_grid_lines(surface, window_w, window_h)
    draw_cells(
        surface,
        state["grid"],
        state["offset_x"],
        state["offset_y"],
        window_w,
        window_h,
        ant.steps,
        ant.highway,
        ant.highway_step,
    )
    draw_ant(surface, ant, state["offset_x"], state["offset_y"])
    draw_ui(
        surface,
        font_large,
        font_small,
        ant.steps,
        state["spf"],
        state["paused"],
        state["show_steps"],
        ant.highway,
        ant.highway_step,
        window_w,
        window_h,
    )
    pygame.display.flip()


def run() -> None:
    logger.info("Starting Langton's Ant")
    logger.info(
        "Settings: TARGET_FPS=%d  STEPS_PER_FRAME=%d  CELL_SIZE=%d",
        settings.TARGET_FPS,
        settings.STEPS_PER_FRAME,
        constants.CELL_SIZE,
    )
    screen, window_w, window_h, font_large, font_small = initialize_display()
    clock = pygame.time.Clock()
    state = make_initial_state(window_w, window_h)
    running = True
    while running:
        clock.tick(settings.TARGET_FPS)
        running = handle_events(state, window_w, window_h)
        update_simulation(state)
        render_frame(screen, state, font_large, font_small, window_w, window_h)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run()
