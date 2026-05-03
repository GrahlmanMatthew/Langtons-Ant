import random
from collections import defaultdict


def make_random_grid(noise_spread: int, num_cells: int) -> defaultdict:
    """Pre-flip a random sample of cells near the origin to seed variety on each reset."""
    grid: defaultdict = defaultdict(bool)
    for _ in range(num_cells):
        x = random.randint(-noise_spread, noise_spread)
        y = random.randint(-noise_spread, noise_spread)
        grid[(x, y)] = True
    return grid
