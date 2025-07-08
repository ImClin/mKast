// Main Renderer - Modular Architecture
// Import all necessary Electron APIs
const { ipcRenderer } = require('electron');
const path = require('path');

// Debug mode - set to true to see all errors in console (turn off for production)
const DEBUG_MODE = false;

// Global module instances
let gameManager;
let uiManager;
let soundManager;
let adminPanel;
let gameLauncher;
let keyboardHandler;
let configManager;

// Global state (minimal)
let config = null;

// Enhanced error logging for debugging
function logError(context, error, extra = {}) {
    console.error(`[${context}]`, error, extra);
    
    if (DEBUG_MODE && error) {
        if (uiManager) {
            uiManager.showNotification(
                `Debug: ${context}`,
                `Error: ${error.message || error.toString()}`,
                'info',
                8000
            );
        }
    }
}

// Global error boundary for async operations
async function withErrorBoundary(asyncFunction, context = 'AsyncOperation') {
    try {
        return await asyncFunction();
    } catch (error) {
        logError(context, error);
        
        // Show user-friendly error message
        const userMessage = getUserFriendlyErrorMessage(error);
        if (uiManager) {
            uiManager.showNotification(
                'Fout Opgetreden',
                userMessage,
                'error',
                5000
            );
        }
        
        // Re-throw for caller handling if needed
        throw error;
    }
}

// Convert technical errors to user-friendly messages
function getUserFriendlyErrorMessage(error) {
    const message = error.message?.toLowerCase() || '';
    
    if (message.includes('enoent') || message.includes('file not found')) {
        return 'Bestand niet gevonden. Controleer of het spel correct is geïnstalleerd.';
    }
    if (message.includes('eacces') || message.includes('permission')) {
        return 'Onvoldoende rechten. Probeer de applicatie als administrator uit te voeren.';
    }
    if (message.includes('network') || message.includes('fetch')) {
        return 'Netwerkfout. Controleer uw internetverbinding.';
    }
    if (message.includes('timeout')) {
        return 'De bewerking duurde te lang. Probeer het opnieuw.';
    }
    
    return 'Er is een onverwachte fout opgetreden. Probeer het opnieuw.';
}

// Initialize the application
async function initializeApp() {
    try {
        // Initialize configuration manager first
        configManager = new ConfigManager();
        config = await configManager.loadConfig();
        
        // Initialize core modules
        gameManager = new GameManager();
        uiManager = new UIManager();
        soundManager = new SoundManager();
        gameLauncher = new GameLauncher();
        adminPanel = new AdminPanelManager();
        keyboardHandler = new KeyboardHandler();
        
        // Make modules globally available for legacy function calls
        window.gameManager = gameManager;
        window.uiManager = uiManager;
        window.soundManager = soundManager;
        window.gameLauncher = gameLauncher;
        window.adminPanel = adminPanel;
        window.keyboardHandler = keyboardHandler;
        window.configManager = configManager;
        
        // Initialize modules with dependencies
        soundManager.initialize(config);
        gameLauncher.initialize(gameManager, uiManager, soundManager);
        adminPanel.initialize(gameManager, uiManager, soundManager, config);
        keyboardHandler.initialize(gameManager, uiManager, soundManager, gameLauncher, adminPanel);
          // Load and initialize games
        gameManager.initializeGames();
        
        // DEBUG: Check game count
        const gameCount = gameManager.getAllGames().length;
        console.log(`🎮 DEBUG: Loaded ${gameCount} games from localStorage`);
        
        uiManager.renderGameGrid(gameManager.getAllGames());
        
        // Setup event listeners
        setupEventListeners();
        
        // Apply initial settings
        applyCursorMode(config.display?.cursorMode || 'auto');
        
        // Preload sounds and play startup sound
        await soundManager.preloadSounds();
        soundManager.playStartupSound();
        
        console.log('🎮 mKast Arcade Launcher initialized successfully!');
        
    } catch (error) {
        logError('InitializeApp', error);
        console.error('Failed to initialize application:', error);
    }
}

// Setup main event listeners
function setupEventListeners() {
    // Admin button
    const adminBtn = document.getElementById('adminBtn');
    if (adminBtn) {
        adminBtn.addEventListener('click', () => {
            soundManager.playClickSound();
            uiManager.showModal('passwordModal');
        });
    }

    // Exit button
    const exitBtn = document.getElementById('exitBtn');
    if (exitBtn) {
        exitBtn.addEventListener('click', () => {
            soundManager.playClickSound();
            uiManager.showModal('exitModal');
        });
    }

    // Modal close on background click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                uiManager.closeAllModals();
            }
        });
    });

    // Game card click handlers (delegated)
    const gamesGrid = document.getElementById('gamesGrid');
    if (gamesGrid) {
        gamesGrid.addEventListener('click', (e) => {
            const gameCard = e.target.closest('.game-card');
            if (gameCard) {
                const gameId = parseInt(gameCard.dataset.gameId);
                const game = gameManager.getGame(gameId);
                if (game) {
                    gameLauncher.selectGame(game);
                }
            }
        });

        // Game card hover handlers (delegated)
        gamesGrid.addEventListener('mouseenter', (e) => {
            const gameCard = e.target.closest('.game-card');
            if (gameCard) {
                soundManager.playHoverSound();
            }
        }, true);
    }
}

// Apply cursor mode
function applyCursorMode(mode) {
    const body = document.body;
    body.classList.remove('cursor-auto', 'cursor-none', 'cursor-hidden');
    
    switch (mode) {
        case 'auto':
            body.classList.add('cursor-auto');
            break;
        case 'none':
            body.classList.add('cursor-none');
            break;
        case 'hidden':
            body.classList.add('cursor-hidden');
            break;
    }
}

// Apply responsive grid classes based on game count
function applyResponsiveGridClasses(gameCount) {
    const gamesGrid = document.getElementById('gamesGrid');
    if (!gamesGrid) return;
    
    // Remove existing game count classes
    gamesGrid.classList.remove('has-many-games', 'has-five-plus-games');
    
    // Add appropriate class based on game count
    if (gameCount >= 7) {
        gamesGrid.classList.add('has-many-games', 'has-five-plus-games');
    } else if (gameCount >= 5) {
        gamesGrid.classList.add('has-five-plus-games');
    } else if (gameCount >= 4) {
        gamesGrid.classList.add('has-many-games');
    }
    
    // Also update CSS custom property for more precise control
    gamesGrid.style.setProperty('--game-count', gameCount);
}

// Cleanup function for when window is closing
function cleanup() {
    try {
        if (gameLauncher) {
            gameLauncher.cleanup();
        }
        if (keyboardHandler) {
            keyboardHandler.cleanup();
        }
        if (soundManager) {
            soundManager.stopAllSounds();
        }
        console.log('Application cleanup completed');
    } catch (error) {
        logError('Cleanup', error);
    }
}

// Debug function to find localStorage location and export data
function findGameDataLocation() {
    console.log('=== GAME DATA LOCATION DEBUG ===');
    
    // Show all localStorage data
    const games = localStorage.getItem('arcadeLauncherGames');
    console.log('Games data found:', games ? 'YES' : 'NO');
    
    if (games) {
        const parsedGames = JSON.parse(games);
        console.log('Number of games:', parsedGames.length);
        console.log('Game data structure:', parsedGames[0] || 'No games');
        console.log('Raw localStorage data:', games);
        
        // Create readable JSON file
        const prettyJson = JSON.stringify(parsedGames, null, 2);
        console.log('Formatted JSON:', prettyJson);
        
        // Export data to file for backup
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(prettyJson);
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "mkast-games-readable.json");
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
        console.log('✅ Games exported to mkast-games-readable.json');
    }
    
    // Show all localStorage keys
    console.log('All localStorage keys:', Object.keys(localStorage));
    
    return games;
}

// Function to import game data from JSON
function importGameData(jsonString) {
    try {
        const games = JSON.parse(jsonString);
        localStorage.setItem('arcadeLauncherGames', JSON.stringify(games));
        console.log('✅ Game data imported successfully');
        if (gameManager) {
            gameManager.initializeGames();
            uiManager.renderGameGrid(gameManager.getAllGames());
        }
    } catch (error) {
        console.error('❌ Failed to import game data:', error);
    }
}

// Global functions for HTML onclick handlers (legacy compatibility)
function showAddGameForm() {
    if (adminPanel) adminPanel.showAddGameForm();
}

function addNewGame() {
    if (adminPanel) adminPanel.addNewGame();
}

function editGame(gameId) {
    if (adminPanel) adminPanel.editGame(gameId);
}

function deleteGame(gameId) {
    if (adminPanel) adminPanel.deleteGame(gameId);
}

function saveEditedGame() {
    if (adminPanel) adminPanel.saveEditedGame();
}

function closeEditGameModal() {
    if (adminPanel) adminPanel.closeEditGameModal();
}

function showAdminSection(section) {
    if (adminPanel) adminPanel.showAdminSection(section);
}

function clearAllGames() {
    if (adminPanel) adminPanel.clearAllGames();
}

function refreshGamesList() {
    if (adminPanel) adminPanel.refreshGamesList();
}

async function browseForExecutable() {
    if (adminPanel) await adminPanel.browseForExecutable();
}

async function browseForImage() {
    if (adminPanel) await adminPanel.browseForImage();
}

async function browseForEditExecutable() {
    if (adminPanel) await adminPanel.browseForEditExecutable();
}

async function browseForEditImage() {
    if (adminPanel) await adminPanel.browseForEditImage();
}

async function verifyAdminPassword() {
    if (adminPanel) await adminPanel.verifyAdminPassword();
}

function closeAdmin() {
    if (adminPanel) adminPanel.closeAdmin();
}

async function confirmExit() {
    // Use custom confirmation dialog instead of standard Windows popup
    if (!uiManager) return;
    
    uiManager.showConfirmDialog(
        'APPLICATIE AFSLUITEN',
        'Weet je zeker dat je de arcade launcher wilt afsluiten?',
        async () => {
            // Confirmed - exit application
            try {
                if (soundManager) soundManager.playShutdownSound();
                if (uiManager) uiManager.showLoadingScreen();
                
                setTimeout(async () => {
                    await ipcRenderer.invoke('exit-application');
                }, 2000);
            } catch (error) {
                console.error('Exit error:', error);
                if (soundManager) soundManager.playErrorSound();
                if (uiManager) uiManager.hideLoadingScreen();
            }
        },
        () => {
            // Cancelled - do nothing, dialog will close automatically
            console.log('Exit cancelled by user');
        }
    );
}

function showAdminPanel() {
    if (adminPanel) adminPanel.showAdminPanel();
}

function exitApplication() {
    // Direct exit without modal - this is called from old references
    confirmExit();
}

function closePasswordModal() {
    if (uiManager) uiManager.closeModal('passwordModal');
}

function closeExitModal() {
    if (uiManager) uiManager.closeModal('exitModal');
}

async function launchGame() {
    if (gameLauncher) await gameLauncher.launchGame();
}

function minimizeEmbeddedGame() {
    if (gameLauncher) gameLauncher.minimizeEmbeddedGame();
}

function closeEmbeddedGame() {
    if (gameLauncher) gameLauncher.closeEmbeddedGame();
}

// Make functions globally available
window.applyResponsiveGridClasses = applyResponsiveGridClasses;
window.showAddGameForm = showAddGameForm;
window.addNewGame = addNewGame;
window.editGame = editGame;
window.deleteGame = deleteGame;
window.saveEditedGame = saveEditedGame;
window.closeEditGameModal = closeEditGameModal;
window.showAdminSection = showAdminSection;
window.clearAllGames = clearAllGames;
window.refreshGamesList = refreshGamesList;
window.browseForExecutable = browseForExecutable;
window.browseForImage = browseForImage;
window.browseForEditExecutable = browseForEditExecutable;
window.browseForEditImage = browseForEditImage;
window.verifyAdminPassword = verifyAdminPassword;
window.closeAdmin = closeAdmin;
window.confirmExit = confirmExit;
window.showAdminPanel = showAdminPanel;
window.exitApplication = exitApplication;
window.closePasswordModal = closePasswordModal;
window.closeExitModal = closeExitModal;
window.launchGame = launchGame;
window.minimizeEmbeddedGame = minimizeEmbeddedGame;
window.closeEmbeddedGame = closeEmbeddedGame;
window.findGameDataLocation = findGameDataLocation;
window.importGameData = importGameData;

// Event listeners
document.addEventListener('DOMContentLoaded', async () => {
    await withErrorBoundary(initializeApp, 'DOMContentLoaded');
});

window.addEventListener('beforeunload', cleanup);

// Global error handlers
window.addEventListener('error', (event) => {
    logError('GlobalError', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    logError('UnhandledRejection', event.reason);
});

console.log('🎮 mKast Arcade Launcher modules loaded');
