import { BaseComponent } from '/static/js/index/BaseComponent.js';

export class NotFoundView extends BaseComponent {
	constructor() {
		super('/not-found-view/');
	}

	async onIni() {
		const element = this.getElementById("not-found-view");
		if (element) {
			
		}
	}
}

customElements.define('not-found-view', NotFoundView);