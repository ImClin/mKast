// Keyboard Handler Module
class KeyboardHandler {
    constructor() {
        this.debugConsoleVisible = false;
        this.secretSequence = [];
        this.maxSequenceLength = 10;
    }

    // Initialize keyboard handler
    initialize(gameManager, uiManager, soundManager, gameLauncher, adminPanel) {
        this.gameManager = gameManager;
        this.uiManager = uiManager;
        this.soundManager = soundManager;
        this.gameLauncher = gameLauncher;
        this.adminPanel = adminPanel;
        
        // Setup event listeners
        this.setupEventListeners();
    }

    // Setup keyboard event listeners
    setupEventListeners() {
        document.addEventListener('keydown', (event) => {
            this.handleKeyPress(event);
        });

        // Enter key handlers for password fields
        const adminPassword = document.getElementById('adminPassword');
        if (adminPassword) {
            adminPassword.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.adminPanel.verifyAdminPassword();
                }
            });
        }

        const exitPassword = document.getElementById('exitPassword');
        if (exitPassword) {
            exitPassword.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.confirmExit();
                }
            });
        }
    }

    // Main keyboard event handler
    handleKeyPress(event) {
        console.log('Key pressed:', event.key);
        
        // Handle secret key sequences
        this.handleSecretKeySequence(event);
        
        // Debug console toggle
        if (event.ctrlKey && event.shiftKey && event.key === 'D') {
            this.toggleDebugConsole();
            event.preventDefault();
            return;
        }
        
        // Don't handle navigation if embedded game is active
        if (this.gameLauncher && this.gameLauncher.isEmbeddedActive()) {
            return;
        }
        
        // Don't handle navigation if modal is active
        const activeModal = document.querySelector('.modal[style*="block"], .modal[style*="flex"]');
        if (activeModal) {
            return;
        }

        // Main navigation
        switch (event.key) {
            case 'ArrowUp':
            case 'ArrowDown':
            case 'ArrowLeft':
            case 'ArrowRight':
                this.navigateGames(event.key);
                event.preventDefault();
                break;
            case 'Enter':
                this.handleEnterKey();
                event.preventDefault();
                break;
            case 'Escape':
                this.handleEscapeKey();
                event.preventDefault();
                break;
        }
    }

    // Handle Enter key
    handleEnterKey() {
        const selectedCard = document.querySelector('.game-card.selected');
        if (selectedCard) {
            const gameId = parseInt(selectedCard.dataset.gameId);
            const game = this.gameManager.getGame(gameId);
            if (game) {
                this.gameLauncher.selectGame(game);
            }
        }
    }

    // Handle Escape key
    handleEscapeKey() {
        // Close any open modals
        this.uiManager.closeAllModals();
        
        // If embedded game is active, minimize it
        if (this.gameLauncher && this.gameLauncher.isEmbeddedActive()) {
            this.gameLauncher.minimizeEmbeddedGame();
        }
    }

    // Navigate games with arrow keys
    navigateGames(direction) {
        const gameCards = document.querySelectorAll('.game-card');
        if (gameCards.length === 0) return;

        let currentSelected = document.querySelector('.game-card.selected');
        let newIndex = 0;

        if (currentSelected) {
            const currentIndex = Array.from(gameCards).indexOf(currentSelected);
            currentSelected.classList.remove('selected');

            switch (direction) {
                case 'ArrowLeft':
                    newIndex = currentIndex > 0 ? currentIndex - 1 : gameCards.length - 1;
                    break;
                case 'ArrowRight':
                    newIndex = currentIndex < gameCards.length - 1 ? currentIndex + 1 : 0;
                    break;
                case 'ArrowUp':
                    // Calculate cards per row based on grid layout
                    const cardsPerRow = this.calculateCardsPerRow();
                    newIndex = currentIndex - cardsPerRow;
                    if (newIndex < 0) {
                        newIndex = Math.floor((gameCards.length - 1) / cardsPerRow) * cardsPerRow + (currentIndex % cardsPerRow);
                        if (newIndex >= gameCards.length) {
                            newIndex -= cardsPerRow;
                        }
                    }
                    break;
                case 'ArrowDown':
                    const cardsPerRowDown = this.calculateCardsPerRow();
                    newIndex = currentIndex + cardsPerRowDown;
                    if (newIndex >= gameCards.length) {
                        newIndex = currentIndex % cardsPerRowDown;
                    }
                    break;
            }
        }

        // Select new card
        if (gameCards[newIndex]) {
            gameCards[newIndex].classList.add('selected');
            gameCards[newIndex].scrollIntoView({ behavior: 'smooth', block: 'center' });
            this.soundManager.playHoverSound();
        }
    }

    // Calculate cards per row in the grid
    calculateCardsPerRow() {
        const gamesGrid = document.getElementById('gamesGrid');
        if (!gamesGrid) return 4; // Default fallback
        
        const gridStyle = window.getComputedStyle(gamesGrid);
        const gridTemplateColumns = gridStyle.gridTemplateColumns;
        
        if (gridTemplateColumns && gridTemplateColumns !== 'none') {
            return gridTemplateColumns.split(' ').length;
        }
        
        // Fallback calculation based on container width
        const containerWidth = gamesGrid.offsetWidth;
        const cardWidth = 300; // Approximate card width
        const gap = 20; // Approximate gap
        return Math.floor(containerWidth / (cardWidth + gap)) || 4;
    }

    // Handle secret key sequences for easter eggs
    handleSecretKeySequence(event) {
        this.secretSequence.push(event.key);
        
        // Keep sequence length manageable
        if (this.secretSequence.length > this.maxSequenceLength) {
            this.secretSequence.shift();
        }
        
        // Check for known sequences
        const sequenceString = this.secretSequence.join('').toLowerCase();
        
        // Konami Code: ↑↑↓↓←→←→ba
        if (sequenceString.includes('arrowuparrowuparrowdownarrowdownarrowleftarrowrightarrowleftarrowrightba')) {
            this.activateKonamiCode();
            this.secretSequence = [];
        }
        
        // Admin shortcut: ctrl+alt+a
        if (event.ctrlKey && event.altKey && event.key === 'a') {
            this.soundManager.playClickSound();
            this.uiManager.showModal('passwordModal');
            event.preventDefault();
        }
    }

    // Activate Konami Code easter egg
    activateKonamiCode() {
        this.soundManager.playSuccessSound();
        this.uiManager.showNotification(
            '🎮 KONAMI CODE ACTIVATED! 🎮',
            'You found the secret! Extra sound effects enabled.',
            'success',
            5000
        );
        
        // Enable enhanced sound effects or other easter egg features
        this.soundManager.setVolume(1.0);
        
        // Add some visual flair
        document.body.style.animation = 'rainbow 2s ease-in-out';
        setTimeout(() => {
            document.body.style.animation = '';
        }, 2000);
    }

    // Debug console functionality
    toggleDebugConsole() {
        if (!this.debugConsoleVisible) {
            this.showDebugConsole();
        } else {
            this.hideDebugConsole();
        }
    }

    showDebugConsole() {
        const console = document.createElement('div');
        console.id = 'debugConsole';
        console.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            width: 400px;
            height: 300px;
            background: rgba(0, 0, 0, 0.9);
            color: #00ff00;
            font-family: monospace;
            font-size: 12px;
            border: 2px solid #00ff00;
            border-radius: 5px;
            padding: 10px;
            z-index: 10001;
            overflow-y: auto;
        `;
        
        const games = this.gameManager ? this.gameManager.getAllGames() : [];
        console.innerHTML = `
            <div style="color: #ffff00; margin-bottom: 10px;">
                <strong>DEBUG CONSOLE (Ctrl+Shift+D om te sluiten)</strong>
            </div>
            <div id="debugLog">
                <div>System Status: OK</div>
                <div>Games Loaded: ${games.length}</div>
                <div>Admin Mode: ${this.adminPanel?.isAdminMode ? 'ON' : 'OFF'}</div>
                <div>Embedded Game: ${this.gameLauncher?.isEmbeddedActive() ? 'ACTIVE' : 'INACTIVE'}</div>
                <div>Sound Manager: ${this.soundManager ? 'LOADED' : 'NOT LOADED'}</div>
                <div>Last Error: None (errors worden hier getoond)</div>
            </div>
        `;
        
        document.body.appendChild(console);
        this.debugConsoleVisible = true;
    }

    hideDebugConsole() {
        const console = document.getElementById('debugConsole');
        if (console) {
            console.remove();
        }
        this.debugConsoleVisible = false;
    }

    // Show exit confirmation directly (no modal)
    exitApplication() {
        this.confirmExit();
    }

    // Exit confirmation
    async confirmExit() {
        try {
            // Use custom confirmation dialog instead of standard Windows popup
            this.uiManager.showConfirmDialog(
                'APPLICATIE AFSLUITEN',
                'Weet je zeker dat je de arcade launcher wilt afsluiten?',
                async () => {
                    // Confirmed - exit application
                    this.soundManager.playShutdownSound();
                    this.uiManager.showLoadingScreen();
                    
                    setTimeout(async () => {
                        await ipcRenderer.invoke('exit-application');
                    }, 2000);
                },
                () => {
                    // Cancelled - do nothing, dialog will close automatically
                    console.log('Exit cancelled by user');
                }
            );
        } catch (error) {
            console.error('ConfirmExit error:', error);
            this.soundManager.playErrorSound();
            this.uiManager.hideLoadingScreen();
        }
    }

    // Clean up event listeners
    cleanup() {
        document.removeEventListener('keydown', this.handleKeyPress);
    }
}

// Export for use in main renderer and testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KeyboardHandler;
} else {
    window.KeyboardHandler = KeyboardHandler;
}
