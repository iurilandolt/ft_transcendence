import { AuthService } from '../index/AuthService.js';

export class LoginView extends BaseComponent {
	constructor() {
		super('/login-view/');
	}

	async onIni() {
		if (AuthService.isAuthenticated) {
			window.location.hash = '#/home';
			return;
		}

		const form = this.getElementById('login-form');
		const errorDiv = this.getElementById('form-errors');

		form?.addEventListener('submit', async (e) => {
			e.preventDefault();
			errorDiv.textContent = '';
			
			try {
				const formData = new FormData(form);
				await AuthService.login(
					formData.get('username'),
					formData.get('password')
				);
				window.location.hash = '#/home';
			} catch (error) {
				errorDiv.textContent = error.message;
			}
		});
	}
}

customElements.define('login-view', LoginView);