import matplotlib.pyplot as plt

from simulation import *
from main_bus import MainBus

whole_day = 1440

# Simulation setup
simulation = Simulation(MainBus)


simulation.reset()
simulation.execute(iterations=whole_day, animate=True, interval=250, save_file='simulation_result.avi')
plt.show()