import os

TARGET_FPS: int = int(os.environ.get("TARGET_FPS", 60))
STEPS_PER_FRAME: int = int(os.environ.get("STEPS_PER_FRAME", 10))
SPEED_STEP: int = int(os.environ.get("SPEED_STEP", 5))
MAX_SPF: int = int(os.environ.get("MAX_SPF", 500))
MIN_SPF: int = int(os.environ.get("MIN_SPF", 1))

NUM_NOISE_CELLS: int = int(os.environ.get("NUM_NOISE_CELLS", 200))
# Fraction of visible grid radius used for initial noise spread: radius // NOISE_SPREAD_DIVISOR
NOISE_SPREAD_DIVISOR: int = int(os.environ.get("NOISE_SPREAD_DIVISOR", 8))
RANDOM_DIRECTIONS: bool = os.environ.get("RANDOM_DIRECTIONS", "true").lower() == "true"
