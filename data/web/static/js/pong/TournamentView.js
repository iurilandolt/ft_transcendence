import { AuthService } from '../index/AuthService.js';
import { MultiPongGame, TournamentLobby } from './SinglePongGame.js';

export class TournamentView extends BaseComponent {
    constructor() {
        super('/tournament-view/');
        this.activeGames = new Set();
    }

    async onIni() {
        await this.contentLoaded;
        const element = this.getElementById("tournament-view");
        if (!element) return;
        
        const menu = new TournamentMenu(element, this);
        await menu.render();
        this.pollInterval = setInterval(() => menu.poll(), 5000);
    }

    registerGame(game) {
        this.activeGames.add(game);
    }

    unregisterGame(game) {
        this.activeGames.delete(game);
    }

    onDestroy() {
        clearInterval(this.pollInterval);
        for (const game of this.activeGames) {
            game.cleanup();
        }
        this.activeGames.clear();
    }
}

class TournamentMenu {
    constructor(parent, view) {
        this.parent = parent;
        this.view = view;
        this.errorDiv = null;
        this.menuDiv = null;
    }

	async render() {
		this.menuDiv = document.createElement('div');
		this.menuDiv.classList.add('tournament-container');
		this.menuDiv.innerHTML = `
			<div id="tournament-content">
				<div class="tournament-history">
					<h2>Previous Tournament</h2>
					<div id="last-tournament">
						<div class="no-history">no history...</div>
					</div>
				</div>
				<div class="tournaments-list">
					<h2>Active Tournaments</h2>
					<div id="tournaments-container" class="scrollable-tournaments"></div>
				</div>
				<div class="tournament-actions">
					<button id="create-tournament" class="tournament-button">Create Tournament</button>
					<button id="join-tournament" class="tournament-button">Join Tournament</button>
					<button id="leave-tournament" class="tournament-button hidden">Leave Tournament</button>
					<div id="tournament-errors" class="error-messages"></div>
				</div>
				<div class="tournament-status">
					<h2>Tournament Status</h2>
					<div id="tournament-state">Not in tournament</div>
				</div>
			</div>`;
	
		// clear parent and append menu
		this.parent.innerHTML = '';
		this.parent.appendChild(this.menuDiv);
		this.errorDiv = this.menuDiv.querySelector('#tournament-errors');
		this.setupEventListeners();
		await this.poll();
	}

	async poll() {
		await this.fetchTournamentHistory();
		await this.fetchTournaments();
	}

	setupEventListeners() {
		const createBtn = this.menuDiv.querySelector("#create-tournament");
		const joinBtn = this.menuDiv.querySelector("#join-tournament");
		const leaveBtn = this.menuDiv.querySelector("#leave-tournament");

		createBtn?.addEventListener('click', () => this.createTournament());
		joinBtn?.addEventListener('click', () => this.joinTournament());
		leaveBtn?.addEventListener('click', () => this.leaveTournament());
	}

    async fetchTournaments() {
        const response = await fetch('/tournament-view/list/', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        this.updateTournamentState(data);
        this.updateTournamentsList(data.tournaments);
    }

	updateTournamentState(data) {
			const stateDiv = this.menuDiv.querySelector("#tournament-state");
			if (!stateDiv) return;

			if (data.in_tournament && data.current_tournament) {
				const t = data.current_tournament;
				let stateHTML = `
					<div>Tournament ID: ${data.current_tournament_id}</div>
					<div>Status: ${t.status}</div>
					${t.status === 'IN_PROGRESS' ? `<div>Round: ${t.current_round + 1}</div>` : ''}
					<div>Players: ${t.players.join(', ')}</div>
				`;

				if (t.status === 'IN_PROGRESS' && t.rounds.length > 0 && t.current_round < t.rounds.length) {
					const currentRoundMatches = t.rounds[t.current_round];
					stateHTML += this.renderCurrentRoundMatches(currentRoundMatches);
				}

				stateDiv.innerHTML = stateHTML;
				this.setupMatchButtons();
			} else {
				stateDiv.innerHTML = 'Not in tournament';
			}
		}

	async fetchTournamentHistory() {
		const response = await fetch('/tournament-view/history/', {
			method: 'GET',
			headers: { 'Content-Type': 'application/json' }
		});
		const data = await response.json();
		this.updateTournamentHistory(data);
	}
	
	updateTournamentHistory(data) {
		const historyDiv = this.menuDiv.querySelector("#last-tournament");
		if (!historyDiv) return;
	
		if (!data.has_history) {
			historyDiv.innerHTML = '<div class="no-tournaments">No tournament history</div>';
			return;
		}
	
		const t = data.tournament;
		const userStatus = t.elimination_round 
			? `Eliminated in round ${t.elimination_round} of ${t.total_rounds}`
			: '🏆 Tournament Winner!';
	
		historyDiv.innerHTML = `
			<div class="tournament-item">
				<div class="tournament-info">
					<span>ID: ${t.id}</span>
					<span>Winner: ${t.winner}</span>
				</div>
				<div class="tournament-info">
					<span>${userStatus}</span>
				</div>
			</div>
		`;
	}

	async joinTournamentMatch(gameId) {
		// remove the menu completely
		this.parent.innerHTML = '';
		
		// create wrapper for game and button
		const wrapper = document.createElement('div');
		wrapper.classList.add('tournament-game-wrapper');
		this.parent.appendChild(wrapper);
		
		// create game container
		const gameContainer = document.createElement('div');
		gameContainer.classList.add('tournament-game-container');
		wrapper.appendChild(gameContainer);
		
		// create lobby in the game container
		const tournamentLobby = new TournamentLobby(gameContainer, this.view, gameId);
		
		// create back button after game container
		const backButton = document.createElement('button');
		backButton.textContent = "Back to Tournament";
		backButton.classList.add('tournament-button', 'tournament-back-button'); 
		wrapper.appendChild(backButton);
		
		backButton.addEventListener('click', () => {
			// remove everything and reload tournament view
			this.view.activeGames.forEach(game => game.cleanup());
			this.view.activeGames.clear();	
            window.location.reload();
		});
		
		tournamentLobby.startLobby();
	}

    renderCurrentRoundMatches(matches) {
        return `
            <h3>Current Round Matches</h3>
            <div class="tournament-matches">
                ${matches.map(match => this.renderMatch(match)).join('')}
            </div>
        `;
    }

    renderMatch(match) {
        return `
            <div class="tournament-match ${match.status.toLowerCase()}">
                <div class="match-players">
                    ${match.player1 || 'TBD'} vs ${match.player2 || 'TBD'}
                </div>
                <div class="match-status">
                    ${match.status !== 'PENDING' ? `Status: ${match.status}` : ''}
                    ${match.winner ? `Winner: ${match.winner}` : ''}
                </div>
                ${match.is_player_match && match.status === 'PENDING' ? `
                    <button class="join-match-button tournament-button" 
                            data-game-id="${match.game_id}">
                        Join Match
                    </button>
                ` : ''}
            </div>
        `;
    }

    setupMatchButtons() {
        this.menuDiv.querySelectorAll('.join-match-button').forEach(button => {
            button.addEventListener('click', () => {
                const gameId = button.dataset.gameId;
                this.joinTournamentMatch(gameId);
            });
        });
    }

    updateTournamentsList(tournaments) {
        const container = this.menuDiv.querySelector("#tournaments-container");
        if (!container) return;

        container.innerHTML = tournaments?.length 
            ? tournaments.map(t => `
                <div class="tournament-item" data-tournament-id="${t.tournament_id}">
                    <div class="tournament-info">
                        <span>ID: ${t.tournament_id}</span>
                        <span>Status: ${t.status}</span>
                        <span>Players: ${t.player_count}/${t.max_players}</span>
                    </div>
                </div>
            `).join('')
            : '<div class="no-tournaments">No active tournaments</div>';

		container.querySelectorAll('.tournament-item').forEach(item => {
			item.addEventListener('click', () => {
				// remove last
				container.querySelectorAll('.tournament-item').forEach(el => 
					el.classList.remove('selected'));
				// add new
				item.classList.add('selected');
			});
		});
    }

    async createTournament() {
        this.clearError();
        const response = await fetch('tournament-view/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': AuthService.getCsrfToken(),
            },
            body: JSON.stringify({ action: 'create' })
        });
        
        const data = await response.json();
        if (!this.handleError(response, data)) {
            await this.fetchTournaments();
        }
    }

    async joinTournament() {
        this.clearError();
        const selectedRow = this.menuDiv.querySelector('.selected');
        if (!selectedRow) return;

        const tournamentId = selectedRow.dataset.tournamentId;
        const response = await fetch('tournament-view/join/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': AuthService.getCsrfToken(),
            },
            body: JSON.stringify({ tournament_id: tournamentId })
        });
        
        const data = await response.json();
        if (!this.handleError(response, data)) {
            await this.fetchTournaments();
        }
    }

    async leaveTournament() {
        this.clearError();
        const response = await fetch('tournament-view/leave/', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': AuthService.getCsrfToken(),
            }
        });
        
        const data = await response.json();
        if (!this.handleError(response, data)) {
            await this.fetchTournaments();
        }
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