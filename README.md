# 🐜 Langton's Ant

A real-time visualizer for one of computer science's most surprising emergent systems — built with Python and Pygame.

---

## Demo
![Langton's Ant demo](output.gif)

---

## What is Langton's Ant?

An ant lives on an infinite grid of black and white cells and follows exactly two rules:

- **On a white cell** — turn right, flip the cell to black, move forward
- **On a black cell** — turn left, flip the cell to white, move forward

That's the entire system. What makes it remarkable is what happens over time:

1. **Early steps** — the ant produces what looks like complete chaos, wandering with no discernible structure
2. **On average after 10,000 steps** — with no warning, it spontaneously begins constructing a perfectly regular diagonal corridor called the **highway**, and continues indefinitely

The exact step at which the highway emerges varies each run depending on the random starting conditions. Nobody has ever formally proved *why* the highway emerges at all, let alone *when* — it has been observed in every simulation ever run, but a mathematical explanation remains an open problem.

---

## Features

- Borderless windowed rendering sized to your monitor resolution
- Randomised starting conditions on each reset — different initial noise and ant direction — so the chaotic phase looks unique every run
- Live step counter with a highway detection banner when the diagonal corridor kicks in
- Smooth colour transition from white → cyan as the highway phase begins
- Adjustable simulation speed

---

## Setup

This project uses Python 3.10.10. If you don't have pyenv installed, get it first:

```bash
# macOS
brew install pyenv

# Linux
curl https://pyenv.run | bash
```

Then install the correct Python version and set up a virtual environment:

```bash
pyenv install 3.10.10
pyenv local 3.10.10

pip install virtualenv
virtualenv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

---

## Usage

```bash
python main.py
```

| Key         | Action                                    |
| ----------- | ----------------------------------------- |
| `SPACE`     | Pause / resume                            |
| `R`         | Reset with new random starting conditions |
| `+` / `=`   | Speed up                                  |
| `-`         | Slow down                                 |
| `S`         | Toggle step counter                       |
| `ESC` / `Q` | Quit                                      |

---

## Tuning

All parameters are at the top of `main.py`:

| Constant            | Default | Description                             |
| ------------------- | ------- | --------------------------------------- |
| `CELL_SIZE`         | `5`     | Pixels per grid cell                    |
| `TARGET_FPS`        | `60`    | Render framerate cap                    |
| `STEPS_PER_FRAME`   | `10`    | Ant steps per rendered frame            |
| `NUM_NOISE_CELLS`   | `200`   | Random cells pre-flipped on reset       |
| `RANDOM_DIRECTIONS` | `True`  | Randomise ant's starting direction      |
| `HIGHWAY_THRESHOLD` | `10000` | Step count at which highway tint begins |