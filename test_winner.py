'''

To test one/ multiple genomes on the orginal game.


'''

import pygame
import sys
import random
from math import sqrt
import neat
import pickle


def main(genomes, config):
	fps_equiv = 2    #2 for 60fps, 1 for 30 fps
	pygame.init()

	screen = pygame.display.set_mode((576, 512))
	clock = pygame.time.Clock()

	bg_surface = pygame.image.load('assets/background-day.png').convert()
	bg_surface = pygame.transform.scale(bg_surface, (576, 512))
	base = pygame.image.load('assets/base.png').convert()
	base = pygame.transform.scale(base, (576, 112))
	bird_surface = pygame.image.load('assets/redbird-upflap.png').convert()
	pipe_surface = pygame.image.load('assets/pipe-red.png').convert()
	flipped_pipe_surface = pygame.transform.flip(pipe_surface, False, True)

	heights = [310,265, 215, 165]

	def show_background():
		screen.blit(bg_surface,(0,0))

	def move_base(base_x):
		screen.blit(base, (base_x, 400))
		screen.blit(base, (base_x+288, 400))

	def check_collision(bird):
		for pipe in pipes.instance:
			if bird.rect.colliderect(pipe.rect) or bird.rect.colliderect(pipe.rect_copy):
				bird.assign_score()
				return True
		if bird.rect.top <=-100 or bird.rect.bottom >= 400:
			bird.assign_score()
			return True
		return False

	def euclid_dist(cord1, cord2):
		#cord1 and cord2 are tuples
		dist =0
		for x1, x2 in zip(cord1, cord2):
			dist += (x1-x2)**2
		return sqrt(dist)

	class pipes():
		instance = []

		def __init__(self, temp=None):
			if temp==None: temp = random.choice(heights)
			self.instance.append(self)
			self.rect = pipe_surface.get_rect(midtop=(700, temp))
			self.rect_copy = flipped_pipe_surface.get_rect(midbottom=(700, temp-100))

		@classmethod
		def move(cls):
			for pipe in cls.instance:
				pipe.rect.centerx -= 10/fps_equiv   
				pipe.rect_copy.centerx -= 10/fps_equiv  
				screen.blit(pipe_surface, pipe.rect)
				screen.blit(flipped_pipe_surface, pipe.rect_copy)
			cls.filter()

		@classmethod
		def filter(cls):
			
			cls.instance[:] = [pipe for pipe in cls.instance if (lambda pipe: pipe.rect.centerx>-100)(pipe)]
		
		@classmethod
		def nearest_pipe_cordinate(cls):
			for pipe in cls.instance:
				if pipe.rect.centerx > 50: return [pipe.rect.topleft, pipe.rect.topright, pipe.rect_copy.bottomleft, pipe.rect_copy.bottomright]

	class birds():
		instance = []
		score = 0

		def __init__(self, net, genome):
			self.genome = genome   
			self.net = net
			self.rect = bird_surface.get_rect(center = (50,170))
			self.instance.append(self)
			self.velocity=0
			self.update_pipe_dist()

		def evaluate_net(self):
			self.output = self.net.activate((self.rect.centery, self.velocity, self.horizontal, self.mid_dist))
			if self.output[0]>0.5: return True
			else: return False

		def flap(self):
			if self.velocity>0:
				self.velocity = -10/fps_equiv 
			else:
				self.velocity -= 6/fps_equiv  

		def update_pipe_dist(self):
			topleft, topright ,bottomleft, bottomright = pipes.nearest_pipe_cordinate()

			assert topleft[0] == bottomleft[0]
			
			self.horizontal = topleft[0]
			self.topleft = topleft[1]
			self.topright = topright[1]
			self.bottomleft = bottomleft[1]
			self.bottomright = bottomright[1]
			self.mid_dist =  (topleft[1] + bottomleft[1])/2

		def assign_score(self):
			self.personal_score = birds.score
			self.personal_score -= abs(self.rect.centery- self.mid_dist)*0.002
			print('Score of genome with key ' + str(self.genome.key) + ' :' + str(round(self.personal_score, 2)))

		@classmethod
		def check_collision_n_filter(cls):
			cls.instance[:] = [bird for bird in cls.instance if not check_collision(bird)]

		
		@classmethod
		def is_birds_exhausted(cls):
			if len(cls.instance)==0:
				return True
			else: return False

		@classmethod
		def show_birds(cls):

			for bird in cls.instance:
				center = bird.rect.center
				screen.blit(bird_surface, bird.rect)

		@classmethod
		def update_birds(cls):
			for bird in cls.instance:
				bird.velocity +=gravity
				bird.rect.centery += bird.velocity
				bird.update_pipe_dist()


	#####

	base_x=0
	gravity = 0.7/fps_equiv/fps_equiv  

	#####

	pipes(random.choice([265, 215, 165]))

	#assign genomes to birds
	for genome_id, genome in genomes:
		net = neat.nn.FeedForwardNetwork.create(genome, config)
		birds(net, genome)


	SPAWNPIPE = 42*fps_equiv

	while True:

		SPAWNPIPE -=1
		
		for bird in birds.instance:
			if bird.evaluate_net():
				bird.flap()


		if SPAWNPIPE==0:
			 SPAWNPIPE=42*fps_equiv
			 pipes()
			

		
		show_background()

		pipes.move() 
		
		birds.update_birds()
	
		birds.check_collision_n_filter() 
		
		birds.show_birds()			
		
		if birds.is_birds_exhausted():
			pygame.quit()
			return

		##base related
		base_x -=10/fps_equiv  
		if base_x<=-288: base_x=0
		move_base(base_x)
		

		pygame.display.update()
		clock.tick(30*fps_equiv)

		birds.score +=0.1
		

if __name__=='__main__':
	with open("winner.pkl", "rb") as f:
		unpickler = pickle.Unpickler(f)
		genome  = unpickler.load()

	#if a single genome is imported. otherwise comment the following line-
	genomes = [(1, genome)]

	config_file = 'config-feedforward-stage2'

	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

	main(genomes, config)








