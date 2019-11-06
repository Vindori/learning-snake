from math import hypot
import random
import json
import os
import sys


black = (0, 0, 0)
size = height, width = (800, 800)
block_dims = (20, 20)
blocks = (size[0] // block_dims[0], size[1] // block_dims[0])
gap = 4 # Gap between snake blocks (even please)
speed = 10 # Moves per second

# directions = {
# 	pygame.K_LEFT: 0, # Left
# 	pygame.K_RIGHT: 1, # Right
# 	pygame.K_UP: 2, # Up
# 	pygame.K_DOWN: 3, # Down
# }

opposite = [1, 0, 3, 2]

offset = [
	(-1, 0),
	(1, 0),
	(0, -1),
	(0, 1)
]

def fill_block(screen, x1, y1, color=(255, 255, 255)):
	x1, y1 = x1 * block_dims[0], y1 * block_dims[1]
	h, w = block_dims[0], block_dims[1]
	rect = pygame.Rect(
		x1 + gap // 2,
		y1 + gap // 2,
		h - gap,
		w - gap
	)
	pygame.draw.rect(screen, color, rect)
	# pygame.draw.circle(screen, color, (x1 + block_dims[0] // 2, y1 + block_dims[1] // 2), 10)

def store_game(data):
	i = 0
	while filename.format(i) in os.listdir(path):
		i += 1
	filepath = os.path.join(path, filename.format(i))
	json.dump(data, open(filepath, 'w'))
	print(f'Stored in {filepath}')

def load_game(name):
	filepath = os.path.join(path, name)
	return json.load(open(filepath, 'r'))

class Snake():
	def __init__(self, length=4, head=[blocks[0] // 2, blocks[1] // 2], direction=1):
		self.length = length	
		self.head = head
		self.tail = [[self.head[0] - i, self.head[1]] for i in range(1, self.length)][::-1]
		self.direction = direction
		# print(f'Head is in {self.head}')
		# print(f'Tail is {self.tail}')
		
	def redirect(self, direction):
		if self.direction != opposite[direction]:
			self.direction = direction

	def move(self, apple):
		bias = offset[self.direction]
		self.tail.append(self.head)
		self.head = [i + j for i, j in zip(self.head, bias)]

		if apple == self.head:
			self.length += 1
			apple = [random.randint(0, blocks[0]) for i in range(2)]
			return True

		self.tail.pop(0)
		return False

	def is_collided(self):
		if self.head[0] not in range(blocks[0]) or self.head[1] not in range(blocks[1]):
			return True

		if self.head in self.tail:
			return True

		return False

	def draw_tail(self, screen, color=(0, 255, 127)):
		for i, j in self.tail:
			fill_block(screen, i, j, color)
		fill_block(screen, *self.head, color)


class Game():

	def __init__(self):
		self.moves = []
		self.breaker = 0
		self.snake = Snake()
		self.seed = random.randint(0, 10 ** 6)
		self.apple = [random.randint(0, blocks[0] - 1), random.randint(0, blocks[1] - 1)]
		self.end = False
		random.seed(self.seed)

	def export(self):
		return json.dumps({'seed': self.seed, 'moves': self.moves})

	def snake_vision(self):
		"""
		0 - top
		1 - right
		2 - bottom
		3 - left
		"""
		apple = self.apple
		snake_head = self.snake.head
		left, top = snake_head
		right, bottom = (j - i for i, j in zip(snake_head, blocks))
		walls = [left, top, right, bottom]
		tail = [0 for i in range(4)]
		
		for i in range(snake_head[1]):
			if [snake_head[0], i] in self.snake.tail:
				tail[0] = snake_head[1] - i

		for i in range(snake_head[0] + 1, blocks[0]):
			if [i, snake_head[1]] in self.snake.tail:
				tail[1] = i - snake_head[0]
				break
		
		for i in range(snake_head[1], blocks[1]):
			if [snake_head[0], i] in self.snake.tail:
				tail[2] = i - snake_head[1]
				break

		for i in range(snake_head[0]):
			if [i, snake_head[1]] in self.snake.tail:
				tail[3] = snake_head[0] - i

		return apple + walls + tail

	def no_viz(self, direction):
		self.moves.append(direction)
		self.breaker += 1
		self.apple = [random.randint(0, blocks[0] - 1), random.randint(0, blocks[1] - 1)]
		self.snake.redirect(direction)
		if self.snake.move(self.apple):
			self.apple = [random.randint(0, blocks[0] - 1), random.randint(0, blocks[1] - 1)]
			self.breaker = 0

		if self.snake.is_collided() or self.breaker > 50:
			self.end = True

		return self.snake.length



	def play(self):
		import pygame
		moves = []
		seed = self.seed
		random.seed(seed)
		pygame.init()
		screen = pygame.display.set_mode(size)
		closed = False
		gameover = False

		self.apple = [random.randint(0, blocks[0] - 1), random.randint(0, blocks[1] - 1)]
		snake = self.snake
		while not gameover and not closed:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					closed = True

				if event.type == pygame.KEYDOWN and event.key in directions.keys():
					if offset[directions[event.key]] == [-i for i in offset[snake.direction]]:
						gameover = True
					else:
						snake.redirect(directions[event.key])

			moves.append(snake.direction)
			screen.fill(black)
			if snake.move(self.apple):
				self.apple = [random.randint(0, blocks[0] - 1), random.randint(0, blocks[1] - 1)]  
			fill_block(screen, *self.apple, (255, 0, 0))
			snake.draw_tail(screen)
			# print(self.snake_vision())
			if snake.is_collided():
				gameover = True
				self.end = True
			pygame.display.flip()
			pygame.time.wait(1000 // speed)
		return {'seed': seed, 'moves': moves}



if __name__ == '__main__':
	game = Game()
	while not game.end:
		game.no_viz(0)
