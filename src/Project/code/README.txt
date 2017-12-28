Before proceeding: Please read the README file in the installation folder.

The file simulation_result.avi shows the result of the simulation of a whole day.
Buses are represented with green squares (regardless their type) and they are associated with a label indicating their id and number of passengers inside the bus.

The travelling process is represented with a 2 steps animation where the bus moves to the first third of the edge connecting the source and destination and appears at its destination after the amount of time implied by the traveling action.
Bus stops are represented with blue dots associated with a label containing their id, abbreviation and number of waiting passengers (in parenthesis).

Running and visualizing a Simulation: 

A new simulation can be created and observed by running the run_simulation.py python script in the command line as `python -m run_simulation.py`. It may take some time to finish. This will create a video file in the same directory named simulation_result.avi. You can open this video to see the simulation visually.

# Training the models

The python notebook file learning.ipynb shows the evolution procedure and training phase for the DQN algorithm. You can open the notebook by running in the command line: `jupyter notebook learning.ipynb`. Note that you will need to install some Python dependencies. For that, please read the README file in the installation folder.