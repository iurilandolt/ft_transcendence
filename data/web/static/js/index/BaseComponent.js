import { AuthService } from '../index/AuthService.js';

export class BaseComponent extends HTMLElement { // all views are based on this class
	constructor(template) {
		super();
		this.contentLoaded = this.loadTemplate(template);
	}

	getElementById(id){ 
		return this.querySelector("#" + id)
	}

	onIni(){
		// overriden in child classes
	}

	disconnectedCallback() {
		this.onDestroy();
	}

	onDestroy(){
		// overriden in child classes
	}

	async loadTemplate(template) {
		try {
			const response = await AuthService.fetchApi(template, 'GET', null);

			if (response.status === 403 ) { 
				window.location.hash = '#/login'; 
				return;
			}

			if (!response.ok) {
				throw new Error('Failed to fetch template');
			}

			const html = await response.text();
			this.innerHTML = html;
			this.onIni();

		} catch (error) {
			console.error('Template loading failed:', error);
		}
	}

}

customElements.define('base-component', BaseComponent);