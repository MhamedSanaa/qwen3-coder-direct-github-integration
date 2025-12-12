# Super Mario-Style Side-Scrolling Game

A simple Super Mario-inspired side-scrolling platformer game built with Python and Pygame.

## Features
- Player character that can move left/right and jump
- Platforms to jump on
- Enemies that patrol back and forth and can attack
- Collectible coins
- Scrolling level that follows the player
- Health system for both player and enemies
- Combat mechanics (jump on enemies to defeat them)
- Attack cooldowns and invincibility periods
- Health bars displayed above characters
- Game over screen with restart option

## Controls
- Left Arrow: Move left
- Right Arrow: Move right
- Space: Jump
- R: Restart game (when game over)
- Escape: Quit game

## Requirements
- Python 3.x
- Pygame library

## Setup
1. Install requirements: `pip install -r requirements.txt`
2. Run the game: `python mario_game.py`

## Game Elements
- Red square: Player character (with health bar above)
- Green rectangles: Platforms
- Brown squares: Enemies (with health bar above)
- Yellow circles: Coins
- Health display: Shows current player health
- Score display: Shows coins collected

## Combat Mechanics
- Jump on enemies from above to defeat them (player bounces slightly)
- Avoid touching enemies from the sides or below to prevent taking damage
- After taking damage, player becomes temporarily invincible (flashes)
- Enemies deal damage when they touch the player
- Defeated enemies disappear from the game
- Player loses health when attacked by enemies
- Game ends when player health reaches 0
