export class AuthService {
    static isAuthenticated = false;
    static currentUser = null;

	static async init() {		
		try {
			const response = await fetch('/check-auth/', {
				credentials: 'include'
			});
			const data = await response.json();
			this.isAuthenticated = data.isAuthenticated;
			this.currentUser = data.user;
		} catch (error) {
			console.error('Auth check failed:', error);
		}
	}


	static async login(username, password) {
		const response = await fetch('/login/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': this.getCsrfToken(),
			},
			body: JSON.stringify({ username, password })
		});

		const data = await response.json();
		if (response.ok) {
			this.isAuthenticated = true;
			this.currentUser = data.user;
		} else {
			const error = new Error(data.error);
			error.status = response.status;
			throw error;
		}
	}


    static async logout() {
        const response = await fetch('/logout/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCsrfToken(),
            }
        });

        if (response.ok) {
            this.isAuthenticated = false;
            this.currentUser = null;
        }
		window.location.hash = '#/home';
    }


    static async register(userData) {
        const response = await fetch('/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken(),
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(Object.values(data).join('\n'));
        }
    }


	static getCsrfToken() {
		return document.cookie
			.split('; ')
			.find(row => row.startsWith('csrftoken='))
			?.split('=')[1];
	}

	// wip
	static authEvent() { // create event to which compoenents can listen?
		const event = new CustomEvent('auth-event', {
			detail: {
				isAuthenticated: this.isAuthenticated,
				user: this.currentUser
			}
		});
		document.dispatchEvent(event);
	}
}