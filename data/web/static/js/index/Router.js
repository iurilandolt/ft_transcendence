document.addEventListener('DOMContentLoaded', () => {

});

class BaseComponent extends HTMLElement {
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
			const response = await fetch(template, {
				method: 'GET'
			});
			if (response.status === 403) {
				window.location.hash = '#/login';  // Redirect to login if forbidden
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

class Router {
	static routes = {};
	static activeComponent = null;

	static subscribe(url, component) {
		url = url.replace(/^\//, '');
		this.routes[url] = component;
	}

    static parseUrl(url) {
        url = url.replace(/^\//, '');
    
        const parts = url.split('/');
        const baseRoute = parts[0];
        const param = parts.length > 1 ? parts[1] : null;
        
        return { baseRoute, param };
    }

	static go(url) {
		const { baseRoute, param } = this.parseUrl(url);
		const component = this.routes[baseRoute];
		
		if (component) {
			const content = document.getElementById('content');
			if (content) {
				content.innerHTML = "";
				const componentInstance = new component(param);
				this.activeComponent = componentInstance;
				content.append(this.activeComponent);
			} else {
				console.error('Content element not found');
			}
		} else {
			console.error(`No component found for route: ${baseRoute}`);
		}
	}

    static init() {
        const defaultRoute = 'home';
        window.addEventListener('hashchange', () => {
            const page = window.location.hash.slice(2) || defaultRoute;
            this.go(page);
        });
        const currentHash = window.location.hash.slice(2);
        this.go(currentHash || defaultRoute);
    }
}



