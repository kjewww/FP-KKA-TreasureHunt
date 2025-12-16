import pygame
import random
import os
import heapq
from collections import deque
from constants import GRID_SIZE, ROWS, COLS, DIRECTION_RIGHT, DIRECTION_UP, DIRECTION_LEFT, DIRECTION_DOWN

class Enemy(pygame.Rect):
    # Added speed parameter to __init__
    def __init__(self, x, y, color='Blue', speed=4):
        super().__init__(x, y, GRID_SIZE, GRID_SIZE)
        self.grid_x = x // GRID_SIZE
        self.grid_y = y // GRID_SIZE
        self.target_x = self.grid_x
        self.target_y = self.grid_y
        self.x = self.grid_x * GRID_SIZE
        self.y = self.grid_y * GRID_SIZE
        self.direction = DIRECTION_RIGHT
        self.moving = False
        
        self.move_speed = speed # Use the passed speed value
        
        self.move_cooldown = 0
        self.cooldown_time = 2
        
        # Animation
        self.color = color
        self.load_animations()
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.animation_counter = 0
        self.facing_direction = 'right'

    def load_animations(self):
        self.walk_frames = []
        path_color = self.color
        walk_path = os.path.join('assets', 'slime', f'walk{path_color}')
        if not os.path.exists(walk_path):
            walk_path = os.path.join('assets', 'slime', f'walkBlue')
        for i in range(1, 3):
            try:
                img = pygame.image.load(os.path.join(walk_path, f'walk{i}.png')).convert_alpha()
                img = pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))
                self.walk_frames.append(img)
            except Exception as e:
                print(f"Error loading sprite: {e}")

    def get_current_sprite(self):
        if not self.walk_frames:
            return pygame.Surface((GRID_SIZE, GRID_SIZE)) 
        frame_index = int(self.animation_frame) % len(self.walk_frames)
        sprite = self.walk_frames[frame_index]
        if self.facing_direction == 'left':
            sprite = pygame.transform.flip(sprite, True, False)
        return sprite

    def update_animation(self):
        self.animation_counter += self.animation_speed
        self.animation_frame = self.animation_counter

    def move_in_direction(self, direction, map_grid, enemies):
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
        
        if not self.is_valid_position(new_grid_x, new_grid_y, map_grid):
            return False

        for enemy in enemies:
            if enemy is self: 
                continue
            if enemy.target_x == new_grid_x and enemy.target_y == new_grid_y:
                return False
        
        self.target_x = new_grid_x
        self.target_y = new_grid_y
        self.moving = True
        return True

    def update_movement(self):
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
        if self.moving:
            target_pixel_x = self.target_x * GRID_SIZE
            target_pixel_y = self.target_y * GRID_SIZE
            if self.x < target_pixel_x:
                self.x = min(self.x + self.move_speed, target_pixel_x)
            elif self.x > target_pixel_x:
                self.x = max(self.x - self.move_speed, target_pixel_x)
            if self.y < target_pixel_y:
                self.y = min(self.y + self.move_speed, target_pixel_y)
            elif self.y > target_pixel_y:
                self.y = max(self.y - self.move_speed, target_pixel_y)
            if self.x == target_pixel_x and self.y == target_pixel_y:
                self.grid_x = self.target_x
                self.grid_y = self.target_y
                self.moving = False
                self.move_cooldown = self.cooldown_time
        self.update_animation()

    def is_valid_position(self, grid_x, grid_y, map_grid):
        if 0 <= grid_y < ROWS and 0 <= grid_x < COLS:
            return map_grid[grid_y][grid_x] == 0
        return False

    def get_map_x(self): return self.grid_x
    def get_map_y(self): return self.grid_y
    def heuristic(self, a_x, a_y, b_x, b_y): 
        return abs(a_x - b_x) + abs(a_y - b_y)

    def calculate_new_direction(self, map_grid, dest_x, dest_y):
        if self.color == 'Green':
            return self.calculate_greedy_direction(map_grid, dest_x, dest_y)
        elif self.color == 'Red':
            return self.calculate_astar_direction(map_grid, dest_x, dest_y)
        else:
            return self.calculate_bfs_direction(map_grid, dest_x, dest_y)

    def calculate_bfs_direction(self, map_grid, dest_x, dest_y):
        if self.grid_x == dest_x and self.grid_y == dest_y: 
            return None
        queue = deque([{
            'x': self.grid_x, 
            'y': self.grid_y, 
            'first_move': None
            }])
        visited = set()
        visited.add((self.grid_x, self.grid_y))
        while queue:
            current = queue.popleft()
            if current['x'] == dest_x and current['y'] == dest_y:
                return current['first_move']
            neighbors = self.get_neighbors(current['x'], current['y'], map_grid)
            for nx, ny, direction in neighbors:
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    next_move = current['first_move'] if current['first_move'] is not None else direction
                    queue.append({'x': nx, 'y': ny, 'first_move': next_move})
        return None

    def calculate_greedy_direction(self, map_grid, dest_x, dest_y):
        if self.grid_x == dest_x and self.grid_y == dest_y: return None
        start_h = self.heuristic(self.grid_x, self.grid_y, dest_x, dest_y)
        pq = [(start_h, self.grid_x, self.grid_y, None)]
        visited = set()
        visited.add((self.grid_x, self.grid_y))
        while pq:
            _, curr_x, curr_y, first_move = heapq.heappop(pq)
            if curr_x == dest_x and curr_y == dest_y: return first_move
            neighbors = self.get_neighbors(curr_x, curr_y, map_grid)
            for nx, ny, direction in neighbors:
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    h = self.heuristic(nx, ny, dest_x, dest_y)
                    next_move = first_move if first_move is not None else direction
                    heapq.heappush(pq, (h, nx, ny, next_move))
        return None

    def calculate_astar_direction(self, map_grid, dest_x, dest_y):
        if self.grid_x == dest_x and self.grid_y == dest_y: return None
        start_h = self.heuristic(self.grid_x, self.grid_y, dest_x, dest_y)
        pq = [(start_h, 0, self.grid_x, self.grid_y, None)]
        cost_so_far = {(self.grid_x, self.grid_y): 0}
        while pq:
            f, g, curr_x, curr_y, first_move = heapq.heappop(pq)
            if curr_x == dest_x and curr_y == dest_y: return first_move
            neighbors = self.get_neighbors(curr_x, curr_y, map_grid)
            for nx, ny, direction in neighbors:
                new_cost = g + 1
                if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                    cost_so_far[(nx, ny)] = new_cost
                    priority = new_cost + self.heuristic(nx, ny, dest_x, dest_y)
                    next_move = first_move if first_move is not None else direction
                    heapq.heappush(pq, (priority, new_cost, nx, ny, next_move))
        return None

    def get_neighbors(self, x, y, mp):
        neighbors = []
        num_rows = len(mp)
        num_cols = len(mp[0])
        directions = [
            (DIRECTION_LEFT, -1, 0), (DIRECTION_RIGHT, 1, 0),
            (DIRECTION_UP, 0, -1), (DIRECTION_DOWN, 0, 1)
        ]
        for direction, dx, dy in directions:
            new_x = x + dx
            new_y = y + dy
            if (0 <= new_x < num_cols and 0 <= new_y < num_rows and mp[new_y][new_x] != 1):
                neighbors.append((new_x, new_y, direction))
        return neighbors

    def update(self, player, map_grid, enemies):
        self.update_movement()
        if self.moving or self.move_cooldown > 0: return
        target_x = player.get_map_x()
        target_y = player.get_map_y()
        new_direction = self.calculate_new_direction(map_grid, target_x, target_y)
        if new_direction is not None:
            self.direction = new_direction
            self.move_in_direction(self.direction, map_grid, enemies)
    
    def draw(self, screen):
        sprite = self.get_current_sprite()
        screen.blit(sprite, (self.x, self.y))