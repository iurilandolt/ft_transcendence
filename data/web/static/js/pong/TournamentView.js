import { AuthService } from '../index/AuthService.js';

export class TournamentView extends BaseComponent {
	constructor() {
		super('/tournament-view/');
		this.errorDiv = null;
	}

	async onIni() {
		const element = this.getElementById("tournament-view");
		if (!element) return;

		this.errorDiv = this.getElementById('tournament-errors');
		this.setupEventListeners();
		await this.fetchTournaments();
        this.pollInterval = setInterval(() => this.fetchTournaments(), 5000);
	}

	onDestroy(){
		clearInterval(this.pollInterval);
	}

	setupEventListeners() {
		const createBtn = this.getElementById("create-tournament");
		const joinBtn = this.getElementById("join-tournament");
		const leaveBtn = this.getElementById("leave-tournament");

		createBtn?.addEventListener('click', () => this.createTournament());
		joinBtn?.addEventListener('click', () => this.joinTournament());
		leaveBtn?.addEventListener('click', () => this.leaveTournament());
	}


	// async fetchTournaments() {
	// 	const response = await fetch('/tournament-view/list/', {
	// 		method: 'GET',
	// 		headers: {
	// 			'Content-Type': 'application/json'
	// 		}
	// 	});
	// 	const data = await response.json();
	// 	const stateDiv = this.getElementById("tournament-state");
		
	// 	stateDiv.innerHTML = data.in_tournament 
	// 		? `In Tournament: ${data.current_tournament_id}`
	// 		: 'Not in tournament';
		
	// 	this.updateTournamentsList(data.tournaments);
	// }


	async fetchTournaments() {
		const response = await fetch('/tournament-view/list/', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		const data = await response.json();
		const stateDiv = this.getElementById("tournament-state");
		
		if (data.in_tournament && data.current_tournament) {
			const t = data.current_tournament;
			stateDiv.innerHTML = `
				<div>Tournament ID: ${data.current_tournament_id}</div>
				<div>Status: ${t.status}</div>
				 ${t.status === 'IN_PROGRESS' ? `<div>Round: ${t.current_round + 1}</div>` : ''}
				<div>Players: ${t.players.join(', ')}</div>
				${t.rounds.length > 0 ? `<div>Current Matches: ${this.formatMatches(t.rounds[t.current_round])}</div>` : ''}
			`;
		} else {
			stateDiv.innerHTML = 'Not in tournament';
		}
		
		this.updateTournamentsList(data.tournaments);
	}
	
	formatMatches(matches) {
		if (!matches) return '';
		return matches.map(match => 
			`${match.player1} vs ${match.player2} ${match.status !== 'PENDING' ? `(${match.status})` : ''}`
		).join(' | ');
	}

	updateTournamentsList(tournaments) {
		const container = this.getElementById("tournaments-container");
		if (!container) return;
	
		if (!tournaments || tournaments.length === 0) {
			container.innerHTML = '<div class="no-tournaments">No active tournaments</div>';
			return;
		}
	
		container.innerHTML = tournaments.map(t => `
			<div class="tournament-item" data-tournament-id="${t.tournament_id}">
				<div class="tournament-info">
					<span>ID: ${t.tournament_id}</span>
					<span>Status: ${t.status}</span>
					<span>Players: ${t.player_count}/${t.max_players}</span>
				</div>
			</div>
		`).join('');
	

		container.querySelectorAll('.tournament-item').forEach(item => {
			item.addEventListener('click', () => {
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
			body: JSON.stringify({
				action: 'create'
			})
		});
		
		if (response.ok) {
			await this.fetchTournaments();
		}

		const data = await response.json();
		if (!this.handleError(response, data)) {
			await this.fetchTournaments();
		}
	}


	async joinTournament() {
		this.clearError();
		const selectedRow = this.getElementById("tournaments-container")?.querySelector('.selected');
		if (!selectedRow) return;
	
		const tournamentId = selectedRow.dataset.tournamentId;
		const response = await fetch('tournament-view/join/', {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': AuthService.getCsrfToken(),
			},
			body: JSON.stringify({
				tournament_id: tournamentId
			})
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