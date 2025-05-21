#!/usr/bin/env python3
import os
import sys
import json
import pygame
import subprocess
from pygame.locals import *
import ctypes
import tkinter as tk
from tkinter import filedialog, simpledialog
import threading
import tempfile
import win32api
import win32ui
import win32con
import win32gui
from PIL import Image, ImageDraw, ImageSequence
import urllib.request

# Initialize pygame
pygame.init()

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Load configuration
def load_config():
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

# Zorg ervoor dat de assets directory bestaat
def ensure_assets_directory():
    # Maak de assets hoofdmap als deze niet bestaat
    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    # Maak de fonts submap als deze niet bestaat
    if not os.path.exists("assets/fonts"):
        os.makedirs("assets/fonts")
    
    # Maak game_images submap als deze niet bestaat
    if not os.path.exists("assets/game_images"):
        os.makedirs("assets/game_images")

# Load games data
def load_games(games_file='games.json'):
    try:
        with open(games_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Games file {games_file} not found. Creating default games file...")
        default_games = {"games": []}
        with open(games_file, 'w') as f:
            json.dump(default_games, f, indent=4)
        return default_games

# Save games data
def save_games(games_data, games_file='games.json'):
    with open(games_file, 'w') as f:
        json.dump(games_data, f, indent=4)

# Function to handle saving game images
def save_game_image(image_path):
    if not image_path:
        return None
        
    # Create game_images directory if it doesn't exist
    if not os.path.exists("assets/game_images"):
        os.makedirs("assets/game_images")
    
    # Get filename from path
    filename = os.path.basename(image_path)
    destination = os.path.join("assets/game_images", filename)
    
    # Copy the file (simple copy operation)
    try:
        # Read source image
        with open(image_path, 'rb') as src:
            image_data = src.read()
            
        # Write to destination
        with open(destination, 'wb') as dest:
            dest.write(image_data)
            
        return os.path.join("assets/game_images", filename)
    except Exception as e:
        print(f"Error copying image: {e}")
        return None

# Function to extract icon from exe file
def extract_icon_from_exe(exe_path):
    try:
        # Create game_images directory if it doesn't exist
        if not os.path.exists("assets/game_images"):
            os.makedirs("assets/game_images")
            
        # Generate a filename based on the exe name
        exe_name = os.path.splitext(os.path.basename(exe_path))[0]
        icon_path = os.path.join("assets/game_images", f"{exe_name}_icon.png")
        
        # Check if we've already extracted this icon
        if os.path.exists(icon_path):
            return icon_path
            
        # Get the large icon
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
        
        large_icon = win32ui.CreateIconFromHandle(
            win32api.ExtractIconEx(exe_path, 0)[0],
            (ico_x, ico_y)
        )
        
        # Create a bitmap to draw the icon on
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
        hdc = hdc.CreateCompatibleDC()
        
        # Draw the icon onto the bitmap
        hdc.SelectObject(hbmp)
        hdc.DrawIcon((0, 0), large_icon.GetHandle())
        
        # Convert the bitmap to a PIL Image and save it
        bmpinfo = hbmp.GetInfo()
        bmpstr = hbmp.GetBitmapBits(True)
        img = Image.frombuffer(
            "RGBA",
            (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
            bmpstr, "raw", "BGRA", 0, 1
        )
        
        # Save the image
        img.save(icon_path)
        
        # Clean up resources
        win32gui.DestroyIcon(large_icon.GetHandle())
        
        return icon_path
        
    except Exception as e:
        print(f"Error extracting icon from {exe_path}: {e}")
        return None

# Main Game Launcher Class
class GameLauncher:
    def __init__(self, games_file="games.json"):
        # Initialize pygame
        pygame.init()
        
        # Zorg ervoor dat de assets directories bestaan
        ensure_assets_directory()
        
        # Load configuration
        self.config = load_config()
        
        # Password for admin access
        self.admin_password = self.config.get("admin_password", "admin")
        self.exit_password = self.config.get("exit_password", "exit")
        
        # Screen setup
        self.resolution = (1920, 1080)  # Default fullscreen resolution
        self.scale_x = self.resolution[0] / 1920  # Scale factor for x
        self.scale_y = self.resolution[1] / 1080  # Scale factor for y
        self.scale_min = min(self.scale_x, self.scale_y)  # Minimum scale
        
        # Create borderless fullscreen window
        os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
        self.screen = pygame.display.set_mode(self.resolution, pygame.NOFRAME)
        pygame.display.set_caption("Game Launcher")
        
        # Initialize clock
        self.clock = pygame.time.Clock()
        
        # Load background color from config
        bg_color = self.config.get("background_color", (173, 216, 230))  # Light blue default
        self.background_color = tuple(bg_color)
        
        # Button colors
        self.button_color = (80, 80, 200)
        self.button_hover_color = (120, 120, 255)
        
        # Laad de pixelart fonts
        self.load_pixel_fonts()
        
        # State management
        self.state = "main"  # main, admin, password
        self.password_input = ""
        self.password_purpose = None  # 'admin' of 'exit'
        
        # Game loading
        self.games_file = games_file
        self.games_data = load_games(games_file)
        self.games = self.games_data.get("games", [])
        
        # GIF cache
        self.gif_cache = {}
        self.gif_frames = {}
        self.gif_index = {}
        self.gif_frame_time = {}
        self.last_gif_update = {}
        
        # Pagination
        self.current_page = 0
        self.games_per_page = 8  # Maximum games per page
        
        # Grid layout
        self.grid_rows = 2
        self.grid_columns = 4
        
        # Admin mode variables
        self.admin_edit_mode = False
        self.admin_edit_index = -1  # -1 betekent nieuw spel toevoegen
        self.admin_form_data = {
            'name': '', 
            'description': '', 
            'executable_path': '',
            'image_path': None
        }
        self.admin_active_field = None
        self.admin_field_text = ''
        
        # Default placeholder image
        self.placeholder_image = None
        
        # Game images cache
        self.game_images = {}
        
        # GIF animations
        self.gif_animations = {}
        self.animation_times = {}
        
        # Header kleuren (uit de config of standaard waarden)
        self.header_color = tuple(self.config.get("theme", {}).get("header_color", (255, 200, 0)))
    
    def load_pixel_fonts(self):
        """Laad pixelart fonts of gebruik fallback naar standaard fonts"""
        # Probeer eerst een aantal veelgebruikte pixel font bestanden te vinden
        # Controleer eerst in assets/fonts directory
        pixel_font_paths = [
            "assets/fonts/pixel.ttf",
            "assets/fonts/pixel_font.ttf", 
            "assets/fonts/arcade.ttf",
            "assets/fonts/8bit.ttf"
        ]
        
        found_pixel_font = None
        
        # Zoek naar bestaande fonts
        for font_path in pixel_font_paths:
            if os.path.exists(font_path):
                try:
                    # Test of het font bruikbaar is
                    temp_font = pygame.font.Font(font_path, 16)
                    test_surface = temp_font.render("Test", True, (255, 255, 255))
                    if test_surface:
                        # Font werkt!
                        found_pixel_font = font_path
                        break
                except Exception as e:
                    print(f"Font {font_path} kan niet worden geladen: {e}")
                    continue
        
        # Als we geen font bestand konden vinden of laden, probeer te downloaden
        if not found_pixel_font:
            print("Geen werkend pixel font gevonden, probeer een font te downloaden...")
            font_path = "assets/fonts/pixel.ttf"
            try:
                if not os.path.exists(font_path):
                    # Download een gratis pixel font 
                    # Dit is een voorbeeld URL, in productie moet je een betrouwbare bron gebruiken
                    font_url = "https://dl.dafont.com/dl/?f=free_pixel"
                    urllib.request.urlretrieve(font_url, font_path)
                    print(f"Font gedownload naar {font_path}")
                    # Test of het gedownloade font werkt
                    temp_font = pygame.font.Font(font_path, 16)
                    test_surface = temp_font.render("Test", True, (255, 255, 255))
                    if test_surface:
                        found_pixel_font = font_path
            except Exception as download_e:
                print(f"Kon geen font downloaden: {download_e}")
        
        # Als we nog steeds geen font hebben, gebruik fallback
        if not found_pixel_font:
            print("Geen werkend pixel font gevonden, gebruik fallback fonts")
            self.use_fallback_fonts()
            return
            
        # Pixel font grootte factoren
        title_size = int(50 * self.scale_min)
        normal_size = int(28 * self.scale_min)
        small_size = int(20 * self.scale_min)
        
        # Laad de juiste fonts
        try:
            self.title_font = pygame.font.Font(found_pixel_font, title_size)
            self.font = pygame.font.Font(found_pixel_font, normal_size)
            self.small_font = pygame.font.Font(found_pixel_font, small_size)
            
            # Test of de fonts werken
            test1 = self.title_font.render("Test", True, (255, 255, 255))
            test2 = self.font.render("Test", True, (255, 255, 255))
            test3 = self.small_font.render("Test", True, (255, 255, 255))
            
            if test1 and test2 and test3:
                print(f"Pixel font geladen: {found_pixel_font}")
                return
            else:
                raise Exception("Font render test mislukt")
        except Exception as e:
            print(f"Fout bij laden pixel font: {e}")
            self.use_fallback_fonts()
    
    def use_fallback_fonts(self):
        """Gebruik standaard pygame fonts als fallback"""
        print("Gebruik standaard fonts als fallback")
        try:
            # Maak grote titel font (met schaduwen om een beetje pixelart effect te krijgen)
            self.title_font = pygame.font.SysFont("impact", int(60 * self.scale_min))
            # Gebruik een monospace font voor de normale tekst voor een meer 'pixel' gevoel
            self.font = pygame.font.SysFont("consolas", int(32 * self.scale_min))
            self.small_font = pygame.font.SysFont("consolas", int(24 * self.scale_min))
        except Exception as e:
            print(f"Fout bij laden SysFont: {e}, gebruik ingebouwde pygame default font")
            # Absolute fallback naar pygame's ingebouwde standaard lettertype
            self.title_font = pygame.font.Font(None, int(60 * self.scale_min))
            self.font = pygame.font.Font(None, int(32 * self.scale_min))
            self.small_font = pygame.font.Font(None, int(24 * self.scale_min))
    
    def create_default_game_image(self):
        # Create a default image for games without an image
        # Scale the image size
        image_size = int(200 * self.scale_min)
        surf = pygame.Surface((image_size, image_size))
        surf.fill((60, 60, 100))
        pygame.draw.rect(surf, (100, 100, 160), (int(10 * self.scale_min), int(10 * self.scale_min), 
                                              int(180 * self.scale_min), int(180 * self.scale_min)))
        font = pygame.font.SysFont("consolas", int(32 * self.scale_min))
        text = font.render("No Image", True, WHITE)
        text_rect = text.get_rect(center=(image_size//2, image_size//2))
        surf.blit(text, text_rect)
        return surf
    
    def load_game_image(self, image_path, size=None):
        # Handle None or empty image path
        if not image_path:
            # Return a default/placeholder image
            return self.get_placeholder_image(size)
            
        # If no size provided, use default
        if size is None:
            size = int(200 * self.scale_min)
            
        # If size is an integer, make it a square tuple
        if isinstance(size, int):
            size = (size, size)
            
        # Check if image is already loaded in cache with current size
        cache_key = f"{image_path}_{size[0]}_{size[1]}"
        if cache_key in self.game_images:
            return self.game_images[cache_key]
            
        # Try to load the image
        try:
            if os.path.exists(image_path):
                # Check if it's a GIF
                if isinstance(image_path, str) and image_path.lower().endswith('.gif'):
                    # Process GIF animation
                    return self._load_animated_gif(image_path, size)
                else:
                    # Regular image
                    img = pygame.image.load(image_path)
                    img = pygame.transform.scale(img, size)
                    self.game_images[cache_key] = img
                    return img
            else:
                # File doesn't exist
                return self.get_placeholder_image(size)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return self.get_placeholder_image(size)
            
    def get_placeholder_image(self, size=None):
        """Generate a placeholder image when no image is available"""
        # If no size provided, use default
        if size is None:
            size = int(200 * self.scale_min)
            
        # If size is an integer, make it a square tuple
        if isinstance(size, int):
            size = (size, size)
            
        # Check if we already created this placeholder
        cache_key = f"placeholder_{size[0]}_{size[1]}"
        if cache_key in self.game_images:
            return self.game_images[cache_key]
            
        # Create a pixel art frame like the reference image
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Main background (transparent)
        surface.fill((0, 0, 0, 0))
        
        # Calculate pixel size for pixel art effect
        pixel_size = max(1, int(size[0] / 32))
        
        # Draw blue pixel border frame
        blue_color = (0, 100, 210)
        
        # Top horizontal border
        for x in range(3*pixel_size, size[0]-3*pixel_size, pixel_size):
            pygame.draw.rect(surface, blue_color, (x, 0, pixel_size, pixel_size))
            pygame.draw.rect(surface, blue_color, (x, pixel_size, pixel_size, pixel_size))
        
        # Bottom horizontal border
        for x in range(3*pixel_size, size[0]-3*pixel_size, pixel_size):
            pygame.draw.rect(surface, blue_color, (x, size[1]-2*pixel_size, pixel_size, pixel_size))
            pygame.draw.rect(surface, blue_color, (x, size[1]-pixel_size, pixel_size, pixel_size))
        
        # Left vertical border
        for y in range(3*pixel_size, size[1]-3*pixel_size, pixel_size):
            pygame.draw.rect(surface, blue_color, (0, y, pixel_size, pixel_size))
            pygame.draw.rect(surface, blue_color, (pixel_size, y, pixel_size, pixel_size))
        
        # Right vertical border
        for y in range(3*pixel_size, size[1]-3*pixel_size, pixel_size):
            pygame.draw.rect(surface, blue_color, (size[0]-2*pixel_size, y, pixel_size, pixel_size))
            pygame.draw.rect(surface, blue_color, (size[0]-pixel_size, y, pixel_size, pixel_size))
        
        # Rounded corners - Specify the exact pixels to create a rounded corner effect
        # Top-left corner (create rounded corner by drawing specific pixels)
        corner_top_left = [
            (0, 2*pixel_size), (1*pixel_size, 1*pixel_size), 
            (2*pixel_size, 0), (1*pixel_size, 0),
            (0, 1*pixel_size)
        ]
        
        for x, y in corner_top_left:
            pygame.draw.rect(surface, blue_color, (x, y, pixel_size, pixel_size))
        
        # Top-right corner
        corner_top_right = [
            (size[0]-1*pixel_size, 0), (size[0]-2*pixel_size, 0),
            (size[0]-1*pixel_size, 1*pixel_size), (size[0]-3*pixel_size, 0),
            (size[0]-pixel_size, 2*pixel_size)
        ]
        
        for x, y in corner_top_right:
            pygame.draw.rect(surface, blue_color, (x, y, pixel_size, pixel_size))
        
        # Bottom-left corner
        corner_bottom_left = [
            (0, size[1]-3*pixel_size), (1*pixel_size, size[1]-1*pixel_size),
            (0, size[1]-1*pixel_size), (2*pixel_size, size[1]-1*pixel_size),
            (1*pixel_size, size[1]-2*pixel_size)
        ]
        
        for x, y in corner_bottom_left:
            pygame.draw.rect(surface, blue_color, (x, y, pixel_size, pixel_size))
        
        # Bottom-right corner
        corner_bottom_right = [
            (size[0]-1*pixel_size, size[1]-1*pixel_size), (size[0]-2*pixel_size, size[1]-1*pixel_size),
            (size[0]-3*pixel_size, size[1]-1*pixel_size), (size[0]-1*pixel_size, size[1]-2*pixel_size),
            (size[0]-1*pixel_size, size[1]-3*pixel_size)
        ]
        
        for x, y in corner_bottom_right:
            pygame.draw.rect(surface, blue_color, (x, y, pixel_size, pixel_size))
        
        # Black stroke/border around the blue frame (1 pixel outside)
        stroke_color = (0, 0, 0)
        
        # Top and bottom black border
        for x in range(0, size[0], pixel_size):
            # Top stroke
            if not any(px == x and py == 0 for px, py in corner_top_left + corner_top_right):
                pygame.draw.rect(surface, stroke_color, (x, 0, pixel_size, pixel_size))
                
            # Bottom stroke
            if not any(px == x and py == size[1]-pixel_size for px, py in corner_bottom_left + corner_bottom_right):
                pygame.draw.rect(surface, stroke_color, (x, size[1]-pixel_size, pixel_size, pixel_size))
        
        # Left and right black border
        for y in range(0, size[1], pixel_size):
            # Left stroke
            if not any(px == 0 and py == y for px, py in corner_top_left + corner_bottom_left):
                pygame.draw.rect(surface, stroke_color, (0, y, pixel_size, pixel_size))
                
            # Right stroke
            if not any(px == size[0]-pixel_size and py == y for px, py in corner_top_right + corner_bottom_right):
                pygame.draw.rect(surface, stroke_color, (size[0]-pixel_size, y, pixel_size, pixel_size))
        
        # Special corner pixels for black stroke
        black_corner_pixels = [
            # Top-left rounded stroke
            (pixel_size, 0), (0, pixel_size),
            # Top-right rounded stroke
            (size[0]-2*pixel_size, 0), (size[0]-pixel_size, pixel_size),
            # Bottom-left rounded stroke
            (pixel_size, size[1]-pixel_size), (0, size[1]-2*pixel_size),
            # Bottom-right rounded stroke
            (size[0]-2*pixel_size, size[1]-pixel_size), (size[0]-pixel_size, size[1]-2*pixel_size)
        ]
        
        for x, y in black_corner_pixels:
            pygame.draw.rect(surface, stroke_color, (x, y, pixel_size, pixel_size))
        
        # White inner area with rounded corners
        inner_margin = 2 * pixel_size
        inner_width = size[0] - 2 * inner_margin
        inner_height = size[1] - 2 * inner_margin
        
        # Fille the main white area
        pygame.draw.rect(surface, WHITE, (inner_margin, inner_margin, inner_width, inner_height))
        
        # Round the white area corners by removing corner pixels
        # Top-left inner corner
        pygame.draw.rect(surface, (0, 0, 0, 0), (inner_margin, inner_margin, pixel_size, pixel_size))
        
        # Top-right inner corner
        pygame.draw.rect(surface, (0, 0, 0, 0), (inner_margin + inner_width - pixel_size, inner_margin, pixel_size, pixel_size))
        
        # Bottom-left inner corner
        pygame.draw.rect(surface, (0, 0, 0, 0), (inner_margin, inner_margin + inner_height - pixel_size, pixel_size, pixel_size))
        
        # Bottom-right inner corner
        pygame.draw.rect(surface, (0, 0, 0, 0), (inner_margin + inner_width - pixel_size, inner_margin + inner_height - pixel_size, pixel_size, pixel_size))
        
        # Cache and return
        self.game_images[cache_key] = surface
        return surface
            
        # Return default image if loading fails
        default_img = pygame.transform.scale(self.default_game_image, size)
        self.game_images[cache_key] = default_img
        return default_img
        
    def _load_animated_gif(self, gif_path, size):
        """Load an animated GIF and prepare it for display"""
        try:
            # Use PIL to open the GIF
            pil_img = Image.open(gif_path)
            
            # Check if it's actually animated
            if not getattr(pil_img, "is_animated", False):
                # Not animated, treat as normal image
                pil_img = pil_img.convert("RGBA")
                img_data = pil_img.resize(size).tobytes()
                img = pygame.image.fromstring(img_data, size, "RGBA")
                return img
                
            # Store frames and timing
            frames = []
            frame_durations = []
            
            try:
                # For animated GIF
                original_index = pil_img.tell()
                animation_loops = 0  # 0 = loop forever
                
                while True:
                    # Get frame duration
                    duration = pil_img.info.get('duration', 100)  # Default to 100ms if not specified
                    frame_durations.append(duration / 1000.0)  # Convert to seconds
                    
                    # Convert frame to pygame surface
                    frame_data = pil_img.convert("RGBA").resize(size).tobytes()
                    frame = pygame.image.fromstring(frame_data, size, "RGBA")
                    frames.append(frame)
                    
                    try:
                        pil_img.seek(pil_img.tell() + 1)
                    except EOFError:
                        break
                        
                # Reset the PIL image
                pil_img.seek(original_index)
                
                # Store the animation data
                self.gif_animations[gif_path] = {
                    'frames': frames,
                    'durations': frame_durations,
                    'current_frame': 0,
                    'last_update': pygame.time.get_ticks() / 1000.0,
                    'loops': animation_loops
                }
                
                # Initialize animation time tracking
                if gif_path not in self.animation_times:
                    self.animation_times[gif_path] = pygame.time.get_ticks() / 1000.0
                
                # Return the first frame
                return frames[0]
                
            except Exception as frame_e:
                print(f"Error processing gif frames: {frame_e}")
                # Fall back to first frame only
                pil_img.seek(0)
                frame_data = pil_img.convert("RGBA").resize(size).tobytes()
                img = pygame.image.fromstring(frame_data, size, "RGBA")
                return img
                
        except Exception as e:
            print(f"Error loading GIF {gif_path}: {e}")
            # Return default image
            return pygame.transform.scale(self.default_game_image, size)
            
    def get_current_gif_frame(self, image_path):
        """Get the current frame of an animated GIF based on timing"""
        if image_path not in self.gif_animations:
            return None
            
        anim_data = self.gif_animations[image_path]
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed = current_time - anim_data['last_update']
        
        # Check if it's time to advance the frame
        if elapsed > anim_data['durations'][anim_data['current_frame']]:
            # Update the frame
            anim_data['current_frame'] = (anim_data['current_frame'] + 1) % len(anim_data['frames'])
            anim_data['last_update'] = current_time
            
        return anim_data['frames'][anim_data['current_frame']]
    
    def update_gif_animation(self, image_path):
        if image_path is None:
            return None
            
        # Make sure the animation is loaded
        if image_path not in self.gif_animations:
            # Try to load it if it wasn't loaded before
            self._load_animated_gif(image_path, (200, 200))
            
        if image_path in self.gif_animations:
            frames = self.gif_animations[image_path]['frames']
            if not frames:  # Empty frames list
                return None
                
            current_time = pygame.time.get_ticks()
            frame_duration = 100  # Duration for each frame in milliseconds
            frame_index = (current_time // frame_duration) % len(frames)
            self.animation_times[image_path] = frame_index
            return frames[frame_index]
        return None
    
    def draw_text(self, text, font, color, x, y, align="left", shadow=True, shadow_color=None, shadow_offset=None):
        lines = text.split('\n')
        y_offset = 0
        
        if shadow_color is None:
            shadow_color = (50, 50, 70)  # Standaard schaduw kleur
            
        if shadow_offset is None:
            shadow_offset = max(1, int(2 * self.scale_min))  # Standaard schaduw offset
        
        # Probeer eerst anti-aliasing uit voor pixel-look
        try_pixel_perfect = True
        
        for line in lines:
            # Pixelart effect: teken de schaduw van de tekst eerst
            if shadow:
                try:
                    if try_pixel_perfect:
                        shadow_surf = font.render(line, False, shadow_color)  # Anti-aliasing uit voor pixel effect
                except pygame.error:
                    # Als dat mislukt, gebruik anti-aliasing
                    try_pixel_perfect = False
                    shadow_surf = font.render(line, True, shadow_color)
                
                if not try_pixel_perfect:
                    shadow_surf = font.render(line, True, shadow_color)
                
                shadow_rect = shadow_surf.get_rect()
                
                if align == "left":
                    shadow_rect.topleft = (x + shadow_offset, y + y_offset + shadow_offset)
                elif align == "center":
                    shadow_rect.midtop = (x + shadow_offset, y + y_offset + shadow_offset)
                elif align == "right":
                    shadow_rect.topright = (x + shadow_offset, y + y_offset + shadow_offset)
                    
                self.screen.blit(shadow_surf, shadow_rect)
            
            # Teken dan de hoofdtekst
            try:
                if try_pixel_perfect:
                    text_surf = font.render(line, False, color)  # Anti-aliasing uit voor pixelart effect
                else:
                    text_surf = font.render(line, True, color)
            except pygame.error:
                # Fallback naar anti-aliasing als pixel-perfect niet werkt
                text_surf = font.render(line, True, color)
            
            text_rect = text_surf.get_rect()
            
            if align == "left":
                text_rect.topleft = (x, y + y_offset)
            elif align == "center":
                text_rect.midtop = (x, y + y_offset)
            elif align == "right":
                text_rect.topright = (x, y + y_offset)
                
            self.screen.blit(text_surf, text_rect)
            y_offset += text_rect.height + 5
        
        return y_offset  # Return total height of drawn text
    
    def draw_button(self, text, x, y, width, height, action=None, hover_color=None):
        mouse_pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        hover_color = hover_color or self.button_hover_color
        
        # Check if mouse is over button
        is_hover = x < mouse_pos[0] < x + width and y < mouse_pos[1] < y + height
        
        # Basis pixel grootte voor pixelachtige randen
        pixel_size = max(2, int(min(width, height) / 30))
        
        # Bepaal kleur op basis van hover status
        color = hover_color if is_hover else self.button_color
        
        # Maak een pixelachtig rechthoek (in plaats van afgeronde hoeken)
        # Teken de basis rechthoek
        pygame.draw.rect(self.screen, color, (x, y, width, height))
        
        # Pixel border effect (dikker bij hover)
        border_color = WHITE
        border_thickness = 2 if is_hover else 1
        
        # Teken top border
        for bx in range(0, width, pixel_size):
            for i in range(border_thickness):
                pygame.draw.rect(self.screen, border_color, 
                               (x + bx, y + i*pixel_size, pixel_size, pixel_size))
        
        # Teken bottom border
        for bx in range(0, width, pixel_size):
            for i in range(border_thickness):
                pygame.draw.rect(self.screen, border_color, 
                               (x + bx, y + height - (i+1)*pixel_size, pixel_size, pixel_size))
        
        # Teken left border
        for by in range(0, height, pixel_size):
            for i in range(border_thickness):
                pygame.draw.rect(self.screen, border_color, 
                               (x + i*pixel_size, y + by, pixel_size, pixel_size))
        
        # Teken right border
        for by in range(0, height, pixel_size):
            for i in range(border_thickness):
                pygame.draw.rect(self.screen, border_color, 
                               (x + width - (i+1)*pixel_size, y + by, pixel_size, pixel_size))
        
        # Draw button text with pixel shadow
        text_color = WHITE  # Altijd witte tekst
        text_shadow_color = (70, 70, 90) if is_hover else (50, 50, 70)
        
        # Probeer anti-aliasing uit voor pixelart effect
        try:
            text_shadow = self.font.render(text, False, text_shadow_color)
            text_surf = self.font.render(text, False, text_color)
        except pygame.error:
            # Fallback naar anti-aliasing als dat niet werkt
            text_shadow = self.font.render(text, True, text_shadow_color)
            text_surf = self.font.render(text, True, text_color)
        
        text_rect = text_surf.get_rect(center=(x + width/2, y + height/2))
        shadow_rect = text_shadow.get_rect(center=(x + width/2 + pixel_size, y + height/2 + pixel_size))
        
        # Teken eerst de schaduw, dan de tekst
        self.screen.blit(text_shadow, shadow_rect)
        self.screen.blit(text_surf, text_rect)
        
        # Check for click and return action if clicked
        if is_hover and click[0] == 1 and action is not None:
            # Add a small delay to prevent multiple clicks
            pygame.time.delay(100)
            return action
        
        return None
    
    def draw_game_entry(self, game, x, y, width, height):
        # Draw game container
        pygame.draw.rect(self.screen, GRAY, (x, y, width, height))
        pygame.draw.rect(self.screen, WHITE, (x, y, width, height), max(1, int(2 * self.scale_min)))
        
        # Calculate scaled image size
        image_size = int(width * 0.3)  # Image takes 30% of card width
        padding = int(10 * self.scale_min)
        
        # Draw game image - handle both static and animated images
        image_path = game.get('image_path')
        if image_path and image_path.lower().endswith('.gif') and image_path in self.gif_animations:
            # Get the current frame of the animated GIF
            img = self.get_current_gif_frame(image_path)
            if img is None:  # Fallback if animation data isn't ready
                img = self.load_game_image(image_path, (image_size, image_size))
        else:
            # Load static image
            img = self.load_game_image(image_path, (image_size, image_size))
            
        img_x = x + padding
        img_y = y + padding
        self.screen.blit(img, (img_x, img_y))
        
        # Draw game title
        title_x = x + image_size + padding * 2
        title_y = y + padding
        self.draw_text(game['name'], self.font, self.header_color, title_x, title_y)
        
        # Draw game description (wrapped to fit)
        desc = game['description']
        # Adjust wrapping based on card size
        max_chars = int((width - image_size - padding * 3) / (8 * self.scale_min))
        if len(desc) > max_chars:
            desc = desc[:max_chars] + "..."
        desc_x = x + image_size + padding * 2
        desc_y = y + padding + int(40 * self.scale_min)
        self.draw_text(desc, self.small_font, WHITE, desc_x, desc_y)
        
        # Draw launch button
        button_width = int(width * 0.4)
        button_height = int(height * 0.2)
        button_x = x + width - button_width - padding
        button_y = y + height - button_height - padding
        action = self.draw_button("Launch", button_x, button_y, 
                                button_width, button_height,
                                lambda: self.launch_game(game['executable_path']))
        
        return action
    
    def draw_main_screen(self):
        # Clear the screen
        self.screen.fill(self.background_color)
        
        # Draw title - Haagse Hogeschool Game Lab in pixel art stijl
        try:
            # Anti-aliasing uit voor pixel effect
            haagse_title = self.title_font.render("HAAGSE", False, (184, 207, 8))
            hogeschool_title = self.title_font.render("HOGESCHOOL", False, (184, 207, 8))
            
            game_title = self.title_font.render("GAME", False, WHITE)
            lab_title = self.title_font.render("LAB", False, WHITE)
            
            # Pixel shadow effect voor meer retro look
            haagse_shadow = self.title_font.render("HAAGSE", False, (100, 120, 0))
            hogeschool_shadow = self.title_font.render("HOGESCHOOL", False, (100, 120, 0))
            game_shadow = self.title_font.render("GAME", False, (100, 100, 100))
            lab_shadow = self.title_font.render("LAB", False, (100, 100, 100))
        except pygame.error:
            # Fallback naar anti-aliasing aan als er problemen zijn met False parameter
            haagse_title = self.title_font.render("HAAGSE", True, (184, 207, 8))
            hogeschool_title = self.title_font.render("HOGESCHOOL", True, (184, 207, 8))
            
            game_title = self.title_font.render("GAME", True, WHITE)
            lab_title = self.title_font.render("LAB", True, WHITE)
            
            # Pixel shadow effect voor meer retro look
            haagse_shadow = self.title_font.render("HAAGSE", True, (100, 120, 0))
            hogeschool_shadow = self.title_font.render("HOGESCHOOL", True, (100, 120, 0))
            game_shadow = self.title_font.render("GAME", True, (100, 100, 100))
            lab_shadow = self.title_font.render("LAB", True, (100, 100, 100))
        
        # Positie van titels
        haagse_x = int(50 * self.scale_x)
        haagse_y = int(30 * self.scale_y)
        hogeschool_x = int(50 * self.scale_x)
        hogeschool_y = int(100 * self.scale_y)
        
        game_x = int(self.resolution[0] - 300 * self.scale_x)
        game_y = int(30 * self.scale_y)
        lab_x = int(self.resolution[0] - 300 * self.scale_x)
        lab_y = int(100 * self.scale_y)
        
        # Teken schaduwen (offset voor pixelachtig effect)
        shadow_offset = int(3 * self.scale_min)
        self.screen.blit(haagse_shadow, (haagse_x + shadow_offset, haagse_y + shadow_offset))
        self.screen.blit(hogeschool_shadow, (hogeschool_x + shadow_offset, hogeschool_y + shadow_offset))
        self.screen.blit(game_shadow, (game_x + shadow_offset, game_y + shadow_offset))
        self.screen.blit(lab_shadow, (lab_x + shadow_offset, lab_y + shadow_offset))
        
        # Teken titels
        self.screen.blit(haagse_title, (haagse_x, haagse_y))
        self.screen.blit(hogeschool_title, (hogeschool_x, hogeschool_y))
        self.screen.blit(game_title, (game_x, game_y))
        self.screen.blit(lab_title, (lab_x, lab_y))
        
        # Teken spellen in grid formaat zoals getoond in de afbeelding
        start_index = self.current_page * self.games_per_page
        end_index = min(start_index + self.games_per_page, len(self.games))
        
        if len(self.games) == 0:
            # Toon "Geen spellen beschikbaar" bericht
            self.draw_text("Geen spellen beschikbaar.", self.font, WHITE, 
                         self.resolution[0]/2, self.resolution[1]/2, align="center")
        else:
            # Bereken grid dimensies - hier maken we een grotere grid zoals in de afbeelding
            grid_margin_x = int(50 * self.scale_x)
            grid_margin_y = int(200 * self.scale_y)  # Meer ruimte voor titels
            grid_spacing_x = int(40 * self.scale_x)
            grid_spacing_y = int(20 * self.scale_y)
            
            # Gebruik 4 kolommen zoals in de afbeelding
            self.grid_columns = 4
            self.grid_rows = 1
            self.games_per_page = self.grid_columns * self.grid_rows
            
            # Bereken kaart dimensies
            available_width = self.resolution[0] - (grid_margin_x * 2) - (grid_spacing_x * (self.grid_columns - 1))
            card_width = available_width // self.grid_columns
            card_height = int(400 * self.scale_y)  # Hogere kaarten voor het pixel art design
            
            # Teken voor elk spel een kaart in de stijl van de afbeelding
            for i in range(start_index, end_index):
                if i >= len(self.games):
                    break
                    
                # Bereken grid positie
                grid_index = i - start_index
                col = grid_index % self.grid_columns
                row = grid_index // self.grid_columns
                
                # Bereken kaart positie
                x = grid_margin_x + col * (card_width + grid_spacing_x)
                y = grid_margin_y + row * (card_height + grid_spacing_y)
                
                game = self.games[i]
                
                # Tekst met pixel schaduw voor game naam
                game_name_text = f"GAME {i+1}"
                name_shadow = self.font.render(game_name_text, True, BLACK)
                game_name = self.font.render(game_name_text, True, WHITE)
                
                # Teken game naam
                name_y = y + int(30 * self.scale_y)
                name_x = x + card_width//2 - game_name.get_width()//2
                
                # Schaduw effect
                shadow_offset = int(2 * self.scale_min)
                self.screen.blit(name_shadow, (name_x + shadow_offset, name_y + shadow_offset))
                self.screen.blit(game_name, (name_x, name_y))
                
                # Foto frame dimensies met ruimer pixelrandje
                frame_margin = int(30 * self.scale_x)
                frame_width = card_width - 2 * frame_margin
                frame_height = frame_width  # Vierkant frame
                frame_x = x + frame_margin
                frame_y = name_y + int(50 * self.scale_y)
                
                # Bereken pixel grootte op basis van frame
                pixel_size = max(2, int(frame_width / 32))
                
                # Teken een pixel frame zoals in de referentieafbeelding maar met ronde hoeken
                blue_color = (0, 100, 210)
                black_stroke = (0, 0, 0)
                
                # Teken eerst een zwarte rand (stroke) rond het hele frame
                # Teken de basis zwarte rechthoek voor de stroke
                pygame.draw.rect(self.screen, black_stroke, 
                               (frame_x - pixel_size, frame_y - pixel_size, 
                                frame_width + 2*pixel_size, frame_height + 2*pixel_size))
                
                # Maak de hoeken rond door zwarte pixels te verwijderen
                # Top-left corner
                pygame.draw.rect(self.screen, self.background_color, 
                               (frame_x - pixel_size, frame_y - pixel_size, pixel_size, pixel_size))
                
                # Top-right corner
                pygame.draw.rect(self.screen, self.background_color, 
                               (frame_x + frame_width, frame_y - pixel_size, pixel_size, pixel_size))
                
                # Bottom-left corner
                pygame.draw.rect(self.screen, self.background_color, 
                               (frame_x - pixel_size, frame_y + frame_height, pixel_size, pixel_size))
                
                # Bottom-right corner
                pygame.draw.rect(self.screen, self.background_color, 
                               (frame_x + frame_width, frame_y + frame_height, pixel_size, pixel_size))
                
                # Teken het blauwe frame (2 pixels dik)
                # Teken de basis blauwe rechthoek
                pygame.draw.rect(self.screen, blue_color, 
                               (frame_x, frame_y, frame_width, frame_height))
                
                # Teken top border (2 pixel dik) maar met ruimte voor ronde hoeken
                for px in range(3*pixel_size, frame_width-3*pixel_size, pixel_size):
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + px, frame_y, pixel_size, pixel_size))
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + px, frame_y + pixel_size, pixel_size, pixel_size))
                
                # Teken bottom border (2 pixel dik) maar met ruimte voor ronde hoeken
                for px in range(3*pixel_size, frame_width-3*pixel_size, pixel_size):
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + px, frame_y + frame_height - 2*pixel_size, pixel_size, pixel_size))
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + px, frame_y + frame_height - pixel_size, pixel_size, pixel_size))
                
                # Teken left border (2 pixel dik) maar met ruimte voor ronde hoeken
                for py in range(3*pixel_size, frame_height-3*pixel_size, pixel_size):
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x, frame_y + py, pixel_size, pixel_size))
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + pixel_size, frame_y + py, pixel_size, pixel_size))
                
                # Teken right border (2 pixel dik) maar met ruimte voor ronde hoeken
                for py in range(3*pixel_size, frame_height-3*pixel_size, pixel_size):
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + frame_width - 2*pixel_size, frame_y + py, pixel_size, pixel_size))
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + frame_width - pixel_size, frame_y + py, pixel_size, pixel_size))
                
                # Teken de ronde hoeken
                # Top-left rounded corner
                corner_pixels_tl = [
                    (0, 2*pixel_size), (0, pixel_size), (pixel_size, 0),
                    (2*pixel_size, 0), (pixel_size, pixel_size)
                ]
                
                for dx, dy in corner_pixels_tl:
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + dx, frame_y + dy, pixel_size, pixel_size))
                
                # Top-right rounded corner
                corner_pixels_tr = [
                    (frame_width - 3*pixel_size, 0), (frame_width - 2*pixel_size, 0),
                    (frame_width - pixel_size, pixel_size), (frame_width - pixel_size, 2*pixel_size)
                ]
                
                for dx, dy in corner_pixels_tr:
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + dx, frame_y + dy, pixel_size, pixel_size))
                
                # Bottom-left rounded corner
                corner_pixels_bl = [
                    (0, frame_height - 3*pixel_size), (0, frame_height - 2*pixel_size),
                    (pixel_size, frame_height - pixel_size), (2*pixel_size, frame_height - pixel_size)
                ]
                
                for dx, dy in corner_pixels_bl:
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + dx, frame_y + dy, pixel_size, pixel_size))
                
                # Bottom-right rounded corner
                corner_pixels_br = [
                    (frame_width - 3*pixel_size, frame_height - pixel_size),
                    (frame_width - 2*pixel_size, frame_height - pixel_size),
                    (frame_width - pixel_size, frame_height - 2*pixel_size),
                    (frame_width - pixel_size, frame_height - 3*pixel_size)
                ]
                
                for dx, dy in corner_pixels_br:
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + dx, frame_y + dy, pixel_size, pixel_size))
                
                # Witte binnenkant met ronde hoeken
                inner_margin = 2 * pixel_size
                pygame.draw.rect(self.screen, WHITE, 
                               (frame_x + inner_margin, frame_y + inner_margin, 
                                frame_width - 2*inner_margin, frame_height - 2*inner_margin))
                
                # Rond de witte hoeken
                # Top-left inner corner
                pygame.draw.rect(self.screen, blue_color, 
                               (frame_x + inner_margin, frame_y + inner_margin, pixel_size, pixel_size))
                
                # Top-right inner corner
                pygame.draw.rect(self.screen, blue_color, 
                               (frame_x + frame_width - inner_margin - pixel_size, 
                                frame_y + inner_margin, pixel_size, pixel_size))
                
                # Bottom-left inner corner
                pygame.draw.rect(self.screen, blue_color, 
                               (frame_x + inner_margin, 
                                frame_y + frame_height - inner_margin - pixel_size, pixel_size, pixel_size))
                
                # Bottom-right inner corner
                pygame.draw.rect(self.screen, blue_color, 
                               (frame_x + frame_width - inner_margin - pixel_size, 
                                frame_y + frame_height - inner_margin - pixel_size, pixel_size, pixel_size))
                
                # Laad en teken game afbeelding
                image_path = game.get('image_path')
                img_size = frame_width - 2*inner_margin
                
                if image_path and image_path.lower().endswith('.gif') and image_path in self.gif_animations:
                    img = self.get_current_gif_frame(image_path)
                    if img is None:
                        img = self.load_game_image(image_path, (img_size, img_size))
                else:
                    img = self.load_game_image(image_path, (img_size, img_size))
                
                self.screen.blit(img, (frame_x + inner_margin, frame_y + inner_margin))
                
                # Teken "FOTO" tekst op de afbeelding met pixel schaduw
                foto_shadow = self.small_font.render("FOTO", True, (180, 180, 180))
                foto_label = self.small_font.render("FOTO", True, BLACK)
                foto_x = frame_x + frame_width//2 - foto_label.get_width()//2
                foto_y = frame_y + frame_height//2 - foto_label.get_height()//2
                
                # Teken schaduw en dan label
                shadow_offset = int(1 * self.scale_min)
                self.screen.blit(foto_shadow, (foto_x + shadow_offset, foto_y + shadow_offset))
                self.screen.blit(foto_label, (foto_x, foto_y))
                
                # Teken categorie label met pixel schaduw
                cat_y = frame_y + frame_height + int(20 * self.scale_y)
                cat_shadow = self.small_font.render("CATEGORIE", True, (100, 100, 100))
                cat_label = self.small_font.render("CATEGORIE", True, WHITE)
                cat_x = x + card_width//2 - cat_label.get_width()//2
                
                # Teken schaduw en dan label
                self.screen.blit(cat_shadow, (cat_x + shadow_offset, cat_y + shadow_offset))
                self.screen.blit(cat_label, (cat_x, cat_y))
                
                # Start spel als erop geklikt wordt (hele kaart is klikbaar)
                mouse_pos = pygame.mouse.get_pos()
                click = pygame.mouse.get_pressed()
                
                # Maak het klikbare gebied iets kleiner dan de kaart voor betere visuele feedback
                card_rect = pygame.Rect(frame_x, frame_y, frame_width, frame_height)
                if card_rect.collidepoint(mouse_pos):
                    # Highlight effect bij hover
                    highlight = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    highlight.fill((255, 255, 255, 50))  # Semi-transparante highlight
                    self.screen.blit(highlight, (frame_x, frame_y))
                    
                    if click[0] == 1:
                        pygame.time.delay(100)  # Voorkom dubbele klikken
                        self.launch_game(game['executable_path'])
            
            # Navigatie pijlen aan de zijkanten van het scherm
            if len(self.games) > self.games_per_page:
                # Links/vorige pijl
                arrow_size = int(60 * self.scale_min)
                arrow_y = grid_margin_y + card_height // 2 - arrow_size // 2
                arrow_margin = int(10 * self.scale_x)
                
                # Pijl links (vorige games)
                if self.current_page > 0:
                    left_arrow_x = grid_margin_x - arrow_size - arrow_margin
                    
                    # Teken een pixelachtige pijl links
                    left_arrow = self.draw_pixel_arrow(arrow_size, "left")
                    self.screen.blit(left_arrow, (left_arrow_x, arrow_y))
                    
                    # Check voor klik op linker pijl
                    left_arrow_rect = pygame.Rect(left_arrow_x, arrow_y, arrow_size, arrow_size)
                    if left_arrow_rect.collidepoint(mouse_pos) and click[0] == 1:
                        pygame.time.delay(100)  # Voorkom dubbele klikken
                        self.change_page(-1)
                
                # Pijl rechts (volgende games)
                if (self.current_page + 1) * self.games_per_page < len(self.games):
                    right_arrow_x = self.resolution[0] - grid_margin_x + arrow_margin
                    
                    # Teken een pixelachtige pijl rechts
                    right_arrow = self.draw_pixel_arrow(arrow_size, "right")
                    self.screen.blit(right_arrow, (right_arrow_x, arrow_y))
                    
                    # Check voor klik op rechter pijl
                    right_arrow_rect = pygame.Rect(right_arrow_x, arrow_y, arrow_size, arrow_size)
                    if right_arrow_rect.collidepoint(mouse_pos) and click[0] == 1:
                        pygame.time.delay(100)  # Voorkom dubbele klikken
                        self.change_page(1)
        
        # Admin en Exit knoppen in een veilige positie
        button_width = int(100 * self.scale_x)
        button_height = int(35 * self.scale_y)
        
        # Admin knop in de hoek linksboven - extra ruimte van hoofdtitels
        admin_button_x = int(haagse_x)  # Align met HAAGSE titel
        admin_button_y = int(hogeschool_y + hogeschool_title.get_height() + 20 * self.scale_y)
        admin_action = self.draw_button("Admin", admin_button_x, admin_button_y, 
                                      button_width, button_height, 
                                      lambda: self.activate_password('admin'))
        if admin_action:
            return admin_action
        
        # Exit knop in de hoek rechtsboven - extra ruimte van hoofdtitels
        exit_button_x = int(game_x + game_title.get_width() - button_width)  # Align rechts met GAME titel
        exit_button_y = int(lab_y + lab_title.get_height() + 20 * self.scale_y)
        exit_action = self.draw_button("Exit", exit_button_x, exit_button_y, 
                                     button_width, button_height,
                                     lambda: self.activate_password('exit'))
        if exit_action:
            return exit_action
            
        return None
    
    def draw_pixel_arrow(self, size, direction="right"):
        """Helper functie om pixelachtige pijl te tekenen"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))  # Transparante achtergrond
        
        # Bereken pixel grootte voor de pijl
        pixel_size = max(2, size // 10)
        
        # Kleuren voor de pijl
        arrow_color = (220, 220, 220)  # Witte pijl
        shadow_color = (100, 100, 100, 180)  # Schaduw
        
        # Bepaal punten voor pijl gebaseerd op richting
        arrow_points = []
        shadow_offset = pixel_size
        
        if direction == "right":
            # Rechter pijl (wijst naar rechts)
            mid_y = size // 2
            
            # Teken rechter pijl als een eenvoudige driehoek met pixels
            for i in range(6):
                # Verticale streep van pijlstaart
                pygame.draw.rect(surface, shadow_color, 
                              (shadow_offset, mid_y - 3*pixel_size + i*pixel_size, pixel_size, pixel_size))
                pygame.draw.rect(surface, arrow_color, 
                              (0, mid_y - 3*pixel_size + i*pixel_size, pixel_size, pixel_size))
            
            # Pijlkop als driehoek
            for i in range(1, 7):
                line_length = i
                y_offset = 3 - i
                
                # Schaduw
                pygame.draw.rect(surface, shadow_color, 
                              (pixel_size + shadow_offset, mid_y + y_offset*pixel_size, line_length*pixel_size, pixel_size))
                pygame.draw.rect(surface, shadow_color, 
                              (pixel_size + shadow_offset, mid_y - (y_offset+1)*pixel_size, line_length*pixel_size, pixel_size))
                
                # Pijl
                pygame.draw.rect(surface, arrow_color, 
                              (pixel_size, mid_y + y_offset*pixel_size, line_length*pixel_size, pixel_size))
                pygame.draw.rect(surface, arrow_color, 
                              (pixel_size, mid_y - (y_offset+1)*pixel_size, line_length*pixel_size, pixel_size))
        else:
            # Linker pijl (wijst naar links)
            mid_y = size // 2
            
            # Teken linker pijl
            for i in range(6):
                # Verticale streep van pijlstaart
                pygame.draw.rect(surface, shadow_color, 
                              (size - pixel_size + shadow_offset, mid_y - 3*pixel_size + i*pixel_size, pixel_size, pixel_size))
                pygame.draw.rect(surface, arrow_color, 
                              (size - pixel_size, mid_y - 3*pixel_size + i*pixel_size, pixel_size, pixel_size))
            
            # Pijlkop als driehoek
            for i in range(1, 7):
                line_length = i
                y_offset = 3 - i
                
                # Schaduw
                pygame.draw.rect(surface, shadow_color, 
                              (size - pixel_size - line_length*pixel_size + shadow_offset, 
                               mid_y + y_offset*pixel_size, line_length*pixel_size, pixel_size))
                pygame.draw.rect(surface, shadow_color, 
                              (size - pixel_size - line_length*pixel_size + shadow_offset, 
                               mid_y - (y_offset+1)*pixel_size, line_length*pixel_size, pixel_size))
                
                # Pijl
                pygame.draw.rect(surface, arrow_color, 
                              (size - pixel_size - line_length*pixel_size, 
                               mid_y + y_offset*pixel_size, line_length*pixel_size, pixel_size))
                pygame.draw.rect(surface, arrow_color, 
                              (size - pixel_size - line_length*pixel_size, 
                               mid_y - (y_offset+1)*pixel_size, line_length*pixel_size, pixel_size))
        
        return surface
    
    def draw_admin_panel(self):
        """Draw the admin panel interface"""
        # Admin panel screen
        self.screen.fill((20, 20, 60))  # Darker background for admin panel
        
        # Draw title with techie style - anti-aliasing UIT voor pixelart effect!
        title_text = "< ADMIN PANEL >"
        title_y = int(30 * self.scale_y)
        
        # Gebruik de aangepaste draw_text functie die de anti-aliasing fout al opvangt
        self.draw_text(title_text, self.title_font, (0, 255, 0), self.resolution[0]/2, title_y, align="center")
        
        # Statische variabelen voor admin formulier
        self.admin_edit_mode = getattr(self, 'admin_edit_mode', False)
        self.admin_edit_index = getattr(self, 'admin_edit_index', -1)  # -1 betekent nieuw spel toevoegen
        self.admin_form_data = getattr(self, 'admin_form_data', {
            'name': '', 
            'description': '', 
            'executable_path': '',
            'image_path': None
        })
        self.admin_active_field = getattr(self, 'admin_active_field', None)
        self.admin_field_text = getattr(self, 'admin_field_text', '')
        
        # Check of we in bewerkingsmodus zijn
        if self.admin_edit_mode:
            # Teken formulier voor bewerken/toevoegen
            return self.draw_admin_edit_form()
        else:
            # Teken lijst van spellen voor beheer
            start_index = self.current_page * self.games_per_page
            end_index = min(start_index + self.games_per_page, len(self.games))
            
            if len(self.games) == 0:
                self.draw_text("Geen spellen beschikbaar.", self.font, WHITE, 
                             self.resolution[0]/2, self.resolution[1]/2, align="center")
                
                # Teken knop om nieuw spel toe te voegen
                add_button_width = int(250 * self.scale_x)
                add_button_height = int(60 * self.scale_y)
                add_button_x = self.resolution[0]/2 - add_button_width/2
                add_button_y = self.resolution[1]/2 + int(80 * self.scale_y)
                
                # Fix: Maak action functie zonder lambda
                add_action = self.start_game_edit
                if self.draw_button("Nieuw Spel Toevoegen", add_button_x, add_button_y, 
                                  add_button_width, add_button_height,
                                  lambda: self.start_game_edit(-1)):
                    print("Nieuw spel toevoegen knop geklikt")
                    return lambda: self.start_game_edit(-1)
            else:
                # Bereken grid dimensies
                grid_margin_x = int(50 * self.scale_x)
                grid_margin_y = int(120 * self.scale_y)  # Ruimte voor titel
                grid_spacing_x = int(20 * self.scale_x)
                grid_spacing_y = int(20 * self.scale_y)
                
                # Gebruik de volledige breedte
                card_width = self.resolution[0] - 2 * grid_margin_x
                card_height = int(100 * self.scale_y)  # Kleinere kaarten in admin panel
                
                # Header
                header_y = grid_margin_y - int(40 * self.scale_y)
                col1_x = grid_margin_x + int(20 * self.scale_x)
                col2_x = grid_margin_x + int(card_width * 0.3)
                col3_x = grid_margin_x + int(card_width * 0.7)
                
                # Teken kolomkoppen
                self.draw_text("Spelnaam", self.font, (0, 255, 0), col1_x, header_y)
                self.draw_text("Bestandspad", self.font, (0, 255, 0), col2_x, header_y)
                self.draw_text("Acties", self.font, (0, 255, 0), col3_x, header_y)
                
                # Teken elk spel in de lijst
                for i in range(start_index, end_index):
                    if i >= len(self.games):
                        break
                        
                    game = self.games[i]
                    y = grid_margin_y + (i - start_index) * (card_height + grid_spacing_y)
                    
                    # Teken achtergrond voor deze rij
                    pygame.draw.rect(self.screen, (40, 40, 70), 
                                   (grid_margin_x, y, card_width, card_height))
                    pygame.draw.rect(self.screen, (0, 180, 0), 
                                   (grid_margin_x, y, card_width, card_height), 1)
                    
                    # Teken naam en executable path
                    name_x = col1_x
                    exe_x = col2_x
                    button_x = col3_x
                    
                    # Verkorte executable path als het te lang is
                    exe_path = game['executable_path']
                    max_path_len = 40
                    if len(exe_path) > max_path_len:
                        exe_path = "..." + exe_path[-max_path_len:]
                    
                    self.draw_text(game['name'], self.font, WHITE, name_x, y + int(15 * self.scale_y))
                    self.draw_text(exe_path, self.small_font, (200, 200, 200), exe_x, y + int(15 * self.scale_y))
                    
                    # Teken bewerk knop
                    edit_button_width = int(120 * self.scale_x)
                    edit_button_height = int(40 * self.scale_y)
                    idx = i  # Sla index op voor gebruik in lambda
                    edit_action = lambda idx=i: self.start_game_edit(idx)
                    if self.draw_button("Bewerken", button_x, y + int(30 * self.scale_y), 
                                      edit_button_width, edit_button_height, edit_action):
                        print(f"Bewerken knop geklikt voor game {i}")
                        return edit_action
                    
                    # Teken verwijder knop
                    delete_button_x = button_x + edit_button_width + int(20 * self.scale_x)
                    delete_action = lambda idx=i: self.delete_game_confirm(idx)
                    if self.draw_button("Verwijderen", delete_button_x, y + int(30 * self.scale_y), 
                                       edit_button_width, edit_button_height, delete_action,
                                       hover_color=(255, 80, 80)):
                        print(f"Verwijderen knop geklikt voor game {i}")
                        return delete_action
                
                # Paginering
                if len(self.games) > self.games_per_page:
                    button_width = int(150 * self.scale_x)
                    button_height = int(50 * self.scale_y)
                    button_y = self.resolution[1] - int(150 * self.scale_y)
                    
                    if self.current_page > 0:
                        prev_button_x = self.resolution[0]/2 - button_width - int(20 * self.scale_x)
                        prev_action = lambda: self.change_page(-1)
                        if self.draw_button("< Vorige", prev_button_x, button_y, 
                                           button_width, button_height, prev_action):
                            print("Vorige pagina knop geklikt")
                            return prev_action
                    
                    if (self.current_page + 1) * self.games_per_page < len(self.games):
                        next_button_x = self.resolution[0]/2 + int(20 * self.scale_x)
                        next_action = lambda: self.change_page(1)
                        if self.draw_button("Volgende >", next_button_x, button_y, 
                                           button_width, button_height, next_action):
                            print("Volgende pagina knop geklikt")
                            return next_action
                
                # Teken knop om nieuw spel toe te voegen
                add_button_width = int(250 * self.scale_x)
                add_button_height = int(60 * self.scale_y)
                add_button_x = self.resolution[0]/2 - add_button_width/2
                add_button_y = self.resolution[1] - int(80 * self.scale_y)
                
                add_action = lambda: self.start_game_edit(-1)
                if self.draw_button("Nieuw Spel Toevoegen", add_button_x, add_button_y, 
                                   add_button_width, add_button_height, add_action):
                    print("Nieuw spel toevoegen knop geklikt")
                    return add_action
        
        # Teken "Back" knop om terug te gaan naar het hoofdscherm
        back_button_width = int(150 * self.scale_x)
        back_button_height = int(50 * self.scale_y)
        back_button_x = int(50 * self.scale_x)
        back_button_y = self.resolution[1] - int(80 * self.scale_y)
        
        back_action = lambda: self.exit_admin_mode()
        if self.draw_button("Terug", back_button_x, back_button_y, 
                           back_button_width, back_button_height, back_action):
            print("Terug naar hoofdmenu knop geklikt")
            return back_action
            
        return None
    
    def draw_admin_edit_form(self):
        """Teken het formulier voor bewerken/toevoegen van spel"""
        form_margin_x = int(100 * self.scale_x)
        form_width = self.resolution[0] - 2 * form_margin_x
        
        # Titel voor het formulier
        is_new = self.admin_edit_index == -1
        form_title = "Nieuw Spel Toevoegen" if is_new else "Spel Bewerken"
        title_y = int(120 * self.scale_y)
        self.draw_text(form_title, self.title_font, (0, 255, 0), self.resolution[0]/2, title_y, align="center")
        
        # Start y-positie voor formuliervelden
        field_y = title_y + int(100 * self.scale_y)
        field_spacing = int(80 * self.scale_y)
        label_width = int(200 * self.scale_x)
        field_width = form_width - label_width - int(40 * self.scale_x)
        field_height = int(50 * self.scale_y)
        
        # Als er een actief veld is en we klikken ergens anders, sla de waarde op
        if self.admin_active_field and pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            field_x = form_margin_x + label_width + int(20 * self.scale_x)
            
            # Controleer voor elk veld of we erbuiten klikken
            fields = ['name', 'description', 'executable_path', 'image_path']
            field_clicked = False
            
            for i, field in enumerate(fields):
                field_y_pos = field_y + i * field_spacing
                field_rect = pygame.Rect(field_x, field_y_pos, field_width, field_height)
                
                if field_rect.collidepoint(mouse_pos):
                    field_clicked = True
                    break
            
            # Als we niet op een veld klikken, sla huidige waarde op en deactiveer veld
            if not field_clicked:
                self.admin_form_data[self.admin_active_field] = self.admin_field_text
                print(f"Veld {self.admin_active_field} opgeslagen: {self.admin_field_text}")
                self.admin_active_field = None
        
        # Helper functie voor formuliervelden
        def draw_form_field(label, field_name, y_pos):
            label_x = form_margin_x
            field_x = form_margin_x + label_width + int(20 * self.scale_x)
            
            # Teken label
            self.draw_text(label, self.font, WHITE, label_x, y_pos + int(10 * self.scale_y))
            
            # Teken invoerveld
            field_bg_color = (60, 60, 100) if self.admin_active_field == field_name else (40, 40, 80)
            pygame.draw.rect(self.screen, field_bg_color, (field_x, y_pos, field_width, field_height))
            pygame.draw.rect(self.screen, (150, 150, 220), (field_x, y_pos, field_width, field_height), 2)
            
            # Teken waarde of huidige invoer
            text_value = self.admin_field_text if self.admin_active_field == field_name else self.admin_form_data.get(field_name, "")
            
            # Zorg ervoor dat text_value altijd een string is
            if text_value is None:
                text_value = ""
            
            # Truncate text als het te lang is
            max_visible_chars = int(field_width / (10 * self.scale_min))
            if len(text_value) > max_visible_chars:
                display_text = "..." + text_value[-max_visible_chars:]
            else:
                display_text = text_value
                
            self.draw_text(display_text, self.font, WHITE, field_x + int(10 * self.scale_x), y_pos + int(10 * self.scale_y))
            
            # Check voor klikken om veld te activeren
            mouse_pos = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            field_rect = pygame.Rect(field_x, y_pos, field_width, field_height)
            
            if field_rect.collidepoint(mouse_pos) and click[0] == 1:
                pygame.time.delay(100)  # Voorkom dubbele klikken
                
                # Als er al een actief veld is, sla de waarde ervan op voordat we veranderen
                if self.admin_active_field and self.admin_active_field != field_name:
                    self.admin_form_data[self.admin_active_field] = self.admin_field_text
                    print(f"Veld {self.admin_active_field} opgeslagen bij selecteren nieuw veld: {self.admin_field_text}")
                
                return field_name  # Geef aan welk veld geactiveerd moet worden
                
            return None
        
        # Teken formuliervelden
        name_field = draw_form_field("Naam:", "name", field_y)
        if name_field:
            activate_func = lambda: self.activate_admin_field(name_field, self.admin_form_data.get('name', ''))
            return activate_func
            
        desc_field = draw_form_field("Beschrijving:", "description", field_y + field_spacing)
        if desc_field:
            activate_func = lambda: self.activate_admin_field(desc_field, self.admin_form_data.get('description', ''))
            return activate_func
            
        exe_field = draw_form_field("Bestandspad:", "executable_path", field_y + 2 * field_spacing)
        if exe_field:
            # Start bestandsverkenner voor exe selectie
            browse_func = lambda: self.launch_file_browser('executable')
            return browse_func
            
        img_field = draw_form_field("Afbeelding:", "image_path", field_y + 3 * field_spacing)
        if img_field:
            # Start bestandsverkenner voor afbeelding selectie
            browse_func = lambda: self.launch_file_browser('image')
            return browse_func
        
        # Teken knoppen
        button_y = field_y + 4 * field_spacing + int(20 * self.scale_y)
        button_width = int(200 * self.scale_x)
        button_height = int(60 * self.scale_y)
        
        # Annuleren knop
        cancel_button_x = self.resolution[0]/2 - button_width - int(20 * self.scale_x)
        cancel_action = lambda: self.cancel_admin_edit()
        if self.draw_button("Annuleren", cancel_button_x, button_y, 
                           button_width, button_height, cancel_action):
            print("Annuleren knop geklikt")
            return cancel_action
            
        # Opslaan knop
        save_button_x = self.resolution[0]/2 + int(20 * self.scale_x)
        save_action = lambda: self.save_admin_edit()
        if self.draw_button("Opslaan", save_button_x, button_y, 
                          button_width, button_height, save_action):
            print("Opslaan knop geklikt")
            return save_action
            
        return None
    
    def start_game_edit(self, index):
        """Start het bewerken van een spel of het toevoegen van een nieuw spel"""
        self.admin_edit_mode = True
        self.admin_edit_index = index
        self.admin_active_field = None
        
        if index == -1:
            # Nieuw spel toevoegen
            self.admin_form_data = {
                'name': '',
                'description': '',
                'executable_path': '',
                'image_path': None
            }
        else:
            # Bestaand spel bewerken
            game = self.games[index]
            self.admin_form_data = {
                'name': game['name'],
                'description': game['description'],
                'executable_path': game['executable_path'],
                'image_path': game['image_path']
            }
    
    def activate_admin_field(self, field_name, current_value):
        """Activeer een tekstveld voor invoer"""
        print(f"activate_admin_field opgeroepen: {field_name} = {current_value}")
        self.admin_active_field = field_name
        self.admin_field_text = current_value
        return None
    
    def launch_file_browser(self, field_type):
        """Start een bestandsverkenner om een bestand te kiezen"""
        print(f"launch_file_browser opgeroepen voor: {field_type}")
        
        # We moeten eerst het juiste veld activeren voordat we de bestandsverkenner openen
        if field_type == 'executable':
            self.admin_active_field = 'executable_path'
            self.admin_field_text = self.admin_form_data.get('executable_path', '')
        elif field_type == 'image':
            self.admin_active_field = 'image_path'
            self.admin_field_text = self.admin_form_data.get('image_path', '') or ""
            
        # Create a separate thread to avoid freezing pygame
        dialog_thread = threading.Thread(target=self._file_browser_thread, args=(field_type,))
        dialog_thread.daemon = True
        dialog_thread.start()
        return None
    
    def _file_browser_thread(self, field_type):
        """Thread-functie voor het starten van bestandsverkenner"""
        root = tk.Tk()
        root.withdraw()
        
        
        if field_type == 'executable':
            file_path = filedialog.askopenfilename(
                title="Selecteer Game Executable",
                filetypes=[("Executable bestanden", "*.exe")]
            )
            if file_path:
                self.admin_form_data['executable_path'] = file_path
                self.admin_field_text = file_path
        elif field_type == 'image':
            file_path = filedialog.askopenfilename(
                title="Selecteer Game Afbeelding",
                filetypes=[("Afbeeldingen", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if file_path:
                # Sla de afbeelding op in de assets map
                saved_path = save_game_image(file_path)
                if saved_path:
                    self.admin_form_data['image_path'] = saved_path
                    self.admin_field_text = saved_path
        
        root.destroy()
    
    def cancel_admin_edit(self):
        """Annuleer bewerking/toevoegen en ga terug naar lijst"""
        print("cancel_admin_edit called")
        # Maak alle actieve velden leeg
        self.admin_edit_mode = False
        self.admin_active_field = None
        return None
    
    def save_admin_edit(self):
        """Sla het bewerkte/nieuwe spel op"""
        print("save_admin_edit called")
        
        # Als er nog een actief veld is, sla de waarde ervan op
        if self.admin_active_field:
            self.admin_form_data[self.admin_active_field] = self.admin_field_text
            print(f"Actief veld {self.admin_active_field} opgeslagen bij opslaan: {self.admin_field_text}")
        
        # Valideer of we alle benodigde gegevens hebben
        if not self.admin_form_data['name']:
            print("Naam is verplicht!")
            return None  # Naam is verplicht
            
        if not self.admin_form_data['executable_path']:
            print("Executable pad is verplicht!")
            return None  # Executable pad is verplicht
            
        # Als er geen afbeelding is geselecteerd, probeer het icoon uit de executable te halen
        if not self.admin_form_data['image_path']:
            print("Geen afbeelding geselecteerd, probeer icoon uit executable te halen")
            icon_path = extract_icon_from_exe(self.admin_form_data['executable_path'])
            self.admin_form_data['image_path'] = icon_path if icon_path else ""
        
        # Maak een nieuw spel object
        game = {
            'name': self.admin_form_data['name'],
            'description': self.admin_form_data['description'] or "Geen beschrijving",
            'executable_path': self.admin_form_data['executable_path'],
            'image_path': self.admin_form_data['image_path'] or ""  # Gebruik lege string in plaats van None
        }
        
        # Update of voeg toe aan lijst
        if self.admin_edit_index == -1:
            # Nieuw spel toevoegen
            print(f"Nieuw spel toegevoegd: {game['name']}")
            self.games.append(game)
        else:
            # Bestaand spel updaten
            print(f"Spel bijgewerkt: {game['name']}")
            self.games[self.admin_edit_index] = game
        
        # Update games.json
        self.games_data['games'] = self.games
        save_games(self.games_data, self.games_file)
        
        # Reset formulier en ga terug naar lijst
        self.admin_edit_mode = False
        self.admin_active_field = None
        return None
    
    def delete_game_confirm(self, index):
        """Verwijder een spel na bevestiging"""
        # Direct verwijdering implementeren
        del self.games[index]
        
        # Update games.json
        self.games_data['games'] = self.games
        save_games(self.games_data, self.games_file)
        
        # Pas huidige pagina aan indien nodig
        max_pages = (len(self.games) - 1) // self.games_per_page + 1
        if self.current_page >= max_pages:
            self.current_page = max(0, max_pages - 1)
    
    def show_password_dialog(self):
        """Show the password dialog to access admin mode"""
        self.password_input = ""
        self.state = "password"
    
    def exit_admin_mode(self):
        """Exit admin mode and return to main screen"""
        self.state = "main"
    
    def activate_password(self, purpose):
        """Activate the password dialog for admin or exit"""
        self.password_input = ""
        self.password_purpose = purpose
        self.state = "password"
    
    def check_password(self):
        """Check if the entered password is correct"""
        if self.password_purpose == 'admin' and self.password_input == self.admin_password:
            self.state = "admin"
            self.admin_edit_mode = False
            self.password_purpose = None
        elif self.password_purpose == 'exit' and self.password_input == self.exit_password:
            self.running = False
        else:
            # Reset password input for retry
            self.password_input = ""
    
    def draw_password_dialog(self):
        """Draw the password dialog for admin access"""
        # Save the background
        bg_copy = self.screen.copy()
        
        # Semi-transparent overlay
        overlay = pygame.Surface(self.resolution, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with alpha
        self.screen.blit(overlay, (0, 0))
        
        # Calculate dialog dimensions
        dialog_width = int(400 * self.scale_x)
        dialog_height = int(200 * self.scale_y)
        dialog_x = (self.resolution[0] - dialog_width) // 2
        dialog_y = (self.resolution[1] - dialog_height) // 2
        
        # Draw dialog background with pixelated border
        pygame.draw.rect(self.screen, (40, 40, 70), (dialog_x, dialog_y, dialog_width, dialog_height))
        
        # Draw pixelated border
        border_color = (0, 255, 0)  # Green border
        border_width = max(2, int(3 * self.scale_min))
        
        # Top border
        pygame.draw.rect(self.screen, border_color, (dialog_x, dialog_y, dialog_width, border_width))
        # Bottom border
        pygame.draw.rect(self.screen, border_color, (dialog_x, dialog_y + dialog_height - border_width, 
                                                  dialog_width, border_width))
        # Left border
        pygame.draw.rect(self.screen, border_color, (dialog_x, dialog_y, border_width, dialog_height))
        # Right border
        pygame.draw.rect(self.screen, border_color, (dialog_x + dialog_width - border_width, dialog_y, 
                                                  border_width, dialog_height))
        
        # Draw title - Anti-aliasing uit voor pixelart effect
        if self.password_purpose == 'admin':
            title = "ADMIN TOEGANG"
        else:
            title = "BEVESTIG AFSLUITEN"
            
        title_y = dialog_y + int(30 * self.scale_y)
        # De draw_text functie vangt anti-aliasing fouten op
        self.draw_text(title, self.font, (0, 255, 0), self.resolution[0] // 2, title_y, align="center", 
                    shadow=True, shadow_color=(0, 100, 0))
        
        # Draw password input field
        input_width = int(300 * self.scale_x)
        input_height = int(40 * self.scale_y)
        input_x = (self.resolution[0] - input_width) // 2
        input_y = dialog_y + int(80 * self.scale_y)
        
        # Draw input box
        pygame.draw.rect(self.screen, (20, 20, 40), (input_x, input_y, input_width, input_height))
        pygame.draw.rect(self.screen, (100, 100, 180), (input_x, input_y, input_width, input_height), 2)
        
        # Draw masked password - pixel effect door anti-aliasing uit te zetten
        masked_text = '*' * len(self.password_input)
        self.draw_text(masked_text, self.font, WHITE, input_x + int(10 * self.scale_x), input_y + int(10 * self.scale_y),
                     shadow=False)  # Geen schaduw voor wachtwoord
        
        # Draw instructions
        if self.password_purpose == 'admin':
            hint_text = "Voer beheerderswachtwoord in"
        else:
            hint_text = "Voer afsluitwachtwoord in"
            
        hint_y = input_y + input_height + int(20 * self.scale_y)
        self.draw_text(hint_text, self.small_font, WHITE, self.resolution[0] // 2, hint_y, align="center",
                     shadow=True, shadow_color=(100, 100, 100))
        
        # Draw buttons
        button_width = int(120 * self.scale_x)
        button_height = int(40 * self.scale_y)
        button_y = dialog_y + dialog_height - int(60 * self.scale_y)
        
        # Cancel button
        cancel_x = dialog_x + int(40 * self.scale_x)
        cancel = self.draw_button("Annuleren", cancel_x, button_y, button_width, button_height, 
                               lambda: setattr(self, 'state', 'main'))
        
        # OK button
        ok_x = dialog_x + dialog_width - button_width - int(40 * self.scale_x)
        ok = self.draw_button("OK", ok_x, button_y, button_width, button_height, 
                           lambda: self.check_password())
        
        return None
        
    def handle_password_mouse(self, mouse_pos):
        """Handle mouse clicks in the password dialog"""
        # Deze functie wordt aangeroepen vanuit handle_events wanneer een muisklik gebeurt in password state
        dialog_width = int(400 * self.scale_x)
        dialog_height = int(200 * self.scale_y)
        dialog_x = (self.resolution[0] - dialog_width) // 2
        dialog_y = (self.resolution[1] - dialog_height) // 2
        
        # Check voor cancel button
        button_width = int(120 * self.scale_x)
        button_height = int(40 * self.scale_y)
        button_y = dialog_y + dialog_height - int(60 * self.scale_y)
        cancel_x = dialog_x + int(40 * self.scale_x)
        
        cancel_rect = pygame.Rect(cancel_x, button_y, button_width, button_height)
        if cancel_rect.collidepoint(mouse_pos):
            self.state = "main"
            return
        
        # Check voor OK button 
        ok_x = dialog_x + dialog_width - button_width - int(40 * self.scale_x)
        ok_rect = pygame.Rect(ok_x, button_y, button_width, button_height)
        
        if ok_rect.collidepoint(mouse_pos):
            self.check_password()
            return
    
    def cancel_password(self):
        self.password_active = False
        self.password_input = ""
    
    def add_game(self):
        # Create a separate thread for tkinter dialog to avoid pygame conflicts
        dialog_thread = threading.Thread(target=self._add_game_dialog)
        dialog_thread.daemon = True
        dialog_thread.start()
        
    def _add_game_dialog(self):
        # This runs in a separate thread to avoid freezing pygame
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Get executable path
        executable_path = filedialog.askopenfilename(
            title="Select Game Executable",
            filetypes=[("Executable files", "*.exe")]
        )
        
        if not executable_path:
            root.destroy()
            return
            
        # Get game name
        game_name = simpledialog.askstring("Game Name", "Enter the name of the game:", parent=root)
        if not game_name:
            root.destroy()
            return
            
        # Get game description
        game_desc = simpledialog.askstring("Game Description", "Enter a description of the game:", parent=root)
        if not game_desc:
            game_desc = "No description provided"
            
        # Ask if user wants to add a custom image
        use_custom_img = simpledialog.askstring("Custom Image", 
                                           "Do you want to use a custom image? (yes/no):", 
                                           parent=root)
        
        saved_image_path = None
        
        # If user wants to add a custom image
        if use_custom_img and use_custom_img.lower() == 'yes':
            image_path = filedialog.askopenfilename(
                title="Select Game Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
            )
            
            # Save the image to the assets folder if selected
            if image_path:
                saved_image_path = save_game_image(image_path)
        else:
            # Try to extract icon from executable
            saved_image_path = extract_icon_from_exe(executable_path)
            
        # Add the new game
        new_game = {
            "name": game_name,
            "description": game_desc,
            "image_path": saved_image_path,
            "executable_path": executable_path
        }
        
        # Update the games list
        self.games.append(new_game)
        self.games_data["games"] = self.games
        save_games(self.games_data, self.games_file)
        
        root.destroy()
    
    def edit_game(self, index):
        # Create a separate thread for tkinter dialog
        dialog_thread = threading.Thread(target=self._edit_game_dialog, args=(index,))
        dialog_thread.daemon = True
        dialog_thread.start()
    
    def _edit_game_dialog(self, index):
        game = self.games[index]
        
        root = tk.Tk()
        root.withdraw()
        
        # Get updated game name
        game_name = simpledialog.askstring("Game Name", "Enter the name of the game:", 
                                       parent=root, initialvalue=game["name"])
        if game_name:
            game["name"] = game_name
            
        # Get updated game description
        game_desc = simpledialog.askstring("Game Description", "Enter a description of the game:", 
                                       parent=root, initialvalue=game["description"])
        if game_desc:
            game["description"] = game_desc
            
        # Ask if user wants to update executable
        update_exe = simpledialog.askstring("Update Executable", 
                                        "Do you want to update the executable path? (yes/no):", 
                                        parent=root)
        if update_exe and update_exe.lower() == 'yes':
            executable_path = filedialog.askopenfilename(
                title="Select Game Executable",
                filetypes=[("Executable files", "*.exe")]
            )
            if executable_path:
                game["executable_path"] = executable_path
                
                # Ask if we should update the icon to match the new executable
                update_icon = simpledialog.askstring("Update Icon", 
                                                "Do you want to update the icon from the new executable? (yes/no):", 
                                                parent=root)
                if update_icon and update_icon.lower() == 'yes':
                    icon_path = extract_icon_from_exe(executable_path)
                    if icon_path:
                        game["image_path"] = icon_path
                
        # Ask if user wants to update image
        update_img = simpledialog.askstring("Update Image", 
                                        "Do you want to update the game image? (yes/no):", 
                                        parent=root)
        if update_img and update_img.lower() == 'yes':
            # Ask for image source
            img_source = simpledialog.askstring("Image Source", 
                                            "Use 'custom' image or 'extract' from exe? (custom/extract):", 
                                            parent=root)
            
            if img_source and img_source.lower() == 'custom':
                image_path = filedialog.askopenfilename(
                    title="Select Game Image",
                    filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
                )
                if image_path:
                    saved_image_path = save_game_image(image_path)
                    if saved_image_path:
                        game["image_path"] = saved_image_path
            
            elif img_source and img_source.lower() == 'extract':
                icon_path = extract_icon_from_exe(game["executable_path"])
                if icon_path:
                    game["image_path"] = icon_path
        
        # Update the games data and save
        self.games_data["games"] = self.games
        save_games(self.games_data, self.games_file)
        
        root.destroy()
        
    def delete_game(self, index):
        # Create a separate thread for confirmation dialog
        dialog_thread = threading.Thread(target=self._delete_game_dialog, args=(index,))
        dialog_thread.daemon = True
        dialog_thread.start()
        
    def _delete_game_dialog(self, index):
        game = self.games[index]
        
        root = tk.Tk()
        root.withdraw()
        
        confirm = simpledialog.askstring("Confirm Delete", 
                                     f"Are you sure you want to delete '{game['name']}'? (yes/no):", 
                                     parent=root)
                                     
        if confirm and confirm.lower() == 'yes':
            del self.games[index]
            self.games_data["games"] = self.games
            save_games(self.games_data, self.games_file)
            
            # Adjust current page if needed
            max_pages = (len(self.games) - 1) // self.games_per_page + 1
            if self.current_page >= max_pages:
                self.current_page = max(0, max_pages - 1)
                
        root.destroy()
    
    def change_page(self, direction):
        self.current_page += direction
        return None
    
    def exit_admin_mode(self):
        self.in_admin_mode = False
        return None
    
    def launch_game(self, executable_path):
        if os.path.exists(executable_path):
            try:
                # Launch the game in a subprocess
                subprocess.Popen([executable_path])
                # Minimize the launcher window (optional)
                pygame.display.iconify()
            except Exception as e:
                print(f"Error launching game: {e}")
        return None
    
    def run(self):
        """Main application loop"""
        self.running = True
        
        while self.running:
            # Cap the frame rate
            self.clock.tick(60)
            
            # Clear screen
            self.screen.fill(self.background_color)
            
            # Handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Handle mouse events and buttons
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        print(f"Mouse click at {event.pos}")
                        if self.state == "password":
                            self.handle_password_mouse(event.pos)
                        elif self.state == "admin" and hasattr(self, 'admin_edit_mode') and self.admin_edit_mode and self.admin_active_field:
                            # Click outside textbox deactivates it
                            mouse_pos = event.pos
                            field_active = False
                            # We don't deactivate hier omdat dat in de draw_admin_edit_form wordt gedaan
                            
                # Handle keyboard events
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "main":
                            self.running = False
                        elif self.state == "admin":
                            if hasattr(self, 'admin_edit_mode') and self.admin_edit_mode:
                                # Als een veld actief is, deactiveer het veld eerst
                                if self.admin_active_field:
                                    # Sla de huidige invoer op in de formuliergegevens
                                    self.admin_form_data[self.admin_active_field] = self.admin_field_text
                                    self.admin_active_field = None
                                else:
                                    # Anders annuleer de bewerking
                                    self.cancel_admin_edit()
                            else:
                                self.state = "main"
                        elif self.state == "password":
                            self.state = "main"
                            
                    # Handle password input
                    elif self.state == "password":
                        if event.key == pygame.K_RETURN:
                            self.check_password()
                        elif event.key == pygame.K_BACKSPACE:
                            self.password_input = self.password_input[:-1]
                        else:
                            # Alleen afdrukbare tekens toevoegen
                            if event.unicode.isprintable():
                                self.password_input += event.unicode
                    
                    # Handle admin text input
                    elif self.state == "admin" and hasattr(self, 'admin_edit_mode') and self.admin_edit_mode and self.admin_active_field:
                        if event.key == pygame.K_RETURN:
                            # Opslaan van huidige veldinhoud
                            self.admin_form_data[self.admin_active_field] = self.admin_field_text
                            print(f"Veld {self.admin_active_field} opgeslagen bij Enter: {self.admin_field_text}")
                            
                            # Ga naar het volgende veld indien beschikbaar
                            fields = ['name', 'description', 'executable_path', 'image_path']
                            if self.admin_active_field in fields:
                                current_index = fields.index(self.admin_active_field)
                                if current_index < len(fields) - 1:
                                    # Ga naar het volgende veld
                                    next_field = fields[current_index + 1]
                                    self.admin_active_field = next_field
                                    self.admin_field_text = self.admin_form_data.get(next_field, '')
                                else:
                                    # Als dit het laatste veld is, deactiveer het veld
                                    self.admin_active_field = None
                            else:
                                # Onbekend veld, deactiveer
                                self.admin_active_field = None
                        elif event.key == pygame.K_BACKSPACE:
                            self.admin_field_text = self.admin_field_text[:-1]
                        else:
                            # Voeg karakter toe aan actieve veld
                            if event.unicode.isprintable():
                                self.admin_field_text += event.unicode
            
            # Draw current state
            if self.state == "main":
                # Main screen
                action = self.draw_main_screen()
                if action:
                    print(f"Main screen action triggered: {action.__name__ if hasattr(action, '__name__') else action}")
                    action()
            elif self.state == "admin":
                # Admin screen
                action = self.draw_admin_panel()
                if action:
                    print(f"Admin panel action triggered: {action.__name__ if hasattr(action, '__name__') else action}")
                    result = action()
                    print(f"Action result: {result}")
            elif self.state == "password":
                # Password dialog
                self.draw_password_dialog()
            
            # Update screen
            pygame.display.flip()
        
        pygame.quit()

# Main entry point
if __name__ == "__main__":
    # Check for command line arguments
    games_file = 'games.json'
    if len(sys.argv) > 1:
        # Check for -g or --games argument
        if sys.argv[1] == '-g' or sys.argv[1] == '--games':
            if len(sys.argv) > 2:
                games_file = sys.argv[2]
                print(f"Loading games from: {games_file}")
        else:
            # Assume the first argument is the games file
            games_file = sys.argv[1]
            print(f"Loading games from: {games_file}")
    
    launcher = GameLauncher(games_file)
    launcher.run()
