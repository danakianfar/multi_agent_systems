import numpy as np
from collections import Counter

class SimulationState:

	# TODO proper static variables
	_positions = None # one-hot diagonal matrix, for current bus positions
	_N = None # number of stations
	_flatten = lambda l: [item for sublist in l for item in sublist]

	def __init__(self, bus):
		self.bus = bus

		if self._N is None:
			self._N = len(self.bus.controller.bus_stops)
			self._positions = np.eye(self._N)

	def get_current_bus_position(self):
		return list(self._positions[self.bus.current_stop.stop_id,:])

	def get_expected_station_capacity(self):

		bus_ids = self.bus.position_beliefs.internal_table.keys()
		bus_capacities = np.array([self.bus.controller.buses[bus_id].capacity for bus_id in bus_ids]).reshape((-1, 1))
		
		K = len(bus_ids) # num of other buses we know about
		M = np.zeros((K, self._N)) # station-bus presence distribution
		
		# for each bus, get its station (future) presence distribution
		for i, bus_id in enumerate(bus_ids):
			M[i,:] = self.bus.position_beliefs.compute_probability_distribution(bus_id, self.bus.position_beliefs.internal_table)

		return list(M.T.dot(bus_capacities)) # (NxK) x (Kx1)
 		 
	def get_stations_waiting_times(self):

		X = np.zeros((self._N, self._N)) # station i -> station j: cumulative waiting time
		for stop_id, stop in self.bus.controller.bus_stops.items():
			for passenger_id in stop.passengers_waiting:
				passenger = self.bus.controller.passengers[passenger_id]
				X[stop_id, passenger.destination.stop_id] += passenger.get_waiting_time()
		
		return SimulationState._flatten(X)

	def get_state(self):

		state = []
		state.append(self.bus.capacity) # bus capacity

		state.extend(self.get_current_bus_position()) # bus position (one-hot)

		state.extend(self.get_expected_station_capacity()) # expected station capacity

		state.extend(self.get_stations_waiting_times()) # station i -> station j cumulative waiting time

		state = np.array(state).reshape((1,-1))

		return state









		# state = np.zeros((N^2+N+1),1)

