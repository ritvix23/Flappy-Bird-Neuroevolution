'''

Original flappy bird game.

Controls- spacebar to flap

'''
import sys, os

#supress print while importing pygame
sys.stdout  =open(os.devnull, 'w')
import pygame
sys.stdout = sys.__stdout__

import sys
import random




fps_equiv = 4   #set 2 for 60fps, 1 for 30 fps 

pygame.init()   #initialize pygame



screen = pygame.display.set_mode((576, 512))  			#setup the display screen
clock = pygame.time.Clock()								#initiate clock


#load necessary images
bg_surface = pygame.image.load('assets/background-day.png').convert()
bg_surface = pygame.transform.scale(bg_surface, (576, 512))				#scale image according to the display screen size
base = pygame.image.load('assets/base.png').convert()
base = pygame.transform.scale(base, (576, 112))
bird = pygame.image.load('assets/redbird-upflap.png').convert()
bird_rect = bird.get_rect(center=(50, 170))              #get rectangle around image
pipe_surface = pygame.image.load('assets/pipe-red.png').convert()
flipped_pipe_surface = pygame.transform.flip(pipe_surface, False, True)			#flip image for inverted pipe

heights = [325, 275, 200, 150]              # set of possible height of pipes.


def show_background():
	screen.blit(bg_surface,(0,0))  			#show background image on the screen

#move the base/ground slowly to the left
def move_base(base_x):
	screen.blit(base, (base_x, 400))
	screen.blit(base, (base_x+288, 400))

#assign new bird velocity when user triggers flap
def flap():
	global velocity 
	if velocity>0:
		velocity = -10/fps_equiv 
	else:
		velocity -= 6/fps_equiv

#check for collision of the bird with pipes and ground
def check_collision(pipes):
	for pipe in pipes.instance:
		if bird_rect.colliderect(pipe.rect) or bird_rect.colliderect(pipe.rect_copy):
			pygame.quit()   		#quit game window if collision happens with a pipe
			print('Your score is : ' + str(round(bird_score,2)))
			sys.exit()
	if bird_rect.top<=-100 or bird_rect.bottom >=400:
		pygame.quit()				#quit game window if the bird flies too high up or too low down 
		print('Your score is : ' + str(round(bird_score,2)))
		sys.exit


#class for handling pipes. each spawned pipe is an instance of this class-
class pipes():
	instance = []

	def __init__(self):
		temp = random.choice(heights)      #randomly choose pipe height from the list of possible heights
		self.rect = pipe_surface.get_rect(midtop=(700, temp))
		self.instance.append(self)
		self.rect_copy = flipped_pipe_surface.get_rect(midbottom=(700, temp-100))   #opening size = 100px

	# move pipes to the left on the screen
	@classmethod
	def move(cls):
		for pipe in cls.instance:
			pipe.rect.centerx -= 10/fps_equiv
			pipe.rect_copy.centerx -= 10/fps_equiv
			screen.blit(pipe_surface, pipe.rect)
			screen.blit(flipped_pipe_surface, pipe.rect_copy)
		cls.filter()

	#remove pipes that went pass the display screen
	@classmethod
	def filter(cls):
		
		cls.instance[:] = [pipe for pipe in cls.instance if (lambda pipe: pipe.rect.centerx>-100)(pipe)]
	

#####

base_x=0

gravity = 0.7/fps_equiv/fps_equiv  

velocity=0

bird_y=170

bird_score = 0

SPAWNPIPE = 42*fps_equiv

#####

pipes()   				#spawn first pipe

while True:

	#spawn pipes at regular intervals-
	SPAWNPIPE-=1
	if SPAWNPIPE==0: 
		SPAWNPIPE=42*fps_equiv
		pipes()

	#loop to listen for events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
			
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				flap()         #flap if spacebar is pressed


	
	show_background()       						#show background

	pipes.move()									#move pipes


	#take in effect, gravity-
	velocity +=gravity
	bird_y += velocity
	bird_rect.centery = bird_y

	screen.blit(bird, bird_rect)					#place bird on screen

	check_collision(pipes)							#check for collision


	#move the base/ground slowly to the left
	base_x -=10/fps_equiv
	if base_x<=-288: base_x=0
	move_base(base_x)

	# bird score is proportional to the #frames elapsed
	bird_score +=0.1						

	pygame.display.update()							#update the screen with changes
	clock.tick(30*fps_equiv)						#maintain a clock







