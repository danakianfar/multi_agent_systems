from main_bus import *
import numpy as np

class GeneticMainBus(MainBus):

    def __init__(self, bus_id, bus_type, init_stop, controller, genome=None):
        MainBus.__init__(self, bus_id, bus_type, init_stop, controller)
        self.genome = genome
        self.exploration_probability = 0
        self.movement_policy_switch_time = MainBus._DEFAULT_MOVEMENT_SWITCH_TIME
        self.initial_buses = 50


    def create_bus(self):
        new_bus_genome_idx = np.random.choice(range(len(self.controller.bus_genomes)),
                                              p=self.controller.genome_distro)
        # print(self.controller.genome_distro, new_bus_genome_idx)
        new_bus_genome = self.controller.bus_genomes[new_bus_genome_idx]

        # Create bus using the sampled genome
        type = int(new_bus_genome[0])
        self.add_bus(type, genome=new_bus_genome)

        self.created_buses_counter += 1
        self.beliefs.internal_table[self.bus_id + self.created_buses_counter] = {
            'arrival_time': self.controller.ticks,
            'destination': 3,
            'capacity': type,
            'vote': 0}


    def bus_creation(self):
        # initial bus creation policy
        if self.initial_creation_policy:
            if self.controller.ticks % 2 == 0:
                self.create_bus()

        # voting bus creation policy
        else:
            # TODO write the voting policy for genetic
            pass


    def compute_next(self, state, possible_actions):

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


    def send_messages(self):

        message = {'type': MainBus._MSG_UPDATE, 'content': self.beliefs.prepare_message()}

        for bus_id, probability in self.beliefs.calculate_transmission_probability().items():
            if bus_id in self.controller.buses.keys():
                if np.random.rand() <= (probability * self.genome[-1]):  # Bernoulli coin flip with probability
                    self.send_message(bus_id, message)
                    self.beliefs.update_external_table(bus_id)
                    self.num_sent_messages += 1