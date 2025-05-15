import { AuthService } from '../index/AuthService.js';
import { BaseComponent } from '/static/js/index/BaseComponent.js';

export class Login42 extends BaseComponent {
	constructor() {
		super('/login-fortytwo/');
	}

	async onIni() {
		if (AuthService.isAuthenticated) {
			window.location.hash = '#/home';
			return;
		}

		const code = this.getUrlParameter('code');
		if (!code) {
			console.log('Authorization code not found in the URL.');
			window.location.hash = '#/login';
			return;
		}
		try {
			const response = await AuthService.fetchApi('/login42/', 'POST', { code });
			if (!response.ok) {
				throw new Error('Failed to validate the authorization code.');
			}
			const data = await response.json();
			const { access, refresh } = data.tokens;
			localStorage.setItem('jwt', access);
			localStorage.setItem('refreshToken', refresh);
			AuthService.isAuthenticated = true;
			AuthService.currentUser = data.user;
			window.location.reload();
			window.location.hash = '#/home';
		} catch (error) {
			console.error('Error during login:', error);
			window.location.hash = '#/login';
			return;
		}
	}

	getUrlParameter(name) {
		const hash = window.location.hash;
		const queryString = hash.includes('?') ? hash.split('?')[1] : '';
		const params = new URLSearchParams(queryString);
	
		return params.get(name);
	}
}

customElements.define('login-fortytwo', Login42);
