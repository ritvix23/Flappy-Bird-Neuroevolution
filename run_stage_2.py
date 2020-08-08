''' 

Import best genomes from Stage 1 and evolve it further on stage 2.

''' 

#necessary imports 
from __future__ import print_function
import os
import neat
import stage_2
import pickle



#evaluation sets up the game for the generation
def eval_genomes(genomes, config):
	
	stage_2.main(genomes, config)





def run(config_file):

	#load configuration
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

	# restore checkpoint-109 from stage 1 and use it as initial population.
	p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-109')
	p.config =config
	

	# Add a stdout reporter to show progress in the terminal.
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	p.add_reporter(neat.Checkpointer(5))

	#run the evolution for up to 100 generations
	winner = p.run(eval_genomes, 100)

	#save the winner genome in a file
	with open("winner_from_stage2.pkl", 'wb') as f:
		pickle.dump(winner, f)
		f.close()


	#display info about winner genome
	print('\nBest genome:\n{!s}'.format(winner))



if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward-stage2')
    run(config_path)
