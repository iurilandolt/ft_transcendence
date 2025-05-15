import { AuthService } from '../index/AuthService.js';
import { BaseComponent } from '/static/js/index/BaseComponent.js';

export class PassResetView extends BaseComponent{
	constructor() {
		super('/pass-reset-view/');
	}

	async onIni() {
		if (AuthService.isAuthenticated) {
			window.location.hash = '#/home';
			return;
		}
		console.log('Initializing PassResetView');
		this.form = this.getElementById('pass-reset-form');
		this.doneMessage = this.getElementById('pass-reset-done');

		this.form.addEventListener('submit', (event) => this.handleFormSubmit(event));

	}

	async handleFormSubmit(event) {
		console.log('Handling form submit');
		event.preventDefault();

		const emailInput = this.form.querySelector('#id_email');
		const email = emailInput.value;

		try {
			const response = await AuthService.fetchApi('/auth/password-reset/', 'POST', { email: email,});

			if (response.ok) {

				this.form.hidden = true;
				this.doneMessage.hidden = false;
			} else {
				this.displayErrors(data.errors || { email: ['An error occurred. Please try again.'] });
			}

		} catch (error) {
			this.displayErrors({ email: ['An unexpected error occurred. Please try again later.'] });
		}
	}

	displayErrors(errors) {
        const errorContainer = this.form.querySelector('#form-errors');
        errorContainer.innerHTML = '';


        for (const [field, messages] of Object.entries(errors)) {	
            messages.forEach((message) => {
                const errorElement = document.createElement('div');
                errorElement.textContent = message;
                errorContainer.appendChild(errorElement);
            });
        }
    }
}

customElements.define('pass-reset-view', PassResetView);
