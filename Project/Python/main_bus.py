from bus import Bus
from position_beliefs import *
from simulation_state import compute_state_vector
import numpy as np


class MainBus(Bus):
    _MSG_UPDATE = 'update_table'
    _SPREAD_TIME = 60
    _EXPLORATION_PROBABILITY = 0.1  # TODO reset to 0.05
    _INITIAL_BUSES = 30



    def init_bus(self):
        self.arrival_time = 0
        self.position_beliefs = PositionBeliefs(self)
        self.created_buses_counter = 0  # used only in bus 24
        self.previous_cost = 0
        self.previous_state = None
        self.previous_action = None
        self.exploration_parameter = 1
        self.state = None
        self.cum_reward = 0

    def bus_creation(self):
        # TODO choose creation policy
        self.add_bus(2)
        self.created_buses_counter += 1
        new_bus_id = self.bus_id + self.created_buses_counter
        self.position_beliefs.internal_table[new_bus_id] = (self.controller.ticks, 3)
        self.controller.buses[new_bus_id] = MainBus(new_bus_id, 2, self.controller.bus_stops[3], self.controller)

    def execute_action(self):
        if self.current_stop:  # call only when at a station
            if self.controller.ticks >= MainBus._SPREAD_TIME and self.exploration_parameter == 1:
                self.exploration_parameter = MainBus._EXPLORATION_PROBABILITY

            self.make_decisions()

        if self.controller.ticks % 2 == 0 and self.bus_id == 24 and self.created_buses_counter < MainBus._INITIAL_BUSES - 1:  # and self.created_buses_counter < 1:
            self.bus_creation()

    def make_decisions(self):

        # drop all passengers
        self.drop_all_passengers()

        # Set reward from previous state
        reward = - self.controller.get_total_cost() + self.previous_cost

        # check inbox
        for tick, sender, message in self.inbox:

            if message['type'] == MainBus._MSG_UPDATE:
                self.position_beliefs.update_beliefs(sender, message['content'])

        self.inbox.clear()

        # compute next station
        action, state = self.compute_next_station()

        # Don't do anything if told to stay put
        if action != self.current_stop.stop_id:
            self.travel_to(action)

            # update arrival time
            self.arrival_time = self.controller.ticks + np.round(
                self.controller.get_distance(self.previous_stop.stop_id, self.next_stop.stop_id))

            # pick up passengers
            self.pick_up_passengers()

        # send messages
        self.send_messages()

        # Save to replay memory ( S[t-1], A[t-1], R[t-1], S[t] )
        if self.previous_action:
            action_vector = np.eye(1, len(self.controller.bus_stops), self.previous_action)
            self.controller.store_replay((self.previous_state,
                                          action_vector, reward, state))

        # Save current state & action
        self.previous_action = action
        self.previous_state = state

    def generate_state(self):
        state = compute_state_vector(self)
        return state

    def softmax(self, w):
        e = np.exp(np.array(w))
        dist = e / np.sum(e)
        return dist

    def compute_next(self, state):

        best_score = - np.inf
        best_action = None

        # Evaluate every possible adjacent station to visit (including self)
        possible_actions = self.connections[self.current_stop.stop_id]  # + [self.current_stop.stop_id]

        # Exploration policy
        if np.random.rand() < self.exploration_parameter:
            best_action = np.random.choice(possible_actions)
            best_score = 100

        else:
            scores = []

            for next_station in possible_actions:
                scores.append( state[0, 24 + next_station] + \
                               state[0, 2 * 24 + next_station] + \
                               state[0, 3 * 24 + next_station] + \
                               state[0, 4 * 24 + next_station])

            soft_scores = self.softmax(scores)

            next_idx = np.random.choice(range(len(scores)), p=soft_scores)

            best_score = soft_scores[next_idx]
            best_action = possible_actions[next_idx]

        return best_action, best_score

    def compute_next_station(self):
        # generate state
        state = self.generate_state()
        self.state = state

        # compute next
        action, score = self.compute_next(state)

        return action, state

    def drop_all_passengers(self):
        passengers_in_bus = [passenger[0] for passenger in self.bus_passengers]
        for passenger_id in passengers_in_bus:
            self.drop_off_passenger(passenger_id)

    def select_passengers(self):
        # Create vector from O to the passenger destiantion weighted by its waiting time
        next_stop_id = self.next_stop.stop_id
        passengers = [self.controller.passengers[p] for p in self.current_stop.passengers_waiting]
        scores = np.array([p.get_attractivity(next_stop_id) for p in passengers])
        selected_passengers = []

        if len(passengers) != 0:
            ordering = np.argsort(-scores)
            # Select the best passengers by their dot product score (if they go in the same direction of the bus) until bus capacity

            for i in ordering:
                if scores[i] > 0:
                    passenger = passengers[i]
                    selected_passengers.append(passenger.passenger_id)
                # If the bus is full, break
                if len(selected_passengers) == self.capacity:
                    break

        return selected_passengers

    def pick_up_passengers(self):
        # passengers_at_stop = self.get_passengers_at_stop(self.current_stop.stop_id)
        selected_passengers = self.select_passengers()

        for passenger_id in selected_passengers:
            self.pick_up_passenger(passenger_id)

    def send_messages(self):

        message = {"type": MainBus._MSG_UPDATE, "content": self.position_beliefs.prepare_message()}

        for bus_id, probability in self.position_beliefs.calculate_transmission_probability().items():

            if np.random.rand() <= probability * 0.01:  # Bernoulli coin flip with probability
                self.send_message(bus_id, message)
                self.position_beliefs.update_external_table(bus_id)
