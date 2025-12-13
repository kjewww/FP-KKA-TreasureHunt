import pygame
import random
import os
from collections import deque
from constants import GRID_SIZE, ROWS, COLS, DIRECTION_RIGHT, DIRECTION_UP, DIRECTION_LEFT, DIRECTION_DOWN

class Enemy(pygame.Rect):
    def __init__(self, x, y, color='Blue'):
        super().__init__(x, y, GRID_SIZE, GRID_SIZE)
        self.grid_x = x // GRID_SIZE
        self.grid_y = y // GRID_SIZE
        self.target_x = self.grid_x
        self.target_y = self.grid_y
        self.x = self.grid_x * GRID_SIZE
        self.y = self.grid_y * GRID_SIZE
        self.direction = DIRECTION_RIGHT
        self.moving = False
        self.move_speed = 4  # Pixel per frame - lebih lambat dari player
        self.move_cooldown = 0
        self.cooldown_time = 2  # Cooldown kecil
        
        # Animation
        self.color = color  # Blue, Red, atau Green
        self.load_animations()
        self.animation_frame = 0
        self.animation_speed = 0.1  # Kecepatan animasi
        self.animation_counter = 0
        self.facing_direction = 'right'  # right atau left

    def load_animations(self):
        self.walk_frames = []
        
        # Load walk sprites berdasarkan warna (2 frames)
        walk_path = os.path.join('assets', 'slime', f'walk{self.color}')
        for i in range(1, 3):  # walk1.png, walk2.png
            img = pygame.image.load(os.path.join(walk_path, f'walk{i}.png')).convert_alpha()
            img = pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))
            self.walk_frames.append(img)

    def get_current_sprite(self):
        frame_index = int(self.animation_frame) % len(self.walk_frames)
        sprite = self.walk_frames[frame_index]
        
        # Flip sprite jika menghadap kiri
        if self.facing_direction == 'left':
            sprite = pygame.transform.flip(sprite, True, False)
        
        return sprite

    def update_animation(self): # Update frame animasi
        self.animation_counter += self.animation_speed
        self.animation_frame = self.animation_counter

    def move_in_direction(self, direction, map_grid): # bergerak per grid/cell
        if self.moving or self.move_cooldown > 0:
            return False
            
        new_grid_x = self.grid_x
        new_grid_y = self.grid_y
        
        if direction == DIRECTION_RIGHT:
            new_grid_x += 1
            self.facing_direction = 'right'
        elif direction == DIRECTION_LEFT:
            new_grid_x -= 1
            self.facing_direction = 'left'
        elif direction == DIRECTION_UP:
            new_grid_y -= 1
        elif direction == DIRECTION_DOWN:
            new_grid_y += 1
        
        # Cek apakah posisi valid
        if self.is_valid_position(new_grid_x, new_grid_y, map_grid):
            self.target_x = new_grid_x
            self.target_y = new_grid_y
            self.moving = True
            return True
        return False

    def update_movement(self): # Update posisi pixel agar animasi tidak kaku
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            
        if self.moving:
            target_pixel_x = self.target_x * GRID_SIZE
            target_pixel_y = self.target_y * GRID_SIZE
            
            # Interpolasi posisi X
            if self.x < target_pixel_x:
                self.x = min(self.x + self.move_speed, target_pixel_x)
            elif self.x > target_pixel_x:
                self.x = max(self.x - self.move_speed, target_pixel_x)
            
            # Interpolasi posisi Y
            if self.y < target_pixel_y:
                self.y = min(self.y + self.move_speed, target_pixel_y)
            elif self.y > target_pixel_y:
                self.y = max(self.y - self.move_speed, target_pixel_y)
            
            # Cek apakah sudah sampai target
            if self.x == target_pixel_x and self.y == target_pixel_y:
                self.grid_x = self.target_x
                self.grid_y = self.target_y
                self.moving = False
                self.move_cooldown = self.cooldown_time
        
        # Update animasi
        self.update_animation()

    def is_valid_position(self, grid_x, grid_y, map_grid): # cek apakah posisi valid
        if 0 <= grid_y < ROWS and 0 <= grid_x < COLS:
            return map_grid[grid_y][grid_x] == 0
        return False

    def get_map_x(self):
        return self.grid_x

    def get_map_y(self):
        return self.grid_y

    # implementasi BFS untuk shortest pathfinding ke player

    def calculate_new_direction(self, map_grid, dest_x, dest_y):
        # Jika sudah di posisi target
        if self.grid_x == dest_x and self.grid_y == dest_y:
            return None
            
        queue = deque([{
            'x': self.grid_x,
            'y': self.grid_y,
            'moves': []
        }])
        
        visited = set()
        visited.add((self.grid_x, self.grid_y))

        while queue:
            popped = queue.popleft()
            
            # Jika sampai tujuan
            if popped['x'] == dest_x and popped['y'] == dest_y:
                return popped['moves'][0] if popped['moves'] else None

            # Cek tetangga
            neighbors = self.get_neighbors(popped, map_grid, visited)
            queue.extend(neighbors)

        return None  # Tidak ada jalur


    def get_neighbors(self, current, mp, visited):
        neighbors = []
        num_rows = len(mp)
        num_cols = len(mp[0])

        directions = [
            (DIRECTION_LEFT, -1, 0),
            (DIRECTION_RIGHT, 1, 0),
            (DIRECTION_UP, 0, -1),
            (DIRECTION_DOWN, 0, 1)
        ]

        for direction, dx, dy in directions:
            new_x = current['x'] + dx
            new_y = current['y'] + dy
            
            # Cek apakah valid dan belum dikunjungi
            if (0 <= new_x < num_cols and 0 <= new_y < num_rows and 
                mp[new_y][new_x] != 1 and (new_x, new_y) not in visited):
                
                visited.add((new_x, new_y))
                temp_moves = current['moves'].copy()
                temp_moves.append(direction)
                neighbors.append({
                    'x': new_x,
                    'y': new_y,
                    'moves': temp_moves
                })

        return neighbors

    def update(self, player, map_grid):
        # Update smooth movement animation
        self.update_movement()
        
        # Jika sedang bergerak, jangan hitung path baru
        if self.moving or self.move_cooldown > 0:
            return

        # Selalu mengejar player (tidak ada patrol mode)
        target_x = player.get_map_x()
        target_y = player.get_map_y()

        # Hitung arah baru menggunakan BFS
        new_direction = self.calculate_new_direction(map_grid, target_x, target_y)
        
        if new_direction is not None:
            self.direction = new_direction
            self.move_in_direction(self.direction, map_grid)
    
    def draw(self, screen): # Draw enemy di layar dgn animasi
        sprite = self.get_current_sprite()
        screen.blit(sprite, (self.x, self.y))