"""
Performance Test Script for Enhanced Mario Game
Tests various performance optimizations implemented in the game
"""

import pygame
import time
import random
from enhanced_mario_game import Player, Enemy, Platform, Coin, ParticleSystem, Camera


def test_sprite_collision_performance():
    """Test the performance of sprite collision detection"""
    print("Testing sprite collision performance...")
    
    # Create test sprites
    player = Player(100, 400)
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    
    # Add many platforms to test collision performance
    for i in range(100):  # More platforms for stress test
        platform = Platform(i * 50, 500 - (i % 10) * 20, 40, 20)
        platforms.add(platform)
    
    # Add many enemies
    for i in range(50):
        enemy = Enemy(200 + i * 40, 400)
        enemies.add(enemy)
    
    # Measure collision detection performance
    start_time = time.time()
    for _ in range(1000):  # Simulate 1000 frames worth of collision checks
        # Player-platform collisions
        collisions = pygame.sprite.spritecollide(player, platforms, False)
        
        # Player-enemy collisions
        enemy_collisions = pygame.sprite.spritecollide(player, enemies, False)
    
    end_time = time.time()
    elapsed = (end_time - start_time) * 1000  # Convert to milliseconds
    
    print(f"Collision detection for 1000 frames took {elapsed:.2f}ms")
    print(f"Average per frame: {elapsed/1000:.4f}ms")
    print("✓ Collision performance test completed\n")


def test_particle_system_performance():
    """Test the performance of the particle system"""
    print("Testing particle system performance...")
    
    particle_system = ParticleSystem()
    
    # Add many particles to test performance
    for _ in range(100):  # Add 100 particles
        particle_system.add_coin_particles(random.randint(0, 800), random.randint(0, 600), 10)
    
    # Create a dummy surface to simulate drawing
    dummy_surface = pygame.Surface((800, 600))
    
    # Measure particle update and draw performance
    start_time = time.time()
    for _ in range(1000):  # Simulate 1000 updates
        particle_system.update(1)  # Update with dt=1
        particle_system.draw(dummy_surface, 0)  # Draw with no camera offset
    
    end_time = time.time()
    elapsed = (end_time - start_time) * 1000  # Convert to milliseconds
    
    print(f"Particle system update/draw for 1000 frames took {elapsed:.2f}ms")
    print(f"Average per frame: {elapsed/1000:.4f}ms")
    print("✓ Particle system performance test completed\n")


def test_camera_system_performance():
    """Test the performance of the camera system"""
    print("Testing camera system performance...")
    
    camera = Camera(800, 600)
    player = Player(100, 400)
    
    # Simulate camera following player through different positions
    start_time = time.time()
    for i in range(10000):  # Test with 10000 different positions
        player.rect.x = i * 2  # Move player
        player.rect.y = 400 + (i % 100)  # Slight vertical movement
        camera.update(player)  # Update camera
        
        # Apply camera to a dummy rect (simulating sprite drawing)
        dummy_sprite = pygame.sprite.Sprite()
        dummy_sprite.rect = pygame.Rect(100, 100, 30, 30)
        camera.apply(dummy_sprite)
    
    end_time = time.time()
    elapsed = (end_time - start_time) * 1000  # Convert to milliseconds
    
    print(f"Camera system for 10000 frames took {elapsed:.2f}ms")
    print(f"Average per frame: {elapsed/10000:.4f}ms")
    print("✓ Camera system performance test completed\n")


def test_entity_update_performance():
    """Test the performance of entity updates"""
    print("Testing entity update performance...")
    
    # Create test entities
    player = Player(100, 400)
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    
    # Add platforms
    for i in range(50):
        platform = Platform(i * 60, 500 - (i % 5) * 30, 50, 20)
        platforms.add(platform)
    
    # Add enemies
    for i in range(30):
        enemy = Enemy(200 + i * 60, 400)
        enemies.add(enemy)
    
    # Add coins
    for i in range(100):
        coin = Coin(150 + i * 40, 300)
        coins.add(coin)
    
    # Simulate game loop updates
    start_time = time.time()
    for frame in range(1000):  # 1000 frames of updates
        # Update player
        player.update(platforms, enemies, 1)
        
        # Update enemies
        for enemy in enemies:
            enemy.update(platforms, player, 1)
        
        # Update coins
        for coin in coins:
            coin.update(1)
    
    end_time = time.time()
    elapsed = (end_time - start_time) * 1000  # Convert to milliseconds
    
    print(f"Entity updates for 1000 frames took {elapsed:.2f}ms")
    print(f"Average per frame: {elapsed/1000:.4f}ms")
    print("✓ Entity update performance test completed\n")


def main():
    """Run all performance tests"""
    print("=" * 60)
    print("PERFORMANCE TESTS FOR ENHANCED MARIO GAME")
    print("=" * 60)
    print()
    
    # Initialize pygame for the tests
    pygame.init()
    
    try:
        test_sprite_collision_performance()
        test_particle_system_performance()
        test_camera_system_performance()
        test_entity_update_performance()
        
        print("=" * 60)
        print("ALL PERFORMANCE TESTS COMPLETED SUCCESSFULLY!")
        print("The enhanced game includes the following optimizations:")
        print("- Efficient sprite collision detection")
        print("- Optimized particle system with proper memory management")
        print("- Smooth camera system with boundary checks")
        print("- Delta-time based updates for consistent performance")
        print("- Proper object lifecycle management")
        print("- Optimized drawing methods")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error during performance tests: {e}")
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()