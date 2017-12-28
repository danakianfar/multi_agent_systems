# Computational Intelligence

[![License](http://img.shields.io/:license-mit-blue.svg)](LICENSE)

## Description

Code for the final project of the [Multi-Agent Systems](http://studiegids.uva.nl/xmlpages/page/2017-2018-en/search-course/course/39202) course at the University of Amsterdam.


We are tasked with designing an autonomous public transportation system for the city of Amsterdam. Given the highly complex and decentralized nature of the problem, a multi-agent system (MAS) design is a natural approach for building an efficient solution without requiring expert engineering. The goal of our system is to minimize:
- the passengers' waiting time
- leasing and operational costs of vehicles
- inter-bus communication costs

In our setup each agent is a bus, and its environment consists of other agents, passengers, and 24 bus stops represented in an undirected graph. Our baseline method is a set of heuristic decision functions modeled in a subsumption architecture, that each agent uses to compute its next action given its current beliefs. We investigated two other methods for designing agents, where we used a Deep Q-network to model the action-value of each state-action pair, and differential evolution for tuning the hyperparameters of our baseline heuristic method.

<p align="center">
<img src="img/flowchart.png" alt="An agent's decision flowchart" style="width: 80px;"/> <br />
<i>An agent's decision flowchart</i>
</p>

## Documents
- [Paper](./documents/report.pdf)
- [Assignment](./documents/assignment.pdf)
- [Slides](./documents/slides.pdf) on [False-Name Bidding and Economic Efﬁciency in Combinatorial Auctions. (Alkalay-Houlihan, Vetta 2014)
](https://pdfs.semanticscholar.org/d594/346bbbbbee0a04c0f78ce0c80048d7990477.pdf)

## Training and Testing

#### Running and visualizing a Simulation: 

A new simulation can be created and observed by running the [run_simulation.py](src/Project/code/run_simulation.py) python script in the command line as `python -m run_simulation.py`. It may take some time to finish. This will create a video file in the same directory named simulation_result.avi. You can open this video to see the simulation visually.

#### Training the models

The iPython notebook file [learning.ipynb](src/Project/code/learning.ipynb) shows the evolution procedure and training phase for the DQN algorithm. You can open the notebook by running in the command line: `jupyter notebook learning.ipynb`. Note that you will need to install the Python dependencies specified below.


## Dependencies
Python 3.x: NumPy, Keras, pandas, jupyter, matplotlib, SciPy, pyparsing

## Contributors
- [Dana Kianfar](https://github.com/danakianfar)
- [Jose Gallego](https://github.com/jgalle29)
- [Marco Federici](https://github.com/MarcoFederici94)

## Copyright

Copyright © 2016 Dana Kianfar, Jose Gallego and Marco Federici.

<p align="justify">
This project is distributed under the <a href="LICENSE">MIT license</a>. Please follow the <a href="http://student.uva.nl/en/az/content/plagiarism-and-fraud/plagiarism-and-fraud.html">UvA regulations governing Fraud and Plagiarism</a> in case you are a student.
</p>
