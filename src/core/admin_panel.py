#!/usr/bin/env python3
"""Admin panel for mKast Game Launcher."""

import pygame  # type: ignore
import threading
import tkinter as tk
from tkinter import filedialog
from src.ui.drawing import WHITE
from src.utils.icon_extractor import extract_icon_from_exe

class AdminPanel:
    """Admin panel for managing games."""
    
    def __init__(self, screen, resolution, drawer, fonts):
        """Initialize admin panel.
        
        Args:
            screen: Pygame display surface
            resolution: Screen resolution tuple (width, height)
            drawer: DrawingHelpers instance
            fonts: Dictionary with font objects
        """
        self.screen = screen
        self.resolution = resolution
        self.drawer = drawer
        self.title_font = fonts['title']
        self.font = fonts['normal']
        self.small_font = fonts['small']
        
        # Scale factors
        self.scale_x = resolution[0] / 1920
        self.scale_y = resolution[1] / 1080
        self.scale_min = min(self.scale_x, self.scale_y)
          # Pagination
        self.current_page = 0
        self.games_per_page = 8  # Games per page in admin view
        
        # Admin edit mode
        self.admin_edit_mode = False
        self.admin_edit_index = -1  # -1 means add new game
        self.admin_form_data = {
            'name': '',
            'description': '',
            'executable_path': '',
            'image_path': None
        }
        self.admin_active_field = None
        self.admin_field_text = ''
        
        # Delete confirmation
        self.delete_confirm_index = None

    def draw(self, games, exit_admin_func, start_game_edit_func, delete_game_confirm_func, change_page_func, delete_game_func=None, save_admin_edit_func=None):
        """Draw the admin panel.
        
        Args:
            games: List of game dictionaries
            exit_admin_func: Function to call to exit admin mode
            start_game_edit_func: Function to call to start editing a game
            delete_game_confirm_func: Function to call to confirm game deletion
            change_page_func: Function to call to change page
            delete_game_func: Function to call to actually delete the game
            save_admin_edit_func: Function to call to save game edits
            
        Returns:
            Action function if a button was clicked, None otherwise
        """
        # Admin panel background
        self.screen.fill((20, 20, 60))  # Darker background for admin panel
        
        # Draw title with techie style - no anti-aliasing for pixel art effect!
        title_text = "< ADMIN PANEL >"
        title_y = int(30 * self.scale_y)
        
        # Use the custom draw_text function that already handles anti-aliasing errors
        self.drawer.draw_text(title_text, self.title_font, (0, 255, 0), self.resolution[0]/2, title_y, align="center")
          # Check if we're in edit mode
        if self.admin_edit_mode:
            # Draw form for editing/adding
            return self.draw_admin_edit_form(save_admin_edit_func)
          # If we have a delete confirmation dialog active, draw it
        if self.delete_confirm_index is not None:
            return self.draw_delete_confirmation(games, delete_game_func or delete_game_confirm_func)
        else:
            # Draw list of games for management
            start_index = self.current_page * self.games_per_page
            end_index = min(start_index + self.games_per_page, len(games))
            
            if len(games) == 0:
                self.drawer.draw_text("No games available.", self.font, WHITE, 
                             self.resolution[0]/2, self.resolution[1]/2, align="center")
                
                # Draw button to add new game
                add_button_width = int(250 * self.scale_x)
                add_button_height = int(60 * self.scale_y)
                add_button_x = self.resolution[0]/2 - add_button_width/2
                add_button_y = self.resolution[1]/2 + int(80 * self.scale_y)
                
                add_action = self.drawer.draw_button("Add New Game", add_button_x, add_button_y, 
                                  add_button_width, add_button_height,
                                  lambda: start_game_edit_func(-1))
                if add_action:
                    return add_action
            else:
                # Calculate grid dimensions
                grid_margin_x = int(50 * self.scale_x)
                grid_margin_y = int(120 * self.scale_y)  # Space for title
                grid_spacing_x = int(20 * self.scale_x)
                grid_spacing_y = int(20 * self.scale_y)
                
                # Use full width
                card_width = self.resolution[0] - 2 * grid_margin_x
                card_height = int(100 * self.scale_y)  # Smaller cards in admin panel
                
                # Header
                header_y = grid_margin_y - int(40 * self.scale_y)
                col1_x = grid_margin_x + int(20 * self.scale_x)
                col2_x = grid_margin_x + int(card_width * 0.3)
                col3_x = grid_margin_x + int(card_width * 0.7)
                
                # Draw column headers
                self.drawer.draw_text("Game Name", self.font, (0, 255, 0), col1_x, header_y)
                self.drawer.draw_text("File Path", self.font, (0, 255, 0), col2_x, header_y)
                self.drawer.draw_text("Actions", self.font, (0, 255, 0), col3_x, header_y)
                
                # Draw each game in the list
                for i in range(start_index, end_index):
                    if i >= len(games):
                        break
                        
                    game = games[i]
                    y = grid_margin_y + (i - start_index) * (card_height + grid_spacing_y)
                    
                    # Draw background for this row
                    pygame.draw.rect(self.screen, (40, 40, 70), 
                                   (grid_margin_x, y, card_width, card_height))
                    pygame.draw.rect(self.screen, (0, 180, 0), 
                                   (grid_margin_x, y, card_width, card_height), 1)
                    
                    # Draw name and executable path
                    name_x = col1_x
                    exe_x = col2_x
                    button_x = col3_x
                    
                    # Shortened executable path if it's too long
                    exe_path = game['executable_path']
                    max_path_len = 40
                    if len(exe_path) > max_path_len:
                        exe_path = "..." + exe_path[-max_path_len:]
                    
                    self.drawer.draw_text(game['name'], self.font, WHITE, name_x, y + int(15 * self.scale_y))
                    self.drawer.draw_text(exe_path, self.small_font, (200, 200, 200), exe_x, y + int(15 * self.scale_y))
                    
                    # Draw edit button
                    edit_button_width = int(120 * self.scale_x)
                    edit_button_height = int(40 * self.scale_y)
                    edit_action = self.drawer.draw_button("Edit", button_x, y + int(30 * self.scale_y), 
                                      edit_button_width, edit_button_height, 
                                      lambda idx=i: start_game_edit_func(idx))
                    if edit_action:
                        return edit_action
                    
                    # Draw delete button
                    delete_button_x = button_x + edit_button_width + int(20 * self.scale_x)
                    delete_action = self.drawer.draw_button("Delete", delete_button_x, y + int(30 * self.scale_y), 
                                       edit_button_width, edit_button_height, 
                                       lambda idx=i: delete_game_confirm_func(idx),
                                       hover_color=(255, 80, 80))
                    if delete_action:
                        return delete_action
                
                # Pagination
                if len(games) > self.games_per_page:
                    button_width = int(150 * self.scale_x)
                    button_height = int(50 * self.scale_y)
                    button_y = self.resolution[1] - int(150 * self.scale_y)
                    
                    if self.current_page > 0:
                        prev_button_x = self.resolution[0]/2 - button_width - int(20 * self.scale_x)
                        prev_action = self.drawer.draw_button("< Previous", prev_button_x, button_y, 
                                           button_width, button_height, 
                                           lambda: change_page_func(-1))
                        if prev_action:
                            return prev_action
                    
                    if (self.current_page + 1) * self.games_per_page < len(games):
                        next_button_x = self.resolution[0]/2 + int(20 * self.scale_x)
                        next_action = self.drawer.draw_button("Next >", next_button_x, button_y, 
                                           button_width, button_height, 
                                           lambda: change_page_func(1))
                        if next_action:
                            return next_action
                
                # Draw button to add new game
                add_button_width = int(250 * self.scale_x)
                add_button_height = int(60 * self.scale_y)
                add_button_x = self.resolution[0]/2 - add_button_width/2
                add_button_y = self.resolution[1] - int(80 * self.scale_y)
                
                add_action = self.drawer.draw_button("Add New Game", add_button_x, add_button_y, 
                                   add_button_width, add_button_height, 
                                   lambda: start_game_edit_func(-1))
                if add_action:
                    return add_action
        
        # Draw "Back" button to return to main screen
        back_button_width = int(150 * self.scale_x)
        back_button_height = int(50 * self.scale_y)
        back_button_x = int(50 * self.scale_x)
        back_button_y = self.resolution[1] - int(80 * self.scale_y)
        
        back_action = self.drawer.draw_button("Back", back_button_x, back_button_y, 
                           back_button_width, back_button_height, 
                           exit_admin_func)
        if back_action:
            return back_action
            
        return None

    def draw_admin_edit_form(self, save_admin_edit_func=None):
        """Draw the form for editing/adding a game.
        
        Args:
            save_admin_edit_func: Function to call to save game edits
        
        Returns:
            Action function if a button was clicked, None otherwise
        """
        form_margin_x = int(100 * self.scale_x)
        form_width = self.resolution[0] - 2 * form_margin_x
        
        # Title for the form
        is_new = self.admin_edit_index == -1
        form_title = "Add New Game" if is_new else "Edit Game"
        title_y = int(120 * self.scale_y)
        self.drawer.draw_text(form_title, self.title_font, (0, 255, 0), self.resolution[0]/2, title_y, align="center")
        
        # Start y-position for form fields
        field_y = title_y + int(100 * self.scale_y)
        field_spacing = int(80 * self.scale_y)
        label_width = int(200 * self.scale_x)
        field_width = form_width - label_width - int(40 * self.scale_x)
        field_height = int(50 * self.scale_y)
        
        # If there's an active field and we click somewhere else, save the value
        if self.admin_active_field and pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            field_x = form_margin_x + label_width + int(20 * self.scale_x)
            
            # Check for each field if we're clicking outside
            fields = ['name', 'description', 'executable_path', 'image_path']
            field_clicked = False
            
            for i, field in enumerate(fields):
                field_y_pos = field_y + i * field_spacing
                field_rect = pygame.Rect(field_x, field_y_pos, field_width, field_height)
                
                if field_rect.collidepoint(mouse_pos):
                    field_clicked = True
                    break
            
            # If we're not clicking on a field, save current value and deactivate field
            if not field_clicked:
                self.admin_form_data[self.admin_active_field] = self.admin_field_text
                print(f"Field {self.admin_active_field} saved: {self.admin_field_text}")
                self.admin_active_field = None
        
        # Helper function for form fields
        def draw_form_field(label, field_name, y_pos):
            label_x = form_margin_x
            field_x = form_margin_x + label_width + int(20 * self.scale_x)
            
            # Draw label
            self.drawer.draw_text(label, self.font, WHITE, label_x, y_pos + int(10 * self.scale_y))
            
            # Draw input field
            field_bg_color = (60, 60, 100) if self.admin_active_field == field_name else (40, 40, 80)
            pygame.draw.rect(self.screen, field_bg_color, (field_x, y_pos, field_width, field_height))
            pygame.draw.rect(self.screen, (150, 150, 220), (field_x, y_pos, field_width, field_height), 2)
            
            # Draw value or current input
            text_value = self.admin_field_text if self.admin_active_field == field_name else self.admin_form_data.get(field_name, "")
            
            # Make sure text_value is always a string
            if text_value is None:
                text_value = ""
            
            # Truncate text if it's too long
            max_visible_chars = int(field_width / (10 * self.scale_min))
            if len(text_value) > max_visible_chars:
                display_text = "..." + text_value[-max_visible_chars:]
            else:
                display_text = text_value
                
            self.drawer.draw_text(display_text, self.font, WHITE, field_x + int(10 * self.scale_x), y_pos + int(10 * self.scale_y))
            
            # Check for clicking to activate field
            mouse_pos = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            field_rect = pygame.Rect(field_x, y_pos, field_width, field_height)
            
            if field_rect.collidepoint(mouse_pos) and click[0] == 1:
                pygame.time.delay(100)  # Prevent double-clicks
                
                # If there's already an active field, save its value before changing
                if self.admin_active_field and self.admin_active_field != field_name:
                    self.admin_form_data[self.admin_active_field] = self.admin_field_text
                    print(f"Field {self.admin_active_field} saved when selecting new field: {self.admin_field_text}")
                
                return field_name  # Indicate which field should be activated
                
            return None
        
        # Draw form fields and handle field activation
        # Each field returns a lambda that will activate that field when called
        name_field = draw_form_field("Name:", "name", field_y)
        if name_field:
            return lambda: self.activate_admin_field(name_field, self.admin_form_data.get('name', ''))
            
        desc_field = draw_form_field("Description:", "description", field_y + field_spacing)
        if desc_field:
            return lambda: self.activate_admin_field(desc_field, self.admin_form_data.get('description', ''))
            
        exe_field = draw_form_field("File Path:", "executable_path", field_y + 2 * field_spacing)
        if exe_field:
            # Start file browser for exe selection
            return lambda: self.launch_file_browser('executable')
            
        img_field = draw_form_field("Image:", "image_path", field_y + 3 * field_spacing)
        if img_field:
            # Start file browser for image selection
            return lambda: self.launch_file_browser('image')
        
        # Draw buttons
        button_y = field_y + 4 * field_spacing + int(20 * self.scale_y)
        button_width = int(200 * self.scale_x)
        button_height = int(60 * self.scale_y)
        
        # Cancel button
        cancel_button_x = self.resolution[0]/2 - button_width - int(20 * self.scale_x)
        cancel_action = self.drawer.draw_button("Cancel", cancel_button_x, button_y, 
                           button_width, button_height, 
                           lambda: self.cancel_admin_edit())
        if cancel_action:
            return cancel_action
              # Save button
        save_button_x = self.resolution[0]/2 + int(20 * self.scale_x)
        save_action = self.drawer.draw_button("Save", save_button_x, button_y, 
                          button_width, button_height, 
                          save_admin_edit_func or (lambda: self.save_admin_edit()))
        if save_action:
            return save_action
            
        return None
    
    def draw_delete_confirmation(self, games, delete_game_func):
        """Draw the delete confirmation dialog.
        
        Args:
            games: List of game dictionaries
            delete_game_func: Function to call to delete the game
            
        Returns:
            Action function if a button was clicked, None otherwise
        """
        index = self.delete_confirm_index
        if index is None or index < 0 or index >= len(games):
            self.delete_confirm_index = None
            return None
            
        game = games[index]
        
        # Semi-transparent overlay
        overlay = pygame.Surface(self.resolution, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with alpha
        self.screen.blit(overlay, (0, 0))
        
        # Calculate dialog dimensions
        dialog_width = int(500 * self.scale_x)
        dialog_height = int(250 * self.scale_y)
        dialog_x = (self.resolution[0] - dialog_width) // 2
        dialog_y = (self.resolution[1] - dialog_height) // 2
        
        # Draw dialog background with pixelated border
        pygame.draw.rect(self.screen, (40, 40, 70), (dialog_x, dialog_y, dialog_width, dialog_height))
        
        # Draw pixelated border
        border_color = (255, 50, 50)  # Red border for delete confirmation
        border_width = max(2, int(3 * self.scale_min))
        
        # Draw borders
        pygame.draw.rect(self.screen, border_color, (dialog_x, dialog_y, dialog_width, border_width))
        pygame.draw.rect(self.screen, border_color, (dialog_x, dialog_y + dialog_height - border_width, dialog_width, border_width))
        pygame.draw.rect(self.screen, border_color, (dialog_x, dialog_y, border_width, dialog_height))
        pygame.draw.rect(self.screen, border_color, (dialog_x + dialog_width - border_width, dialog_y, border_width, dialog_height))
        
        # Draw title
        title = "DELETE GAME"
        title_y = dialog_y + int(30 * self.scale_y)
        self.drawer.draw_text(title, self.font, (255, 50, 50), self.resolution[0] // 2, title_y, align="center", 
                      shadow=True, shadow_color=(100, 0, 0))
        
        # Draw confirmation message
        message = f"Are you sure you want to delete the game:"
        game_name = f"\"{game['name']}\""
        
        message_y = dialog_y + int(80 * self.scale_y)
        game_y = dialog_y + int(120 * self.scale_y)
        
        self.drawer.draw_text(message, self.font, WHITE, self.resolution[0] // 2, message_y, align="center")
        self.drawer.draw_text(game_name, self.font, (255, 255, 0), self.resolution[0] // 2, game_y, align="center", 
                      shadow=True, shadow_color=(100, 100, 0))
        
        # Draw buttons
        button_width = int(150 * self.scale_x)
        button_height = int(50 * self.scale_y)
        button_y = dialog_y + dialog_height - int(80 * self.scale_y)
        
        # Cancel button
        cancel_x = dialog_x + int(50 * self.scale_x)
        cancel_action = self.drawer.draw_button("Cancel", cancel_x, button_y, button_width, button_height, 
                               lambda: self.cancel_delete())
        if cancel_action:
            return cancel_action
        
        # Delete button
        delete_x = dialog_x + dialog_width - button_width - int(50 * self.scale_x)
        delete_action = self.drawer.draw_button("Delete", delete_x, button_y, button_width, button_height, 
                               lambda: self.confirm_delete(delete_game_func),
                               hover_color=(255, 0, 0))
        if delete_action:
            return delete_action
            
        return None
        
    def cancel_delete(self):
        """Cancel the delete confirmation.
        
        Returns:
            None
        """
        self.delete_confirm_index = None
        return None
        
    def confirm_delete(self, delete_game_func):
        """Confirm the deletion of a game.
        
        Args:
            delete_game_func: Function to call to delete the game
            
        Returns:
            None
        """
        # Call the delete function with the index
        if self.delete_confirm_index is not None:
            delete_game_func(self.delete_confirm_index)
        
        # Reset delete confirmation
        self.delete_confirm_index = None
        return None
    
    def activate_admin_field(self, field_name, current_value):
        """Activate a text field for input.
        
        Args:
            field_name: Name of the field to activate
            current_value: Current value of the field
        """
        print(f"activate_admin_field called: {field_name} = {current_value}")
        self.admin_active_field = field_name
        self.admin_field_text = current_value
        return None
    
    def launch_file_browser(self, field_type):
        """Launch a file browser to choose a file.
        
        Args:
            field_type: Type of file to browse for ('executable' or 'image')
        """
        print(f"launch_file_browser called for: {field_type}")
        
        # We need to activate the right field before opening the file browser
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
        """Run file browser in a separate thread to avoid freezing pygame.
        
        Args:
            field_type: Type of file to browse for ('executable' or 'image')
        """
        # Create a root window but hide it
        root = tk.Tk()
        root.withdraw()
        
        try:
            if field_type == 'executable':
                # File browser for executables
                file_path = filedialog.askopenfilename(
                    title="Select Executable",
                    filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
                )
                
                if file_path:
                    self.admin_form_data['executable_path'] = file_path
                    
            elif field_type == 'image':
                # File browser for images
                file_path = filedialog.askopenfilename(
                    title="Select Image",
                    filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
                )
                
                if file_path:
                    self.admin_form_data['image_path'] = file_path
        finally:
            # Make sure to destroy the root window
            root.destroy()
        
        # Clear active field
        self.admin_active_field = None
    
    def cancel_admin_edit(self):
        """Cancel editing/adding and return to list.
        
        Returns:
            None        """
        print("cancel_admin_edit called")
        # Clear all active fields
        self.admin_edit_mode = False
        self.admin_active_field = None
        return None

    def save_admin_edit(self):
        """Save the edited/new game.
        
        Returns:
            dict: The created game object, or None if validation failed
        """
        print("save_admin_edit called")
        
        # If there's still an active field, save its value
        if self.admin_active_field:
            self.admin_form_data[self.admin_active_field] = self.admin_field_text
            print(f"Active field {self.admin_active_field} saved when saving: {self.admin_field_text}")
        
        # Validate that we have all required data
        if not self.admin_form_data['name']:
            print("Name is required!")
            return None  # Name is required
            
        if not self.admin_form_data['executable_path']:
            print("Executable path is required!")
            return None  # Executable path is required
            
        # If no image is selected, try to extract icon from executable
        if not self.admin_form_data['image_path']:
            print("No image selected, trying to extract icon from executable")
            icon_path = extract_icon_from_exe(self.admin_form_data['executable_path'])
            self.admin_form_data['image_path'] = icon_path if icon_path else ""
        
        # Create a new game object
        game = {
            'name': self.admin_form_data['name'],
            'description': self.admin_form_data['description'] or "No description",
            'executable_path': self.admin_form_data['executable_path'],
            'image_path': self.admin_form_data['image_path'] or ""  # Use empty string instead of None
        }
        
        # Store the game object for GameLauncher to access
        self.edited_game = game
        
        # Reset form and return to list
        self.admin_edit_mode = False
        
        return game
        self.admin_active_field = None
        return None
    
    def confirm_delete_game(self, delete_game_confirm_func):
        """Confirm deletion of a game.
        
        Args:
            delete_game_confirm_func: Function to call to confirm game deletion
        """
        if self.delete_confirm_index is not None:
            delete_game_confirm_func(self.delete_confirm_index)
            self.delete_confirm_index = None
    
    def cancel_delete_confirmation(self):
        """Cancel the delete confirmation dialog."""
        self.delete_confirm_index = None
        
    def set_current_page(self, page):
        """Set the current page for pagination.
        
        Args:
            page: Page number
        """
        self.current_page = page
        
    def start_game_edit(self, index, games):
        """Start editing a game or adding a new game.
        
        Args:
            index: Index of the game to edit, or -1 for a new game
            games: List of games
        """
        game_data = None
        if index >= 0 and index < len(games):
            game_data = games[index]
        
        self.set_edit_mode(True, index, game_data)
    
    def delete_game_confirm(self, index):
        """Show delete confirmation for a game.
        
        Args:
            index: Index of the game to delete
        """
        # Set the index of the game to delete
        self.delete_confirm_index = index
        print(f"delete_game_confirm called for index: {index}")
        return None
    
    def set_edit_mode(self, is_edit_mode, index=-1, game_data=None):
        """Set edit mode for admin panel.
        
        Args:
            is_edit_mode: Whether to enable edit mode
            index: Index of game to edit (-1 for new game)
            game_data: Game data to edit (for existing game)
        """
        self.admin_edit_mode = is_edit_mode
        self.admin_edit_index = index
        
        if is_edit_mode:
            if index == -1:
                # Adding new game
                self.admin_form_data = {
                    'name': '',
                    'description': '',
                    'executable_path': '',
                    'image_path': None
                }
            else:
                # Editing existing game
                self.admin_form_data = {
                    'name': game_data['name'],
                    'description': game_data['description'],
                    'executable_path': game_data['executable_path'],
                    'image_path': game_data['image_path']
                }
            
            self.admin_active_field = None
