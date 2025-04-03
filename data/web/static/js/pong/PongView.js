import { QuickLobby, SinglePongGame, AIPongGame } from './SinglePongGame.js';

// import * as THREE from 'three';
export class PongView extends BaseComponent {
	constructor() {
		super('/pong-view/');  
		this.activeGames = new Set();
	}

	async onIni() {
		await this.contentLoaded;
		const element = this.getElementById("pong-view");
		if (!element) return;
		
		const menu = new PongStartMenu(element, this);
		menu.init();

		window.addEventListener('beforeunload', () => {
			const canvas = document.querySelector('canvas');
			if (canvas) {
				for (const game of this.activeGames) {
					game.cleanup();
				}
			}
		});
	}

	registerGame(game) {
		this.activeGames.add(game);
	}

	unregisterGame(game) {
		this.activeGames.delete(game);
	}

	onDestroy() {
		for (const game of this.activeGames) {
			game.cleanup();
		}
		this.activeGames.clear();
		window.removeEventListener('beforeunload', this.beforeUnloadListener);
	}
}

customElements.define('pong-view', PongView);


export class PongStartMenu {
    constructor(parent, view) {
        this.parent = parent;
        this.view = view;
    }

    init() {
        const menuContainer = this.parent.querySelector('.pong-menu-container');
        const menuDiv = this.parent.querySelector('.pong-menu');
        const startVersus = menuDiv.querySelector('#start-versus');
        const startAi = menuDiv.querySelector('#start-ai');
        const startQuick = menuDiv.querySelector('#start-quick');
        const startTournament = menuDiv.querySelector('#start-tournament');

        startVersus.addEventListener('click', () => {
            this.parent.removeChild(menuContainer); // Remove the container instead of menu
            const game = new SinglePongGame(this.parent, this.view);
            game.startGame('vs');  
        });

        startAi.addEventListener('click', () => {
            this.parent.removeChild(menuContainer); // Remove the container instead of menu
            const game = new AIPongGame(this.parent, this.view);
            game.startGame('ai');
        });

        startQuick.addEventListener('click', () => {
            this.parent.removeChild(menuContainer); // Remove the container instead of menu
            const lobby = new QuickLobby(this.parent, this.view);  
            lobby.startLobby();
        });

        startTournament.addEventListener('click', () => {
            this.parent.removeChild(menuContainer); // Remove the container instead of menu
            window.location.hash = '#/tournament';
        });
    }
}
