from bus import Bus
from position_beliefs import *
from simulation_state import SimulationState


class MainBus(Bus):
    _MSG_UPDATE = 'update_table'

    def init_bus(self):
        self.arrival_time = 0
        self.position_beliefs = PositionBeliefs(self)
        self.created_buses_counter = 0 # used only in bus 24

    def execute_action(self):
        if self.current_stop:
            self.make_decisions()

        if self.controller.ticks % 5 == 0 and not self.current_stop and self.bus_id == 24 and self.controller.ticks <= 50:
            self.add_bus(1)
            self.created_buses_counter += 1 
            self.position_beliefs.internal_table[self.bus_id + self.created_buses_counter] = (self.controller.ticks, 3)


    def make_decisions(self):

        # drop all passengers
        self.drop_all_passengers()

        # check inbox
        for tick, sender, message in self.inbox:

            if message['type'] == MainBus._MSG_UPDATE:
                self.position_beliefs.update_beliefs(sender, message['content'])
            else:
                print(message)

        self.inbox.clear()

        # compute next station
        self.travel_to(self.compute_next_station())

        # update arrival time
        self.arrival_time = self.controller.ticks + np.round(
            self.controller.get_distance(self.previous_stop.stop_id, self.next_stop.stop_id))

        # pick up passengers
        self.pick_up_passengers()

        # send messages
        self.send_messages()

    def generate_state(self):
        state = SimulationState(self)
        return state.get_state()

    def compute_next(self, state):
        # TODO neural code goes here
        return np.random.choice(self.connections[self.current_stop.stop_id])

    def compute_next_station(self):
        # generate state
        state = self.generate_state()

        # compute next
        next = self.compute_next(state)

        return next

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
