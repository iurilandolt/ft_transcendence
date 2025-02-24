import { AuthService } from '../index/AuthService.js';

export class RegisterView extends BaseComponent {
	constructor() {
		super('/register-view/');
	}

	async onIni() {
		if (AuthService.isAuthenticated) {
			window.location.hash = '#/home';
			return;
		}

		const form = this.getElementById('registration-form'); 
		const errorDiv = this.getElementById('form-errors');

		form?.addEventListener('submit', async (e) => {
			e.preventDefault();
			errorDiv.textContent = '';
			
			try {
				const formData = new FormData(form);
				await AuthService.register(Object.fromEntries(formData));
				window.location.hash = '#/login';
			} catch (error) {
				errorDiv.textContent = error.message;
			}
		});
	}
}

customElements.define('register-view', RegisterView);