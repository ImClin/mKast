# Creating Pixelart for mKast Game Launcher

This guide will help you create and use pixelart images and animations for your game launcher.

## Quick Start for Adding Games with Pixelart

1. **Launch the Admin Panel**:
   - Click the "Admin" button at the top of the launcher
   - Enter admin password (default: "admin123")

2. **Add a New Game**:
   - Click "Add New Game" at the bottom of the admin panel
   - Browse to select your game's executable (.exe file)
   - Enter game name and description

3. **Add Custom Pixelart**:
   - When prompted about using a custom image, select "yes"
   - Browse to select your pixelart PNG or animated GIF
   - The system will copy your image to the assets folder

4. **Automatic Icon Extraction**:
   - If you don't have custom pixelart, choose "extract" to get an icon from the .exe file
   - The system will automatically resize and optimize the icon

## Creating Your Own Pixel Art

### Recommended Tools

- **[Aseprite](https://www.aseprite.org/)** - Professional pixel art editor (paid)
- **[Piskel](https://www.piskelapp.com/)** - Free online pixel art editor
- **[GIMP](https://www.gimp.org/)** - Free alternative with pixel art capabilities
- **[LibreSprite](https://libresprite.github.io/)** - Free and open-source Aseprite fork

### Size Guidelines

For best results with the Game Launcher:

- **Static Images**: 128x128 or 256x256 pixels (PNG format)
- **Animated GIFs**: 128x128 to 256x256 pixels with transparent background
- **Aspect Ratio**: Square (1:1) works best with the grid layout
- **File Size**: Keep under 1MB for optimal performance

### Animation Guidelines

The Game Launcher now supports animated GIFs:

- **Frame Rate**: 8-12 frames per second works well
- **Loop Duration**: 1-3 seconds is ideal
- **Transparency**: Use alpha transparency for better integration
- **File Format**: Save as GIF with animation

### Pixel Art Style Tips

1. **Limit Your Palette**: Use 8-16 colors for a classic pixel art look
2. **Use Pixel-Perfect Lines**: Avoid anti-aliasing when drawing
3. **Establish a Consistent Scale**: Keep pixel size consistent within your art
4. **Use Strong Silhouettes**: Make your icons recognizable at small sizes
5. **Add Simple Animation**: Even 2-4 frames of movement adds a lot of character

## Example Process

1. Create a 128x128 canvas in your pixel art tool
2. Sketch your game icon or character
3. Define a limited color palette (8-16 colors)
4. Add pixel details and clean up the edges
5. For animations, create 2-8 frames of movement
6. Export as PNG (static) or GIF (animated)
7. Add to the game launcher using the admin panel

## Optimization Tips

- **Reduce Colors**: Fewer colors means smaller file size
- **Limit Frames**: Only animate what's necessary
- **Crop Efficiently**: Remove unnecessary transparent areas
- **Use Indexed Color**: Save GIFs with indexed colors (128 colors max)

## Inspiration Resources

- [Lospec Palette List](https://lospec.com/palette-list) - Color palettes for pixel art
- [Game-Icons.net](https://game-icons.net/) - Game-themed icon designs
- [OpenGameArt.org](https://opengameart.org/) - Free game assets including pixel art

---

Have fun creating pixel art for your game launcher! These visuals will make your collection more vibrant and personalized.
   - If you select "no" for custom image, the launcher will extract the icon from the .exe file
   - This works as a fallback but custom pixelart usually looks better

## Creating Your Own Pixelart

### Option 1: Using Online Pixelart Tools

1. **Piskel** (Free, online): https://www.piskelapp.com/
   - Create static or animated pixel art
   - Export as PNG or animated GIF
   - Tutorial: https://www.youtube.com/watch?v=Nt1PSQ4Zn-U

2. **Lospec Pixel Editor** (Free, online): https://lospec.com/pixel-editor/
   - Lightweight browser-based editor
   - Great for quick pixelart creation

### Option 2: Desktop Applications

1. **Aseprite** (Paid, but worth it): https://www.aseprite.org/
   - Industry standard for pixel art and animation
   - Full animation timeline
   - Export as PNG or animated GIF

2. **GraphicsGale** (Free): https://graphicsgale.com/us/
   - Specialized for pixel art and animation
   - Windows only

3. **GIMP** (Free): https://www.gimp.org/
   - Set up grid and snap-to-grid for pixel perfect work
   - Use indexed color mode for pixel art style

## Pixelart Best Practices

1. **Use a Limited Color Palette**:
   - 8-16 colors often work best for retro feel
   - Try palettes from classic systems like NES, SNES, Game Boy
   - Find palettes at: https://lospec.com/palette-list

2. **Maintain Consistent Pixel Size**:
   - Don't mix different sized pixels
   - Recommended game icon size: 200x200 pixels

3. **For Animations**:
   - Keep it simple - 4-8 frames is often enough
   - Create keyframes first, then add in-betweens
   - Use animation onion skinning to see adjacent frames
   - Recommended frame rate: 8-12 FPS for retro feel

4. **Pixelart Techniques**:
   - Use "dithering" to create gradients with limited colors
   - Add "outlines" to make objects stand out
   - Use "anti-aliasing" sparingly (or not at all for strict pixel art)

## Example Files

Check the `assets/game_images` folder for example animated GIFs you can use:
- `arcade_anim.gif` - Animated arcade machine
- `space_invader.gif` - Space invader character
- `controller.gif` - Animated game controller

Feel free to use these as placeholders or reference for your own creations!

## Additional Resources

- **Lospec Tutorials**: https://lospec.com/pixel-art-tutorials/
- **Pixelart Subreddit**: https://www.reddit.com/r/PixelArt/
- **Pixel Art Class**: https://pixelartclass.com/ (free tutorials)
