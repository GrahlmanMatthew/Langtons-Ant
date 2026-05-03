from langtons_ant.simulation.grid import make_random_grid


def test_make_random_grid_cell_count():
    grid = make_random_grid(noise_spread=20, num_cells=50)
    white_cells = sum(1 for v in grid.values() if v)
    # Duplicates are possible (same coordinate drawn twice), so count is at most num_cells
    assert 1 <= white_cells <= 50


def test_make_random_grid_within_bounds():
    noise_spread = 10
    grid = make_random_grid(noise_spread=noise_spread, num_cells=100)
    for (x, y), is_white in grid.items():
        if is_white:
            assert -noise_spread <= x <= noise_spread, f"x={x} out of bounds"
            assert -noise_spread <= y <= noise_spread, f"y={y} out of bounds"


def test_make_random_grid_returns_defaultdict():
    grid = make_random_grid(noise_spread=5, num_cells=10)
    # Unset keys should default to False (black)
    assert grid[(999, 999)] is False


def test_make_random_grid_zero_spread():
    grid = make_random_grid(noise_spread=0, num_cells=5)
    # All cells must land on (0, 0)
    assert len([k for k, v in grid.items() if v]) == 1
    assert grid[(0, 0)] is True
