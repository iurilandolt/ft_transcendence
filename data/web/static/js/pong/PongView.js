import { QuickLobby, SinglePongGame, MultiPongGame } from './SinglePongGame.js';
export class PongView extends BaseComponent {
	constructor() {
		super('/pong-view/');  // endpoint instead of static file
		this.activeGames = new Set();
	}

	async onIni() {
		await this.contentLoaded;
		const element = this.getElementById("pong-view");
		if (!element) return;
		
		const menu = new PongStartMenu(element, this);
		menu.render();
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
	}
}

customElements.define('pong-view', PongView);


export class PongStartMenu {
	constructor(parent, view) {
		this.parent = parent;
		this.view = view;
	}

	render() {
		const menuDiv = document.createElement('div');
		const startVersus = document.createElement('button');
		const startAi = document.createElement('button');
		const startQuick = document.createElement('button');
		const startTournament = document.createElement('button');

		menuDiv.classList.add('pong-menu');
		startVersus.textContent = "Start Versus";
		startAi.textContent = "Start AI";
		startQuick.textContent = "Quick Match";
		startTournament.textContent = "Tournament";

		[startVersus, startAi, startQuick, startTournament].forEach(button => {
			button.classList.add('pong-menu-button');
			menuDiv.appendChild(button);
		}); 

		startVersus.addEventListener('click', () => {
			this.parent.removeChild(menuDiv);
			const game = new SinglePongGame(this.parent, this.view);
			game.startGame('vs');  
		});

		startAi.addEventListener('click', () => {
			this.parent.removeChild(menuDiv);
			const game = new SinglePongGame(this.parent, this.view);  
			game.startGame('ai');
		});

		startQuick.addEventListener('click', () => {
			this.parent.removeChild(menuDiv);
			const lobby = new QuickLobby(this.parent, this.view, 'quick');  
			lobby.startLobby();
		});

		startTournament.addEventListener('click', () => {
			this.parent.removeChild(menuDiv);
			const lobby = new QuickLobby(this.parent, this.view, 'tournament');  
			lobby.startLobby();
		});	
		

		this.parent.appendChild(menuDiv);
	}
}
