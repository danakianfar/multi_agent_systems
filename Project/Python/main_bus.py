from bus import Bus
from position_beliefs import *

class MainBus(Bus):

	_MSG_UPDATE = 'update_table'

	def init_bus(self):
		self.arrival_time = 0
		self.position_beliefs = PositionBeliefs(self)

	def execute_action(self):
		if self.current_stop:
			self.make_decisions()

		if self.controller.ticks %5 == 0 and self.bus_id == 24 and self.controller.ticks <= 50:
			self.add_bus(1)	

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
		self.arrival_time = self.controller.ticks + np.round(self.controller.get_distance(self.previous_stop.stop_id, self.next_stop.stop_id))

		# pick up passengers 
		self.pick_up_passengers()

		# send messages
		self.send_messages()

	def compute_next_station(self):
		return np.random.choice(self.connections[self.current_stop.stop_id])

	def drop_all_passengers(self):
		passengers_in_bus = [passenger[0] for passenger in self.bus_passengers]
		
		for passenger_id in passengers_in_bus:
			self.drop_off_passenger(passenger_id)


	def pick_up_passengers(self):
		passengers_at_stop = self.get_passengers_at_stop(self.current_stop.stop_id)
		
		for passenger_id in passengers_at_stop:

			if len(self.bus_passengers) == self.capacity:
				# print('Bus full')
				break

			self.pick_up_passenger(passenger_id)

	def send_messages(self):

		message = {'type': MainBus._MSG_UPDATE, 'content': self.position_beliefs.prepare_message()}

		for bus_id, probability in self.position_beliefs.calculate_transmission_probability():

			if np.rand.rand() <= probability: # Bernoulli coin flip with probability
				self.send_message(bus_id, self.position_beliefs, message)
				self.position_beliefs.update_external_table(bus_id)


