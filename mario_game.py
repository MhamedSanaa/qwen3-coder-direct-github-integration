import pygame
import sys

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15
MOVE_SPEED = 5

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

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(RED)  # Simple red rectangle for Mario
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 400
        self.vel_y = 0
        self.jumping = False
        self.direction = 1  # 1 for right, -1 for left
        
        # Health and attack properties
        self.health = 100
        self.max_health = 100
        self.invincible = False  # Invincibility after being hit
        self.invincible_timer = 0
        self.max_invincible_time = 60  # Frames of invincibility
        self.attack_cooldown = 0  # Cooldown for attacking enemies
        self.max_attack_cooldown = 20  # Frames between attacks
        self.attack_range = 50  # Range at which player can kill enemies
        self.attack_damage = 30  # Damage dealt to enemies when attacking from above
        
    def update(self, platforms):
        # Update invincibility timer
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Handle horizontal movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= MOVE_SPEED
            self.direction = -1
        if keys[pygame.K_RIGHT]:
            self.rect.x += MOVE_SPEED
            self.direction = 1
            
        # Handle jumping
        if keys[pygame.K_SPACE] and not self.jumping:
            self.vel_y = JUMP_STRENGTH
            self.jumping = True
            
        # Apply gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        # Check for collisions with platforms
        collisions = pygame.sprite.spritecollide(self, platforms, False)
        for platform in collisions:
            if self.vel_y > 0:  # Falling
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.jumping = False
            elif self.vel_y < 0:  # Jumping up
                self.rect.top = platform.rect.bottom
                self.vel_y = 0

    def take_damage(self, damage):
        if not self.invincible:
            self.health -= damage
            self.invincible = True
            self.invincible_timer = self.max_invincible_time
            if self.health <= 0:
                self.health = 0

    def attack_enemy(self, enemy):
        """Attack an enemy from above"""
        if self.attack_cooldown == 0 and self.rect.bottom <= enemy.rect.top + 10:
            enemy.take_damage(self.attack_damage)
            self.attack_cooldown = self.max_attack_cooldown
            # Bounce off enemy
            self.vel_y = JUMP_STRENGTH * 0.7  # Small bounce
            return True
        return False

    def draw_health_bar(self, screen, camera_x):
        """Draw health bar above player"""
        bar_width = 50
        bar_height = 6
        health_width = int((self.health / self.max_health) * bar_width)
        
        # Draw background (red)
        pygame.draw.rect(screen, RED, (self.rect.x - camera_x, self.rect.y - 15, bar_width, bar_height))
        # Draw health (green)
        pygame.draw.rect(screen, GREEN, (self.rect.x - camera_x, self.rect.y - 15, health_width, bar_height))

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2
        self.direction = 1
        
        # Health and combat properties
        self.health = 50
        self.max_health = 50
        self.alive = True
        self.attack_range = 40  # Range at which enemy can attack player
        self.attack_damage = 25  # Damage dealt to player
        self.attack_cooldown = 0  # Cooldown between attacks
        self.max_attack_cooldown = 90  # Frames between attacks
        self.move_counter = 0
        self.move_limit = 100  # How far the enemy moves before turning around

    def update(self, platforms, player):
        if not self.alive:
            return
            
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Move horizontally
        self.rect.x += self.speed * self.direction
        self.move_counter += 1

        # Change direction if moved too far or hit a boundary
        if self.move_counter >= self.move_limit or self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH * 2:
            self.direction *= -1
            self.move_counter = 0

        # Make sure enemy stays on platforms
        on_platform = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.rect.bottom <= platform.rect.top + 10:  # Slightly above the platform
                    self.rect.bottom = platform.rect.top
                    on_platform = True
                    break

        # If not on platform, fall down
        if not on_platform:
            self.rect.y += 5  # Simple gravity for enemies

        # Check for attack on player
        distance_to_player = abs(self.rect.centerx - player.rect.centerx)
        if distance_to_player < self.attack_range and self.attack_cooldown == 0:
            if pygame.Rect.colliderect(self.rect, player.rect):
                player.take_damage(self.attack_damage)
                self.attack_cooldown = self.max_attack_cooldown

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.kill()  # Remove from all sprite groups

    def draw_health_bar(self, screen, camera_x):
        """Draw health bar above enemy"""
        if not self.alive:
            return
            
        bar_width = 30
        bar_height = 4
        health_width = int((self.health / self.max_health) * bar_width)
        
        # Draw background (red)
        pygame.draw.rect(screen, RED, (self.rect.x - camera_x, self.rect.y - 8, bar_width, bar_height))
        # Draw health (green)
        pygame.draw.rect(screen, GREEN, (self.rect.x - camera_x, self.rect.y - 8, health_width, bar_height))

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        pygame.draw.circle(self.image, YELLOW, (10, 10), 10)
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Style Game")
        self.clock = pygame.time.Clock()
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        
        # Create player
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Create platforms
        self.create_level()
        
        # Camera offset for scrolling
        self.camera_x = 0
        
    def create_level(self):
        # Ground platform
        ground = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH * 3, 40)
        self.platforms.add(ground)
        self.all_sprites.add(ground)
        
        # Additional platforms
        platforms_data = [
            (200, 450, 100, 20),
            (400, 400, 100, 20),
            (600, 350, 100, 20),
            (800, 300, 100, 20),
            (1000, 350, 100, 20),
            (1200, 400, 100, 20),
            (1400, 450, 100, 20),
        ]
        
        for x, y, width, height in platforms_data:
            platform = Platform(x, y, width, height)
            self.platforms.add(platform)
            self.all_sprites.add(platform)
        
        # Add enemies
        enemy1 = Enemy(300, SCREEN_HEIGHT - 70)
        enemy2 = Enemy(700, SCREEN_HEIGHT - 70)
        enemy3 = Enemy(1100, SCREEN_HEIGHT - 70)
        
        self.enemies.add(enemy1, enemy2, enemy3)
        self.all_sprites.add(enemy1, enemy2, enemy3)
        
        # Add coins
        for i in range(20):
            coin = Coin(200 + i * 100, 300)
            self.coins.add(coin)
            self.all_sprites.add(coin)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def update(self):
        # Update all sprites
        self.player.update(self.platforms)
        for enemy in self.enemies:
            enemy.update(self.platforms, self.player)
        
        # Check for collisions with coins
        coin_collisions = pygame.sprite.spritecollide(self.player, self.coins, True)
        
        # Check for collisions between player and enemies
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemy_hits:
            if enemy.alive and self.player.rect.colliderect(enemy.rect):
                # Check if player is jumping on enemy from above
                if self.player.rect.bottom <= enemy.rect.top + 10 and self.player.vel_y > 0:
                    # Player jumps on enemy
                    self.player.attack_enemy(enemy)
                else:
                    # Enemy hits player
                    if not self.player.invincible:
                        self.player.take_damage(enemy.attack_damage)
        
        # Update camera to follow player
        self.camera_x = self.player.rect.x - SCREEN_WIDTH // 3
        
        # Keep camera from going negative too much
        if self.camera_x < 0:
            self.camera_x = 0
    
    def draw(self):
        # Fill the screen with sky blue
        self.screen.fill(SKY_BLUE)
        
        # Draw all sprites relative to camera position
        for sprite in self.all_sprites:
            if isinstance(sprite, Enemy) and not sprite.alive:
                continue  # Don't draw dead enemies
                
            screen_x = sprite.rect.x - self.camera_x
            
            # Draw player with invincibility effect
            if isinstance(sprite, Player) and sprite.invincible and sprite.invincible_timer % 6 < 3:
                # Flash during invincibility
                flash_image = pygame.Surface((sprite.rect.width, sprite.rect.height))
                flash_image.fill((255, 100, 100))  # Lighter red when invincible
                self.screen.blit(flash_image, (screen_x, sprite.rect.y))
            else:
                self.screen.blit(sprite.image, (screen_x, sprite.rect.y))
        
        # Draw health bars for player and enemies
        self.player.draw_health_bar(self.screen, self.camera_x)
        for enemy in self.enemies:
            enemy.draw_health_bar(self.screen, self.camera_x)
        
        # Draw score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Coins: {len(self.coins)}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw player health
        health_text = font.render(f"Health: {self.player.health}", True, WHITE)
        self.screen.blit(health_text, (10, 50))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            
            # Check if player is dead
            if self.player.health <= 0:
                # Display game over screen
                font = pygame.font.SysFont(None, 72)
                game_over_text = font.render("GAME OVER", True, RED)
                text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                
                self.screen.fill(SKY_BLUE)
                self.screen.blit(game_over_text, text_rect)
                
                restart_font = pygame.font.SysFont(None, 36)
                restart_text = restart_font.render("Press R to Restart or ESC to Quit", True, WHITE)
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
                self.screen.blit(restart_text, restart_rect)
                
                pygame.display.flip()
                
                # Wait for restart or quit input
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r:
                                # Restart the game
                                self.__init__()  # Reinitialize the game
                                waiting = False
                            elif event.key == pygame.K_ESCAPE:
                                pygame.quit()
                                sys.exit()
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()