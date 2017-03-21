from main_bus import *
import numpy as np

class GeneticMainBus(MainBus):
    def __init__(self, bus_id, bus_type, init_stop, controller, genome=None):
        MainBus.__init__(self, bus_id, bus_type, init_stop, controller)
        self.genome = genome

    def bus_creation(self):
        new_bus_genome_idx = np.random.choice(range(len(self.controller.bus_genomes)),
                                              p=self.controller.genome_distro)
        # print(self.controller.genome_distro, new_bus_genome_idx)
        new_bus_genome = self.controller.bus_genomes[new_bus_genome_idx]

        # Create bus using the sampled genome
        self.add_bus(int(new_bus_genome[0]), genome=new_bus_genome)

        self.created_buses_counter += 1
        self.position_beliefs.internal_table[self.bus_id + self.created_buses_counter] = (self.controller.ticks, 3)

    def compute_next(self, state):

        # Evaluate every possible adjacent station to visit (including self)
        possible_actions = self.connections[self.current_stop.stop_id]  # + [self.current_stop.stop_id]

        # Exploration policy
        if np.random.rand() < self.exploration_parameter:
            best_action = np.random.choice(possible_actions)
            best_score = 100

        else:  # Exploitation policy
            scores = []

            for next_station in possible_actions:
                scores.append(self.genome[0] * state[0, 24 + next_station] + \
                              self.genome[1] * state[0, 2 * 24 + next_station] + \
                              self.genome[2] * state[0, 3 * 24 + next_station] + \
                              self.genome[3] * state[0, 4 * 24 + next_station])

            soft_scores = self.softmax(scores)

            next_idx = np.random.choice(range(len(scores)), p=soft_scores)

            best_score = soft_scores[next_idx]
            best_action = possible_actions[next_idx]

        return best_action, best_score