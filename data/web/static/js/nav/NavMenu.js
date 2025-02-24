import { AuthService } from '../index/AuthService.js';

export class NavMenu extends BaseComponent {
	constructor() {
		super('static/html/nav-menu.html');
	}

	async onIni() {
		const menu = this.querySelector('.nav-menu'); 
		if (!menu) return;

		// Add menu button class
		menu.classList.add('menu-button');

		// Create navigation buttons container
		const buttonContainer = document.createElement('div');
		buttonContainer.classList.add('menu-buttons');

		// Create buttons
		const homeButton = this.createNavButton('HOME', '#/home');
		const pongButton = this.createNavButton('PONG', '#/pong');
		
		// Add buttons to container
		buttonContainer.appendChild(homeButton);
		buttonContainer.appendChild(pongButton);

		// Add container to menu
		menu.appendChild(buttonContainer);

		// Toggle menu expansion
		menu.addEventListener('click', (e) => {
			e.stopPropagation();
			menu.classList.toggle('expanded');
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
		});
		return button;
	}
}

customElements.define('nav-menu', NavMenu);