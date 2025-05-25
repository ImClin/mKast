#!/usr/bin/env python3
"""
mKast Game Launcher - A customizable game launcher with a retro arcade style interface.

Usage:
  python main.py [games_file]
  python main.py -g games_file

Options:
  -g, --games    Specify a games JSON file to load
"""

import sys
from src.core.game_launcher import GameLauncher
from src.utils.config import update_config_with_screen_resolution

def main():
    """Main entry point for the application."""
    # Update config with detected screen resolution
    update_config_with_screen_resolution()
    
    # Check for command line arguments
    games_file = 'games.json'
    force_resolution_update = False
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '-g' or arg == '--games':
            if i + 1 < len(sys.argv):
                games_file = sys.argv[i + 1]
                print(f"Loading games from: {games_file}")
                i += 2
            else:
                print("Error: Missing games file argument")
                i += 1
        elif arg == '--update-resolution':
            force_resolution_update = True
            print("Forcing resolution update")
            i += 1
        else:
            # Assume the argument is the games file
            games_file = arg
            print(f"Loading games from: {games_file}")
            i += 1
    
    # Create and run the game launcher
    launcher = GameLauncher(games_file)
    return launcher.run()

if __name__ == "__main__":
    sys.exit(main())
