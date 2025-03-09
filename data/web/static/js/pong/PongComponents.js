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
        const material = new THREE.MeshStandardMaterial({ 
            color: color,
            emissive: color,
            emissiveIntensity: 0,
        });
		this.mesh = new THREE.Mesh(geometry, material);
		this.position = { x, y };
		this.dimensions = { width: w, height: h };
		this.mesh.position.set(x, -y - h / 2, depth / 2);
		scene.add(this.mesh);

        const edgesGeometry = new THREE.EdgesGeometry(geometry);
        const edgesMaterial = new THREE.LineBasicMaterial({ color: 0x9D9494, linewidth: 2 });
        this.edges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
        this.edges.position.set(x, -y - h / 2, depth / 2);
        scene.add(this.edges);
		this.fadeInColor(material, 1);
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
		}
        if (this.edges) {
            this.edges.position.x = this.position.x;
            this.edges.position.y = -this.position.y - this.dimensions.height / 2;
        }
	}

	fadeInColor(material, value, duration = 5000) {
		const start = performance.now();
		const animate = (time) => {
			const elapsed = time - start;
			const t = Math.min(elapsed / duration, 1); // Normalized time (0 to 1)
			const intensity = value * Math.pow(t, 3); // Exponential interpolation
			material.emissiveIntensity = intensity;
			if (elapsed < duration) {
				requestAnimationFrame(animate);
			}
		};
		requestAnimationFrame(animate);
	}

	remove() {
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
	}
}

export class Ball {
	constructor() {
		this.mesh = null;
		this.position = { x: 0, y: 0 };
		this.size = 0;
		this.direction = { x: 0, y: 0 };
		this.rotationSpeed = 0.01;
	}
	
	createMesh(scene, x, y, size, color = 0xffffff) {
		const geometry = new THREE.SphereGeometry(size/2, 16, 16);
        const material = new THREE.MeshStandardMaterial({ 
            color: color,
            emissive: color,
            emissiveIntensity: 1,
        });
		this.mesh = new THREE.Mesh(geometry, material);
		this.position = { x, y };
		this.size = size;
		this.mesh.position.set(x, -y, size/2);
		scene.add(this.mesh);

        const boxGeometry = new THREE.BoxGeometry(size, size, size);
        const edgesGeometry = new THREE.EdgesGeometry(boxGeometry);
        const edgesMaterial = new THREE.LineBasicMaterial({ color: 0x9D9494, linewidth: 2 });
        this.edges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
        this.edges.position.set(x, -y, size / 2);
        scene.add(this.edges);
		this.fadeInColor(material, 1, 3000);
		this.animate();

		return this.mesh;
	}

	update(x, y, w, scene) {
		this.directionIndicator(scene, x, y);
		this.position.x = x;
		this.position.y = y;
		this.size = w;
		
		if (this.mesh) {
			this.mesh.position.x = this.position.x;
			this.mesh.position.y = -this.position.y; 	
		}
		if (this.edges) {
            this.edges.position.x = this.position.x;
            this.edges.position.y = -this.position.y;
        }
	}

	directionIndicator(scene, x, y) {
		let dx = x > this.position.x ? 1 : x < this.position.x ? -1 : 0;
		let dy = y > this.position.y ? 1 : y < this.position.y ? -1 : 0;
		this.direction = { x: dx, y: dy };
		if (this.edges) {
			const color = dx === 1 ? 0x0000ff : dx === -1 ? 0xff0000 : 0x9D9494;
			this.edges.material.color.setHex(color);
			// let rotation = Math.atan2(dy, dx);
			// this.edges.rotation.set(rotation, rotation, rotation);
			if (dx === 0) {
				this.edges.rotation.set(0, 0, 0)
			}
		}
	}

    animate() {
        requestAnimationFrame(() => this.animate());
        if (this.edges) {
            this.edges.rotation.x += this.rotationSpeed * this.direction.x;
            this.edges.rotation.y += this.rotationSpeed * this.direction.x;
            this.edges.rotation.z += this.rotationSpeed * this.direction.x;
        }
    }

	fadeInColor(material, value, duration = 5000) {
		const start = performance.now();
		const animate = (time) => {
			const elapsed = time - start;
			const t = Math.min(elapsed / duration, 1); 
			const intensity = value * Math.pow(t, 3); 
			material.emissiveIntensity = intensity;
			if (elapsed < duration) {
				requestAnimationFrame(animate);
			}
		};
		requestAnimationFrame(animate);
	}

	remove() { 
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
	}
}

export class GameField {
	constructor() {
		this.mesh = null;
		this.edges = null;
		this.centerLine = null;
		this.dimensions = { width: 0, height: 0 };
	}

	createMesh(scene, width, height, depth = 10, color = 0x000000) {
		this.dimensions = { width, height };
		const geometry = new THREE.PlaneGeometry(width, height);
		const material = new THREE.MeshPhongMaterial({ 
			color: color,
			side: THREE.DoubleSide
		});

		this.mesh = new THREE.Mesh(geometry, material);
		this.mesh.position.set(width/2, -height/2, -depth); 
		scene.add(this.mesh);

		const centerGeometry = new THREE.BufferGeometry().setFromPoints([
			new THREE.Vector3(width / 2, 0, -depth + 1),
			new THREE.Vector3(width / 2, -height, -depth + 1)
		]);

		const centerMaterial = new THREE.LineDashedMaterial({ 
			color: 0x9D9494, 
			dashSize: 20, 
			gapSize: 10,
			linewidth: 3,
		});

		this.centerLine = new THREE.Line(centerGeometry, centerMaterial);
		this.centerLine.computeLineDistances(); 
    	scene.add(this.centerLine);
		
		const edgesGeometry = new THREE.EdgesGeometry(new THREE.PlaneGeometry(width, height));
		const edgesMaterial = new THREE.LineBasicMaterial({ color: 0x9D9494, linewidth: 2 });
		this.edges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
		this.edges.position.set(width / 2, -height / 2, -depth);
		scene.add(this.edges);
		
		return this.mesh;
	}

	remove() {
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

export class ScoreBoard {
    constructor(element) {
		this.element = element;
        element.id = 'score-board';
        element.innerHTML = `
            <div class="scoreboard-container">
                <div class="player-info" id="player1-info">
                    <div class="player-sets" id="player1-sets"></div>
                    <div class="player-name" id="player1-name"></div>
                    <div class="player-points" id="player1-points"></div>
                </div>
                <div class="separator"></div>
                <div class="player-info" id="player2-info">
                	<div class="player-points" id="player2-points"></div>    
					<div class="player-name" id="player2-name"></div>
					<div class="player-sets" id="player2-sets"></div>
                </div>
            </div>
        `;
        this.player1Name = element.querySelector("#player1-name");
        this.player1Sets = element.querySelector("#player1-sets");
        this.player1Points = element.querySelector("#player1-points");
        this.player2Name = element.querySelector("#player2-name");
        this.player2Sets = element.querySelector("#player2-sets");
        this.player2Points = element.querySelector("#player2-points");
        this.playerID = { left: null, right: null };
    }

    createUi(win_points, win_sets) {
        this.win_points = win_points;
        this.win_sets = win_sets;
        this.player1Sets.innerHTML = this.createSetIndicators(0, 'left');
        this.player1Points.innerHTML = this.createPointIndicators(0, 'left');
        this.player2Sets.innerHTML = this.createSetIndicators(0, 'right');
        this.player2Points.innerHTML = this.createPointIndicators(0, 'right');
    }

    update(leftScore, rightScore, leftSets, rightSets, leftID = this.playerID.left, rightID = this.playerID.right) {
        this.playerID.left = leftID;
        this.playerID.right = rightID;
        this.player1Name.textContent = leftID;
        this.player1Sets.innerHTML = this.createSetIndicators(leftSets, 'left');
        this.player1Points.innerHTML = this.createPointIndicators(leftScore, 'left');
        this.player2Name.textContent = rightID;
        this.player2Sets.innerHTML = this.createSetIndicators(rightSets, 'right');
        this.player2Points.innerHTML = this.createPointIndicators(rightScore, 'right');
    }

	createSetIndicators(sets, direction) {
		let indicators = '';
		for (let i = 0; i < this.win_sets; i++) {
			const index = direction === 'right' ? this.win_sets - 1 - i : i;
			indicators += `<span class="set-indicator ${index < sets ? 'won' : ''}"></span>`;
		}
		return indicators;
	}

	createPointIndicators(points, player) {
		let indicators = '';
		for (let i = 0; i < this.win_points; i++) {
			const index = player === 'right' ? this.win_points - 1 - i : i;
			indicators += `<span class="point-indicator ${index < points ? 'won' : ''} ${player}"></span>`;
		}
		return indicators;
    }

    showWinner(winnerID) {
        this.element.innerHTML = `
            <div class="scoreboard-container">
                <div class="winner-text">🏆 ${winnerID} 🏆</div>
            </div>
        `;
    }
}