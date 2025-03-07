import * as THREE from 'three';

export class Player {
	constructor(id, paddle, socket, side) {
		this.id = id;
		this.socket = socket;
		this.paddle = paddle;
		this.intervalID = null;
		this.side = side; // redundant for mp
		this.keydownListener = null;
		this.keyupListener = null;
	}

	inputManager(upKey, downKey) {
		let lastPressed = null;
		const keys = {
			[upKey]: false,
			[downKey]: false
		};
	
		this.keydownListener = (e) => {
			if (e.key in keys && !keys[e.key]) {
				keys[e.key] = true;
				lastPressed = e.key;
				this.socket.send(JSON.stringify({
					action: "paddle_move_start",
					direction: e.key === upKey ? "up" : "down",
					side: this.side
				}));
			}
		};

		this.keyupListener = (e) => {
			if (e.key in keys) {
				keys[e.key] = false;
				if (e.key === lastPressed) {
					lastPressed = keys[upKey] ? upKey : keys[downKey] ? downKey : null;
				}
				this.socket.send(JSON.stringify({
					action: keys[upKey] || keys[downKey] ? "paddle_move_start" : "paddle_move_stop",
					direction: lastPressed === upKey ? "up" : lastPressed === downKey ? "down" : e.key === upKey ? "up" : "down",
					side: this.side
				}));
			}
		};

        window.addEventListener("keydown", this.keydownListener);
        window.addEventListener("keyup", this.keyupListener);
    }

	remove() {
		if (this.keydownListener) {
			window.removeEventListener("keydown", this.keydownListener);
		}
		if (this.keyupListener) {
			window.removeEventListener("keyup", this.keyupListener);
		}
	}
	
}

export class AiOpponent extends Player {
	constructor(id, paddle, socket, side) {
		super(id, paddle, socket, side);
		this.intervalID = null;
	}

	inputManager() {
		//pass
	}

	removeInputManager() {
		//pass
	}
}

export class Paddle {
	constructor() {
		this.mesh = null;
		this.position = { x: 0, y: 0 };
		this.dimensions = { width: 0, height: 0 };
	}

	createMesh(scene, x, y, w, h, depth = 10, color = 0xffffff) {
		const geometry = new THREE.BoxGeometry(w, h, depth);
		const material = new THREE.MeshPhongMaterial({ color: color });
		this.mesh = new THREE.Mesh(geometry, material);
		this.position = { x, y };
		this.dimensions = { width: w, height: h };
		this.mesh.position.set(x, -y - h / 2, depth / 2);
		scene.add(this.mesh);
		return this.mesh;
	}

	update(y, x, w, h) {
		if (x !== undefined) this.position.x = x;
		if (y !== undefined) this.position.y = y;
		if (w !== undefined) this.dimensions.width = w;
		if (h !== undefined) this.dimensions.height = h;
		
		if (this.mesh) {
			this.mesh.position.x = this.position.x;
			this.mesh.position.y = -this.position.y - this.dimensions.height / 2;
			
			if (w !== undefined || h !== undefined) {
				this.mesh.geometry.dispose();
				this.mesh.geometry = new THREE.BoxGeometry(this.dimensions.width, this.dimensions.height, 5);
			}
		}
	}

	destroy() {
		if (this.mesh && this.mesh.parent) {
			this.mesh.parent.remove(this.mesh);
			if (this.mesh.geometry) this.mesh.geometry.dispose();
			if (this.mesh.material) this.mesh.material.dispose();
		}
	}
}

export class Ball {
	constructor() {
		this.mesh = null;
		this.position = { x: 0, y: 0 };
		this.size = 0;
	}
	
	createMesh(scene, x, y, size, color = 0xffffff) {
		const geometry = new THREE.SphereGeometry(size/2, 16, 16);
		const material = new THREE.MeshPhongMaterial({ color: color });
		this.mesh = new THREE.Mesh(geometry, material);
		this.position = { x, y };
		this.size = size;
		this.mesh.position.set(x, -y, size/2);
		scene.add(this.mesh);
		return this.mesh;
	}

	update(x, y, w, h) {
		if (x !== undefined) this.position.x = x;
		if (y !== undefined) this.position.y = y;
		if (w !== undefined) this.size = w;
		
		if (this.mesh) {
			this.mesh.position.x = this.position.x;
			this.mesh.position.y = -this.position.y; 	
			if (w !== undefined) {
				this.mesh.geometry.dispose();
				this.mesh.geometry = new THREE.SphereGeometry(this.size/2, 16, 16);
			}
		}
	}

	destroy() {
		if (this.mesh && this.mesh.parent) {
			this.mesh.parent.remove(this.mesh);
			if (this.mesh.geometry) this.mesh.geometry.dispose();
			if (this.mesh.material) this.mesh.material.dispose();
		}
	}
}

export class ScoreBoard {
	constructor(element) {
		this.player1Info = element.querySelector("#player1-info");
		this.player2Info = element.querySelector("#player2-info");
		this.playerID = { left: null, right: null };
	}
	
	update(leftScore, rightScore, leftSets, rightSets, leftID = this.playerID.left, rightID = this.playerID.right) {
		this.playerID.left = leftID;
		this.playerID.right = rightID;
		this.player1Info.textContent = `${leftID} : ${leftSets} : ${leftScore}`;
		this.player2Info.textContent = `${rightScore} : ${rightSets} : ${rightID}`;
	}
}

export class GameField {
	constructor() {
		this.mesh = null;
		this.edges = null;
		this.centerLine = null;
		this.dimensions = { width: 0, height: 0 };
	}

	createMesh(scene, width, height, depth = 10, color = 0x000000, lineColor = 0x444444) {
		this.dimensions = { width, height };
		const geometry = new THREE.PlaneGeometry(width, height);
		const material = new THREE.MeshPhongMaterial({ 
			color: color,
			side: THREE.DoubleSide
		});

		this.mesh = new THREE.Mesh(geometry, material);
		this.mesh.position.set(width/2, -height/2, -depth); 
		scene.add(this.mesh);
		const centerGeometry = new THREE.BufferGeometry();
		const centerPoints = [
			new THREE.Vector3(width/2, 0, -depth + 1),      
			new THREE.Vector3(width/2, -height, -depth + 1)  
		];
		centerGeometry.setFromPoints(centerPoints);
		const centerMaterial = new THREE.LineBasicMaterial({ color: 0xffffff });
		this.centerLine = new THREE.Line(centerGeometry, centerMaterial);
		scene.add(this.centerLine);
		
		return this.mesh;
	}

	update(w, h) {
		this.dimensions = { width: w, height: h };
		
		if (this.mesh && (this.mesh.geometry.parameters.width !== w || this.mesh.geometry.parameters.height !== h)) {
			this.mesh.geometry.dispose();
			this.mesh.geometry = new THREE.PlaneGeometry(w, h);
			this.mesh.position.set(w/2, -h/2, -5);
			
			if (this.edges) {
				this.edges.geometry.dispose();
				const boxGeometry = new THREE.BoxGeometry(w, 10, h);
				const wireframe = new THREE.EdgesGeometry(boxGeometry);
				this.edges.geometry = wireframe;
				this.edges.position.set(w/2, -h/2, 0);
			}
			
			if (this.centerLine) {
				this.centerLine.geometry.dispose();
				const centerGeometry = new THREE.BufferGeometry();
				const centerPoints = [
					new THREE.Vector3(w/2, 0, -5 + 0.1),
					new THREE.Vector3(w/2, -h, -5 + 0.1)
				];
				centerGeometry.setFromPoints(centerPoints);
				this.centerLine.geometry = centerGeometry;
			}
		}
	}

	destroy() {
		if (this.mesh && this.mesh.parent) {
			this.mesh.parent.remove(this.mesh);
			if (this.mesh.geometry) this.mesh.geometry.dispose();
			if (this.mesh.material) this.mesh.material.dispose();
		}
		
		if (this.edges && this.edges.parent) {
			this.edges.parent.remove(this.edges);
			if (this.edges.geometry) this.edges.geometry.dispose();
			if (this.edges.material) this.edges.material.dispose();
		}
		
		if (this.centerLine && this.centerLine.parent) {
			this.centerLine.parent.remove(this.centerLine);
			if (this.centerLine.geometry) this.centerLine.geometry.dispose();
			if (this.centerLine.material) this.centerLine.material.dispose();
		}
	}
}
