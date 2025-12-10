import pygame

# Inisialisasi Pygame
pygame.init()

# Ukuran layar dan grid
WIDTH, HEIGHT = 630, 690  # 21 cols x 30 = 630, 23 rows x 30 = 690
GRID_SIZE = 30  # Ukuran per grid cell
ROWS, COLS = HEIGHT // GRID_SIZE, WIDTH // GRID_SIZE  # 23 rows, 21 cols

# Warna
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)  # Player
YELLOW = (255, 255, 0)  # Key
RED = (255, 0, 0)  # Treasure
DARK_RED = (139, 0, 0)  # Enemy

# Arah konstan
DIRECTION_RIGHT = 4
DIRECTION_UP = 3
DIRECTION_LEFT = 2
DIRECTION_DOWN = 1

# Target acak untuk musuh (pojok-pojok peta)
random_targets_for_enemies = [
    (1 * GRID_SIZE, 1 * GRID_SIZE),  # (30, 30)
    (1 * GRID_SIZE, (ROWS - 2) * GRID_SIZE),  # (30, 630)
    ((COLS - 2) * GRID_SIZE, 1 * GRID_SIZE),  # (570, 30)
    ((COLS - 2) * GRID_SIZE, (ROWS - 2) * GRID_SIZE)  # (570, 630)
]