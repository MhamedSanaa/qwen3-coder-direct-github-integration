#!/usr/bin/env python3
"""
Launcher script for Enhanced Super Mario Style Game
Includes headless mode detection and better error handling
"""

import os
import sys
import subprocess

def check_display():
    """Check if a display is available"""
    return os.environ.get('DISPLAY') is not None or os.environ.get('WAYLAND_DISPLAY') is not None

def main():
    try:
        # Import pygame to check if it's available
        import pygame
        print("Pygame is available.")
    except ImportError:
        print("Pygame is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        import pygame
        print("Pygame installed successfully!")
    
    # Check if running in headless environment
    if not check_display():
        print("No display detected. Running performance tests instead...")
        print("To run the actual game, use a system with a graphical display.")
        
        # Run performance tests to verify the code works
        from performance_test import main as run_performance_tests
        run_performance_tests()
        return
    
    # Run the enhanced game
    print("Starting the Enhanced Mario Game...")
    from enhanced_mario_game import Game
    game = Game()
    game.run()

if __name__ == "__main__":
    main()