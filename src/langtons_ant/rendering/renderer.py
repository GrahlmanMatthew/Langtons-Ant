from collections import defaultdict

import pygame

from langtons_ant.config.constants import (
    ACCENT_COLOUR,
    ANT_COLOUR,
    CELL_SIZE,
    GRID_COLOUR,
    HIGHWAY_COLOUR,
    UI_COLOUR,
    WHITE_CELL,
)
from langtons_ant.simulation.ant import Ant


def world_to_screen(wx: int, wy: int, offset_x: int, offset_y: int) -> tuple[int, int]:
    return (wx + offset_x) * CELL_SIZE, (wy + offset_y) * CELL_SIZE


def draw_grid_lines(surface: pygame.Surface, window_w: int, window_h: int) -> None:
    """Subtle grid — only drawn when cells are large enough to warrant it."""
    if CELL_SIZE < 6:
        return
    for x in range(0, window_w, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOUR, (x, 0), (x, window_h))
    for y in range(0, window_h, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOUR, (0, y), (window_w, y))


def draw_cells(
    surface: pygame.Surface,
    grid: defaultdict,
    offset_x: int,
    offset_y: int,
    window_w: int,
    window_h: int,
    steps: int,
    highway: bool,
    highway_step: int,
) -> None:
    if highway:
        t = min(1.0, (steps - highway_step) / 2000)
        cell_colour = (
            int(WHITE_CELL[0] * (1 - t) + HIGHWAY_COLOUR[0] * t),
            int(WHITE_CELL[1] * (1 - t) + HIGHWAY_COLOUR[1] * t),
            int(WHITE_CELL[2] * (1 - t) + HIGHWAY_COLOUR[2] * t),
        )
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


def draw_ant(surface: pygame.Surface, ant: Ant, offset_x: int, offset_y: int) -> None:
    sx = (ant.x + offset_x) * CELL_SIZE
    sy = (ant.y + offset_y) * CELL_SIZE
    cx = sx + CELL_SIZE // 2
    cy = sy + CELL_SIZE // 2
    r = max(2, CELL_SIZE // 2)
    glow_surf = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
    for i in range(4, 0, -1):
        pygame.draw.circle(glow_surf, (*ANT_COLOUR, 40 * i), (r * 3, r * 3), r * i)
    surface.blit(glow_surf, (cx - r * 3, cy - r * 3))
    pygame.draw.circle(surface, ANT_COLOUR, (cx, cy), r)


def draw_ui(
    surface: pygame.Surface,
    font_large: pygame.font.Font,
    font_small: pygame.font.Font,
    steps: int,
    spf: int,
    paused: bool,
    show_steps: bool,
    highway: bool,
    highway_step: int,
    window_w: int,
    window_h: int,
) -> None:
    if show_steps:
        label = font_large.render(f"{steps:,}", True, ACCENT_COLOUR)
        surface.blit(label, (12, 8))
        sub = font_small.render("steps", True, UI_COLOUR)
        surface.blit(sub, (14, 8 + label.get_height()))

    speed_txt = font_small.render("⏸  PAUSED" if paused else f"×{spf} steps/frame", True, UI_COLOUR)
    surface.blit(speed_txt, (12, window_h - 28))

    hint = font_small.render(
        "SPACE pause  |  R reset  |  +/− speed  |  S toggle counter  |  ESC quit",
        True,
        (80, 80, 110),
    )
    surface.blit(hint, (window_w // 2 - hint.get_width() // 2, window_h - 22))

    if highway:
        banner_alpha = min(255, int(255 * (steps - highway_step) / 500))
        banner = font_small.render("◆  HIGHWAY EMERGED  ◆", True, HIGHWAY_COLOUR)
        banner.set_alpha(banner_alpha)
        surface.blit(banner, (window_w - banner.get_width() - 12, 12))
