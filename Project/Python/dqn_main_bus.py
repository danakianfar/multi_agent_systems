from main_bus import MainBus
import numpy as np

class DQNMainBus(MainBus):

    def init_bus(self):
        self.destination_model = self.controller.destination_model
        MainBus.init_bus(self)

    def compute_next(self, state):

        # Evaluate every possible adjacent station to visit (including self)
        possible_actions = self.connections[self.current_stop.stop_id] #+ [self.current_stop.stop_id]

        # Exploration policy
        if np.random.rand() < self.exploration_parameter:
            best_action = np.random.choice(possible_actions)
            best_score = 100

        else:
            best_score = -np.inf

            # Exploitation policy
            for next_station in possible_actions:
                action = np.eye(1, len(self.controller.bus_stops), next_station) # one-hot encoding of next station

                score = self.destination_model.predict(state, action)[0,0]
                # print(next_station, score)
                if score > best_score:
                    best_score = score
                    best_action = next_station

        return best_action, best_score