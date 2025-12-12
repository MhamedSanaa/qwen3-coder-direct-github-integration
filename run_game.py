#!/usr/bin/env python3
"""
Launcher script for Super Mario Style Game
"""

import subprocess
import sys

def main():
    try:
        # Import pygame to check if it's available
        import pygame
        print("Pygame is available. Starting the game...")
    except ImportError:
        print("Pygame is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        import pygame
        print("Pygame installed successfully!")
    
    # Run the enhanced game
    import enhanced_mario_game

if __name__ == "__main__":
    main()