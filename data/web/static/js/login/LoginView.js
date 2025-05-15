import { AuthService } from '../index/AuthService.js';
import { BaseComponent } from '/static/js/index/BaseComponent.js';

export class LoginView extends BaseComponent {
	constructor() {
		super('/login-view/');
	}

	async onIni() {
		const form = this.getElementById('login-form');
		const errorDiv = this.getElementById('form-errors');
		const login42Button = this.getElementById('login_42');

		form?.addEventListener('submit', async (e) => {
			e.preventDefault();
			errorDiv.textContent = '';

			try {
				const formData = new FormData(form);
				await AuthService.login(
					formData.get('username'),
					formData.get('password'),
				);
			} catch (error) {
				errorDiv.textContent = error.message;
			}
		});

		login42Button?.addEventListener('click', async () => {
			AuthService.login42();
		});
	}
}

customElements.define('login-view', LoginView);
