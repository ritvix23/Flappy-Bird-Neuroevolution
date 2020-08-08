'''
This is stage 1 of evolution. It trains the birds to do well in a semi deterministic scenario.

In this stage, first few pipes are placed at deterministic heights(and randomly after that). The distance between pipes is 
decreased slowly to equal the distance in original game.

Also pipes in this stage take only extreme height(far up/ far down) alternatively. I designed it like this because I observed that 
the birds were facing issues when exposed to extreme height pipes consecutively.


'''


#necessary imports
import pygame
import sys
import random
from math import sqrt
import neat


def main(genomes, config):

	#fps_equiv  = (wanted fps rate)/30. Try to keep fps 30/60.
	fps_equiv = 2

	#initialize the game
	pygame.init()

	#prepare the screen. Values in bracket are dimensions of the screen in pixels.
	screen = pygame.display.set_mode((576, 512))

	clock = pygame.time.Clock()

	#load necessary images
	bg_surface = pygame.image.load('assets/background-day.png').convert()
	bg_surface = pygame.transform.scale(bg_surface, (576, 512))
	base = pygame.image.load('assets/base.png').convert()
	base = pygame.transform.scale(base, (576, 112))
	bird_surface = pygame.image.load('assets/redbird-upflap.png').convert()
	pipe_surface = pygame.image.load('assets/pipe-red.png').convert()
	flipped_pipe_surface = pygame.transform.flip(pipe_surface, False, True)

	# list of all discrete heights the pipes can be placed. Only extreme heights in this stage.
	heights = [325, 150]

	#backgound image appears on the screen-
	def show_background():
		screen.blit(bg_surface,(0,0))

	#to move the base/ground in the game-
	def move_base(base_x):
		screen.blit(base, (base_x, 400))
		screen.blit(base, (base_x+288, 400))


	#to check if any bird has collided with a pipe or ground.
	def check_collision(bird):
		for pipe in pipes.instance:
			if bird.rect.colliderect(pipe.rect) or bird.rect.colliderect(pipe.rect_copy):
				bird.assign_fitness()
				return True
		if bird.rect.top <=-100 or bird.rect.bottom >= 400:
			bird.assign_fitness()
			return True
		return False

	#helper function to calculate euclid dist between two points in 2D plane.
	def euclid_dist(cord1, cord2):
		#cord1 and cord2 are tuples
		dist =0
		for x1, x2 in zip(cord1, cord2):
			dist += (x1-x2)**2
		return sqrt(dist)

	# class to manage pipes. Each spawned pipe is an instance of this class.
	class pipes():
		instance = []

		def __init__(self, temp=None):
			if temp==None: temp = random.choice(heights)   #randomly choose height, if not pre-provided
			self.instance.append(self)
			self.rect = pipe_surface.get_rect(midtop=(700, temp))
			self.rect_copy = flipped_pipe_surface.get_rect(midbottom=(700, temp-100))

		#to move pipes on screen-
		@classmethod
		def move(cls):
			for pipe in cls.instance:
				pipe.rect.centerx -= 10/fps_equiv   # -5 for 60fps
				pipe.rect_copy.centerx -= 10/fps_equiv  # -5 for 60fps
				screen.blit(pipe_surface, pipe.rect)
				screen.blit(flipped_pipe_surface, pipe.rect_copy)
			cls.filter()

		#destroy pipes that went past the display screen
		@classmethod
		def filter(cls):
			cls.instance[:] = [pipe for pipe in cls.instance if (lambda pipe: pipe.rect.centerx>-100)(pipe)]
		
		
		# returns corner's cordinates of the pipes nearest to the bird. 
		@classmethod
		def nearest_pipe_cordinate(cls):
			for pipe in cls.instance:
				if pipe.rect.centerx > 50: return [pipe.rect.topleft, pipe.rect.topright, pipe.rect_copy.bottomleft, pipe.rect_copy.bottomright]


	#class to manage birds. Each spawned bird is an instance of this class.
	class birds():
		instance = []			#list of instance of alive birds.
		fitness = 0             #keep track of fitness as each frame passes.

		def __init__(self, net, genome):
			self.genome = genome   			#genome data of each bird
			self.net = net 					#neural net of bird
			self.rect = bird_surface.get_rect(center = (50,170))
			self.instance.append(self)
			self.velocity=0				#velocity of bird.
			self.update_pipe_dist()

		#feed-forward of neural net of a bird
		def evaluate_net(self):
			# inputs are -(y cordinate of bird, velocity of bird, x cordinate of nearest pipe, y cordinate of center of opening of nearest pipe)
			self.output = self.net.activate((self.rect.centery, self.velocity, self.horizontal, self.mid_dist))
			#output is a nuumber between 0-1. It being >=0.5 implies flap.
			if self.output[0]>0.5: return True
			else: return False

		#change velocity of bird when it flaps
		def flap(self):
			if self.velocity>0:
				self.velocity = -10/fps_equiv # -5 for 60fps
			else:
				self.velocity -= 6/fps_equiv   #-3 for 60fps

		# assign various attributes related to the nearest pipe.
		def update_pipe_dist(self):
			topleft, topright ,bottomleft, bottomright = pipes.nearest_pipe_cordinate()

			assert topleft[0] == bottomleft[0]
			
			self.horizontal = topleft[0]
			self.topleft = topleft[1]
			self.topright = topright[1]
			self.bottomleft = bottomleft[1]
			self.bottomright = bottomright[1]
			self.mid_dist =  (topleft[1] + bottomleft[1])/2

		#assign fitness to the bird when it collides.
		def assign_fitness(self):
			self.personal_fitness = birds.fitness
			#fitness is proportional to the #frames passed by the bird. Also, birds are penalized for how far they die from the center of the nearest pipe opening
			self.personal_fitness -= abs(self.rect.centery- self.mid_dist)*0.002 
			self.genome.fitness = self.personal_fitness
			

		#gravity effect-
		@classmethod
		def update_birds(cls):
			for bird in cls.instance:
				bird.velocity +=gravity
				bird.rect.centery += bird.velocity
				bird.update_pipe_dist()

		#update the list of instance of alive birds -
		@classmethod
		def check_collision_n_filter(cls):
			cls.instance[:] = [bird for bird in cls.instance if not check_collision(bird)]

		#check if the birds are exhausted-
		@classmethod
		def is_birds_exhausted(cls):
			if len(cls.instance)==0:
				return True
			else: return False

		#place birds on screen-
		@classmethod
		def show_birds(cls):
			for bird in cls.instance:
				center = bird.rect.center
				screen.blit(bird_surface, bird.rect)


		
				
	#####

	gravity = 0.7/fps_equiv/fps_equiv 

	base_x=0

	#####


	pipes(heights[0]) #spawn first pipe

	#assign genomes to birds
	for genome_id, genome in genomes:
		net = neat.nn.FeedForwardNetwork.create(genome, config)
		birds(net, genome)


	SPAWNPIPE = 42*fps_equiv

	
	####
	exp = 129
	trigger = False
	off = 4
	####

	while True:
		SPAWNPIPE -=1
		if not trigger:
			exp -=1
		
		#evaluate decision of birds based on current inputs
		for bird in birds.instance:
			if bird.evaluate_net():
				bird.flap()


		#determistic pipes, at slightly more distance
		if exp ==0 and not trigger:

			exp = 129
			if off==4: pipes(heights[1])
			elif off==3 : pipes(heights[0])
			elif off== 2: pipes(heights[1])
			elif off==1: 
				pipes(heights[0])
				SPAWNPIPE=120
				trigger=True
				
			off-= 1

		#pipes at decreasing distance
		if SPAWNPIPE==0 and trigger:
			if off ==-9:
				SPAWNPIPE=42*fps_equiv
				pipes() 
			elif off ==0: 
				SPAWNPIPE=115
				pipes(heights[1])
				off-=1
			elif off==-1: 
				SPAWNPIPE=110
				pipes(heights[0])
				off-=1
			elif off==-2:
				SPAWNPIPE=105
				pipes(heights[1])
				off-=1
			elif off ==-3:
				SPAWNPIPE=100
				pipes(heights[0])
				off-=1
			elif off==-4 :
				SPAWNPIPE= 95
				pipes(heights[1])
				off-=1
			elif off==-5:
				SPAWNPIPE=95
				pipes(heights[0])
				off-=1
			elif off==-6:
				SPAWNPIPE = 90
				pipes(heights[1])
				off-=1
			elif off==-7 :
				SPAWNPIPE= 90
				pipes(heights[0])
				off-=1
			elif off==-8:
				SPAWNPIPE= 42*fps_equiv
				pipes(heights[1])
				off-=1


			

		
		show_background()  								#show background on screen

		pipes.move()   									# move all the pipes to the left
		
		birds.update_birds()							#take in the effect of gravity
	
		birds.check_collision_n_filter() 				#check for collision and filter accordingly
		
		birds.show_birds()								#place all the alive birds on screen
		
		# if all birds gets collided
		if birds.is_birds_exhausted():
			pygame.quit()								# quit game
			return

		# to move the ground to the left
		base_x -=10/fps_equiv   #5 for 60fps
		if base_x<=-288: base_x=0
		move_base(base_x)
		

		pygame.display.update()							#update the pygame screen with new data
		clock.tick(30*fps_equiv)						#maintain a clock

		#increase fitness per frame(fitness is prportional to #frames elapsed)
		birds.fitness +=0.1
		




if __name__=='__main__':
	main(genomes, config)





