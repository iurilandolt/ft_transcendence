export class ProfileView extends BaseComponent {
	constructor() {
		super('/profile-view/');
	}

	async onIni() {
		if (element) {
			// Initialize home view
		}
	}
}

customElements.define('profile-view', ProfileView);
