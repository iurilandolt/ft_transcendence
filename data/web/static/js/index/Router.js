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
				content.innerHTML = ""; // triggers BaseComponent disconnectedCallback
				const componentInstance = new component(param);
				this.activeComponent = componentInstance;
				content.append(this.activeComponent);
			} else {
				console.error('Content element not found');
			}
		} else {
			window.location.hash = '#/not-found'
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



