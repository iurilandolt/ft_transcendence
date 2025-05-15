import { AuthService } from "../index/AuthService.js";
import { BaseComponent } from '/static/js/index/BaseComponent.js';
export class LanguageView extends BaseComponent {
	constructor() {
		super('/language-menu/');
	}

	async onIni() {
		const menu = this.querySelector('.language-menu');
		if (!menu) return;
		menu.addEventListener('click', (event) => {
			const target = event.target;
			if (target.classList.contains('language-menu__link')) {
				event.preventDefault();
				const selectedLang = target.getAttribute('data-lang');
				this.changeLanguage(selectedLang);
			}
		});
	}

	async changeLanguage(lang) {
		try {
			const response = await AuthService.fetchApi(`/set-language/?lang=${lang}`, 'POST', null);

			if (response.ok) {
				window.location.reload();
			} else {
				console.error('Failed to change language');
			}
		} catch (error) {
			console.error('Error changing language:', error);
		}
	}
}

customElements.define('language-menu', LanguageView);