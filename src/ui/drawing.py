#!/usr/bin/env python3
"""UI drawing utilities for mKast Game Launcher."""

import pygame  # type: ignore

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

class DrawingHelpers:
    """Helper class for common UI drawing operations."""
    
    def __init__(self, screen, fonts, scale_factors):
        """Initialize drawing helpers.
        
        Args:
            screen: Pygame display surface
            fonts: Dictionary with 'title', 'normal', and 'small' font objects
            scale_factors: Dictionary with 'x', 'y', and 'min' scale factors
        """
        self.screen = screen
        self.title_font = fonts['title']
        self.font = fonts['normal']
        self.small_font = fonts['small']
        self.scale_x = scale_factors['x']
        self.scale_y = scale_factors['y']
        self.scale_min = scale_factors['min']

    def draw_text(self, text, font, color, x, y, align="left", shadow=True, shadow_color=None, shadow_offset=None):
        """Draw text with optional shadow and alignment.
        
        Args:
            text: Text string to draw (can include newlines)
            font: Pygame font object
            color: RGB color tuple for text
            x, y: Position coordinates
            align: Text alignment ('left', 'center', or 'right')
            shadow: Whether to draw shadow
            shadow_color: Color for the shadow
            shadow_offset: Offset for shadow
            
        Returns:
            Total height of drawn text
        """
        lines = text.split('\n')
        y_offset = 0
        
        if shadow_color is None:
            shadow_color = (50, 50, 70)  # Default shadow color
            
        if shadow_offset is None:
            shadow_offset = max(1, int(2 * self.scale_min))  # Default shadow offset
        
        # Try pixel-perfect rendering first
        try_pixel_perfect = True
        
        for line in lines:
            # Draw text shadow first if enabled
            if shadow:
                try:
                    if try_pixel_perfect:
                        shadow_surf = font.render(line, False, shadow_color)  # No anti-aliasing for pixel effect
                except pygame.error:
                    # If that fails, use anti-aliasing
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
            
            # Draw main text
            try:
                if try_pixel_perfect:
                    text_surf = font.render(line, False, color)  # No anti-aliasing for pixel art effect
                else:
                    text_surf = font.render(line, True, color)
            except pygame.error:
                # Fallback to anti-aliasing if pixel-perfect doesn't work
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

    def draw_button(self, text, x, y, width, height, action=None, hover_color=None, button_color=None):
        """Draw a button with pixelated borders and hover effect.
        
        Args:
            text: Button text
            x, y: Position coordinates
            width, height: Button dimensions
            action: Function to call when button is clicked
            hover_color: Color when mouse hovers (optional)
            button_color: Base button color (optional)
            
        Returns:
            Action function if clicked, None otherwise
        """
        mouse_pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        if button_color is None:
            button_color = (80, 80, 200)  # Default button color
            
        hover_color = hover_color or (120, 120, 255)  # Default hover color
        
        # Check if mouse is over button
        is_hover = x < mouse_pos[0] < x + width and y < mouse_pos[1] < y + height
        
        # Base pixel size for pixelated borders
        pixel_size = max(2, int(min(width, height) / 30))
        
        # Determine color based on hover status
        color = hover_color if is_hover else button_color
        
        # Draw the base rectangle
        pygame.draw.rect(self.screen, color, (x, y, width, height))
        
        # Pixel border effect (thicker on hover)
        border_color = WHITE
        border_thickness = 2 if is_hover else 1
        
        # Draw top border
        for bx in range(0, width, pixel_size):
            for i in range(border_thickness):
                pygame.draw.rect(self.screen, border_color, 
                               (x + bx, y + i*pixel_size, pixel_size, pixel_size))
        
        # Draw bottom border
        for bx in range(0, width, pixel_size):
            for i in range(border_thickness):
                pygame.draw.rect(self.screen, border_color, 
                               (x + bx, y + height - (i+1)*pixel_size, pixel_size, pixel_size))
        
        # Draw left border
        for by in range(0, height, pixel_size):
            for i in range(border_thickness):
                pygame.draw.rect(self.screen, border_color, 
                               (x + i*pixel_size, y + by, pixel_size, pixel_size))
        
        # Draw right border
        for by in range(0, height, pixel_size):
            for i in range(border_thickness):
                pygame.draw.rect(self.screen, border_color, 
                               (x + width - (i+1)*pixel_size, y + by, pixel_size, pixel_size))
        
        # Draw button text with pixel shadow
        text_color = WHITE  # Always white text
        text_shadow_color = (70, 70, 90) if is_hover else (50, 50, 70)
        
        # Try to use no anti-aliasing for pixel art effect
        try:
            text_shadow = self.font.render(text, False, text_shadow_color)
            text_surf = self.font.render(text, False, text_color)
        except pygame.error:
            # Fallback to anti-aliasing if needed
            text_shadow = self.font.render(text, True, text_shadow_color)
            text_surf = self.font.render(text, True, text_color)
        
        text_rect = text_surf.get_rect(center=(x + width/2, y + height/2))
        shadow_rect = text_shadow.get_rect(center=(x + width/2 + pixel_size, y + height/2 + pixel_size))
        
        # Draw shadow first, then text
        self.screen.blit(text_shadow, shadow_rect)
        self.screen.blit(text_surf, text_rect)
          # Return action if clicked
        if is_hover and click[0] == 1 and action is not None:
            # Add a small delay to prevent multiple clicks
            pygame.time.delay(100)
            return action
        
        return None
        
    def draw_pixel_arrow(self, size, direction="right"):
        """Draw a pixelated arrow.
        
        Args:
            size: Size of the arrow
            direction: "right" or "left"
            
        Returns:
            Pygame surface with the drawn arrow
        """
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))  # Transparent background
        
        # Calculate pixel size for the arrow
        pixel_size = max(3, size // 8)
        
        # Colors for the arrow - brighter and more colorful
        arrow_color = (255, 220, 0)  # Yellow-gold arrow
        outline_color = (0, 0, 0)  # Black outline
        glow_color = (255, 150, 0, 150)  # Orange glow with alpha
          # Determine points for arrow based on direction
        outline_offset = 1
        glow_size = pixel_size * 2
        
        if direction == "right":
            # Right-pointing arrow
            mid_y = size // 2
            
            # Draw glow effect first (behind everything)
            pygame.draw.circle(surface, glow_color, (size // 3, mid_y), size // 3)
            
            # Draw arrow shaft with pixels
            for i in range(6):
                y_pos = mid_y - 3*pixel_size + i*pixel_size
                
                # Black outline
                pygame.draw.rect(surface, outline_color, 
                              (-outline_offset, y_pos-outline_offset, 
                               pixel_size+2*outline_offset, pixel_size+2*outline_offset))
                
                # Arrow shaft
                pygame.draw.rect(surface, arrow_color, 
                              (0, y_pos, pixel_size, pixel_size))
            
            # Arrow head as triangle
            for i in range(1, 7):
                line_length = i
                y_offset = 3 - i
                
                y_top = mid_y - (y_offset+1)*pixel_size
                y_bottom = mid_y + y_offset*pixel_size
                x_start = pixel_size
                
                # Black outline for arrow head top
                pygame.draw.rect(surface, outline_color, 
                              (x_start-outline_offset, y_top-outline_offset, 
                               line_length*pixel_size+2*outline_offset, pixel_size+2*outline_offset))
                
                # Black outline for arrow head bottom
                pygame.draw.rect(surface, outline_color, 
                              (x_start-outline_offset, y_bottom-outline_offset, 
                               line_length*pixel_size+2*outline_offset, pixel_size+2*outline_offset))
                  # Arrow head top and bottom
                pygame.draw.rect(surface, arrow_color, 
                              (x_start, y_top, line_length*pixel_size, pixel_size))
                pygame.draw.rect(surface, arrow_color, 
                              (x_start, y_bottom, line_length*pixel_size, pixel_size))
        else:
            # Left-pointing arrow
            mid_y = size // 2
            
            # Draw glow effect first (behind everything)
            pygame.draw.circle(surface, glow_color, (2*size // 3, mid_y), size // 3)
            
            # Draw left-pointing arrow
            for i in range(6):
                y_pos = mid_y - 3*pixel_size + i*pixel_size
                
                # Black outline
                pygame.draw.rect(surface, outline_color, 
                              (size - pixel_size - outline_offset, y_pos-outline_offset, 
                               pixel_size+2*outline_offset, pixel_size+2*outline_offset))
                
                # Arrow shaft
                pygame.draw.rect(surface, arrow_color, 
                              (size - pixel_size, y_pos, pixel_size, pixel_size))
            
            # Arrow head as triangle
            for i in range(1, 7):
                line_length = i
                y_offset = 3 - i
                
                y_top = mid_y - (y_offset+1)*pixel_size
                y_bottom = mid_y + y_offset*pixel_size
                x_end = size - pixel_size
                
                # Black outline for arrow head top
                pygame.draw.rect(surface, outline_color, 
                              (x_end - line_length*pixel_size-outline_offset, y_top-outline_offset, 
                               line_length*pixel_size+2*outline_offset, pixel_size+2*outline_offset))
                
                # Black outline for arrow head bottom
                pygame.draw.rect(surface, outline_color, 
                              (x_end - line_length*pixel_size-outline_offset, y_bottom-outline_offset, 
                               line_length*pixel_size+2*outline_offset, pixel_size+2*outline_offset))
                
                # Arrow head top and bottom
                pygame.draw.rect(surface, arrow_color, 
                              (x_end - line_length*pixel_size, y_top, line_length*pixel_size, pixel_size))
                pygame.draw.rect(surface, arrow_color, 
                              (x_end - line_length*pixel_size, y_bottom, line_length*pixel_size, pixel_size))
        
        return surface
