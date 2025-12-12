# Enhanced Super Mario-Style Side-Scrolling Game

An advanced Super Mario-inspired side-scrolling platformer game built with Python and Pygame, optimized for performance and production readiness.

## Features

- **Player character** that can move left/right and jump with physics-based movement
- **Multiple levels** with increasing difficulty
- **Enemies** that patrol back and forth and can attack
- **Collectible coins** with particle effects
- **Smooth scrolling level** that follows the player
- **Health system** for both player and enemies
- **Combat mechanics** (jump on enemies to defeat them)
- **Attack cooldowns and invincibility periods**
- **Health bars** displayed above characters
- **Game states** (playing, paused, game over, level complete)
- **Lives system** and scoring
- **Particle effects** for coin collection
- **Configurable settings** via JSON configuration
- **Performance optimizations** for smooth gameplay

## Controls

- **Left Arrow** or **A**: Move left
- **Right Arrow** or **D**: Move right
- **Space** or **Up Arrow**: Jump
- **Escape**: Pause/Resume game
- **R**: Restart game (when game over)
- **N**: Go to next level (when level complete)

## Requirements

- Python 3.6+
- Pygame library

## Setup

1. Install requirements: `pip install -r requirements.txt`
2. Run the game: `python run_game.py`

## Game Elements

- **Red square**: Player character (with health bar above)
- **Green rectangles**: Platforms
- **Brown squares**: Enemies (with health bar above)
- **Yellow circles**: Coins (with floating animation)
- **UI elements**: Health, coins collected, lives, level info

## Game Progression

- Complete levels by defeating all enemies and collecting all coins
- Multiple lives system to continue playing
- Increasing challenge in subsequent levels
- Score tracking based on coins collected and enemies defeated

## Technical Optimizations

- **Sprite grouping** for efficient rendering
- **Camera system** for smooth scrolling
- **Delta time calculations** for consistent physics across different hardware
- **Particle system** for visual effects
- **State management** for different game modes
- **Memory-efficient collision detection**
- **Object pooling concepts** for temporary effects

## Configuration

The game can be customized through the `game_config.json` file:
- Adjust game settings (screen size, physics, etc.)
- Modify player and enemy stats
- Change controls mapping
- Update color schemes

## Development Notes

This enhanced version includes:
- Better game architecture with clear separation of concerns
- Improved collision detection algorithms
- Enhanced visual feedback (particles, animations)
- More robust state management
- Configurable game parameters
- Performance improvements for handling more entities
- Better error handling and game flow management