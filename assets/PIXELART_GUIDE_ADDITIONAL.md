# Additional Tips for Using Pixel Art in mKast Game Launcher

## Troubleshooting Common Issues

### Images Not Loading

If your pixel art images aren't loading properly:

1. **Check file format compatibility**: Ensure your files are PNG or GIF
2. **Verify file location**: Images should be in the `assets/game_images/` folder
3. **Check file permissions**: Make sure the files are readable
4. **Try a different image**: Some formats may not be compatible

### Animated GIFs Too Slow/Fast

If your GIF animations aren't running at the right speed:

1. **Check frame duration**: Edit your GIF to adjust timing between frames
2. **Reduce number of frames**: Fewer frames may run more smoothly
3. **Resize the animation**: Smaller GIFs (128x128) perform better

### Icons Not Extracting from EXE Files

If icon extraction isn't working:

1. **Check EXE file permissions**: Make sure the file is accessible
2. **Try a different EXE**: Some executables don't contain proper icons
3. **Use a custom image instead**: Create your own pixel art as an alternative

## Advanced Customization

### Editing the Game Grid Layout

The launcher now uses a grid layout that shows more games per page. You can adjust this in the config:

```json
{
  "grid_columns": 3,
  "grid_rows": 2
}
```

Increase these values to fit more games on screen, but be careful not to make the game cards too small.

### Creating Animated Icon Effects

To make your game icons more dynamic:

1. **Hover Effects**: Create a second GIF for hover state
2. **Selection Animations**: Make a special animation for when a game is selected
3. **Transition Effects**: Add fade-in/out frames for smooth transitions

### Creating Themed Icon Sets

For a consistent look across your game collection:

1. **Use a consistent style/palette** for all game icons
2. **Create a template** with your game's logo in a consistent position
3. **Group by genre** with similar visual elements for each game type

## Performance Tips

For smoother operation with many animated icons:

1. **Limit animated GIFs** to 5-10 games per page
2. **Optimize file sizes** using tools like [EZGIF.com](https://ezgif.com/optimize)
3. **Use fewer colors** in your palette (8-16 colors is ideal)
4. **Reduce frame count** to the minimum needed for the animation

## Community Resources

- Join pixel art communities like [r/PixelArt](https://www.reddit.com/r/PixelArt/) for feedback
- Share your launcher themes with other mKast users
- Contribute your best icons to the project for others to use

---

Remember, great pixel art communicates the essence of your games with minimal detail. Focus on recognizable silhouettes and distinctive colors to make your game library visually engaging!
