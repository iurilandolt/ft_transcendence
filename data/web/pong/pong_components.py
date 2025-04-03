import json, asyncio, random, math

GAME_SETTINGS = {
	'field': {
		'width': 1024,
		'height': 768,
	},
	'paddle': {
		'width': 15,
		'height': 100,
		'velo': 6 
	},
	'l_paddle': {
		'start_y': 334,
		'start_x': 20,
	},
	'r_paddle': {
		'start_y': 334,
		'start_x': 1004,
	},
	'ball': {
		'size': 15,
		'start_x': 512,
		'start_y': 384,
		'velo': 7,
	},
	'match': {
		'win_points': 3,
		'win_sets': 2
	},
	'display': {
		'fps': 60
	},
}


class Player:
	def __init__(self, username, paddle):
		self.player_id = username
		self.paddle = paddle
		self.score = 0
		self.sets = 0

	def score_point(self):
		self.score += 1
		
	def win_set(self):
		self.sets += 1

class GameField:
	def __init__(self):
		self.width = GAME_SETTINGS['field']['width']
		self.height = GAME_SETTINGS['field']['height']


class ScoreBoard:
	def __init__(self, instance, left_player: Player, right_player: Player):
		self.instance = instance
		self.left_player = left_player
		self.right_player = right_player
		self.last_scored = None

	def update(self, last_scored: Player = None):
		self.last_scored = last_scored
		if last_scored:
			asyncio.create_task(self.send())

	def new_set(self, winner : Player):
		winner.win_set()
		self.left_player.score = self.right_player.score = 0


	def end_match(self):
		if self.left_player.sets >= GAME_SETTINGS['match']['win_sets']:
			return self.left_player
		elif self.right_player.sets >= GAME_SETTINGS['match']['win_sets']:
			return self.right_player
		return None

	async def send(self):
		score_data = {
			'event': 'score_update',
			'state': {
				'player1_score': self.left_player.score,
				'player2_score': self.right_player.score,
				'player1_sets': self.left_player.sets,
				'player2_sets': self.right_player.sets,
			}
		}
		await self.instance.broadcast_game_score(score_data)


class Paddle:
	def __init__(self, x=0, y=0):
		self.x = self.start_x = x
		self.y = self.start_y = y
		self.width = GAME_SETTINGS['paddle']['width']
		self.height = GAME_SETTINGS['paddle']['height']
		self.direction = 0

	def reset(self):
		self.x = self.start_x
		self.y = self.start_y
	
	def move(self, y):
		self.y = max(0, min(GAME_SETTINGS['field']['height'] - GAME_SETTINGS['paddle']['height'], y))

	def update(self):
		self.y += self.direction * GAME_SETTINGS['paddle']['velo']
		self.move(self.y)


class Ball:
	def __init__(self):
		self.x = GAME_SETTINGS['ball']['start_x']
		self.y = GAME_SETTINGS['ball']['start_y']
		self.size = GAME_SETTINGS['ball']['size']
		self.velo = GAME_SETTINGS['ball']['velo']
		self.dx = 0
		self.dy = 0
		self.wait_time = None
		self.is_waiting = False

	def _get_random_angle(self, min_angle, max_angle, excluded_angles):
		"""Return a random angle (in radians) between min_angle & max_angle,
		excluding anything in 'excluded_angles' (in degrees)."""
		angle_in_degrees = 0
		while angle_in_degrees in excluded_angles:
			angle_in_degrees = random.randrange(min_angle, max_angle)
		return math.radians(angle_in_degrees)

	async def countdown(self, duration):
		await asyncio.sleep(duration)
		self.is_waiting = False

	def coin_toss(self):
		angle = self._get_random_angle(-35, 35, [0])
		pos = 1 if random.random() < 0.5 else -1
		self.dx = pos * abs(math.cos(angle))
		self.dy = math.sin(angle)

	def reset(self, scoreBoard : ScoreBoard, leftPlayer : Player, rightPlayer : Player):
		"""
		Resets the ball for the next play.
		"""
		self.x = GAME_SETTINGS['ball']['start_x']
		self.y = GAME_SETTINGS['ball']['start_y']
		self.velo = GAME_SETTINGS['ball']['velo']
		angle = self._get_random_angle(-35, 35, [0])

		if scoreBoard.last_scored is None:
			pos = 1 if random.random() < 0.5 else -1
			self.dx = pos * abs(math.cos(angle))
		else:
			if scoreBoard.last_scored == rightPlayer:
				self.dx = abs(math.cos(angle))
			else:
				self.dx = -abs(math.cos(angle))

		self.dy = math.sin(angle)
		self.is_waiting = True
		leftPlayer.paddle.reset()
		rightPlayer.paddle.reset()
		asyncio.create_task(self.countdown(3))

	def update(self, scoreBoard : ScoreBoard, leftPlayer : Player, rightPlayer : Player):
		if self.is_waiting:
			return

		self.x += self.velo * self.dx
		self.y += self.velo * self.dy

		if self.y <= self.size and self.dy < 0:
			self.dy *= -1
		
		if self.y >= GAME_SETTINGS['field']['height'] - self.size and self.dy > 0:
			self.dy *= -1


		if (self.x <= leftPlayer.paddle.x + leftPlayer.paddle.width and
			self.x + self.size >= leftPlayer.paddle.x and
			self.y + self.size >= leftPlayer.paddle.y and
			self.y <= leftPlayer.paddle.y + leftPlayer.paddle.height):
			paddle_center = leftPlayer.paddle.y + leftPlayer.paddle.height / 2
			offset = (self.y + self.size / 2) - paddle_center
			normalized = offset / (leftPlayer.paddle.height / 2)
			angle = normalized * math.radians(60) + random.uniform(-0.15, 0.15)
			self.dx = abs(math.cos(angle))
			self.dy = math.sin(angle)
			self.velo += 0.3
			self.x = leftPlayer.paddle.x + leftPlayer.paddle.width

		if (self.x + self.size >= rightPlayer.paddle.x and
			self.y + self.size >= rightPlayer.paddle.y and
			self.y <= rightPlayer.paddle.y + rightPlayer.paddle.height):
			paddle_center = rightPlayer.paddle.y + rightPlayer.paddle.height / 2
			offset = (self.y + self.size / 2) - paddle_center
			normalized = offset / (rightPlayer.paddle.height / 2)
			angle = normalized * math.radians(60) + random.uniform(-0.15, 0.15)
			self.dx = -abs(math.cos(angle))
			self.dy = math.sin(angle)
			self.velo += 0.3
			self.x = rightPlayer.paddle.x - self.size

		if self.x <= 0:
			rightPlayer.score_point()
			if rightPlayer.score >= GAME_SETTINGS['match']['win_points']:
				scoreBoard.update(rightPlayer)
				scoreBoard.new_set(rightPlayer)
			else:
				scoreBoard.update(rightPlayer)
			self.reset(scoreBoard, leftPlayer, rightPlayer)

		elif self.x >= GAME_SETTINGS['field']['width']:
			leftPlayer.score_point()
			if leftPlayer.score >= GAME_SETTINGS['match']['win_points']:
				scoreBoard.update(leftPlayer)
				scoreBoard.new_set(leftPlayer)
			else:
				scoreBoard.update(leftPlayer)
			self.reset(scoreBoard, leftPlayer, rightPlayer)
		scoreBoard.update()


class AIPlayer(Player):
	# def update(self, ball: Ball):
	# 	paddle_center = self.paddle.y + (self.paddle.height / 2)
	# 	ball_center = ball.y + (ball.size / 2)
	# 	dead_zone = 20
	# 	diff = ball_center - paddle_center
	# 	if abs(diff) < dead_zone:
	# 		self.paddle.direction = 0
	# 	else:
	# 		self.paddle.direction = 1 if diff > 0 else -1
	pass
