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
        
    def update(self, platforms):
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
        
    def update(self, platforms):
        self.rect.x += self.speed * self.direction
        
        # Simple AI: turn around at edges of platforms
        # For now, just reverse direction when hitting screen boundaries
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.direction *= -1

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
        self.enemies.update(self.platforms)
        
        # Check for collisions with coins
        coin_collisions = pygame.sprite.spritecollide(self.player, self.coins, True)
        
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
            screen_x = sprite.rect.x - self.camera_x
            self.screen.blit(sprite.image, (screen_x, sprite.rect.y))
        
        # Draw score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Coins: {len(self.coins)}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()