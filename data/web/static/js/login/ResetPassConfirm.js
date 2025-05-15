import { AuthService } from '../index/AuthService.js';
import { BaseComponent } from '/static/js/index/BaseComponent.js';

export class PassResetConfirmView extends BaseComponent {
	constructor() {
		super('/pass-reset-confirm-view/');
	}

	async onIni() {
		if (AuthService.isAuthenticated) {
			window.location.hash = '#/home';
			return;
		}
	
		console.log('Initializing PassResetConfirmView');
		this.form = this.getElementById('pass-reset-confirm-form');
		this.doneMessage = this.getElementById('pass-reset-confirm-done');
	
		this.uidb64 = this.getUrlParameter('uidb64');
		this.token = this.getUrlParameter('token');

		this.form.addEventListener('submit', (event) => this.handleFormSubmit(event));
	
		console.log('UIDB64:', this.uidb64);
		console.log('Token:', this.token);
	
		if (!this.uidb64 || !this.token) {
			console.log('Invalid or missing reset link');
			this.displayErrors({ general: ['Invalid or missing reset link.'] });
			return;
		}
	
		try {
			console.log('Fetching password reset confirmation form');
			const response = await AuthService.fetchApi(`/auth/reset/${this.uidb64}/${this.token}/`, 'GET');
	
			if (!response.ok) {
				const data = await response.json();
				console.error('Token validation failed:', data.error);
				this.displayErrors({ general: [data.error || 'Invalid or expired reset link.'] });
				return;
			}
	
			console.log('Token and UID validated successfully');
		} catch (error) {
			console.error('Error during password reset:', error);
			this.displayErrors({ general: ['An unexpected error occurred. Please try again later.'] });
		}
	
		this.form.addEventListener('submit', (event) => this.handleFormSubmit(event));
	}

	async handleFormSubmit(event) {
		event.preventDefault();

		const passwordInput = this.form.querySelector('#id_new_password1');
		const password2Input = this.form.querySelector('#id_new_password2');
		const password = passwordInput.value;
		const confirmPassword = password2Input.value;

		if (password !== confirmPassword) {
			this.displayErrors({ password: ['Passwords do not match.'] });
			return;
		}

		try {
			const response = await AuthService.fetchApi(`/auth/reset/${this.uidb64}/${this.token}/`, 'POST', { new_password1: password, new_password2: confirmPassword });

			const data = await response.json();
			if (response.ok) {
				if (data.success) {
					this.form.hidden = true;
					this.doneMessage.hidden = false;
					return;
				}
			}
			this.displayErrors({ general: [data.error] });
		} catch (error) {
			this.displayErrors({ 'error': error.message });
		}
				
	}

	displayErrors(errors) {
		const errorContainer = document.getElementById('pass-reset-confirm-error');
		const errorMessageElement = errorContainer.querySelector('p'); // The paragraph inside the error container
	
		errorMessageElement.textContent = '';
	
		for (const [field, messages] of Object.entries(errors)) {
			messages.forEach((message) => {
				errorMessageElement.textContent += `${message} `;
			});
		}
		// Show the error container
		errorContainer.hidden = false;
	}

	getUrlParameter(name) {
		const hash = window.location.href.split('#/pass-reset-confirm/')[1];
		if (!hash) {
			console.log('No parameters found in the URL.');
			return null;
		}

		const params = new URLSearchParams(hash);
		console.log('Parsed parameters:', params);
	
		return params.get(name);
	}
}

customElements.define('pass-reset-confirm-view', PassResetConfirmView);
