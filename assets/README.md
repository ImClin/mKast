# mKast Game Launcher - Adding Pixelart Images and GIFs

This guide will help you add custom pixelart images and animated GIFs to your game launcher.

## File Structure

All game images are stored in the `assets/game_images` folder. The folder structure should look like this:

```
assets/
  ├── fonts/
  ├── game_images/
  │    ├── game1_icon.png
  │    ├── game2_icon.gif
  │    └── ...
  └── images/
```

## Adding Images to Games

There are two ways to add images to your games:

### 1. Automatic Icon Extraction (from EXE)

When adding a new game, you can choose to automatically extract the icon from the executable file. This is the easiest option:

1. Click "Admin" and enter your admin password (default: `admin123`)
2. Click "Add New Game"
3. Select the game executable (`.exe` file)
4. Enter the game name and description
5. When asked "Do you want to use a custom image?", select "no" to automatically extract the icon

### 2. Adding Custom Pixelart Images or GIFs

For better visuals, you can create custom pixelart images or animated GIFs:

1. Create your pixelart image or animation in your preferred software
   - Recommended size: 200x200 pixels (the launcher will scale it appropriately)
   - Supported formats: PNG, JPG, GIF (animated)
   
2. Save your image in a location you can easily find

3. When adding or editing a game:
   - Click "Admin" and enter your password
   - Add a new game or edit an existing one
   - When prompted for an image, select "yes" to use a custom image
   - Browse to and select your pixelart image or GIF

## Creating Pixel Art

Here are some free tools you can use to create pixel art:

- [Piskel](https://www.piskelapp.com/) - Free online pixel art editor
- [Aseprite](https://www.aseprite.org/) - Professional pixel art tool (paid)
- [GIMP](https://www.gimp.org/) - Free image editor with pixel art capabilities
- [LibreSprite](https://github.com/LibreSprite/LibreSprite) - Free/open source fork of Aseprite

## Tips for Good Pixel Art

1. Keep it simple - pixel art relies on simplicity to convey information clearly
2. Use a limited color palette - 8 to 16 colors often work best for a retro feel
3. For animations, use a few frames for a classic retro feel
4. Consider using a transparent background (PNG or GIF with transparency)
5. The classic pixelart style uses no anti-aliasing (no partially transparent pixels)

## Animated GIFs

The launcher supports animated GIFs:

1. Create your animation in a pixel art tool that exports to GIF
2. Keep the file size reasonable (under 1MB) for best performance
3. Use a frame rate of 8-12 frames per second for a classic retro feel
4. Test your animation before adding it to make sure it looks good

## Manual Addition to assets/game_images

You can also add images manually:

1. Create your pixelart image or GIF
2. Save it to the `assets/game_images` folder
3. When editing a game, type the path manually as: `assets/game_images/your_image.png`
