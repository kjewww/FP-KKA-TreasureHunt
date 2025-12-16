import pygame
import os
import random
from constants import WIDTH, HEIGHT, BLACK, BLUE, DARK_RED, YELLOW, RED, GRID_SIZE, WHITE
from Map import Map
from Player import Player
from Enemy import Enemy

class Game:
    def __init__(self):
        # Setup layar
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Treasure Hunt")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 28)
        self.menu_font = pygame.font.Font(None, 40)
        
        # Setup Audio
        self.bgm = pygame.mixer.Sound(os.path.join('assets', 'audio', 'bgm1.wav'))
        self.bgm.set_volume(0.5)
        self.lose_sound = pygame.mixer.Sound(os.path.join('assets', 'audio', 'lose.wav'))
        self.lose_sound.set_volume(0.7)
        self.win_sound = pygame.mixer.Sound(os.path.join('assets', 'audio', 'win.mp3'))
        self.win_sound.set_volume(0.7)
        self.get_item_sound = pygame.mixer.Sound(os.path.join('assets', 'audio', 'get_item.wav'))
        self.get_item_sound.set_volume(0.7)
        
        # Inisialisasi map
        self.map = Map()
        
        # Load sprites
        self.key_sprite = self.load_sprite('key.png')
        self.treasure_sprite = self.load_sprite('treasure.png')
        
        # Game Settings Defaults
        self.settings = {
            'level': 0,      # Index 0-4
            'color': 'Green', # Green, Red, Blue, Random
            'count': 3,      # 1-5
            'speed': 4       # 1-6
        }
        self.available_colors = ['Random', 'Green', 'Red', 'Blue']
        
        # Menu State
        self.state = 'MENU' # MENU, PLAYING, GAME_OVER
        self.menu_selection = 4 # 0=Level, 1=Color, 2=Count, 3=Speed, 4=Start
        
        self.running = True
        
    def load_sprite(self, filename):
        path = os.path.join('assets', 'item', filename)
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (GRID_SIZE, GRID_SIZE))
        return image

    def init_game(self): 
        # Apply Selected Map
        self.map.select_map(self.settings['level'])
        
        self.player = Player(GRID_SIZE, GRID_SIZE)
        self.key_pos = self.map.get_random_position()
        self.treasure_pos = None
        self.has_key = False
        
        self.win_sound.stop()
        self.lose_sound.stop()
        self.bgm.play(loops=-1)
        
        # Spawn Enemies based on settings
        self.enemies = []
        player_pos = (self.player.x, self.player.y)
        
        count = self.settings['count']
        speed = self.settings['speed']
        selected_color = self.settings['color']
        
        for i in range(count):
            enemy_pos = self.map.get_random_position(min_distance_from=player_pos, min_distance=8)
            
            # Determine color
            if selected_color == 'Random':
                actual_color = random.choice(['Green', 'Red', 'Blue'])
            else:
                actual_color = selected_color
                
            self.enemies.append(Enemy(*enemy_pos, color=actual_color, speed=speed))
        
        self.game_state = 'playing'
        self.state = 'PLAYING'

    def handle_menu_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                # Vertical Navigation
                if event.key == pygame.K_UP:
                    self.menu_selection = (self.menu_selection - 1) % 5
                elif event.key == pygame.K_DOWN:
                    self.menu_selection = (self.menu_selection + 1) % 5
                
                # Horizontal Adjustment
                elif event.key == pygame.K_LEFT:
                    self.adjust_setting(-1)
                elif event.key == pygame.K_RIGHT:
                    self.adjust_setting(1)
                    
                # Select/Start
                elif event.key == pygame.K_RETURN:
                    if self.menu_selection == 4: # Start Game
                        self.init_game()

    def adjust_setting(self, direction):
        if self.menu_selection == 0: # Level
            self.settings['level'] = (self.settings['level'] + direction) % len(self.map.all_maps)
        
        elif self.menu_selection == 1: # Color
            current_idx = self.available_colors.index(self.settings['color'])
            new_idx = (current_idx + direction) % len(self.available_colors)
            self.settings['color'] = self.available_colors[new_idx]
            
        elif self.menu_selection == 2: # Count
            self.settings['count'] = max(1, min(5, self.settings['count'] + direction))
            
        elif self.menu_selection == 3: # Speed
            self.settings['speed'] = max(1, min(6, self.settings['speed'] + direction))

    def draw_level_preview(self, start_x, start_y):
        preview_grid = self.map.all_maps[self.settings['level']]
        # Smaller tile size for preview
        PREVIEW_TILE = 8 
        
        # Border
        pygame.draw.rect(self.screen, WHITE, (start_x - 5, start_y - 5, (21 * PREVIEW_TILE) + 10, (23 * PREVIEW_TILE) + 10), 2)
        
        for r, row in enumerate(preview_grid):
            for c, tile in enumerate(row):
                color = (50, 50, 50) # Empty
                if tile == 1: color = (150, 150, 150) # Wall
                
                pygame.draw.rect(self.screen, color, 
                                (start_x + c * PREVIEW_TILE, 
                                start_y + r * PREVIEW_TILE, 
                                PREVIEW_TILE, PREVIEW_TILE))

    def draw_menu(self):
        self.screen.fill(BLACK)
        
        title = self.menu_font.render("GAME CONFIGURATION", True, YELLOW)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        labels = ["Level", "Slime Color", "Slime Count", "Slime Speed", "START GAME"]
        
        # Display Values
        val_level = f"Map {self.settings['level'] + 1}"
        val_color = self.settings['color']
        val_count = str(self.settings['count'])
        val_speed = str(self.settings['speed'])
        
        values = [val_level, val_color, val_count, val_speed, ""]
        
        start_y = 150
        gap = 50
        
        for i, label in enumerate(labels):
            color = WHITE
            prefix = "  "
            if i == self.menu_selection:
                color = YELLOW
                prefix = "> "
            
            text_str = f"{prefix}{label}"
            text = self.font.render(text_str, True, color)
            self.screen.blit(text, (100, start_y + i*gap))
            
            if values[i]:
                val_text = self.font.render(f"< {values[i]} >", True, color)
                self.screen.blit(val_text, (350, start_y + i*gap))
        
        # Draw Preview on the right side
        self.draw_level_preview(400, 400)
        
        # Instruction
        inst = self.button_font.render("Use Arrow Keys to Navigate & Modify", True, (100, 100, 100))
        self.screen.blit(inst, (WIDTH//2 - inst.get_width()//2, HEIGHT - 50))
        
        pygame.display.flip()

    def handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and self.game_state != 'playing':
                mouse_pos = pygame.mouse.get_pos()
                
                # menu
                if self.menu_button.collidepoint(mouse_pos):
                    self.state = 'MENU'
                    self.bgm.stop()
                    
                # restart
                # elif self.restart_button.collidepoint(mouse_pos):
                #     self.init_game()
                    
                # quit
                elif self.quit_button.collidepoint(mouse_pos):
                    self.running = False

    def handle_player_movement(self):
        if self.game_state != 'playing': return
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]: dx = -1
        elif keys[pygame.K_RIGHT]: dx = 1
        elif keys[pygame.K_UP]: dy = -1
        elif keys[pygame.K_DOWN]: dy = 1
        
        if dx or dy: self.player.move(dx, dy, self.map.grid)
        self.player.update()
    
    def update_enemies(self):
        if self.game_state != 'playing': 
            return
        for enemy in self.enemies:
            enemy.update(self.player, self.map.grid, self.enemies)
    
    def check_collisions(self):
        if self.game_state != 'playing': 
            return
        
        # key
        if not self.has_key and self.player.colliderect(pygame.Rect(self.key_pos[0], self.key_pos[1], GRID_SIZE, GRID_SIZE)):
            self.has_key = True
            self.treasure_pos = self.map.get_random_position()
            self.get_item_sound.play()
        
        # chest
        if self.has_key and self.treasure_pos and self.player.colliderect(pygame.Rect(self.treasure_pos[0], self.treasure_pos[1], GRID_SIZE, GRID_SIZE)):
            self.game_state = 'won'
            self.bgm.stop()
            self.win_sound.play()
        
        # enemies
        for enemy in self.enemies:
            if self.player.colliderect(enemy):
                self.game_state = 'lost'
                self.bgm.stop()
                self.lose_sound.play()
    
    def draw_buttons(self):
        button_width = 200
        button_height = 50
        button_spacing = 20
        # restart_x = WIDTH // 2 - button_width * 0.5
        menu_x = WIDTH // 2 - button_width - button_spacing // 2
        quit_x = WIDTH // 2 + button_spacing // 2
        button_y = HEIGHT // 2 + 50
        
        # self.restart_button = pygame.Rect(restart_x, HEIGHT // 2 + 120, button_width, button_height)
        self.menu_button = pygame.Rect(menu_x, button_y, button_width, button_height)
        self.quit_button = pygame.Rect(quit_x, button_y, button_width, button_height)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # restart
        # restart_game_color = (0, 150, 200) if self.restart_button.collidepoint(mouse_pos) else (0, 100, 150)
        # pygame.draw.rect(self.screen, restart_game_color, self.restart_button, border_radius=10)
        # pygame.draw.rect(self.screen, WHITE, self.restart_button, 3, border_radius=10)
        # restart_text = self.button_font.render("RESTART", True, WHITE) 
        # restart_text_rect = restart_text.get_rect(center=self.restart_button.center)
        # self.screen.blit(restart_text, restart_text_rect)
        
        # menu
        menu_color = (0, 200, 0) if self.menu_button.collidepoint(mouse_pos) else (0, 150, 0)
        pygame.draw.rect(self.screen, menu_color, self.menu_button, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.menu_button, 3, border_radius=10)
        restart_text = self.button_font.render("MENU", True, WHITE)
        restart_text_rect = restart_text.get_rect(center=self.menu_button.center)
        self.screen.blit(restart_text, restart_text_rect)
        
        # quit
        quit_color = (200, 0, 0) if self.quit_button.collidepoint(mouse_pos) else (150, 0, 0)
        pygame.draw.rect(self.screen, quit_color, self.quit_button, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.quit_button, 3, border_radius=10)
        quit_text = self.button_font.render("QUIT", True, WHITE)
        quit_text_rect = quit_text.get_rect(center=self.quit_button.center)
        self.screen.blit(quit_text, quit_text_rect)
    
    def draw_game_over_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.game_state == 'won':
            message = "YOU WIN!"
            color = YELLOW
        else:
            message = "GAME OVER!"
            color = RED
        
        text = self.font.render(message, True, color)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)
        self.draw_buttons()
    
    def draw_game(self):
        self.screen.fill(BLACK)
        self.map.draw(self.screen)
        
        if not self.has_key:
            self.screen.blit(self.key_sprite, (self.key_pos[0], self.key_pos[1], GRID_SIZE, GRID_SIZE))
        if self.has_key and self.treasure_pos:
            self.screen.blit(self.treasure_sprite, (self.treasure_pos[0], self.treasure_pos[1], GRID_SIZE, GRID_SIZE))
        
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        self.player.draw(self.screen)
        
        if self.game_state != 'playing':
            self.draw_game_over_screen()
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            if self.state == 'MENU':
                self.handle_menu_input()
                self.draw_menu()
            elif self.state == 'PLAYING':
                self.handle_game_events()
                self.handle_player_movement()
                self.update_enemies()
                self.check_collisions()
                self.draw_game()
            self.clock.tick(60)
        pygame.quit()