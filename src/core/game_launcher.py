#!/usr/bin/env python3
"""Main game launcher class for mKast Game Launcher."""

import os
import sys
import pygame  # type: ignore
import subprocess
from pygame.locals import *  # type: ignore

from src.utils.config import load_config, ensure_assets_directory
from src.utils.game_data import load_games, save_games
from src.utils.icon_extractor import extract_icon_from_exe
from src.ui.fonts import load_pixel_fonts
from src.ui.images import ImageManager
from src.ui.drawing import DrawingHelpers
from src.core.main_screen import MainScreen
from src.core.admin_panel import AdminPanel
from src.core.password_dialog import PasswordDialog

class GameLauncher:
    """Main Game Launcher class that manages the application."""
    
    def __init__(self, games_file="games.json"):
        """Initialize the game launcher.
        
        Args:
            games_file: Path to the games JSON file
        """
        # Initialize pygame
        pygame.init()
        
        # Ensure assets directories exist
        ensure_assets_directory()
        
        # Load configuration
        self.config = load_config()
        
        # Passwords for access control
        self.admin_password = self.config.get("admin_password", "admin123")
        self.exit_password = self.config.get("exit_password", "exit123")
        
        # Get configured resolution or use default
        configured_resolution = self.config.get("resolution", [1920, 1080])
        self.resolution = (configured_resolution[0], configured_resolution[1])
        
        # Calculate scale factors
        self.scale_x = self.resolution[0] / 1920  # Scale factor for x
        self.scale_y = self.resolution[1] / 1080  # Scale factor for y
        self.scale_min = min(self.scale_x, self.scale_y)  # Minimum scale
        
        # Set up fullscreen window
        os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
        fullscreen = self.config.get("fullscreen", True)
        display_mode = pygame.NOFRAME if fullscreen else 0
        self.screen = pygame.display.set_mode(self.resolution, display_mode)
        pygame.display.set_caption("Game Launcher")
        
        # Initialize clock
        self.clock = pygame.time.Clock()
        
        # Get theme colors from config
        theme = self.config.get("theme", {})
        self.colors = {
            'background_color': tuple(theme.get("background_color", [10, 10, 40])),
            'button_color': tuple(theme.get("button_color", [80, 80, 200])),
            'button_hover_color': tuple(theme.get("button_hover_color", [120, 120, 255])),
            'text_color': tuple(theme.get("text_color", [255, 255, 255])),
            'header_color': tuple(theme.get("header_color", [255, 200, 0]))
        }
        
        # Load fonts
        self.fonts = load_pixel_fonts(self.scale_min)
        
        # Initialize image manager
        self.image_manager = ImageManager(self.scale_min)
          # Initialize drawing helpers
        scale_factors = {'x': self.scale_x, 'y': self.scale_y, 'min': self.scale_min}
        self.drawer = DrawingHelpers(self.screen, self.fonts, scale_factors)
        
        # Load games data
        self.games_file = games_file
        self.games_data = load_games(games_file)
        self.games = self.games_data.get("games", [])
        
        # Initialize screens
        self.main_screen = MainScreen(self.screen, self.resolution, self.drawer, 
                                     self.image_manager, self.colors, self.fonts)
        self.admin_panel = AdminPanel(self.screen, self.resolution, self.drawer, self.fonts)
        self.password_dialog = PasswordDialog(self.screen, self.resolution, self.drawer, self.fonts)
        
        # Game launcher state
        self.state = "main"  # main, admin, password
        self.running = True
          # Mouse handling
        self.last_click_time = 0
        self.click_delay = 300  # milliseconds
    
    def run(self):
        """Run the game launcher main loop."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.activate_password('exit')
                  # Handle keyboard input for password dialog
                if event.type == pygame.KEYDOWN and self.state == "password":
                    if event.key == pygame.K_RETURN:
                        self.check_password()
                    elif event.key == pygame.K_ESCAPE:
                        self.cancel_password()
                    elif event.key == pygame.K_BACKSPACE:
                        self.password_dialog.remove_char()
                    elif event.unicode.isprintable():
                        self.password_dialog.add_char(event.unicode)
                
                # Handle keyboard input for admin panel text fields
                elif event.type == pygame.KEYDOWN and self.state == "admin" and self.admin_panel.admin_active_field:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                        # Save the current field and deactivate it
                        field_name = self.admin_panel.admin_active_field
                        field_text = self.admin_panel.admin_field_text
                        self.admin_panel.admin_form_data[field_name] = field_text
                        self.admin_panel.admin_active_field = None
                        print(f"Field {field_name} saved: {field_text}")
                    elif event.key == pygame.K_ESCAPE:
                        # Cancel editing the field
                        self.admin_panel.admin_active_field = None
                    elif event.key == pygame.K_BACKSPACE:
                        # Remove the last character
                        if len(self.admin_panel.admin_field_text) > 0:
                            self.admin_panel.admin_field_text = self.admin_panel.admin_field_text[:-1]
                    elif event.unicode.isprintable():
                        # Add the character to the field
                        self.admin_panel.admin_field_text += event.unicode
            
            # Handle states
            if self.state == "main":
                action = self.main_screen.draw(self.games, 
                                           lambda: self.activate_password('admin'),
                                           lambda: self.activate_password('exit'),                                           self.launch_game,                                           self.change_page)
                if action:
                    action()
            elif self.state == "admin":
                action = self.admin_panel.draw(self.games, self.exit_admin_mode, 
                                           self.start_game_edit, self.delete_game_confirm,
                                           self.change_page, self.delete_game, self.save_admin_edit)
                if action:
                    action()
                
                # Check for escape key to exit admin mode
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    self.exit_admin_mode()
            elif self.state == "password":
                action = self.password_dialog.draw(self.check_password, self.cancel_password)
                if action:
                    action()
            
            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()
        return 0
    
    def activate_password(self, purpose):
        """Activate password dialog.
        
        Args:
            purpose: Purpose of the password check ('admin' or 'exit')
        """
        self.password_dialog.activate(purpose)
        self.state = "password"
    
    def check_password(self):
        """Check the entered password against the stored password."""
        password_input = self.password_dialog.password_input
        
        if self.password_dialog.password_purpose == 'admin' and password_input == self.admin_password:
            self.state = "admin"
            self.admin_panel.admin_edit_mode = False
            self.password_dialog.password_purpose = None
        elif self.password_dialog.password_purpose == 'exit' and password_input == self.exit_password:
            self.running = False
        else:
            # Reset password input for retry
            self.password_dialog.password_input = ""
    
    def cancel_password(self):
        """Cancel password entry and return to previous state."""
        self.state = "main"
    
    def launch_game(self, executable_path):
        """Launch a game executable.
        
        Args:
            executable_path: Path to the game executable
        """
        if os.path.exists(executable_path):
            try:
                # Launch the game in a subprocess
                subprocess.Popen([executable_path])
                # Minimize the launcher window (optional)
                pygame.display.iconify()
            except Exception as e:
                print(f"Error launching game: {e}")
    
    def change_page(self, direction):
        """Change the current page or scroll games for the active screen.
        
        Args:
            direction: Direction to change (1 for next, -1 for previous)
        """
        if self.state == "main":
            # In main screen, implement scrolling one game at a time
            new_index = self.main_screen.current_index + direction
            if 0 <= new_index and new_index + self.main_screen.games_per_screen <= len(self.games) + self.main_screen.games_per_screen - 1:
                self.main_screen.current_index = new_index
        elif self.state == "admin":
            # Keep page-based navigation for admin panel
            new_page = self.admin_panel.current_page + direction
            if 0 <= new_page * self.admin_panel.games_per_page < len(self.games):
                self.admin_panel.set_current_page(new_page)
    
    def exit_admin_mode(self):
        """Exit admin mode and return to main screen."""
        self.state = "main"
    
    def start_game_edit(self, index):
        """Start editing a game or adding a new game.
        
        Args:
            index: Index of the game to edit, or None for a new game
        """
        self.admin_panel.start_game_edit(index, self.games)
    
    def delete_game_confirm(self, index):
        """Show delete confirmation for a game.
        
        Args:            index: Index of the game to delete
        """
        if 0 <= index < len(self.games):
            self.admin_panel.delete_game_confirm(index)

    def save_admin_edit(self):
        """Save game edit from admin panel."""        # Call admin panel's save method to get the game object
        game = self.admin_panel.save_admin_edit()
        
        if game is None:
            # Validation failed, don't save
            return
            
        if self.admin_panel.admin_edit_index != -1:
            # Edit existing game
            self.games[self.admin_panel.admin_edit_index] = game
        else:
            # Add new game
            self.games.append(game)
        
        # Save games to file
        self.games_data["games"] = self.games
        save_games(self.games_data, self.games_file)
        
        # Exit edit mode (already done in admin_panel.save_admin_edit, but keeping for safety)
        self.admin_panel.admin_edit_mode = False
    
    def cancel_admin_edit(self):
        """Cancel game edit from admin panel."""
        self.admin_panel.admin_edit_mode = False
    
    def delete_game(self, index):
        """Delete a game from the list.
        
        Args:
            index: Index of the game to delete
        """
        if 0 <= index < len(self.games):
            del self.games[index]
            
            # Save games to file
            self.games_data["games"] = self.games
            save_games(self.games_data, self.games_file)
        
        # Reset delete confirmation
        self.admin_panel.delete_confirm_index = None
