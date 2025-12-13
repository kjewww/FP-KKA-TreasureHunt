import pygame
import os
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
        self.bgm = pygame.mixer.Sound(os.path.join('assets', 'bgm1.wav'))
        self.bgm.set_volume(0.5)
        self.lose_sound = pygame.mixer.Sound(os.path.join('assets', 'lose.wav'))
        self.lose_sound.set_volume(0.7)
        self.win_sound = pygame.mixer.Sound(os.path.join('assets', 'win.mp3'))
        self.win_sound.set_volume(0.7)
        self.get_item_sound = pygame.mixer.Sound(os.path.join('assets', 'get_item.wav'))
        self.get_item_sound.set_volume(0.7)
        
        # Inisialisasi map
        self.map = Map()
        
        # Load sprites
        self.key_sprite = self.load_sprite('key.png')
        self.treasure_sprite = self.load_sprite('treasure.png')
        
        # Game state
        self.game_state = 'playing'  # playing, won, lost
        self.running = True
        
        # Initialize game objects
        self.init_game()
        
    def init_game(self): # inisialisasi game
        self.map.select_random_map()
        self.player = Player(GRID_SIZE, GRID_SIZE)
        self.key_pos = self.map.get_random_position()
        self.treasure_pos = None
        self.has_key = False
        self.win_sound.stop()
        self.lose_sound.stop()
        self.bgm.play(loops=-1)
        
        # Inisialisasi enemies dengan warna berbeda dan jarak minimum dari player
        enemy_colors = ['Blue', 'Red', 'Green']
        self.enemies = []
        player_pos = (self.player.x, self.player.y)
        for i, color in enumerate(enemy_colors):
            enemy_pos = self.map.get_random_position(min_distance_from=player_pos, min_distance=8)
            self.enemies.append(Enemy(*enemy_pos, color=color))
        
        self.game_state = 'playing'
        
        # load sprite dri folder 'images'
    def load_sprite(self, filename):
        path = os.path.join('images', filename)
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (GRID_SIZE, GRID_SIZE))
        return image
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle button clicks saat game selesai
            if event.type == pygame.MOUSEBUTTONDOWN and self.game_state != 'playing':
                mouse_pos = pygame.mouse.get_pos()
                if self.restart_button.collidepoint(mouse_pos):
                    self.init_game()  # Restart game
                elif self.quit_button.collidepoint(mouse_pos):
                    self.running = False  # Quit game
    
    def handle_player_movement(self):
        if self.game_state != 'playing':
            return
            
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_RIGHT]:
            dx = 1
        elif keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_DOWN]:
            dy = 1
        
        if dx or dy:
            self.player.move(dx, dy, self.map.grid)
        
        # Update player cooldown
        self.player.update()
    
    def update_enemies(self):
        if self.game_state != 'playing':
            return
            
        for enemy in self.enemies:
            enemy.update(self.player, self.map.grid)
    
    # cek collision antara player dengan key, treasure, dan enemies
    def check_collisions(self):
        if self.game_state != 'playing':
            return
            
        # Cek collision dengan key
        if not self.has_key and self.player.colliderect(pygame.Rect(self.key_pos[0], self.key_pos[1], GRID_SIZE, GRID_SIZE)):
            self.has_key = True
            self.treasure_pos = self.map.get_random_position()
            self.get_item_sound.play()
        
        # Cek collision dengan treasure
        if self.has_key and self.treasure_pos and self.player.colliderect(pygame.Rect(self.treasure_pos[0], self.treasure_pos[1], GRID_SIZE, GRID_SIZE)):
            self.game_state = 'won'
            self.bgm.stop()
            self.win_sound.play()
        
        # Cek collision dengan enemies
        for enemy in self.enemies:
            if self.player.colliderect(enemy):
                self.game_state = 'lost'
                self.bgm.stop()
                self.lose_sound.play()
    
    # draw tombol restart dan quit
    def draw_buttons(self):
        # Posisi tombol
        button_width = 200
        button_height = 50
        button_spacing = 20
        
        restart_x = WIDTH // 2 - button_width - button_spacing // 2
        quit_x = WIDTH // 2 + button_spacing // 2
        button_y = HEIGHT // 2 + 50
        
        # Buat rect untuk tombol
        self.restart_button = pygame.Rect(restart_x, button_y, button_width, button_height)
        self.quit_button = pygame.Rect(quit_x, button_y, button_width, button_height)
        
        # Get mouse position untuk hover effect
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw restart button
        restart_color = (0, 200, 0) if self.restart_button.collidepoint(mouse_pos) else (0, 150, 0)
        pygame.draw.rect(self.screen, restart_color, self.restart_button, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.restart_button, 3, border_radius=10)
        restart_text = self.button_font.render("RESTART", True, WHITE)
        restart_text_rect = restart_text.get_rect(center=self.restart_button.center)
        self.screen.blit(restart_text, restart_text_rect)
        
        # Draw quit button
        quit_color = (200, 0, 0) if self.quit_button.collidepoint(mouse_pos) else (150, 0, 0)
        pygame.draw.rect(self.screen, quit_color, self.quit_button, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.quit_button, 3, border_radius=10)
        quit_text = self.button_font.render("QUIT", True, WHITE)
        quit_text_rect = quit_text.get_rect(center=self.quit_button.center)
        self.screen.blit(quit_text, quit_text_rect)
    
    # menampilkan game over
    def draw_game_over_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Message
        if self.game_state == 'won':
            message = "YOU WIN!"
            color = YELLOW
        else:
            message = "GAME OVER!"
            color = RED
        
        text = self.font.render(message, True, color)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)
        
        # Draw buttons
        self.draw_buttons()
    
    # draw semua elemen game
    def draw(self):
        self.screen.fill(BLACK)
        self.map.draw(self.screen)
        
        # Draw key jika belum diambil
        if not self.has_key:
            self.screen.blit(self.key_sprite, (self.key_pos[0], self.key_pos[1], GRID_SIZE, GRID_SIZE))
        
        # Draw treasure jika sudah punya key
        if self.has_key and self.treasure_pos:
            self.screen.blit(self.treasure_sprite, (self.treasure_pos[0], self.treasure_pos[1], GRID_SIZE, GRID_SIZE))
        
        # Draw enemies dengan animasi
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw player dengan animasi (terakhir agar di atas enemies)
        self.player.draw(self.screen)
        
        # Draw game over screen jika game selesai
        if self.game_state != 'playing':
            self.draw_game_over_screen()
        
        pygame.display.flip()
    
    # loop game
    def run(self):
        while self.running:
            self.handle_events()
            self.handle_player_movement()
            self.update_enemies()
            self.check_collisions()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()