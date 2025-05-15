export class AuthService {
	static isAuthenticated = false;
	static currentUser = null;
	static currentpfp = null;
	static host = null;
	static jwt = localStorage.getItem('jwt') || null;;
	static refreshToken = localStorage.getItem('refreshToken') || null;
	static loginMenu = null;


	static async init() {
		try {
			await this.check_auth();
			await this.fetchHost();
			console.log(this.currentUser, this.isAuthenticated, this.host);

		} catch (error) {
			throw error;
		}

	}

	static async refreshJWT() {
		const refresh = localStorage.getItem('refreshToken');
		if (!refresh) return false;

		try {

			const response = await fetch('/auth/login/refresh', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': this.getCsrfToken(),
				},
				body: JSON.stringify({ refresh })
			});

			const data = await response.json();
			console.log('Refreshed JWT:', data);
	
			if (response.ok && data.success) {  
				this.jwt = data.access;
				localStorage.setItem('jwt', this.jwt);
				return true;
			}
	
			localStorage.removeItem('refreshToken');
			this.refreshToken = null;
			return false;
			
		} catch (error) {
			console.error('Error refreshing token:', error);
			localStorage.removeItem('refreshToken');
			this.refreshToken = null;
		}
	}


	static async fetchApi(endpoint, method, body = null) {
		const headers = {
			'X-CSRFToken': this.getCsrfToken(),
			'X-Template-Only': 'true'
		};

		if (!(body instanceof FormData)) {
			headers['Content-Type'] = 'application/json';
		}

		if (this.jwt) {
			headers['Authorization'] = `Bearer ${this.jwt}`;
		}

		try {
			const response = await fetch(endpoint, {
				method: method,
				headers: headers,
				body: body instanceof FormData ? body : (body ? JSON.stringify(body) : null)
			});
	
			if (response.status === 401 && this.refreshToken) {
				const refreshed = await this.refreshJWT();
				if (refreshed) {
					const hash = window.location.hash.substring(2);
					Router.go(hash);
					this.loginMenu.reloadElements();
					return response;
				}
				else {
					localStorage.removeItem('jwt');
					localStorage.removeItem('refreshToken');
					this.jwt = null;
					this.refreshToken = null;
					this.isAuthenticated = false;
					this.currentUser = null;
					return {status: 403, ok: false};
				}

			}
			return response;
	
		} catch (error) {
			console.error('Error:', error);
			throw error;
		}	
	}


	static async login(username, password) {
		const response = await this.fetchApi('/auth/login/', 'POST', { username, password });

		const data = await response.json();
		if (response.ok) {

			if (response.status === 201) {
				await this.handle2faResponse(username);
			} else {
				this.jwt = data.tokens.access;
				this.refreshToken = data.tokens.refresh;
				localStorage.setItem('jwt', this.jwt);
				localStorage.setItem('refreshToken', this.refreshToken);			

				this.isAuthenticated = true;
				this.currentUser = data.user;
				window.location.reload();
			}

		} else {
			const error = new Error(data.error);
			error.status = response.status;
			throw error;
		}
	}

	static async handle2faResponse(username, code) {
		document.getElementById('login-form').hidden = true;
		document.getElementById('2fa-form').hidden = false;

		const storedUsername = username;

		document.getElementById('2fa-form').onsubmit = async (e) => {
			e.preventDefault();
			const code = document.getElementById('2fa-code').value;
			const response = await this.fetchApi('/verify_2fa_login/', 'POST', { username: storedUsername, code });
			
			const data = await response.json();
			if (response.ok) {
				this.jwt = data.tokens.access;
				this.refreshToken = data.tokens.refresh;
				localStorage.setItem('jwt', this.jwt);
				localStorage.setItem('refreshToken', this.refreshToken);	

				this.isAuthenticated = true;
				this.currentUser = data.user;
				window.location.reload();
			} else {
				alert(data.error); 
			}
		};
	}

	static async login42() {
		const host = this.host;
		const redirectUri = encodeURIComponent(`https://${host}/oauth/callback/`);
		window.location.href = `https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-f8562a1795538b5f2a9185781d374e1152c6466501442d50530025b059fe92ad&redirect_uri=${redirectUri}&response_type=code`;
	}


	static async logout() {
		const response = await this.fetchApi('/auth/logout/', 'POST');
		if (response.ok) {
			localStorage.removeItem('jwt');
			localStorage.removeItem('refreshToken');
			this.jwt = null;
			this.refreshToken = null;
			this.isAuthenticated = false;
			this.currentUser = null;
		}
		window.location.reload();
	}


	static async register(userData) {
		const response = await this.fetchApi('/auth/register/', 'POST', userData);

		const data = await response.json();
		if (!response.ok) {
			throw new Error(Object.values(data).join('\n'));
		}
	}


	static async changePassword(oldpsw, newpsw) {
		const response = await this.fetchApi('/auth/change-password/', 'POST', {
			current_password: oldpsw,
			new_password: newpsw
		});
		return response;
	}


	static async toggle2fa(enabled) {
		const response = await this.fetchApi('/disable_2fa/', 'POST', {
			two_factor_enable: enabled
		});
		return response;
	}



	static async deleteAccount(password) {
		const response = await this.fetchApi('/auth/delete-account/', 'DELETE', {
			password: password
		});
		if (response.ok) {
			localStorage.removeItem('jwt');
			localStorage.removeItem('refreshToken');
			this.jwt = null;
			this.refreshToken = null;
			this.isAuthenticated = false;
			this.currentUser = null;
		}
		return response;
	}


	static async check_auth() {
		const response = await this.fetchApi('/auth/status/', 'GET', null);

		const data = await response.json();
		this.isAuthenticated = data.isAuthenticated;
		if (this.isAuthenticated && data.user) {
			this.currentUser = data.user.username;
			this.currentpfp = data.user.profile_pic;
		} else {
			this.currentUser = null;
			this.currentpfp = null;
		}
	}


	static async fetchHost() {
		const response = await this.fetchApi('/auth/get-host/', 'GET', null);

		const data = await response.json();
		this.host = data.host;
	}


	static getCsrfToken() {
		return document.cookie
			.split('; ')
			.find(row => row.startsWith('csrftoken='))
			?.split('=')[1];
	}

}
