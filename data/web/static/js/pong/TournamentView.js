import { AuthService } from '../index/AuthService.js';
import { TournamentLobby } from './SinglePongGame.js';
import { BaseComponent } from '/static/js/index/BaseComponent.js';

export class TournamentView extends BaseComponent { // could extend pongview ?
	constructor() {
		super('/tournament-view/');
		this.activeGames = new Set();
	}

	async onIni() {
		await this.contentLoaded;
		this.element = this.getElementById("tournament-view");
		if (!this.element) return;
		
		this.menu = new TournamentMenu(this.element, this);
		this.menu.setupEventListeners();
		this.menu.setupMatchButtons();
		this.pollInterval = setInterval(() => this.menu.poll(), 5000);
		this.beforeUnloadListener = () => {
			for (const game of this.activeGames) {
				game.cleanup();
			}
			this.activeGames.clear();
			if (this.gameElement) {
				this.gameElement.cleanup();
			}
		};
		window.addEventListener('beforeunload', this.beforeUnloadListener);
	}

	registerGame(game) {
		this.activeGames.add(game);
	}

	unregisterGame(game) {
		this.activeGames.delete(game);
	}

	insertBackButton() {
		const backButton = document.createElement('button');
		backButton.textContent = "Back to Tournament";
		backButton.classList.add('btn', 'btn-outline-light', 'tournament-back-button'); 
		this.element.appendChild(backButton);
		
		backButton.addEventListener('click', () => {
			this.activeGames.forEach(game => game.cleanup());
			this.activeGames.clear();  
			const hash = window.location.hash.substring(2);
			Router.go(hash);
		});
		
	}

	onDestroy() {
		clearInterval(this.pollInterval);
		for (const game of this.activeGames) {
			game.cleanup();
		}
		this.activeGames.clear();
		window.removeEventListener('beforeunload', this.beforeUnloadListener);
	}

}

class TournamentMenu {
	constructor(parent, view) {
		this.parent = parent;
		this.view = view;
		this.errorDiv = this.parent.querySelector('#tournament-errors');
		this.menuDiv = null;
	}

	async poll() {
		this.reloadElements();
	}

	async reloadElements() {
		const currentErrorMessage = this.errorDiv?.textContent || '';
		const response = await AuthService.fetchApi('/tournament-view/', 'GET', null);

		if (response.ok) {
			const html = await response.text();
			const tempDiv = document.createElement('div');
			tempDiv.innerHTML = html;
			const newTournamentContainer = tempDiv.querySelector('#tournament-content');
			if (newTournamentContainer) {
				const currentTournamentContainer = document.querySelector('#tournament-content');
				if (currentTournamentContainer) {
					currentTournamentContainer.innerHTML = newTournamentContainer.innerHTML;
					// this.view.pollInterval =setInterval(() => this.menu.poll(), 5000);
					this.setupEventListeners();
					this.setupMatchButtons();
				}
			}

			this.errorDiv = this.parent.querySelector('#tournament-errors');
			if (this.errorDiv && currentErrorMessage) {
				this.errorDiv.textContent = currentErrorMessage;
			}
	
		}
	}

    setupEventListeners() {
        const createBtn = this.parent.querySelector("#create-tournament");
        const joinBtn = this.parent.querySelector("#join-tournament");
        const leaveBtn = this.parent.querySelector("#leave-tournament");

        createBtn?.addEventListener('click', () => this.createTournament());
        joinBtn?.addEventListener('click', () => this.joinTournament());
        leaveBtn?.addEventListener('click', () => this.leaveTournament());

        const container = this.parent.querySelector("#tournaments-container");
        if (container) {
            container.querySelectorAll('.tournament-item').forEach(item => {
                item.addEventListener('click', () => {
                    container.querySelectorAll('.tournament-item').forEach(el => 
                        el.classList.remove('active'));
                    item.classList.add('active');
                });
            });
        }
    }

	async createTournament() {
		this.clearError();
		const response = await AuthService.fetchApi('tournament-view/create/', 'POST', { action: 'create' });

		const data = await response.json();
		if (!this.handleError(response, data)) {
			this.reloadElements();
		}
	}

	async joinTournament() {
		this.clearError();
		const selectedRow = this.parent.querySelector('.active');
		if (!selectedRow) {
			this.handleError({ ok: false }, { message: 'No tournament selected' });
			return;
		}

		const tournamentId = selectedRow.dataset.tournamentId;
		const response = await AuthService.fetchApi('tournament-view/join/', 'PUT', { tournament_id: tournamentId });
		
		const data = await response.json();
		if (!this.handleError(response, data)) {
			this.reloadElements();
		}
	}

	async leaveTournament() {
		this.clearError();
		const response = await AuthService.fetchApi('tournament-view/leave/', 'DELETE', null);
		
		const data = await response.json();
		if (!this.handleError(response, data)) {
			this.reloadElements();
		}
	}

	async joinTournamentMatch(gameId) {
		this.parent.innerHTML = '';
		
		const wrapper = document.createElement('div');
		wrapper.classList.add('tournament-game-wrapper', 'h-100', 'd-flex', 'flex-column');
		this.parent.appendChild(wrapper);
		
		const gameContainer = document.createElement('div');
		gameContainer.classList.add('tournament-game-container', 'flex-grow-1', 'mb-3');
		wrapper.appendChild(gameContainer);
		
		clearInterval(this.view.pollInterval);

		const tournamentLobby = new TournamentLobby(gameContainer, this.view, gameId);
		tournamentLobby.startLobby();
	}

	setupMatchButtons() {
		this.parent.querySelectorAll('.join-match-button').forEach(button => {
			button.addEventListener('click', () => {
				const gameId = button.dataset.gameId;
				this.joinTournamentMatch(gameId);
			});
		});
	}

	clearError() {
		if (this.errorDiv) {
			this.errorDiv.textContent = '';
		}
	}

	handleError(response, data) {
		if (!response.ok && this.errorDiv) {
			this.errorDiv.textContent = data.message;
			return true;
		}
		return false;
	}
}

customElements.define('tournament-view', TournamentView);