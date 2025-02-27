import neat
import pickle
import pygame
import math
import random
from .pong_components import GAME_SETTINGS
import logging

logger = logging.getLogger('pong')

pygame.init()

class AITraining:
	def __init__(self, config):
				
		self.config = config
		self.run_neat()

	def run_neat(self):
		"""Starts the NEAT training process."""
		p = neat.Population(self.config)
		#p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-14')
		p.add_reporter(neat.StdOutReporter(True))
		stats = neat.StatisticsReporter()
		p.add_reporter(stats)
		p.add_reporter(neat.Checkpointer(1))

		# Run training without modifying eval_genomes signature
		winner = p.run(self.eval_genomes, 50)

		# Save the trained AI
		with open("pong/best_ai-3", "wb") as f:
			pickle.dump(winner, f)

	@staticmethod
	def eval_genomes(genomes, config):
		"""Runs AI training games and assigns fitness scores."""
		width, height = GAME_SETTINGS['field']['width'], GAME_SETTINGS['field']['height']
		window = pygame.display.set_mode((width, height))

		for i, (genome_id1, genome1) in enumerate(genomes):
			if i == len(genomes) - 1:
				break
			genome1.fitness = 0
			for genome_id2, genome2 in genomes[i+1:]:
				genome2.fitness = 0 if genome2.fitness == None else genome2.fitness
				game = PongGame(window, width, height)
				game.train_ai(genome1, genome2, config)


class PongGame:
	def __init__(self, window, width, height):
		self.game = Game(window, width, height)
		self.left_paddle = self.game.left_paddle
		self.right_paddle = self.game.right_paddle
		self.ball = self.game.ball

	def train_ai(self, genome1, genome2, config):
		net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
		net2 = neat.nn.FeedForwardNetwork.create(genome2, config)

		run = True
		while run:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					quit()
			output1 = net1.activate(
				(self.left_paddle.y, self.ball.y, abs(self.left_paddle.x - self.ball.x)))
			decision1 = output1.index(max(output1))

			if decision1 == 0:
				pass
			elif decision1 == 1:
				self.game.move_paddle(left=True, up=True)
			else:
				self.game.move_paddle(left=True, up=False)

			output2 = net2.activate(
				(self.right_paddle.y, self.ball.y, abs(self.right_paddle.x - self.ball.x)))
			decision2 = output2.index(max(output2))

			if decision2 == 0:
				pass
			elif decision2 == 1:
				self.game.move_paddle(left=False, up=True)
			else:
				self.game.move_paddle(left=False, up=False)

			game_info = self.game.loop()

			# self.game.draw(draw_score=False, draw_hits=True)
			# pygame.display.update()

			if game_info.left_score >= 1 or game_info.right_score >= 1 or game_info.left_hits > 50:
				self.calculate_fitness(genome1, genome2, game_info)
				break


	def calculate_fitness(self, genome1, genome2, game_info):
		genome1.fitness += game_info.left_hits
		genome2.fitness += game_info.right_hits


class Ball:
	MAX_VEL = GAME_SETTINGS['ball']['velo']
	RADIUS = 10

	def __init__(self, x, y):
		self.x = self.original_x = x
		self.y = self.original_y = y

		angle = self._get_random_angle(-60, 60, [0])
		pos = 1 if random.random() < 0.5 else -1

		self.x_vel = pos * abs(math.cos(angle) * self.MAX_VEL)
		self.y_vel = math.sin(angle) * self.MAX_VEL

	def _get_random_angle(self, min_angle, max_angle, excluded):
		angle = 0
		while angle in excluded:
			angle = math.radians(random.randrange(min_angle, max_angle))

		return angle

	def draw(self, win):
		pygame.draw.circle(win, (255, 255, 255), (self.x, self.y), self.RADIUS)

	def move(self):
		self.x += self.x_vel
		self.y += self.y_vel

	def reset(self):
		self.x = self.original_x
		self.y = self.original_y

		angle = self._get_random_angle(-60, 60, [0])
		x_vel = abs(math.cos(angle) * self.MAX_VEL)
		y_vel = math.sin(angle) * self.MAX_VEL

		self.y_vel = y_vel
		self.x_vel *= -1


class Paddle:
	VEL = GAME_SETTINGS['paddle']['velo']
	WIDTH = GAME_SETTINGS['paddle']['width']
	HEIGHT = GAME_SETTINGS['paddle']['height']

	def __init__(self, x, y):
		self.x = self.original_x = x
		self.y = self.original_y = y

	def draw(self, win):
		pygame.draw.rect(
			win, (255, 255, 255), (self.x, self.y, self.WIDTH, self.HEIGHT))

	def move(self, up=True):
		if up:
			self.y -= self.VEL
		else:
			self.y += self.VEL

	def reset(self):
		self.x = self.original_x
		self.y = self.original_y



class GameInformation:
	def __init__(self, left_hits, right_hits, left_score, right_score):
		self.left_hits = left_hits
		self.right_hits = right_hits
		self.left_score = left_score
		self.right_score = right_score


class Game:
	SCORE_FONT = pygame.font.SysFont("comicsans", 50)
	WHITE = (255, 255, 255)
	BLACK = (11, 4, 38)
	RED = (255, 0, 0)

	def __init__(self, window, window_width, window_height):
		self.window_width = window_width
		self.window_height = window_height

		self.left_paddle = Paddle(
			10, self.window_height // 2 - Paddle.HEIGHT // 2)
		self.right_paddle = Paddle(
			self.window_width - 10 - Paddle.WIDTH, self.window_height // 2 - Paddle.HEIGHT//2)
		self.ball = Ball(self.window_width // 2, self.window_height // 2)

		self.left_score = 0
		self.right_score = 0
		self.left_hits = 0
		self.right_hits = 0
		self.window = window

	def _draw_score(self):
		left_score_text = self.SCORE_FONT.render(
			f"{self.left_score}", 1, self.WHITE)
		right_score_text = self.SCORE_FONT.render(
			f"{self.right_score}", 1, self.WHITE)
		self.window.blit(left_score_text, (self.window_width //
										4 - left_score_text.get_width()//2, 20))
		self.window.blit(right_score_text, (self.window_width * (3/4) -
											right_score_text.get_width()//2, 20))

	def _draw_hits(self):
		hits_text = self.SCORE_FONT.render(
			f"{self.left_hits + self.right_hits}", 1, self.RED)
		self.window.blit(hits_text, (self.window_width //
									2 - hits_text.get_width()//2, 10))

	def _draw_divider(self):
		for i in range(10, self.window_height, self.window_height//20):
			if i % 2 == 1:
				continue
			pygame.draw.rect(
				self.window, self.WHITE, (self.window_width//2, i, 2, self.window_height//20))

	def _handle_collision(self):
		ball = self.ball
		left_paddle = self.left_paddle
		right_paddle = self.right_paddle

		if ball.y + ball.RADIUS >= self.window_height:
			ball.y_vel *= -1
		elif ball.y - ball.RADIUS <= 0:
			ball.y_vel *= -1

		if ball.x_vel < 0:
			if ball.y >= left_paddle.y and ball.y <= left_paddle.y + Paddle.HEIGHT:
				if ball.x - ball.RADIUS <= left_paddle.x + Paddle.WIDTH:
					ball.x_vel *= -1

					middle_y = left_paddle.y + Paddle.HEIGHT / 2
					difference_in_y = middle_y - ball.y
					reduction_factor = (Paddle.HEIGHT / 2) / ball.MAX_VEL
					y_vel = difference_in_y / reduction_factor
					ball.y_vel = -1 * y_vel
					self.left_hits += 1

		else:
			if ball.y >= right_paddle.y and ball.y <= right_paddle.y + Paddle.HEIGHT:
				if ball.x + ball.RADIUS >= right_paddle.x:
					ball.x_vel *= -1

					middle_y = right_paddle.y + Paddle.HEIGHT / 2
					difference_in_y = middle_y - ball.y
					reduction_factor = (Paddle.HEIGHT / 2) / ball.MAX_VEL
					y_vel = difference_in_y / reduction_factor
					ball.y_vel = -1 * y_vel
					self.right_hits += 1

	def draw(self, draw_score=True, draw_hits=False):
		self.window.fill(self.BLACK)

		self._draw_divider()

		if draw_score:
			self._draw_score()

		if draw_hits:
			self._draw_hits()

		for paddle in [self.left_paddle, self.right_paddle]:
			paddle.draw(self.window)

		self.ball.draw(self.window)

	def move_paddle(self, left=True, up=True):
		if left:
			if up and self.left_paddle.y - Paddle.VEL < 0:
				return False
			if not up and self.left_paddle.y + Paddle.HEIGHT > self.window_height:
				return False
			self.left_paddle.move(up)
		else:
			if up and self.right_paddle.y - Paddle.VEL < 0:
				return False
			if not up and self.right_paddle.y + Paddle.HEIGHT > self.window_height:
				return False
			self.right_paddle.move(up)

		return True


	def loop(self):
		self.ball.move()
		self._handle_collision()

		if self.ball.x < 0:
			self.ball.reset()
			self.right_score += 1
		elif self.ball.x > self.window_width:
			self.ball.reset()
			self.left_score += 1

		game_info = GameInformation(
			self.left_hits, self.right_hits, self.left_score, self.right_score)

		return game_info

	def reset(self):
		self.ball.reset()
		self.left_paddle.reset()
		self.right_paddle.reset()
		self.left_score = 0
		self.right_score = 0
		self.left_hits = 0
		self.right_hits = 0
