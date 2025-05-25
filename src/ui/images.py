#!/usr/bin/env python3
"""Image handling for mKast Game Launcher."""

import os
import pygame  # type: ignore
from PIL import Image, ImageSequence  # type: ignore

class ImageManager:
    """Manager for game images and animations."""
    
    def __init__(self, scale_min):
        """Initialize image manager.
        
        Args:
            scale_min: Minimum scale factor
        """
        self.scale_min = scale_min
        self.game_images = {}  # Cache for loaded images
        self.gif_animations = {}  # Cache for GIF animations
        self.animation_times = {}  # Timing for animations
    
    def create_default_game_image(self):
        """Create a default image for games without an image.
        
        Returns:
            Pygame surface with default image
        """
        # Scale the image size
        image_size = int(200 * self.scale_min)
        surf = pygame.Surface((image_size, image_size))
        surf.fill((60, 60, 100))
        pygame.draw.rect(surf, (100, 100, 160), (int(10 * self.scale_min), int(10 * self.scale_min), 
                                              int(180 * self.scale_min), int(180 * self.scale_min)))
        font = pygame.font.SysFont("consolas", int(32 * self.scale_min))
        text = font.render("No Image", True, (255, 255, 255))
        text_rect = text.get_rect(center=(image_size//2, image_size//2))
        surf.blit(text, text_rect)
        return surf
    
    def load_game_image(self, image_path, size=None):
        """Load a game image with caching.
        
        Args:
            image_path: Path to image file
            size: Size to scale image to (int or tuple)
            
        Returns:
            Pygame surface with loaded image
        """
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
        """Generate a placeholder image when no image is available.
        
        Args:
            size: Size of placeholder (int or tuple)
            
        Returns:
            Pygame surface with placeholder image
        """
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
            
        # Create a pixel art frame
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
        # Top-left corner
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
        
        # Black stroke/border around the blue frame
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
        
        # Fill the main white area
        pygame.draw.rect(surface, (255, 255, 255), (inner_margin, inner_margin, inner_width, inner_height))
        
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
    
    def _load_animated_gif(self, gif_path, size):
        """Load an animated GIF and prepare it for display.
        
        Args:
            gif_path: Path to GIF file
            size: Size to scale frames to
            
        Returns:
            Pygame surface with the first frame (animation updated later)
        """
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
            # Return placeholder image
            return self.get_placeholder_image(size)
    
    def get_current_gif_frame(self, image_path):
        """Get the current frame of an animated GIF based on timing.
        
        Args:
            image_path: Path to GIF file
            
        Returns:
            Pygame surface with current frame
        """
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
        """Update GIF animation and return current frame.
        
        Args:
            image_path: Path to GIF file
            
        Returns:
            Pygame surface with current frame
        """
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
