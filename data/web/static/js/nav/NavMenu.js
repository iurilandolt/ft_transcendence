import { BaseComponent } from '/static/js/index/BaseComponent.js';
export class NavMenu extends BaseComponent {
    constructor() {
        super('/nav-menu/');
    }

    async onIni() {
        const menu = this.querySelector('.nav-menu'); 
        if (!menu) return;

        menu.classList.add('menu-button');

        const homeButton = this.querySelector('#home-button');
        const pongButton = this.querySelector('#pong-button');
		const LadderboardButton = this.querySelector('#ladderboard-button');
        
        if (homeButton) this.addNavButtonHandler(homeButton, '#/home');
        if (pongButton) this.addNavButtonHandler(pongButton, '#/pong');
		if (LadderboardButton) this.addNavButtonHandler(LadderboardButton, '#/ladderboard');

        menu.addEventListener('click', (e) => {
            e.stopPropagation();
            menu.classList.toggle('expanded');
        });

        document.addEventListener('click', () => {
            menu.classList.remove('expanded');
        });
    }
	
	addNavButtonHandler(button, hash) {
		button.addEventListener('click', () => {
			if (window.location.hash === hash)
				Router.go(hash.substring(2));
			else
				window.location.hash = hash;
		});
	}
}

customElements.define('nav-menu', NavMenu);