"""
Enhanced Super Mario-Style Side-Scroller Game
Production-ready prototype with performance optimizations
"""

import pygame
import json
import os
from enum import Enum
from typing import List, Tuple, Optional
import math

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15
MOVE_SPEED = 5
SCROLL_THRESHOLD = 200

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
SKY_BLUE = (135, 206, 235)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    LEVEL_COMPLETE = 5

class AnimationState(Enum):
    IDLE = 1
    WALKING = 2
    JUMPING = 3
    ATTACKING = 4
    DAMAGED = 5

class Player(pygame.sprite.Sprite):
    def __init__(self, x=100, y=400):
        super().__init__()
        self.width = 30
        self.height = 50
        
        # Create basic surface if no assets loaded
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Physics
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        
        # Movement
        self.max_speed = MOVE_SPEED
        self.jump_power = JUMP_STRENGTH
        self.move_direction = 0  # -1 for left, 1 for right, 0 for no movement
        
        # Combat and health
        self.health = 100
        self.max_health = 100
        self.invincible = False
        self.invincible_timer = 0
        self.max_invincible_time = 60
        self.attack_cooldown = 0
        self.max_attack_cooldown = 20
        self.attack_range = 50
        self.attack_damage = 30
        
        # Animation and visual state
        self.animation_state = AnimationState.IDLE
        self.animation_frame = 0
        self.animation_speed = 0.1  # Fractional increment per frame
        self.last_update = pygame.time.get_ticks()
        
        # Stats
        self.coins_collected = 0
        self.enemies_defeated = 0
        self.lives = 3

    def update(self, platforms, enemies, dt):
        # Update timers
        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False
                
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # Handle input
        keys = pygame.key.get_pressed()
        self.move_direction = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.move_direction = -1
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.move_direction = 1
            self.facing_right = True
            
        # Jumping
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
            self.animation_state = AnimationState.JUMPING

        # Apply movement
        self.vel_x = self.move_direction * self.max_speed
        self.rect.x += self.vel_x

        # Apply gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Check platform collisions
        self.handle_collisions(platforms)

        # Update animation state
        self.update_animation(dt)

        # Keep player in bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 10000:  # Assuming level width
            self.rect.right = 10000

    def handle_collisions(self, platforms):
        # Horizontal collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:  # Moving right
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:  # Moving left
                    self.rect.left = platform.rect.right
                self.vel_x = 0

        # Vertical collisions
        self.on_ground = False
        collisions = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collisions:
            if self.vel_y > 0:  # Falling
                if self.rect.bottom <= platform.rect.top + 10:  # Only collide from top
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.animation_state = AnimationState.IDLE
            elif self.vel_y < 0:  # Jumping up
                if self.rect.top >= platform.rect.bottom - 10:  # Only collide from bottom
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

    def update_animation(self, dt):
        # Update animation frame based on state
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > 100:  # 10fps for animations
            self.animation_frame = (self.animation_frame + 1) % 4
            self.last_update = current_time
            
        # Determine animation state
        if not self.on_ground:
            self.animation_state = AnimationState.JUMPING
        elif self.vel_x != 0:
            self.animation_state = AnimationState.WALKING
        else:
            self.animation_state = AnimationState.IDLE

    def take_damage(self, damage):
        if not self.invincible:
            self.health -= damage
            self.invincible = True
            self.invincible_timer = self.max_invincible_time
            self.animation_state = AnimationState.DAMAGED
            if self.health <= 0:
                self.health = 0
                return True  # Player died
        return False

    def attack_enemy(self, enemy):
        """Attack an enemy from above"""
        if self.attack_cooldown <= 0 and self.rect.bottom <= enemy.rect.top + 10:
            enemy.take_damage(self.attack_damage)
            self.attack_cooldown = self.max_attack_cooldown
            # Bounce off enemy
            self.vel_y = self.jump_power * 0.7
            return True
        return False

    def draw_health_bar(self, screen, camera_x):
        """Draw health bar above player"""
        bar_width = 50
        bar_height = 6
        health_width = int((self.health / self.max_health) * bar_width)
        
        # Draw background (red)
        pygame.draw.rect(screen, RED, (self.rect.x - camera_x, self.rect.y - 20, bar_width, bar_height))
        # Draw health (green)
        pygame.draw.rect(screen, GREEN, (self.rect.x - camera_x, self.rect.y - 20, health_width, bar_height))

    def get_render_image(self):
        """Get image to render (handles invincibility flashing)"""
        if self.invincible and int(pygame.time.get_ticks() / 100) % 2:
            # Flash during invincibility
            flash_image = pygame.Surface((self.width, self.height))
            flash_image.fill((255, 100, 100))
            return flash_image
        return self.image

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=GREEN):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = width
        self.height = height

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="goomba"):
        super().__init__()
        self.enemy_type = enemy_type
        self.width = 30
        self.height = 30
        
        # Create basic surface if no assets loaded
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Movement
        self.speed = 2
        self.direction = 1
        self.move_counter = 0
        self.move_limit = 100
        
        # Combat
        self.health = 50
        self.max_health = 50
        self.alive = True
        self.attack_range = 40
        self.attack_damage = 25
        self.attack_cooldown = 0
        self.max_attack_cooldown = 90
        
        # Animation
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.last_update = pygame.time.get_ticks()

    def update(self, platforms, player, dt):
        if not self.alive:
            return
            
        # Update timers
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # Move horizontally
        self.rect.x += self.speed * self.direction
        self.move_counter += 1

        # Change direction if moved too far or hit a boundary
        if self.move_counter >= self.move_limit or self.rect.left <= 0:
            self.direction *= -1
            self.move_counter = 0

        # Check platform collisions to stay on platforms
        on_platform = False
        for platform in platforms:
            if (self.rect.bottom <= platform.rect.top + 5 and 
                self.rect.bottom + self.speed >= platform.rect.top and
                self.rect.right > platform.rect.left and 
                self.rect.left < platform.rect.right):
                self.rect.bottom = platform.rect.top
                on_platform = True
                break

        # If not on platform, fall down
        if not on_platform:
            self.rect.y += 5  # Simple gravity for enemies

        # Check for attack on player
        distance_to_player = abs(self.rect.centerx - player.rect.centerx)
        if (distance_to_player < self.attack_range and 
            self.attack_cooldown <= 0 and 
            pygame.Rect.colliderect(self.rect, player.rect)):
            player.take_damage(self.attack_damage)
            self.attack_cooldown = self.max_attack_cooldown

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.kill()  # Remove from all sprite groups
            return True
        return False

    def draw_health_bar(self, screen, camera_x):
        """Draw health bar above enemy"""
        if not self.alive:
            return
            
        bar_width = 30
        bar_height = 4
        health_width = int((self.health / self.max_health) * bar_width)
        
        # Draw background (red)
        pygame.draw.rect(screen, RED, (self.rect.x - camera_x, self.rect.y - 10, bar_width, bar_height))
        # Draw health (green)
        pygame.draw.rect(screen, GREEN, (self.rect.x - camera_x, self.rect.y - 10, health_width, bar_height))

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 20
        self.height = 20
        self.image = pygame.Surface((self.width, self.height))
        pygame.draw.circle(self.image, YELLOW, (10, 10), 10)
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Animation for floating effect
        self.start_y = y
        self.float_offset = 0
        self.float_speed = 0.05

    def update(self, dt):
        # Floating animation
        self.float_offset += self.float_speed
        self.rect.y = self.start_y + math.sin(self.float_offset) * 5

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add_coin_particles(self, x, y, count=5):
        for _ in range(count):
            particle = {
                'x': x,
                'y': y,
                'vx': (pygame.time.get_ticks() % 10) - 5,  # Random velocity
                'vy': (pygame.time.get_ticks() % 10) - 8,  # Random velocity
                'life': 30,  # Frames until death
                'max_life': 30,
                'color': YELLOW
            }
            self.particles.append(particle)

    def update(self, dt):
        for particle in self.particles[:]:  # Copy list to avoid modification during iteration
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # Gravity
            particle['life'] -= dt
            
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw(self, screen, camera_x):
        for particle in self.particles:
            alpha = particle['life'] / particle['max_life']
            color = tuple(int(c * alpha) for c in particle['color'])
            pygame.draw.circle(
                screen, 
                color, 
                (int(particle['x'] - camera_x), int(particle['y'])), 
                3
            )

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(-self.camera.x, -self.camera.y)

    def update(self, target):
        # Center camera on target
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)

        # Limit scrolling to map boundaries
        x = min(0, x)  # Left boundary
        y = max(-(10000 - SCREEN_WIDTH), y)  # Right boundary (assuming level width)
        y = min(0, y)  # Top boundary
        y = max(-(10000 - SCREEN_HEIGHT), y)  # Bottom boundary

        self.camera = pygame.Rect(x, y, self.width, self.height)

class LevelManager:
    def __init__(self):
        self.levels = []
        self.current_level = 0
        self.load_levels()

    def load_levels(self):
        # Define some sample levels
        level1 = {
            'platforms': [
                (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH * 3, 40),
                (200, 450, 100, 20),
                (400, 400, 100, 20),
                (600, 350, 100, 20),
                (800, 300, 100, 20),
                (1000, 350, 100, 20),
                (1200, 400, 100, 20),
                (1400, 450, 100, 20),
            ],
            'enemies': [(300, SCREEN_HEIGHT - 70), (700, SCREEN_HEIGHT - 70), (1100, SCREEN_HEIGHT - 70)],
            'coins': [(200 + i * 100, 300) for i in range(20)]
        }
        
        level2 = {
            'platforms': [
                (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH * 4, 40),
                (200, 450, 80, 20),
                (400, 400, 80, 20),
                (600, 350, 80, 20),
                (800, 300, 80, 20),
                (1000, 250, 80, 20),
                (1200, 300, 80, 20),
                (1400, 350, 80, 20),
                (1600, 400, 80, 20),
                (1800, 450, 80, 20),
            ],
            'enemies': [(300, SCREEN_HEIGHT - 70), (700, SCREEN_HEIGHT - 70), 
                       (1100, SCREEN_HEIGHT - 70), (1500, SCREEN_HEIGHT - 70)],
            'coins': [(200 + i * 80, 280) for i in range(25)]
        }
        
        self.levels = [level1, level2]

    def get_current_level_data(self):
        if 0 <= self.current_level < len(self.levels):
            return self.levels[self.current_level]
        return self.levels[0]  # Default to first level

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Enhanced Super Mario-Style Game")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = GameState.PLAYING
        self.running = True
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.particles = ParticleSystem()
        
        # Initialize systems
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.level_manager = LevelManager()
        
        # Create player
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Create level
        self.create_level()
        
        # UI elements
        self.font_large = pygame.font.SysFont(None, 72)
        self.font_medium = pygame.font.SysFont(None, 36)
        self.font_small = pygame.font.SysFont(None, 24)
        
        # Timing
        self.last_time = pygame.time.get_ticks()
        self.dt = 0

    def create_level(self):
        # Clear existing sprites
        self.platforms.empty()
        self.enemies.empty()
        self.coins.empty()
        self.all_sprites.empty()
        
        # Get level data
        level_data = self.level_manager.get_current_level_data()
        
        # Create platforms
        for x, y, width, height in level_data['platforms']:
            platform = Platform(x, y, width, height)
            self.platforms.add(platform)
            self.all_sprites.add(platform)
        
        # Create enemies
        for x, y in level_data['enemies']:
            enemy = Enemy(x, y)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
        
        # Create coins
        for x, y in level_data['coins']:
            coin = Coin(x, y)
            self.coins.add(coin)
            self.all_sprites.add(coin)
        
        # Add player to group
        self.all_sprites.add(self.player)
        self.player.rect.x = 100
        self.player.rect.y = 400

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.GAME_OVER:
                        self.restart_game()
                elif event.key == pygame.K_r and self.state == GameState.GAME_OVER:
                    self.restart_game()
                elif event.key == pygame.K_n and self.state == GameState.LEVEL_COMPLETE:
                    self.next_level()

    def update(self):
        current_time = pygame.time.get_ticks()
        self.dt = (current_time - self.last_time) / 16.67  # Normalize to ~60fps
        self.last_time = current_time
        
        if self.state != GameState.PLAYING:
            return
            
        # Update camera to follow player
        self.camera.update(self.player)
        
        # Update player
        self.player.update(self.platforms, self.enemies, self.dt)
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.platforms, self.player, self.dt)
        
        # Update coins
        for coin in self.coins:
            coin.update(self.dt)
        
        # Update particles
        self.particles.update(self.dt)
        
        # Check coin collection
        coin_collisions = pygame.sprite.spritecollide(self.player, self.coins, True)
        for coin in coin_collisions:
            self.player.coins_collected += 1
            self.particles.add_coin_particles(coin.rect.centerx, coin.rect.centery)
        
        # Check enemy collisions
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemy_hits:
            if enemy.alive and self.player.rect.colliderect(enemy.rect):
                # Check if player is jumping on enemy from above
                if (self.player.rect.bottom <= enemy.rect.top + 10 and 
                    self.player.vel_y > 0):
                    # Player jumps on enemy
                    killed = self.player.attack_enemy(enemy)
                    if killed:
                        self.player.enemies_defeated += 1
                else:
                    # Enemy hits player
                    if not self.player.invincible:
                        died = self.player.take_damage(enemy.attack_damage)
                        if died:
                            self.state = GameState.GAME_OVER
        
        # Check if player fell off the map
        if self.player.rect.top > SCREEN_HEIGHT + 100:
            self.player.lives -= 1
            if self.player.lives <= 0:
                self.state = GameState.GAME_OVER
            else:
                # Reset player position
                self.player.rect.x = 100
                self.player.rect.y = 400
                self.player.vel_x = 0
                self.player.vel_y = 0
        
        # Check if level is complete (all enemies defeated and coins collected)
        if len(self.enemies) == 0 and len(self.coins) == 0:
            self.state = GameState.LEVEL_COMPLETE

    def draw(self):
        # Clear screen
        self.screen.fill(SKY_BLUE)
        
        # Draw sprites with camera offset
        for sprite in self.all_sprites:
            if hasattr(sprite, 'alive') and not sprite.alive:
                continue  # Skip dead enemies
            
            screen_pos = self.camera.apply(sprite)
            
            if isinstance(sprite, Player):
                # Draw player with special effects
                render_img = sprite.get_render_image()
                self.screen.blit(render_img, screen_pos)
            else:
                self.screen.blit(sprite.image, screen_pos)
        
        # Draw particles
        self.particles.draw(self.screen, self.camera.camera.x)
        
        # Draw UI elements
        self.draw_ui()
        
        # Draw state-specific screens
        if self.state == GameState.PAUSED:
            self.draw_pause_screen()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over_screen()
        elif self.state == GameState.LEVEL_COMPLETE:
            self.draw_level_complete_screen()
        
        pygame.display.flip()

    def draw_ui(self):
        # Draw health bar
        self.player.draw_health_bar(self.screen, self.camera.camera.x)
        
        # Draw stats
        coins_text = self.font_small.render(f"Coins: {self.player.coins_collected}", True, WHITE)
        health_text = self.font_small.render(f"Health: {self.player.health}", True, WHITE)
        lives_text = self.font_small.render(f"Lives: {self.player.lives}", True, WHITE)
        
        self.screen.blit(coins_text, (10, 10))
        self.screen.blit(health_text, (10, 35))
        self.screen.blit(lives_text, (10, 60))
        
        # Draw level info
        level_text = self.font_small.render(f"Level: {self.level_manager.current_level + 1}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH - 120, 10))

    def draw_pause_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("PAUSED", True, WHITE)
        continue_text = self.font_medium.render("Press ESC to Continue", True, WHITE)
        
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        
        self.screen.blit(pause_text, pause_rect)
        self.screen.blit(continue_text, continue_rect)

    def draw_game_over_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        score_text = self.font_medium.render(f"Final Score: {self.player.coins_collected * 10 + self.player.enemies_defeated * 50}", True, WHITE)
        restart_text = self.font_medium.render("Press R to Restart or ESC to Quit", True, WHITE)
        
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)

    def draw_level_complete_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(GREEN)
        self.screen.blit(overlay, (0, 0))
        
        complete_text = self.font_large.render("LEVEL COMPLETE!", True, WHITE)
        score_text = self.font_medium.render(f"Score: {self.player.coins_collected * 10 + self.player.enemies_defeated * 50}", True, WHITE)
        next_text = self.font_medium.render("Press N for Next Level or ESC to Quit", True, WHITE)
        
        complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        next_rect = next_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        
        self.screen.blit(complete_text, complete_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(next_text, next_rect)

    def restart_game(self):
        self.player = Player()
        self.player.lives = 3
        self.player.health = self.player.max_health
        self.level_manager.current_level = 0
        self.create_level()
        self.state = GameState.PLAYING

    def next_level(self):
        self.level_manager.current_level += 1
        if self.level_manager.current_level >= len(self.level_manager.levels):
            self.level_manager.current_level = 0  # Loop back to first level
        self.create_level()
        self.state = GameState.PLAYING

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()