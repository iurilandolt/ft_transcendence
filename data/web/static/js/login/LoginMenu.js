import { AuthService } from '../index/AuthService.js';

export class LoginMenu extends BaseComponent {
	constructor() {
		super('static/html/login-menu.html'); 
	}

	async onIni() {
		const menu = this.querySelector('.login-menu');
		if (!menu) return;

		// Add menu button class
		menu.classList.add('menu-button');

		// Create a container for buttons
		const buttonContainer = document.createElement('div');
		buttonContainer.classList.add('menu-buttons');

		// Create buttons
		const profileButton = this.createNavButton('PROFILE', '#/profile');
		const loginButton = this.createNavButton('LOG IN', '#/login');
		const logoutButton = this.createNavButton('LOG OUT', '#/home', () => AuthService.logout());

		// Add buttons to container
		buttonContainer.appendChild(profileButton);

		// Conditionally display login or logout button on initialization
		const toggleButton = AuthService.isAuthenticated ? logoutButton : loginButton;
		toggleButton.classList.add('toggle-button');
		buttonContainer.appendChild(toggleButton);

		// Append the container to the menu
		menu.appendChild(buttonContainer);

		// Toggle menu expansion and assign toggle button based on authentication state
		menu.addEventListener('click', (e) => {
			e.stopPropagation();
			menu.classList.toggle('expanded');

			// Remove existing toggle button if any
			const existingToggleButton = buttonContainer.querySelector('.toggle-button');
			if (existingToggleButton) {
				buttonContainer.removeChild(existingToggleButton);
			}

			// Conditionally assign the toggle button
			const toggleButton = AuthService.isAuthenticated ? logoutButton : loginButton;
			toggleButton.classList.add('toggle-button');
			buttonContainer.appendChild(toggleButton);
		});

		// Close menu when clicking outside
		document.addEventListener('click', () => {
			menu.classList.remove('expanded');
		});
	}

	createNavButton(text, hash, onClick) {
		const button = document.createElement('div');
		button.classList.add('nav-button');
		button.textContent = text;
		button.addEventListener('click', () => {
			window.location.hash = hash;
			if (onClick) onClick();
		});
		return button;
	}
}

customElements.define('login-menu', LoginMenu);