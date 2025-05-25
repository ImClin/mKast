#!/usr/bin/env python3
"""Font management for mKast Game Launcher."""

import os
import pygame  # type: ignore
import urllib.request

def load_pixel_fonts(scale_min):
    """Load pixel art fonts or use fallback fonts.
    
    Args:
        scale_min: Minimum scale factor
        
    Returns:
        Dictionary with 'title', 'normal', and 'small' font objects
    """
    # Try to find common pixel font files
    pixel_font_paths = [
        "assets/fonts/pixel.ttf",
        "assets/fonts/Pixel Emulator.otf",
        "assets/fonts/pixel_font.ttf", 
        "assets/fonts/arcade.ttf",
        "assets/fonts/8bit.ttf"
    ]
    
    found_pixel_font = None
    
    # Look for existing fonts
    for font_path in pixel_font_paths:
        if os.path.exists(font_path):
            try:
                # Test if font is usable
                temp_font = pygame.font.Font(font_path, 16)
                test_surface = temp_font.render("Test", True, (255, 255, 255))
                if test_surface:
                    # Font works!
                    found_pixel_font = font_path
                    break
            except Exception as e:
                print(f"Font {font_path} could not be loaded: {e}")
                continue
    
    # If no font file was found or loaded, try to download one
    if not found_pixel_font:
        print("No working pixel font found, trying to download a font...")
        font_path = "assets/fonts/pixel.ttf"
        try:
            if not os.path.exists(font_path):
                # Make sure directory exists
                os.makedirs(os.path.dirname(font_path), exist_ok=True)
                
                # Try to download a free pixel font
                # Note: This is an example URL, in production use a reliable source
                font_url = "https://dl.dafont.com/dl/?f=free_pixel"
                urllib.request.urlretrieve(font_url, font_path)
                print(f"Font downloaded to {font_path}")
                
                # Test if the downloaded font works
                temp_font = pygame.font.Font(font_path, 16)
                test_surface = temp_font.render("Test", True, (255, 255, 255))
                if test_surface:
                    found_pixel_font = font_path
        except Exception as download_e:
            print(f"Could not download font: {download_e}")
    
    # If we still don't have a font, use fallback fonts
    if not found_pixel_font:
        print("No working pixel font found, using fallback fonts")
        return use_fallback_fonts(scale_min)
        
    # Pixel font size factors
    title_size = int(50 * scale_min)
    normal_size = int(28 * scale_min)
    small_size = int(20 * scale_min)
    
    # Load the fonts
    try:
        title_font = pygame.font.Font(found_pixel_font, title_size)
        normal_font = pygame.font.Font(found_pixel_font, normal_size)
        small_font = pygame.font.Font(found_pixel_font, small_size)
        
        # Test if the fonts work
        test1 = title_font.render("Test", True, (255, 255, 255))
        test2 = normal_font.render("Test", True, (255, 255, 255))
        test3 = small_font.render("Test", True, (255, 255, 255))
        
        if test1 and test2 and test3:
            print(f"Pixel font loaded: {found_pixel_font}")
            return {
                'title': title_font,
                'normal': normal_font,
                'small': small_font
            }
        else:
            raise Exception("Font render test failed")
    except Exception as e:
        print(f"Error loading pixel font: {e}")
        return use_fallback_fonts(scale_min)

def use_fallback_fonts(scale_min):
    """Use standard pygame fonts as fallback.
    
    Args:
        scale_min: Minimum scale factor
        
    Returns:
        Dictionary with 'title', 'normal', and 'small' font objects
    """
    print("Using standard fonts as fallback")
    try:
        # Create large title font (with shadows to get a bit of a pixel art effect)
        title_font = pygame.font.SysFont("impact", int(60 * scale_min))
        # Use a monospace font for normal text for more of a 'pixel' feel
        normal_font = pygame.font.SysFont("consolas", int(32 * scale_min))
        small_font = pygame.font.SysFont("consolas", int(24 * scale_min))
        
        return {
            'title': title_font,
            'normal': normal_font,
            'small': small_font
        }
    except Exception as e:
        print(f"Error loading SysFont: {e}, using built-in pygame default font")
        # Absolute fallback to pygame's built-in default font
        title_font = pygame.font.Font(None, int(60 * scale_min))
        normal_font = pygame.font.Font(None, int(32 * scale_min))
        small_font = pygame.font.Font(None, int(24 * scale_min))
        
        return {
            'title': title_font,
            'normal': normal_font,
            'small': small_font
        }
