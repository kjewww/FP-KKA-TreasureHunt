# Player.py
import pygame
import os
from constants import GRID_SIZE, ROWS, COLS

class Player(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, GRID_SIZE, GRID_SIZE)
        self.grid_x = x // GRID_SIZE
        self.grid_y = y // GRID_SIZE
        self.target_x = self.grid_x
        self.target_y = self.grid_y
        self.x = self.grid_x * GRID_SIZE
        self.y = self.grid_y * GRID_SIZE
        self.moving = False
        self.move_speed = 6  # Pixel per frame untuk smooth movement
        self.move_cooldown = 0
        self.cooldown_time = 2  # Cooldown lebih kecil karena ada animasi
        
        # Animation
        self.direction = 'right'  # right, left, up, down
        self.load_animations()
        self.current_animation = 'idle'
        self.animation_frame = 0
        self.animation_speed = 0.15  # Kecepatan animasi
        self.animation_counter = 0

    def load_animations(self):
        """Load semua sprite animasi"""
        self.animations = {
            'idle': [],
            'walk': []
        }
        
        # Load idle sprites (2 frames)
        idle_path = os.path.join('assets', 'player', 'idle')
        for i in range(1, 3):  # idle1.png, idle2.png
            img = pygame.image.load(os.path.join(idle_path, f'wizard_idle{i}.png')).convert_alpha()
            img = pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))
            self.animations['idle'].append(img)
        
        # Load walk sprites (4 frames)
        walk_path = os.path.join('assets', 'player', 'walk')
        for i in range(1, 5):  # walk1.png, walk2.png, walk3.png, walk4.png
            img = pygame.image.load(os.path.join(walk_path, f'wizard_{i}.png')).convert_alpha()
            img = pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))
            self.animations['walk'].append(img)

    def get_current_sprite(self):
        """Dapatkan sprite saat ini berdasarkan animasi dan arah"""
        frames = self.animations[self.current_animation]
        frame_index = int(self.animation_frame) % len(frames)
        sprite = frames[frame_index]
        
        # Flip sprite berdasarkan arah
        if self.direction == 'left':
            sprite = pygame.transform.flip(sprite, True, False)
        # elif self.direction == 'up':
        #     sprite = pygame.transform.rotate(sprite, 90)
        # elif self.direction == 'down':
        #     sprite = pygame.transform.rotate(sprite, -90)
        
        return sprite

    def update_animation(self):
        """Update frame animasi"""
        self.animation_counter += self.animation_speed
        self.animation_frame = self.animation_counter
        
        # Set animasi berdasarkan state
        if self.moving:
            self.current_animation = 'walk'
        else:
            self.current_animation = 'idle'
            self.animation_counter = 0
            self.animation_frame = 0

    def move(self, dx, dy, map_grid):
        # Hanya bisa bergerak jika tidak sedang bergerak atau cooldown
        if self.moving or self.move_cooldown > 0:
            return
            
        new_grid_x = self.grid_x + dx
        new_grid_y = self.grid_y + dy
        
        if self.is_valid_move(new_grid_x, new_grid_y, map_grid):
            self.target_x = new_grid_x
            self.target_y = new_grid_y
            self.moving = True
            
            # Update arah berdasarkan input
            if dx > 0:
                self.direction = 'right'
            elif dx < 0:
                self.direction = 'left'
            elif dy > 0:
                self.direction = 'down'
            elif dy < 0:
                self.direction = 'up'

    def update(self):
        # Kurangi cooldown setiap frame
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
        
        # Smooth movement menuju target
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

    def is_valid_move(self, grid_x, grid_y, map_grid):
        # Cek apakah posisi grid valid dan bukan wall
        if 0 <= grid_y < ROWS and 0 <= grid_x < COLS:
            return map_grid[grid_y][grid_x] == 0
        return False

    def get_map_x(self):
        return self.grid_x

    def get_map_y(self):
        return self.grid_y
    
    def draw(self, screen):
        """Draw player dengan animasi"""
        sprite = self.get_current_sprite()
        screen.blit(sprite, (self.x, self.y))