from bus import Bus
from position_beliefs import *
from simulation_state import compute_state_vector


class MainBus(Bus):
    _MSG_UPDATE = 'update_table'
    _SPREAD_TIME = 100
    _EXPLORATION_PROBABILITY = 0.05

    def init_bus(self):
        self.arrival_time = 0
        self.position_beliefs = PositionBeliefs(self)
        self.created_buses_counter = 0 # used only in bus 24
        self.destination_model = self.controller.destination_model 
        self.previous_cost = 0
        self.previous_state = None
        self.previous_action = None
        self.exploration_parameter = 1

    def execute_action(self):
        if self.current_stop: # call only when at a station
            if self.controller.ticks >= MainBus._SPREAD_TIME and self.exploration_parameter == 1:
                self.exploration_parameter = MainBus._EXPLORATION_PROBABILITY

            self.make_decisions()

        if self.controller.ticks % 5 == 0 and not self.current_stop and self.bus_id == 24 and self.controller.ticks <= 50:
            self.add_bus(1)
            self.created_buses_counter += 1 
            self.position_beliefs.internal_table[self.bus_id + self.created_buses_counter] = (self.controller.ticks, 3)


    def make_decisions(self):

        # drop all passengers
        self.drop_all_passengers()

        # Set reward from previous state
        reward = - self.controller.get_total_cost() + self.previous_cost

        # check inbox
        for tick, sender, message in self.inbox:

            if message['type'] == MainBus._MSG_UPDATE:
                self.position_beliefs.update_beliefs(sender, message['content'])
            else:
                print(message)

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
            action_vector = np.eye(1 , len(self.controller.bus_stops), self.previous_action)
            self.controller.store_replay((self.previous_state, 
                action_vector, reward, state))

        # Save current state & action
        self.previous_action = action
        self.previous_state = state


    def generate_state(self):
        state = compute_state_vector(self)
        return state

    def compute_next(self, state):
        
        best_score = - np.inf
        best_action = None

        # Evaluate every possible adjacent station to visit (including self)
        possible_actions = self.connections[self.current_stop.stop_id] + [self.current_stop.stop_id]

        # Exploration policy
        if np.random.rand() < self.exploration_parameter:
            best_action = np.random.choice(possible_actions)
            best_score = 100
        
        else: # Exploitation policy            
            for next_station in possible_actions:
                action = np.eye(1 , len(self.controller.bus_stops), next_station) # one-hot encoding of next station

                score = self.destination_model.predict(state, action)[0,0]
                # print(next_station, score)
                if score > best_score:
                    best_score = score
                    best_action = next_station

        return best_action, best_score

    def compute_next_station(self):
        # generate state
        state = self.generate_state()

        # compute next
        action, score = self.compute_next(state)

        return action, state

    def drop_all_passengers(self):
        passengers_in_bus = [passenger[0] for passenger in self.bus_passengers]

        for passenger_id in passengers_in_bus:
            self.drop_off_passenger(passenger_id)


    def select_passengers(self):
        # Create vector from O to the passenger destiantion weighted by its waiting time

        passengers = [self.controller.passengers[p] for p in self.current_stop.passengers_waiting]
        selected_passengers = []

        if len(passengers) != 0:

            V = np.array(
                [[p.get_waiting_time() * (p.destination.x - self.current_stop.x),
                  p.get_waiting_time() * (p.destination.y - self.current_stop.y)]
                 for p in passengers])

            # Create vector from O to D
            w = np.array([self.next_stop.x - self.current_stop.x, self.next_stop.y - self.current_stop.y]).T

            # Multiply V with w (equivalent to taking dot product between each v and w)
            x = np.dot(V, w)

            # Order the passengers by descending dot product
            ordering = np.argsort(-x)

            # Select the best passengers by their dot product score (if they go in the same direction of the bus) until bus capacity

            for i in range(len(ordering)):
                if x[i] > 0:
                    selected_passengers.append(passengers[ordering[i]].passenger_id)
                # If the bus is full, brake
                if len(selected_passengers) == self.capacity:
                    break

        return selected_passengers

    def pick_up_passengers(self):
        # passengers_at_stop = self.get_passengers_at_stop(self.current_stop.stop_id)
        selected_passengers = self.select_passengers()

        # for passenger_id in selected_passengers:
        #
        #     if len(self.bus_passengers) == self.capacity:
        #         # print('Bus full')
        #         break
        #
        #     self.pick_up_passenger(passenger_id)

        for passenger_id in selected_passengers:
            self.pick_up_passenger(passenger_id)

    def send_messages(self):

        message = {'type': MainBus._MSG_UPDATE, 'content': self.position_beliefs.prepare_message()}

        for bus_id, probability in self.position_beliefs.calculate_transmission_probability().items():

            if np.random.rand() <= probability:  # Bernoulli coin flip with probability
                self.send_message(bus_id, message)
                self.position_beliefs.update_external_table(bus_id)
