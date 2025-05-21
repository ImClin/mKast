# mKast Game Launcher - Quick Start Guide

## Overview

mKast is a customizable game launcher with a retro arcade style interface. It allows you to organize and launch your games from a single, attractive interface with support for:

- Automatic game icon extraction from EXE files
- Custom pixelart images and animated GIFs
- Grid layout that adapts to your screen resolution
- Admin mode for adding/editing games
- Password protection to prevent unauthorized exit

## Getting Started

1. **Run the launcher**:
   ```
   python game_launcher.py
   ```

2. **Default passwords**:
   - Admin mode: `admin123`
   - Exit: `exit123`
   
   These can be changed in the `config.json` file.

3. **Adding games**:
   - Click "Admin" and enter the admin password
   - Click "Add New Game"
   - Select a game executable (.exe file)
   - Enter name and description
   - Choose whether to use a custom image or extract the icon from the EXE

4. **Launching games**:
   - Click on any game in the grid
   - Click the "Launch" button to start the game
   - The launcher will minimize while the game is running

## Configuration

The `config.json` file contains settings you can customize:

```json
{
    "admin_password": "admin123",
    "exit_password": "exit123",
    "fullscreen": true,
    "resolution": [1920, 1080],
    "theme": {
        "background_color": [10, 10, 40],
        "button_color": [80, 80, 200],
        "button_hover_color": [120, 120, 255],
        "text_color": [255, 255, 255],
        "header_color": [255, 200, 0]
    }
}
```

- To run in windowed mode, set `"fullscreen": false`
- Customize colors by changing RGB values in `theme`
- Change passwords for security

## Custom Pixelart

For the best visual appeal, consider using custom pixelart images:

1. **Static images**: Use PNG format with a recommended size of 200x200 pixels
2. **Animations**: Use GIF format with 4-8 frames for a retro feel
3. **Detailed guides**:
   - Check `assets/README.md` for instructions on adding images
   - Check `assets/PIXELART_GUIDE.md` for creating your own pixelart

## Demo Content

Try the `games_demo.json` file to see examples of animated GIFs:

```
python game_launcher.py -g games_demo.json
```

Or copy the demo images to your regular games list.

## Tips & Tricks

1. **Custom fonts**: Place a pixel font named `pixel.ttf` in the `assets/fonts` folder
2. **Performance**: If animations are slow, use static PNGs instead of GIFs
3. **Organizing games**: You can edit the `games.json` file directly if you prefer
4. **Screen scaling**: The grid automatically adjusts based on your screen resolution

## Keyboard Shortcuts

- `ESC` key: Exit admin mode (only works when in admin mode)
- All other exits are password-protected for arcade-style security

## Troubleshooting

If you encounter issues:
1. Check that all required Python libraries are installed
2. Verify file paths in your games.json are correct
3. Make sure assets folders exist and have proper permissions

## Credits

The mKast Game Launcher uses:
- Pygame for graphics and UI
- PIL/Pillow for image processing
- Pixel Emulator font by Genshichi Yasui
