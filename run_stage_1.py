'''

Create population from scratch and evolve on stage 1. 

'''

#necessary imports
from __future__ import print_function
import os
import neat
import stage_1
import pickle



#evaluation sets up the game for the generation
def eval_genomes(genomes, config):
	
	stage_1.main(genomes, config)
	



def run(config_file):

	#load configuration
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

	# Create the population, which is the top-level object for a NEAT run.
	p = neat.Population(config)

	# Add a stdout reporter to show progress in the terminal.
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	#save a checkpoint at intervals of 5 generations 
	p.add_reporter(neat.Checkpointer(5))

	# Run for up to 150 generations.
	winner = p.run(eval_genomes, 150)

	#save the winner genome data in a file
	with open("winner.pkl", 'wb') as f:
		pickle.dump(winner, f)
		f.close()

	# Display the winning genome
	print('\nBest genome:\n{!s}'.format(winner))







if __name__ == '__main__':

    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward-stage1')
    run(config_path)
