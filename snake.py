import pygame
import random
import json
import os
import sys


black = (0, 0, 0)
size = height, width = (800, 800)
block_dims = (20, 20)
blocks = (size[0] // block_dims[0], size[1] // block_dims[0])
gap = 4 # Gap between snake blocks (even please)
speed = 20 # Moves per second
path = 'games/'
filename = 'stored_game_{}.json'

directions = {
	pygame.K_LEFT: 0, # Left
	pygame.K_RIGHT: 1, # Right
	pygame.K_UP: 2, # Up
	pygame.K_DOWN: 3, # Down
}

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
		print(f'Head is in {self.head}')
		print(f'Tail is {self.tail}')
		
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



def main():
	moves = []
	seed = random.randint(0, 10 ** 6)
	random.seed(seed)
	pygame.init()
	screen = pygame.display.set_mode(size)
	closed = False
	gameover = False

	apple = [random.randint(0, blocks[0]), random.randint(0, blocks[1])]
	snake = Snake()
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
		if snake.move(apple):
			apple = [random.randint(0, blocks[0]), random.randint(0, blocks[1])]  
		fill_block(screen, *apple, (255, 0, 0))
		snake.draw_tail(screen)
		if snake.is_collided():
			gameover = True

		pygame.display.flip()
		pygame.time.wait(1000 // speed)
	return {'seed': seed, 'moves': moves}

def emulate_game(data):
	random.seed(data['seed'])
	pygame.init()
	screen = pygame.display.set_mode(size)
	closed = False
	gameover = False
	i = 0
	apple = [random.randint(0, blocks[0] - 1), random.randint(0, blocks[1] - 1)]
	snake = Snake()
	while not gameover and not closed and i < len(data['moves']):

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				closed = True

		snake.redirect(data['moves'][i])

		screen.fill(black)

		if snake.move(apple):
			apple = [random.randint(0, blocks[0] - 1), random.randint(0, blocks[1] - 1)]
		fill_block(screen, *apple, (255, 0, 0))

		snake.draw_tail(screen)
		
		if snake.is_collided():
			gameover = True
		pygame.display.flip()
		pygame.time.wait(1000 // speed)
		i += 1

if __name__ == '__main__':
	data = main()
	store_game(data)
	emulate_game(data)