const { app, BrowserWindow, globalShortcut, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow;
let config;

function createWindow() {
  // Get screen dimensions to cover taskbar
  const { screen } = require('electron');
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;
  const { x, y } = primaryDisplay.bounds;

  // Create the main window with borderless fullscreen settings
  mainWindow = new BrowserWindow({
    x: x,
    y: y,
    width: primaryDisplay.bounds.width,   // Full screen width
    height: primaryDisplay.bounds.height, // Full screen height (covers taskbar)
    fullscreen: false,
    frame: false,  // Borderless
    resizable: false,
    alwaysOnTop: false,  // Allow games to go on top
    skipTaskbar: false,  // Keep in taskbar for Alt+Tab
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false
    }
  });

  // Don't use maximize() - set exact bounds to cover taskbar
  mainWindow.setBounds({
    x: 0,
    y: 0, 
    width: primaryDisplay.bounds.width,
    height: primaryDisplay.bounds.height
  });
  
  // Load the main HTML file
  mainWindow.loadFile('index.html');
  
  // Allow normal window closing with Alt+F4
  // mainWindow.on('close', (event) => {
  //   // Window can be closed normally
  // });

  // Hide menu bar for cleaner look
  mainWindow.setMenuBarVisibility(false);
}

app.whenReady().then(() => {
  // Load configuration
  loadConfig();
  
  createWindow();

  // Remove all system shortcuts restrictions - allow normal Windows behavior
  // globalShortcut.register('Alt+F4', () => {
  //   // Allow Alt+F4 to close the app normally
  //   return false;
  // });

  // globalShortcut.register('F11', () => {
  //   // Allow F11 to toggle fullscreen normally
  //   return false;
  // });

  // Allow DevTools for debugging
  // globalShortcut.register('CommandOrControl+Shift+I', () => {
  //   // Allow DevTools
  //   return false;
  // });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  // Allow app to quit normally when all windows are closed
  app.quit();
});

// Handle password verification for exit
ipcMain.handle('verify-exit-password', (event, password) => {
  return password === config.security.exitPassword;
});

// Handle password verification for admin panel
ipcMain.handle('verify-admin-password', (event, password) => {
  return password === config.security.adminPassword;
});

// Handle getting configuration
ipcMain.handle('get-config', () => {
  return config;
});

// Handle saving configuration
ipcMain.handle('save-config', (event, newConfig) => {
  config = { ...config, ...newConfig };
  saveConfig();
  return true;
});

// Handle actual app exit
ipcMain.handle('exit-application', () => {
  app.isQuitting = true;
  app.quit();
});

// Handle file browser dialog
ipcMain.handle('browse-for-file', async (event, fileType = 'executable') => {
  try {
    let filters = [];
    let title = 'Selecteer een bestand';
    
    if (fileType === 'executable') {
      filters = [
        { name: 'Executable Files (*.exe)', extensions: ['exe'] },
        { name: 'Batch Files (*.bat, *.cmd)', extensions: ['bat', 'cmd'] },
        { name: 'All Files', extensions: ['*'] }
      ];
      title = 'Selecteer Game Executable';
    } else if (fileType === 'image') {
      filters = [
        { name: 'Image Files', extensions: ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'] },
        { name: 'All Files', extensions: ['*'] }
      ];
      title = 'Selecteer Game Afbeelding';
    }
    
    const result = await dialog.showOpenDialog(mainWindow, {
      title: title,
      buttonLabel: 'Selecteren',
      filters: filters,
      properties: ['openFile']
    });
    
    if (!result.canceled && result.filePaths.length > 0) {
      let selectedPath = result.filePaths[0];
      
      // Handle .lnk files by resolving them
      if (selectedPath.endsWith('.lnk')) {
        try {
          // Try to resolve the shortcut to get the actual target
          const fs = require('fs');
          const path = require('path');
          
          // Read the .lnk file to try to extract target path
          // This is a simplified approach - for production, you might want to use a proper .lnk parser
          const stats = fs.statSync(selectedPath);
          if (stats.isFile()) {
            return {
              path: selectedPath,
              isShortcut: true,
              warning: 'Snelkoppeling geselecteerd. Voor beste resultaten, navigeer naar de installatiemap en selecteer het .exe bestand direct.'
            };
          }        } catch (error) {
          return {
            path: selectedPath,
            isShortcut: true,
            warning: 'Snelkoppeling geselecteerd. Dit kan problemen veroorzaken bij het starten. Probeer het originele .exe bestand te vinden.'
          };
        }
      }
      
      return {
        path: selectedPath,
        isShortcut: false
      };
    }
    return null;
  } catch (error) {
    console.error('Error in file browser:', error);
    return null;
  }
});

// Handle game launching
ipcMain.handle('launch-game', async (event, gamePath) => {
  try {
    const { spawn } = require('child_process');
    
    // Minimize the launcher window to give games priority
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.minimize();
    }
    
    const gameProcess = spawn(gamePath, [], { 
      detached: true,   // Detach so game runs independently 
      stdio: 'ignore'   // Don't capture output to avoid interference
    });
    
    // Unref so launcher doesn't wait for game to close
    gameProcess.unref();
    
    // Don't restore the launcher automatically - let it stay minimized
    // The user can Alt+Tab back to it if needed
    
    return { success: true, message: 'Game gestart!' };
  } catch (error) {
    console.error('Error launching game:', error);
    // Only restore window if game actually failed to start
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.restore();
    }
    return { success: false, message: `Fout bij starten game: ${error.message}` };
  }
});

// Handle bringing launcher back to front
ipcMain.handle('restore-launcher', () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.restore();
    mainWindow.focus();
    mainWindow.show();
  }
});

// Handle minimizing launcher (for games)
ipcMain.handle('minimize-launcher', () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.minimize();
  }
});

// Load configuration from file
function loadConfig() {
  try {
    const configPath = path.join(__dirname, 'config.json');
    const configData = fs.readFileSync(configPath, 'utf8');
    config = JSON.parse(configData);
  } catch (error) {
    console.error('Error loading config:', error);
    // Use default config if file doesn't exist
    config = {
      security: {
        exitPassword: "arcade2025",
        adminPassword: "admin123"
      },
      branding: {
        instituteName: "Haagse Hogeschool",
        projectName: "mKast Arcade Launcher",
        version: "1.0.0"
      }
    };
  }
}

// Save configuration to file
function saveConfig() {
  try {
    const configPath = path.join(__dirname, 'config.json');
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  } catch (error) {
    console.error('Error saving config:', error);
  }
}

app.on('will-quit', () => {
  // Unregister all shortcuts
  globalShortcut.unregisterAll();
});

// Global error handlers to prevent crashes and external dialogs
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  // Don't exit the process, just log the error
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('show-error-notification', {
      title: 'Systeem Fout',
      message: 'Er is een onverwachte fout opgetreden.',
      type: 'error'
    });
  }
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('show-error-notification', {
      title: 'Systeem Fout', 
      message: 'Er is een onverwachte fout opgetreden bij een bewerking.',
      type: 'error'
    });
  }
});
