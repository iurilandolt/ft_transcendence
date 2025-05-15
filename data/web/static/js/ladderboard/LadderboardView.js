import { BaseComponent } from '/static/js/index/BaseComponent.js';
export class LadderboardView extends BaseComponent {
	constructor(page = null) {
		super(page ? `/ladderboard-view/${encodeURIComponent(page)}/` : '/ladderboard-view/');
		this.currentPage = page;
	}


	async onIni() {
		await this.contentLoaded;
		const element = this.getElementById("ladderboard-view");
		if (!element) return;
		

	}
}

customElements.define('ladderboard-view', LadderboardView);