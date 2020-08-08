'''

This is stage 2 of evolution. It exposes the genomes to the original flappy bird game that we are trying the birds to be good at.

A little twist, for fitness assessment purposes, is that each generation has to go through the game 4 times. Each time, the first pipe is placed at different height, 
and thus in 4 iterations of the game the set of all possible heights that the first pipe can be placed at is exhausted.

This type of evaluation is necessary because, apparently, height of first pipe influences the function learned by a bird, and thus to make the function perform well to all
the different heights the first pipe can take, it is crucial.

'''



#necessary imports
import pygame
import sys
import random
from math import sqrt
import neat
import statistics




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


	# list of all discrete heights the pipes can be placed.
	heights = [310,265, 215, 165]

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
				bird.destroy_n_assign_score()     				# if collided with pipe, then remove the bird and assign its score.
				return True
		if bird.rect.top <=-100 or bird.rect.bottom >= 400:
			bird.destroy_n_assign_score()						# if collided with ground, then remove the bird and assign its score.
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
		instance = []                                  # all active(non-destroyed) pipes are present in this list
		
		def __init__(self, temp=None):
			if temp==None: temp = random.choice(heights)        #randomly choose height for the pipe from set of possible heights
			self.instance.append(self)							
			self.rect = pipe_surface.get_rect(midtop=(700, temp))
			self.rect_copy = flipped_pipe_surface.get_rect(midbottom=(700, temp-100))

		#to move pipes on screen-
		@classmethod
		def move(cls):
			for pipe in cls.instance: 
				pipe.rect.centerx -= 10/fps_equiv   
				pipe.rect_copy.centerx -= 10/fps_equiv 
				screen.blit(pipe_surface, pipe.rect)
				screen.blit(flipped_pipe_surface, pipe.rect_copy)
			cls.filter()

		#destroy pipes that went past the display screen
		@classmethod
		def filter(cls):
			cls.instance[:] = [pipe for pipe in cls.instance if (lambda pipe: pipe.rect.centerx>-100)(pipe)]  #remove the pipe if it has passed the bird and has gone too far. 
		
		# returns corner's cordinates of the pipes nearest to the bird. 
		@classmethod
		def nearest_pipe_cordinate(cls):
			for pipe in cls.instance:
				if pipe.rect.centerx > 50: return [pipe.rect.topleft, pipe.rect.topright, pipe.rect_copy.bottomleft, pipe.rect_copy.bottomright]


		# destroy all pipes simultaneously
		@classmethod
		def destroy_all(cls):
			cls.instance =[]


	# class that handles birds. All birds are instances of this class.
	class birds():
		instance = []        # list of instance of alive birds
		score = 0    		# keeps track of score as each frame passes
		destroyed =[]		# list of birds that met their fate.


		def __init__(self, net, genome):
			self.genome = genome   						#genome data of bird
			self.net = net  							# neural net of bird
			self.rect = bird_surface.get_rect(center = (50,170))
			self.instance.append(self)  
			self.velocity=0      # velocity of bird	
			self.scores = []    # will contain list of scores of the bird obtained in 4 iterations

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
				self.velocity = -10/fps_equiv 
			else:
				self.velocity -= 6/fps_equiv  


		# assign various attributes related to the nearest pipe.
		def update_pipe_dist(self):
			topleft, topright ,bottomleft, bottomright = pipes.nearest_pipe_cordinate()

			assert topleft[0] == bottomleft[0]
			
			self.horizontal = topleft[0]   # x cordinate of the nearest pipe
			self.topleft = topleft[1]		
			self.topright = topright[1]
			self.bottomleft = bottomleft[1]
			self.bottomright = bottomright[1]
			self.mid_dist =  (topleft[1] + bottomleft[1])/2  	# y cordinate of center of pipe opening of the nearest pipe


		#destroy a bird and assign it with its score for the current iteration
		def destroy_n_assign_score(self):
			self.scores.append(birds.score - abs(self.rect.centery- self.mid_dist)*0.002)       #birds are penalized for how far they die from the center of the pipe opening
			self.destroy()


		#list destroyed birds in 'destroyed' list
		def destroy(self):
			self.velocity = 0
			self.rect.centery = 170
			self.destroyed.append(self)

		#gravity effect-
		@classmethod
		def update_birds(cls):
			for bird in cls.instance:
				bird.velocity +=gravity
				bird.rect.centery += bird.velocity
				bird.update_pipe_dist()

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
				

		#update the list of instance of alive birds -
		@classmethod
		def check_collision_n_filter(cls):
			cls.instance[:] = [bird for bird in cls.instance if not check_collision(bird)]  # update instance list by removing destroyed birds

		
				
	#####
	
	gravity = 0.7/fps_equiv/fps_equiv 

	#####


	#spawn birds using the genomes-
	for genome_id, genome in genomes:
		net = neat.nn.FeedForwardNetwork.create(genome, config)
		birds(net, genome)
		# print(len(birds.instance))



	for i in range(4):    #let the generation play the game 4 times (as explained at the beginning of this code) 

		
		SPAWNPIPE = 42*fps_equiv   

		pipes(heights[i])          	#on each iteration first pipe takes different height.

		for bird in birds.instance:
			bird.update_pipe_dist()


		base_x=0

		#keep playing until all birds get exhausted/collided
		while True:

			SPAWNPIPE -=1
			
			#evaluate decision of birds based on current inputs
			for bird in birds.instance:
				if bird.evaluate_net():
					bird.flap()


			if SPAWNPIPE==0:				
				 SPAWNPIPE=42*fps_equiv
				 pipes()									# spawnpipes at regular intervals
				

			
			show_background()  						#show background on screen

			pipes.move()   							# move all the pipes to the left
			
			birds.update_birds()					#take in the effect of gravity
		
			birds.check_collision_n_filter() 		#check for collision and filter accordingly.
			
			birds.show_birds()						#place all the alive birds on screen
			

			# if all birds gets collided
			if birds.is_birds_exhausted():
				pipes.destroy_all()       # destroy the pipes on screen
				break						# go for next iteration


			# to move the ground to the left
			base_x -=10/fps_equiv   
			if base_x<=-288: base_x=0
			move_base(base_x)
			

			pygame.display.update()    		#update the pygame screen with new data
			clock.tick(30*fps_equiv)		#maintain a clock

			#increase the score per frame(score is proportional to #of frames elapsed)
			birds.score +=0.1



		# reset score to zero for next iteration
		birds.score = 0   

		# make all birds alive for next iteration
		birds.instance = birds.destroyed.copy()  
		birds.destroyed = []                     



	pygame.quit()     			#quit the pygame window when done

	#calculate fitness of each birds based on their scores in 4 iterations above
	for bird in birds.instance:
		mean_scores = statistics.mean(bird.scores)									 #mean of scores
		stdev_scores_normalized = statistics.stdev(bird.scores)/mean_scores			#normalized standar deviation of scores

		
		fitness = mean_scores - stdev_scores_normalized*0.1							#fitness function
		bird.genome.fitness = fitness												#assign fitness

	return



		

if __name__=='__main__':
	main(genomes, config)






