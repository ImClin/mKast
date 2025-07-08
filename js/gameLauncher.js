// Game Launcher Module
class GameLauncher {
    constructor() {
        this.selectedGame = null;
        this.isEmbeddedGameActive = false;
    }

    // Initialize launcher
    initialize(gameManager, uiManager, soundManager) {
        this.gameManager = gameManager;
        this.uiManager = uiManager;
        this.soundManager = soundManager;
    }

    // Select a game for launching
    selectGame(game) {
        console.log('🎮 DEBUG: selectGame called with:', game);
        this.selectedGame = game;
        this.gameManager.selectedGame = game;
        this.uiManager.showGameModal(game);
        this.soundManager.playSelectSound();
        console.log('🎮 DEBUG: Game selected:', this.selectedGame.title);
    }    // Launch selected game
    async launchGame() {
        console.log('🎮 DEBUG: launchGame called, selectedGame:', this.selectedGame);
        
        if (!this.selectedGame) {
            console.log('🎮 DEBUG: No game selected, exiting launchGame');
            return;
        }

        console.log('🎮 DEBUG: Launching game:', this.selectedGame.title, 'Type:', this.selectedGame.type);        // Check if game can be embedded
        if (this.gameManager.canGameBeEmbedded(this.selectedGame)) {
            console.log('🎮 DEBUG: Launching as embedded game');
            this.launchEmbeddedGame(this.selectedGame);
        } else {
            console.log('🎮 DEBUG: Launching as external game');
            await this.launchExternalGame(this.selectedGame);
        }    }

    // Launch game embedded in the launcher
    launchEmbeddedGame(game) {
        try {
            console.log(`Launching embedded game: ${game.title}`);
            
            // Set game title
            document.getElementById('embeddedGameTitle').textContent = game.title;
            
            // Load game in iframe
            const gameFrame = document.getElementById('embeddedGameFrame');
            gameFrame.src = game.executable;
            
            // Show embedded game container
            const embeddedContainer = document.getElementById('embeddedGameContainer');
            embeddedContainer.style.display = 'flex';
            
            // Hide main game grid
            document.querySelector('.game-container').style.display = 'none';
            
            // Close game modal
            this.uiManager.closeModal('gameModal');
            
            // Update state
            this.isEmbeddedGameActive = true;
            
            // Update statistics
            this.updateGameStats(game.id);
            
            // Play launch sound
            this.soundManager.playLaunchSound();
            
            // Don't show notification for regular game launches
            // to prevent launcher from coming back to foreground
            console.log(`Game ${game.title} started successfully`);
            
        } catch (error) {
            console.error('LaunchEmbeddedGame error:', error);
            this.uiManager.showNotification(
                'Fout bij Laden',
                `Kon ${game.title} niet laden: ${error.message}`,
                'error',
                5000
            );
        }
    }

    // Launch game externally
    async launchExternalGame(game) {
        this.uiManager.showLoadingScreen();
        this.soundManager.playLaunchSound();
        this.updateGameStats(game.id);

        try {
            const result = await ipcRenderer.invoke('launch-game', game.executable);
            
            if (result.success) {
                console.log(`Successfully launched: ${game.executable}`);
                
                setTimeout(() => {
                    this.uiManager.hideLoadingScreen();
                    this.uiManager.closeModal('gameModal');
                    
                    // Don't show notification to prevent launcher from coming back
                    console.log(`Game ${game.title} started externally`);
                }, 2000);
                
            } else {
                throw new Error(result.message || 'Onbekende fout bij starten van het spel');
            }
            
        } catch (error) {
            this.uiManager.hideLoadingScreen();
            console.error('LaunchExternalGame error:', error);
            
            this.uiManager.showNotification(
                'Fout bij Starten',
                `Kon ${game.title} niet starten: ${error.message}`,
                'error',
                5000
            );
        }
    }

    // Minimize embedded game
    minimizeEmbeddedGame() {
        try {
            const gameContainer = document.getElementById('embeddedGameContainer');
            if (gameContainer) {
                gameContainer.style.display = 'none';
            }
            
            const mainContainer = document.querySelector('.game-container');
            if (mainContainer) {
                mainContainer.style.display = 'block';
            }
            
            this.isEmbeddedGameActive = false;
            
            if (this.selectedGame) {
                this.uiManager.showNotification(
                    'SPEL GEMINIMALISEERD',
                    `${this.selectedGame.title} blijft op de achtergrond actief.`,
                    'info',
                    2000
                );
            }
            
            console.log('Game minimized to background');
            
        } catch (error) {
            console.error('MinimizeEmbeddedGame error:', error);
        }
    }

    // Close embedded game
    closeEmbeddedGame() {
        console.log('Closing embedded game...');
        
        try {
            // Clear iframe
            const gameFrame = document.getElementById('embeddedGameFrame');
            if (gameFrame) {
                gameFrame.src = '';
            }
            
            // Hide embedded game container
            const gameContainer = document.getElementById('embeddedGameContainer');
            if (gameContainer) {
                gameContainer.style.display = 'none';
            }
            
            // Show main game container
            const mainContainer = document.querySelector('.game-container');
            if (mainContainer) {
                mainContainer.style.display = 'block';
            }
            
            // Update state
            this.isEmbeddedGameActive = false;
            
            // Show notification
            if (this.selectedGame) {
                this.uiManager.showNotification(
                    'SPEL GESTOPT',
                    `${this.selectedGame.title} is afgesloten.`,
                    'success', 
                    3000
                );
            }
            
            // Clear selected game
            this.selectedGame = null;
            this.gameManager.selectedGame = null;
            
            console.log('Embedded game closed');
            
        } catch (error) {
            console.error('CloseEmbeddedGame error:', error);
        }
    }

    // Update game statistics
    updateGameStats(gameId) {
        try {
            const stats = JSON.parse(localStorage.getItem('gameStats') || '{}');
            if (!stats[gameId]) {
                stats[gameId] = {
                    playCount: 0,
                    lastPlayed: null,
                    totalPlayTime: 0
                };
            }
            
            stats[gameId].playCount++;
            stats[gameId].lastPlayed = new Date().toISOString();
            
            localStorage.setItem('gameStats', JSON.stringify(stats));
        } catch (error) {
            console.error('UpdateGameStats error:', error);
        }
    }

    // Get game statistics
    getGameStats() {
        try {
            return JSON.parse(localStorage.getItem('gameStats') || '{}');
        } catch (error) {
            console.error('GetGameStats error:', error);
            return {};
        }
    }

    // Clean up embedded games on window close
    cleanup() {
        if (this.isEmbeddedGameActive) {
            const gameFrame = document.getElementById('embeddedGameFrame');
            if (gameFrame) {
                gameFrame.src = 'about:blank';
            }
            console.log('Cleaned up embedded games on window close');
        }
    }

    // Check if embedded game is currently active
    isEmbeddedActive() {
        return this.isEmbeddedGameActive;
    }

    // Get currently selected game
    getSelectedGame() {
        return this.selectedGame;
    }
}

// Export for use in main renderer and testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GameLauncher;
} else {
    window.GameLauncher = GameLauncher;
}
