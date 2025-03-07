import { AuthService } from '../index/AuthService.js';

export class NavMenu extends BaseComponent {
	constructor() {
		super('static/html/nav-menu.html');
	}

	async onIni() {
		const menu = this.querySelector('.nav-menu'); 
		if (!menu) return;

		menu.classList.add('menu-button');

		// create navigation container
		const buttonContainer = document.createElement('div');
		buttonContainer.classList.add('menu-buttons');

		// create buttons
		const homeButton = this.createNavButton('HOME', '#/home');
		const pongButton = this.createNavButton('PONG', '#/pong');
		
		buttonContainer.appendChild(homeButton);
		buttonContainer.appendChild(pongButton);
		menu.appendChild(buttonContainer);

		//  menu expansion
		menu.addEventListener('click', (e) => {
			e.stopPropagation();
			menu.classList.toggle('expanded');
		});

		// close menu when clicking outside
		document.addEventListener('click', () => {
			menu.classList.remove('expanded');
		});
	}

	createNavButton(text, hash) {
		const button = document.createElement('div');
		button.classList.add('nav-button');
		button.textContent = text;
		button.addEventListener('click', () => {
			if (window.location.hash === hash)
				window.location.reload();
			else
				window.location.hash = hash;
		});
		return button;
	}
}

customElements.define('nav-menu', NavMenu);