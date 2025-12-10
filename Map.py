# Map.py
import pygame
import random
import os
from constants import GRID_SIZE, ROWS, COLS

class Map:
    def __init__(self):
        self.grid = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1], 
            [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        self.wall_sprite = self.load_sprite('wall.png')
        
    def load_sprite(self, filename):
        """Load sprite dari folder images/ dengan path relatif"""
        path = os.path.join('images', filename)
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (GRID_SIZE, GRID_SIZE))
        return image
    
    def get_random_position(self, min_distance_from=None, min_distance=5):
        """
        Mendapatkan posisi random yang bebas (bukan wall)
        min_distance_from: tuple (x, y) posisi yang harus dijauhi
        min_distance: jarak minimum dalam grid cells
        """
        max_attempts = 100  # Batasi percobaan untuk menghindari infinite loop
        attempts = 0
        
        while attempts < max_attempts:
            grid_x = random.randint(1, COLS - 2)
            grid_y = random.randint(1, ROWS - 2)
            x = grid_x * GRID_SIZE
            y = grid_y * GRID_SIZE
            
            if self.grid[grid_y][grid_x] == 0:  # Hanya 0 = bebas
                # Jika ada posisi yang harus dijauhi, cek jaraknya
                if min_distance_from is not None:
                    from_grid_x = min_distance_from[0] // GRID_SIZE
                    from_grid_y = min_distance_from[1] // GRID_SIZE
                    distance = abs(grid_x - from_grid_x) + abs(grid_y - from_grid_y)
                    
                    if distance >= min_distance:
                        return x, y
                else:
                    return x, y
            
            attempts += 1
        
        # Jika tidak menemukan posisi ideal, kembalikan posisi random biasa
        while True:
            grid_x = random.randint(1, COLS - 2)
            grid_y = random.randint(1, ROWS - 2)
            x = grid_x * GRID_SIZE
            y = grid_y * GRID_SIZE
            if self.grid[grid_y][grid_x] == 0:
                return x, y
    
    def draw(self, screen):
        """Draw map ke screen"""
        for row in range(ROWS):
            for col in range(COLS):
                if self.grid[row][col] == 1:
                    screen.blit(self.wall_sprite, (col * GRID_SIZE, row * GRID_SIZE))