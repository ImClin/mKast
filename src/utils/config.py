#!/usr/bin/env python3
"""Configuration utilities for mKast Game Launcher."""

import os
import json
import pygame  # type: ignore

def load_config():
    """Load configuration from config.json or create default if not found."""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Config file not found. Creating default config...")
        default_config = {
            "admin_password": "admin123",
            "exit_password": "exit123",
            "fullscreen": True,
            "resolution": [1920, 1080],
            "theme": {
                "background_color": [10, 10, 40],
                "button_color": [80, 80, 200],
                "button_hover_color": [120, 120, 255],
                "text_color": [255, 255, 255],
                "header_color": [255, 200, 0]
            }
        }
        with open('config.json', 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config

def ensure_assets_directory():
    """Ensure required asset directories exist."""
    # Create main assets directory if it doesn't exist
    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    # Create fonts subdirectory if it doesn't exist
    if not os.path.exists("assets/fonts"):
        os.makedirs("assets/fonts")
    
    # Create game_images subdirectory if it doesn't exist
    if not os.path.exists("assets/game_images"):
        os.makedirs("assets/game_images")

def detect_screen_resolution():
    """Detect the current screen resolution using pygame.
    
    Returns:
        tuple: (width, height) of the screen
    """
    # Initialize pygame if not already initialized
    if not pygame.get_init():
        pygame.init()
        
    # Get the display info
    info = pygame.display.Info()
    return (info.current_w, info.current_h)

def update_config_with_screen_resolution():
    """Update config.json with detected screen resolution."""
    # Load the current config
    config = load_config()
    
    # Detect screen resolution
    width, height = detect_screen_resolution()
    
    # Update the config if resolution is different
    if config.get("resolution") != [width, height]:
        config["resolution"] = [width, height]
        
        # Save the updated config
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"Updated config.json with detected screen resolution: {width}x{height}")
    
    return config
