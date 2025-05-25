#!/usr/bin/env python3
"""Main screen for mKast Game Launcher."""

import pygame  # type: ignore  # type: ignore
from src.ui.drawing import WHITE

class MainScreen:
    """Main screen with game grid and navigation."""
    
    def __init__(self, screen, resolution, drawer, image_manager, colors, fonts):
        """Initialize main screen.
        
        Args:
            screen: Pygame display surface
            resolution: Screen resolution tuple (width, height)
            drawer: DrawingHelpers instance
            image_manager: ImageManager instance
            colors: Dictionary with color settings
            fonts: Dictionary with font objects
        """
        self.screen = screen
        self.resolution = resolution
        self.drawer = drawer
        self.image_manager = image_manager
        self.background_color = colors.get('background_color', (10, 10, 40))
        self.header_color = colors.get('header_color', (255, 200, 0))
        self.title_font = fonts['title']
        self.font = fonts['normal']
        self.small_font = fonts['small']
        
        # Scale factors
        self.scale_x = resolution[0] / 1920
        self.scale_y = resolution[1] / 1080
        self.scale_min = min(self.scale_x, self.scale_y)
        
        # Grid layout
        self.grid_columns = 4
        self.grid_rows = 1
          # Pagination
        self.current_index = 0  # Starting index (first game to show)
        self.games_per_screen = self.grid_columns * self.grid_rows  # 4 games per screen
    
    def draw(self, games, admin_password_action, exit_password_action, launch_game_func, change_page_func):
        """Draw the main screen.
        
        Args:
            games: List of game dictionaries
            admin_password_action: Function to call for admin access
            exit_password_action: Function to call for exit
            launch_game_func: Function to call to launch a game
            change_page_func: Function to call to change page
            
        Returns:
            Action function if a button was clicked, None otherwise
        """
        # Clear the screen
        self.screen.fill(self.background_color)
        
        # Draw title - Haagse Hogeschool Game Lab in pixel art style
        try:
            # No anti-aliasing for pixel effect
            haagse_title = self.title_font.render("HAAGSE", False, (184, 207, 8))
            hogeschool_title = self.title_font.render("HOGESCHOOL", False, (184, 207, 8))
            
            game_title = self.title_font.render("GAME", False, WHITE)
            lab_title = self.title_font.render("LAB", False, WHITE)
            
            # Pixel shadow effect for more retro look
            haagse_shadow = self.title_font.render("HAAGSE", False, (100, 120, 0))
            hogeschool_shadow = self.title_font.render("HOGESCHOOL", False, (100, 120, 0))
            game_shadow = self.title_font.render("GAME", False, (100, 100, 100))
            lab_shadow = self.title_font.render("LAB", False, (100, 100, 100))
        except pygame.error:
            # Fallback to anti-aliasing if there are problems with False parameter
            haagse_title = self.title_font.render("HAAGSE", True, (184, 207, 8))
            hogeschool_title = self.title_font.render("HOGESCHOOL", True, (184, 207, 8))
            
            game_title = self.title_font.render("GAME", True, WHITE)
            lab_title = self.title_font.render("LAB", True, WHITE)
            
            # Pixel shadow effect for more retro look
            haagse_shadow = self.title_font.render("HAAGSE", True, (100, 120, 0))
            hogeschool_shadow = self.title_font.render("HOGESCHOOL", True, (100, 120, 0))
            game_shadow = self.title_font.render("GAME", True, (100, 100, 100))
            lab_shadow = self.title_font.render("LAB", True, (100, 100, 100))
        
        # Title positions
        haagse_x = int(50 * self.scale_x)
        haagse_y = int(30 * self.scale_y)
        hogeschool_x = int(50 * self.scale_x)
        hogeschool_y = int(100 * self.scale_y)
        
        game_x = int(self.resolution[0] - 300 * self.scale_x)
        game_y = int(30 * self.scale_y)
        lab_x = int(self.resolution[0] - 300 * self.scale_x)
        lab_y = int(100 * self.scale_y)
        
        # Draw shadows (offset for pixel-like effect)
        shadow_offset = int(3 * self.scale_min)
        self.screen.blit(haagse_shadow, (haagse_x + shadow_offset, haagse_y + shadow_offset))
        self.screen.blit(hogeschool_shadow, (hogeschool_x + shadow_offset, hogeschool_y + shadow_offset))
        self.screen.blit(game_shadow, (game_x + shadow_offset, game_y + shadow_offset))
        self.screen.blit(lab_shadow, (lab_x + shadow_offset, lab_y + shadow_offset))
        
        # Draw titles
        self.screen.blit(haagse_title, (haagse_x, haagse_y))
        self.screen.blit(hogeschool_title, (hogeschool_x, hogeschool_y))
        self.screen.blit(game_title, (game_x, game_y))
        self.screen.blit(lab_title, (lab_x, lab_y))
          # Draw games in grid format
        if len(games) == 0:
            # Show "No games available" message
            self.drawer.draw_text("No games available.", self.font, WHITE, 
                         self.resolution[0]/2, self.resolution[1]/2, align="center")
        else:
            # Calculate grid dimensions
            grid_margin_x = int(50 * self.scale_x)
            grid_margin_y = int(200 * self.scale_y)  # More space for titles
            grid_spacing_x = int(40 * self.scale_x)
            grid_spacing_y = int(20 * self.scale_y)
            
            # Calculate card dimensions
            available_width = self.resolution[0] - (grid_margin_x * 2) - (grid_spacing_x * (self.grid_columns - 1))
            card_width = available_width // self.grid_columns
            card_height = int(400 * self.scale_y)  # Taller cards for pixel art design
              # Draw a card for each game
            end_index = min(self.current_index + self.games_per_screen, len(games))
            for i in range(self.current_index, end_index):
                if i >= len(games):
                    break
                    
                # Calculate grid position
                grid_index = i - self.current_index
                col = grid_index % self.grid_columns
                row = grid_index // self.grid_columns
                
                # Calculate card position
                x = grid_margin_x + col * (card_width + grid_spacing_x)
                y = grid_margin_y + row * (card_height + grid_spacing_y)
                
                game = games[i]
                
                # Text with pixel shadow for game name
                game_name_text = f"GAME {i+1}"
                name_shadow = self.font.render(game_name_text, True, (0, 0, 0))
                game_name = self.font.render(game_name_text, True, WHITE)
                
                # Draw game name
                name_y = y + int(30 * self.scale_y)
                name_x = x + card_width//2 - game_name.get_width()//2
                
                # Shadow effect
                shadow_offset = int(2 * self.scale_min)
                self.screen.blit(name_shadow, (name_x + shadow_offset, name_y + shadow_offset))
                self.screen.blit(game_name, (name_x, name_y))
                
                # Photo frame dimensions with wider pixel border
                frame_margin = int(30 * self.scale_x)
                frame_width = card_width - 2 * frame_margin
                frame_height = frame_width  # Square frame
                frame_x = x + frame_margin
                frame_y = name_y + int(50 * self.scale_y)
                
                # Calculate pixel size based on frame
                pixel_size = max(2, int(frame_width / 32))
                
                # Draw a pixel frame with rounded corners
                blue_color = (0, 100, 210)
                black_stroke = (0, 0, 0)
                
                # First draw a black stroke around the entire frame
                # Draw the base black rectangle for the stroke
                pygame.draw.rect(self.screen, black_stroke, 
                               (frame_x - pixel_size, frame_y - pixel_size, 
                                frame_width + 2*pixel_size, frame_height + 2*pixel_size))
                
                # Make the corners round by removing black pixels
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
                
                # Draw the blue frame (2 pixels thick)
                # Draw the base blue rectangle
                pygame.draw.rect(self.screen, blue_color, 
                               (frame_x, frame_y, frame_width, frame_height))
                
                # Draw top border (2 pixels thick) but with space for rounded corners
                for px in range(3*pixel_size, frame_width-3*pixel_size, pixel_size):
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + px, frame_y, pixel_size, pixel_size))
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + px, frame_y + pixel_size, pixel_size, pixel_size))
                
                # Draw bottom border (2 pixels thick) but with space for rounded corners
                for px in range(3*pixel_size, frame_width-3*pixel_size, pixel_size):
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + px, frame_y + frame_height - 2*pixel_size, pixel_size, pixel_size))
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + px, frame_y + frame_height - pixel_size, pixel_size, pixel_size))
                
                # Draw left border (2 pixels thick) but with space for rounded corners
                for py in range(3*pixel_size, frame_height-3*pixel_size, pixel_size):
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x, frame_y + py, pixel_size, pixel_size))
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + pixel_size, frame_y + py, pixel_size, pixel_size))
                
                # Draw right border (2 pixels thick) but with space for rounded corners
                for py in range(3*pixel_size, frame_height-3*pixel_size, pixel_size):
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + frame_width - 2*pixel_size, frame_y + py, pixel_size, pixel_size))
                    pygame.draw.rect(self.screen, blue_color, 
                                   (frame_x + frame_width - pixel_size, frame_y + py, pixel_size, pixel_size))
                
                # Draw the rounded corners
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
                
                # White interior with rounded corners
                inner_margin = 2 * pixel_size
                pygame.draw.rect(self.screen, WHITE, 
                               (frame_x + inner_margin, frame_y + inner_margin, 
                                frame_width - 2*inner_margin, frame_height - 2*inner_margin))
                
                # Round the white corners
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
                
                # Load and draw game image
                image_path = game.get('image_path')
                img_size = frame_width - 2*inner_margin
                
                if image_path and image_path.lower().endswith('.gif') and image_path in self.image_manager.gif_animations:
                    img = self.image_manager.get_current_gif_frame(image_path)
                    if img is None:
                        img = self.image_manager.load_game_image(image_path, (img_size, img_size))
                else:
                    img = self.image_manager.load_game_image(image_path, (img_size, img_size))
                
                self.screen.blit(img, (frame_x + inner_margin, frame_y + inner_margin))
                
                # Draw "PHOTO" text on the image with pixel shadow
                foto_shadow = self.small_font.render("PHOTO", True, (180, 180, 180))
                foto_label = self.small_font.render("PHOTO", True, (0, 0, 0))
                foto_x = frame_x + frame_width//2 - foto_label.get_width()//2
                foto_y = frame_y + frame_height//2 - foto_label.get_height()//2
                
                # Draw shadow then label
                shadow_offset = int(1 * self.scale_min)
                self.screen.blit(foto_shadow, (foto_x + shadow_offset, foto_y + shadow_offset))
                self.screen.blit(foto_label, (foto_x, foto_y))
                
                # Draw category label with pixel shadow
                cat_y = frame_y + frame_height + int(20 * self.scale_y)
                cat_shadow = self.small_font.render("CATEGORY", True, (100, 100, 100))
                cat_label = self.small_font.render("CATEGORY", True, WHITE)
                cat_x = x + card_width//2 - cat_label.get_width()//2
                
                # Draw shadow then label
                self.screen.blit(cat_shadow, (cat_x + shadow_offset, cat_y + shadow_offset))
                self.screen.blit(cat_label, (cat_x, cat_y))
                
                # Launch game if clicked on (entire card is clickable)
                mouse_pos = pygame.mouse.get_pos()
                click = pygame.mouse.get_pressed()
                
                # Make clickable area slightly smaller than the card for better visual feedback
                card_rect = pygame.Rect(frame_x, frame_y, frame_width, frame_height)
                if card_rect.collidepoint(mouse_pos):
                    # Highlight effect on hover
                    highlight = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    highlight.fill((255, 255, 255, 50))  # Semi-transparent highlight
                    self.screen.blit(highlight, (frame_x, frame_y))
                    
                    if click[0] == 1:
                        pygame.time.delay(100)  # Prevent double-clicks
                        return lambda exe_path=game['executable_path']: launch_game_func(exe_path)
              # Navigation arrows on sides of screen
            if len(games) > self.games_per_screen:
                # Arrow size and position
                arrow_size = int(80 * self.scale_min)  # Larger arrows
                arrow_y = grid_margin_y + card_height // 2 - arrow_size // 2
                arrow_margin = int(20 * self.scale_x)  # More space from edge
                
                # Get mouse info for click detection
                mouse_pos = pygame.mouse.get_pos()
                click = pygame.mouse.get_pressed()
                
                # Left arrow (previous games)
                if self.current_index > 0:
                    # Position left arrow properly inside the screen
                    left_arrow_x = max(arrow_margin, grid_margin_x // 2 - arrow_size // 2)
                    
                    # Draw a pixelated left arrow
                    left_arrow = self.drawer.draw_pixel_arrow(arrow_size, "left")
                    self.screen.blit(left_arrow, (left_arrow_x, arrow_y))
                    
                    # Check for click on left arrow
                    left_arrow_rect = pygame.Rect(left_arrow_x, arrow_y, arrow_size, arrow_size)
                    if left_arrow_rect.collidepoint(mouse_pos) and click[0] == 1:
                        pygame.time.delay(100)  # Prevent double-clicks
                        return lambda: change_page_func(-1)
                
                # Right arrow (next games)
                if self.current_index + self.games_per_screen < len(games):
                    # Position right arrow properly inside the screen
                    right_arrow_x = min(self.resolution[0] - arrow_size - arrow_margin, 
                                      self.resolution[0] - grid_margin_x // 2 - arrow_size // 2)
                    
                    # Draw a pixelated right arrow
                    right_arrow = self.drawer.draw_pixel_arrow(arrow_size, "right")
                    self.screen.blit(right_arrow, (right_arrow_x, arrow_y))
                    
                    # Check for click on right arrow
                    right_arrow_rect = pygame.Rect(right_arrow_x, arrow_y, arrow_size, arrow_size)
                    if right_arrow_rect.collidepoint(mouse_pos) and click[0] == 1:
                        pygame.time.delay(100)  # Prevent double-clicks
                        return lambda: change_page_func(1)
        
        # Admin and Exit buttons in a safe position
        button_width = int(100 * self.scale_x)
        button_height = int(35 * self.scale_y)
        
        # Admin button in top-left corner - extra space from main titles
        admin_button_x = int(haagse_x)  # Align with HAAGSE title
        admin_button_y = int(hogeschool_y + hogeschool_title.get_height() + 20 * self.scale_y)
        admin_action = self.drawer.draw_button("Admin", admin_button_x, admin_button_y, 
                                      button_width, button_height, 
                                      admin_password_action)
        if admin_action:
            return admin_action
          # Exit button in top-right corner - extra space from main titles
        exit_button_x = int(game_x + game_title.get_width() - button_width)  # Align right with GAME title
        exit_button_y = int(lab_y + lab_title.get_height() + 20 * self.scale_y)
        exit_action = self.drawer.draw_button("Exit", exit_button_x, exit_button_y, 
                                     button_width, button_height,
                                     exit_password_action)
        if exit_action:
            return exit_action
            
        return None
        
    def set_current_page(self, page):
        """Set the current page for pagination (legacy method, kept for compatibility).
        
        Args:
            page: Page number
        """
        # Convert page number to an index
        self.current_index = page * self.games_per_screen
        
    def scroll_games(self, direction):
        """Scroll the games by one in the specified direction.
        
        Args:
            direction: 1 for forward (right), -1 for backward (left)
        """
        new_index = self.current_index + direction
        if new_index >= 0:
            self.current_index = new_index
