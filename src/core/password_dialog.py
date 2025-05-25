#!/usr/bin/env python3
"""Password dialog for mKast Game Launcher."""

import pygame  # type: ignore
from src.ui.drawing import WHITE

class PasswordDialog:
    """Password dialog for admin access and exit confirmation."""
    
    def __init__(self, screen, resolution, drawer, fonts):
        """Initialize password dialog.
        
        Args:
            screen: Pygame display surface
            resolution: Screen resolution tuple (width, height)
            drawer: DrawingHelpers instance
            fonts: Dictionary with font objects
        """
        self.screen = screen
        self.resolution = resolution
        self.drawer = drawer
        self.font = fonts['normal']
        self.small_font = fonts['small']
        
        # Scale factors
        self.scale_x = resolution[0] / 1920
        self.scale_y = resolution[1] / 1080
        self.scale_min = min(self.scale_x, self.scale_y)
        
        # Password input
        self.password_input = ""
        self.password_purpose = None  # 'admin' or 'exit'
    
    def draw(self, check_password_func, cancel_func):
        """Draw the password dialog.
        
        Args:
            check_password_func: Function to call to check password
            cancel_func: Function to call to cancel
            
        Returns:
            Action function if a button was clicked, None otherwise
        """
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
        
        # Draw title
        if self.password_purpose == 'admin':
            title = "ADMIN ACCESS"
        else:
            title = "CONFIRM EXIT"
            
        title_y = dialog_y + int(30 * self.scale_y)
        # The draw_text function handles anti-aliasing errors
        self.drawer.draw_text(title, self.font, (0, 255, 0), self.resolution[0] // 2, title_y, align="center", 
                    shadow=True, shadow_color=(0, 100, 0))
        
        # Draw password input field
        input_width = int(300 * self.scale_x)
        input_height = int(40 * self.scale_y)
        input_x = (self.resolution[0] - input_width) // 2
        input_y = dialog_y + int(80 * self.scale_y)
        
        # Draw input box
        pygame.draw.rect(self.screen, (20, 20, 40), (input_x, input_y, input_width, input_height))
        pygame.draw.rect(self.screen, (100, 100, 180), (input_x, input_y, input_width, input_height), 2)
        
        # Draw masked password - pixel effect by turning off anti-aliasing
        masked_text = '*' * len(self.password_input)
        self.drawer.draw_text(masked_text, self.font, WHITE, input_x + int(10 * self.scale_x), input_y + int(10 * self.scale_y),
                     shadow=False)  # No shadow for password
        
        # Draw instructions
        if self.password_purpose == 'admin':
            hint_text = "Enter admin password"
        else:
            hint_text = "Enter exit password"
            
        hint_y = input_y + input_height + int(20 * self.scale_y)
        self.drawer.draw_text(hint_text, self.small_font, WHITE, self.resolution[0] // 2, hint_y, align="center",
                     shadow=True, shadow_color=(100, 100, 100))
        
        # Draw buttons
        button_width = int(120 * self.scale_x)
        button_height = int(40 * self.scale_y)
        button_y = dialog_y + dialog_height - int(60 * self.scale_y)
        
        # Cancel button
        cancel_x = dialog_x + int(40 * self.scale_x)
        cancel = self.drawer.draw_button("Cancel", cancel_x, button_y, button_width, button_height, 
                               cancel_func)
        if cancel:
            return cancel
        
        # OK button
        ok_x = dialog_x + dialog_width - button_width - int(40 * self.scale_x)
        ok = self.drawer.draw_button("OK", ok_x, button_y, button_width, button_height, 
                           check_password_func)
        if ok:
            return ok
        
        return None
    
    def handle_mouse(self, mouse_pos, check_password_func, cancel_func):
        """Handle mouse clicks in the password dialog.
        
        Args:
            mouse_pos: Mouse position tuple (x, y)
            check_password_func: Function to call to check password
            cancel_func: Function to call to cancel
            
        Returns:
            Action function if a button was clicked, None otherwise
        """
        # Calculate dialog dimensions
        dialog_width = int(400 * self.scale_x)
        dialog_height = int(200 * self.scale_y)
        dialog_x = (self.resolution[0] - dialog_width) // 2
        dialog_y = (self.resolution[1] - dialog_height) // 2
        
        # Button dimensions
        button_width = int(120 * self.scale_x)
        button_height = int(40 * self.scale_y)
        button_y = dialog_y + dialog_height - int(60 * self.scale_y)
        
        # Check for cancel button
        cancel_x = dialog_x + int(40 * self.scale_x)
        cancel_rect = pygame.Rect(cancel_x, button_y, button_width, button_height)
        if cancel_rect.collidepoint(mouse_pos):
            return cancel_func
        
        # Check for OK button 
        ok_x = dialog_x + dialog_width - button_width - int(40 * self.scale_x)
        ok_rect = pygame.Rect(ok_x, button_y, button_width, button_height)
        if ok_rect.collidepoint(mouse_pos):
            return check_password_func
            
        return None
    
    def activate(self, purpose):
        """Activate the password dialog with the given purpose.
        
        Args:
            purpose: Purpose ('admin' or 'exit')
        """
        self.set_purpose(purpose)
    
    def set_purpose(self, purpose):
        """Set the purpose of the password dialog.
        
        Args:
            purpose: Purpose ('admin' or 'exit')
        """
        self.password_purpose = purpose
        self.password_input = ""
    
    def get_input(self):
        """Get the password input.
        
        Returns:
            Current password input
        """
        return self.password_input
    
    def add_char(self, char):
        """Add a character to the password input.
        
        Args:
            char: Character to add
        """
        self.password_input += char
    
    def remove_char(self):
        """Remove the last character from the password input."""
        self.password_input = self.password_input[:-1]
