from main_bus import MainBus
import numpy as np

class DQNMainBus(MainBus):
    _EXPLORATION_PARAMETER = 0.05

    def __init__(self, bus_id, bus_type, init_stop, controller):
        MainBus.__init__(self, bus_id, bus_type, init_stop, controller)
        self.exploration_probability = DQNMainBus._EXPLORATION_PARAMETER
        self.movement_policy_switch_time = MainBus._DEFAULT_MOVEMENT_SWITCH_TIME
        self.initial_buses = MainBus._DEFAULT_INITIAL_BUS_COUNT
        self.destination_model = self.controller.destination_model
        self.previously_delivered = 0
        self.previous_state = None
        self.previous_action = None

    def init_bus(self):
        MainBus.init_bus(self)


    def compute_next(self, state, possible_actions):
        best_score = -np.inf

        for next_station in possible_actions:
            action = np.eye(1, len(self.controller.bus_stops), next_station) # one-hot encoding of next station

            score = self.destination_model.predict(state, action)[0,0]
            # print(next_station, score)
            if score > best_score:
                best_score = score
                best_action = next_station

        return best_action, best_score

    def make_decisions(self):

        # drop all passengers
        self.drop_all_passengers()

        reward = self.controller.num_passengers_delivered - self.previously_delivered
        self.previously_delivered = self.controller.num_passengers_delivered

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

        # Save to replay memory ( S[t-1], A[t-1], R[t-1], S[t] )
        if self.previous_action:
            action_vector = np.eye(1, len(self.controller.bus_stops), self.previous_action)
            self.controller.store_replay((self.previous_state,
                                          action_vector, reward, state))

        # Save current state & action
        self.previous_action = action
        self.previous_state = state