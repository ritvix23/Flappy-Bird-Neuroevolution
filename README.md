# Flappy-Bird-Neuroevolution
Developing ANN, that is good at playing random flappy bird game, through Neuro Evolution.

### About NEAT -
NEAT stands for NeuroEvolution of Augmenting Topologies and is a kind of genetic algorithm. NEAT searches for solution function/network 
by continuously evolving neural networks starting from minimal networks. In the process of evolution, nodes and connections are added
to continuously build complex networks to solve the problem, unlike evolutionary algorithms proposed before NEAT(like TWEANNS) that evolved fixed topologies.<br />
The way NEAT works is absolutely intriguing and is highly inspired by the way evolution works in nature. Population consists of genomes, which basically encode the network structure. Each genome is evaluated for its fitness (which is user defined fuction) to determine how well that specific genome performs on the given problem. Best performing genomes are selected, crossed and mutated to form population for new generation. Also, population of networks in any generation is divided in species based on a compatibility function. The basic motive behind this speciation is to preserve innovations, the same way nature does. Members of a specie are not crossed with members of other species, this helps eradicate the problem of competing conventions
(different networks representing the same solution).

### Inspiration for this project - 

I came across NEAT while doing my previous project on CPPNs, which are pattern producing networks. In one of the papers, CPPNs were used with 
NEAT to imitate the structural evolution that happened among organisms in nature. From there I searched and came across a video where NEAT was used to learn play games and on other control tasks. I, then, thought to gave it a try myself.

### Evolution Scheme and other specifics -
In this project, I have evolved the population in two stages. The basic idea was to first train the genomes to accomplish a semi deterministic easier task(stage 1) and then evolve them further on the non-deterministic harder task(stage 2) wherein pipes spawn at random heights. This allowed the evolution process to avoid some serious local optima in the vast search space of stage 2 and sped up the evolution process.<br />
During stage 1 the population is initiated from minimal NN which have direct connections to the output. Nodes and connections can be added by the evolution process. Population was evolved for 109 generations in stage 1 after which the resulting genomes were saved in a checkpoint file. Other specifics regarding stage1 can be found in 'config-feedforward-stage-1' file. <br />
In stage 2, I disabled node and connection additions, primarily because I felt that the networks had been complex enough and just needed weight 
mutations to get to the right weights. After approx 60 generations of evolution on stage 2,  I could get a specie that performed well enough (included as winner.pkl in the repo). Other specifics of stage 2 can be found in 'config-feedforward-stage-2' file.<br /><br />
The neat folder contains files related to NEAT algorithm. These have been directly taken from the NEAT-Python library(link attached) with little modifications here and there to suit best for this specific problem.

### Prerequisites-
1. Pygame library<br /><br />
To install pygame library for python3 on ubuntu, execute the following in the terminal-
```
sudo pip3 install pygame
```
### How to use this repo-
* Clone the repository and navigate into it.

To run stage 1 evolution - 
1. Open terminal with the repository as present working directory.
1. Execute the following-

```
python3 run_stage_1.py
```
You'd see the pygame window popping up. Once all birds die the info regarding the performance of the generation is displayed in the terminal.<br />
The evolution runs until 150 gen(can be changed in run_stage_1.py file) or until the threshold fitness is achieved. A checkpoint is saved after every 5 generations. I have included a checkpoint from my run after 109 generations.

*Note: Although I'd highly recommend to keep the configuration parameters as they are, these can be altered in 'config-feedforward-stage1'(for stage 1, 'config-feedforward-stage2' for stage 2) file. Save the changes before executing the piece of code above. To better understand these parameters visit -*<br />
https://neat-python.readthedocs.io/en/latest/config_file.html

To run stage 2 evolution-
1. Execute the following
```
python3 run_stage_1.py
```

This time one round of evaluation is done by letting each genome play the game four times. The evolution runs until 100 gen(can be changed in run_stage_2.py file) or until the threshold fitness is achieved. A checkpoint is saved after every 5 generations. Winner genome is saved after completion.<br />
I have included a winner from my run as winner.pkl in the repo.<br /><br />
To test the winner-
To test the winner genome on the original game, execute the following in the terminal
```
python3 test_winner.py
```
This will load the genome in winner.pkl and will evaluate its score on the original flappy bird game.

### Challenges faced -
1. Parameter tuning- It took a lot of time(almost 5 days straight) and patience to tweak the parameters slowly to get to the right parameters.
1. Local optima - Worked around using two stages of evolution.
1. Height of first pipe influencing the function learned - This was a subtle issue. Worked around by designing stage 2 such that the performance 
was evaluated as average performance after 4 iterations of each genome on the game. In each iteration, the first pipe was spawned at different
height in order to drive the genomes to perform better at all heights.
<br />

### Acknowledgements - 

1. Amazing video on using pygame to build flappy bird-<br />
  https://www.youtube.com/watch?v=UZg49z76cLw

### Related Links -

1. Evolving Neural Networks through Augmenting Topologies, original paper on NEAT by Stanley and Miikkulainen-<br />
  http://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf
  
2. Neat-Python official documentation -<br />
  https://neat-python.readthedocs.io/en/latest/index.html






