from bus import Bus
from beliefs import *
from simulation_state import compute_state_vector
from simulation_state import get_leftovers
import numpy as np


class MainBus(Bus):
    _MSG_UPDATE = 'update_table'
    _DEFAULT_INITIAL_BUS_COUNT = 30
    _DEFAULT_MOVEMENT_SWITCH_TIME = 60
    _UPDATE_VOTES_PERCENTAGE_REQUIRED = 0.5
    _ALLOWED_WAITING_PASSENGERS = 50
    _WAITING_TIME_VOTING_SMOOTHING = 0.001
    _MINIMUM_TIME_BEWEEN_VOTES = 1000#10
    _SENDING_PROBABILITY_SMOOTHING = 0.1#0.1
    _CREATE_EVERY = 2

    def __init__(self, bus_id, bus_type, init_stop, controller):
        Bus.__init__(self, bus_id, bus_type, init_stop, controller)
        # tunable parameters
        self.exploration_probability = 0
        self.movement_policy_switch_time = MainBus._DEFAULT_MOVEMENT_SWITCH_TIME
        self.initial_buses = MainBus._DEFAULT_INITIAL_BUS_COUNT


    def init_bus(self):
        self.arrival_time = 0
        self.beliefs = Beliefs(self)
        self.created_buses_counter = 0  # used only in bus 24
        self.exploration_parameter = 1
        self.state = None
        self.initial_creation_policy = True
        self.initial_movement_policy = True

        # internal performance evaluation
        self.cum_reward = 0
        self.num_sent_messages = 0
        self.last_vote = 0

    def create_bus(self, type):
        self.add_bus(2)
        self.created_buses_counter += 1
        new_bus_id = self.bus_id + self.created_buses_counter

        self.beliefs.internal_table[new_bus_id] = {
            'arrival_time': self.controller.ticks,
            'destination': 3,
            'capacity': type,
            'vote': -1}

    def bus_creation(self):

        # initial bus creation policy
        if self.initial_creation_policy:
            if self.controller.ticks % MainBus._CREATE_EVERY == 0:
                self.create_bus(2)

        # voting bus creation policy
        else:
            vote_result = self.check_votes()
            type = 0
            if vote_result < (0 + Bus._bus_type_capacity[1]) / 2.0:
                pass
            elif vote_result < (Bus._bus_type_capacity[1] + Bus._bus_type_capacity[2]) / 2.0:
                type = 1
            elif vote_result < (Bus._bus_type_capacity[2] + Bus._bus_type_capacity[3]) / 2.0:
                type = 2
            else:
                type = 3

            if type > 0:
                self.create_bus(type)
                self.last_vote = self.controller.ticks + MainBus._MINIMUM_TIME_BEWEEN_VOTES


    def execute_action(self):
        # switch from the random initial policy to the rational one
        if self.controller.ticks >= self.movement_policy_switch_time:
            self.initial_movement_policy = False

        # switch from initial creation policy to voting policy
        if self.created_buses_counter >= self.initial_buses - 1:
            self.initial_creation_policy = False

        # make decisions every time the bus is at a station
        if self.current_stop:
            self.make_decisions()

        # bus 24 is in charge of creating new buses
        if self.bus_id == 24:
            self.bus_creation()


    def check_votes(self):
        new_votes = 1
        vote = self.vote()
        for bus_id in self.beliefs.internal_table.keys():
            if self.beliefs.internal_table[bus_id]['arrival_time'] > self.last_vote and self.beliefs.internal_table[bus_id]['vote'] > 0:
                new_votes += 1
            vote += self.beliefs.internal_table[bus_id]['vote']
            # return the average wanted capacity

        if new_votes > len(self.beliefs.internal_table) * MainBus._UPDATE_VOTES_PERCENTAGE_REQUIRED:
            vote /= len(self.beliefs.internal_table) + 1
        else:
            vote = 0
        return vote


    def make_decisions(self):

        # drop all passengers
        self.drop_all_passengers()

        # check inbox
        for tick, sender, message in self.inbox:

            if message['type'] == MainBus._MSG_UPDATE:
                self.beliefs.update_beliefs(sender, message['content'])

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

    def generate_state(self):
        state = compute_state_vector(self)
        return state

    def softmax(self, w):
        e = np.exp(np.array(w))
        dist = e / np.sum(e)
        return dist

    def compute_next(self, state, possible_actions):
        scores = []

        for next_station in possible_actions:
            scores.append(1 * state[0, 24 + next_station] + \
                          1 * state[0, 2 * 24 + next_station] + \
                          1 * state[0, 3 * 24 + next_station] + \
                          1 * state[0, 4 * 24 + next_station])

        soft_scores = self.softmax(scores)

        next_idx = np.random.choice(range(len(scores)), p=soft_scores)

        best_score = soft_scores[next_idx]
        best_action = possible_actions[next_idx]
        return best_action, best_score

    def get_next_station(self, state):

        best_score = - np.inf
        best_action = None

        # Evaluate every possible adjacent station to visit (including self)
        possible_actions = self.connections[self.current_stop.stop_id]  # + [self.current_stop.stop_id]

        # Exploration policy at the beginning and at random if exploration_parameter > 0
        if np.random.rand() < self.exploration_parameter or self.initial_movement_policy:
            best_action = np.random.choice(possible_actions)
            best_score = 100
        else:
            best_action, best_score = self.compute_next(state, possible_actions)

        return best_action, best_score

    def compute_next_station(self):
        # generate state
        state = self.generate_state()
        self.state = state

        # compute next
        action, score = self.get_next_station(state)

        return action, state

    def drop_all_passengers(self):
        passengers_in_bus = [passenger[0] for passenger in self.bus_passengers]
        delivered = 0
        for passenger_id in passengers_in_bus:
            delivered += self.drop_off_passenger(passenger_id)
        return delivered

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

    def vote(self):
        leftovers = get_leftovers(self, self.controller) - MainBus._ALLOWED_WAITING_PASSENGERS
        leftovers[leftovers<0] = 0
        vote = leftovers.sum()
        average_waiting_time = self.controller.waiting_time_matrix.mean()
        smoothed_vote = (1 - 1 / (MainBus._WAITING_TIME_VOTING_SMOOTHING * average_waiting_time + 1)) * vote
        return smoothed_vote


    def send_messages(self):

        message = {"type": MainBus._MSG_UPDATE, "content": self.beliefs.prepare_message()}

        for bus_id, probability in self.beliefs.calculate_transmission_probability().items():

            if np.random.rand() <= probability*self._SENDING_PROBABILITY_SMOOTHING:  # Bernoulli coin flip with probability
                self.send_message(bus_id, message)
                self.beliefs.update_external_table(bus_id)
                self.num_sent_messages += 1
                #print(self.bus_id, 'sending message ', str(message))

