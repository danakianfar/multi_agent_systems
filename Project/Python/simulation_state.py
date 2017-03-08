import numpy as np
from collections import Counter

class SimulationState:

	_positions = None # one-hot diagonal matrix, for current bus positions
	_N = -1 # number of stations
	_flatten = lambda l: [item for sublist in l for item in sublist]

	def __init__(self, bus):
		self.bus = bus

		if _N is -1:
			_N = len(self.bus.controller.bus_stops)
			_positions = np.eye(_N)

	def get_current_bus_position(self):
		return list(_positions[self.bus.current_stop.stop_id,:])

	def get_expected_station_capacity(self):

		bus_ids = self.bus.position_beliefs.internal_table
		bus_capacities = np.array([self.bus.controller.buses{bus_id}.capacity for bus_id in bus_ids])
		
		K = len(bus_ids) # num of other buses we know about
		M = np.zeros(K, _N) # station-bus presence distribution
		
		# for each bus, get its station (future) presence distribution
		for i, bus_id in enumerate(bus_ids):
			M[i,:] = self.bus.position_beliefs.compute_probability_distribution(bus_id, self.bus.position_beliefs.internal_table)

		return list(M.T.dot(bus_capacities)) # (NxK) x (Kx1)
 		 
	def get_stations_waiting_times(self):

		X = np.zeros((_N, _N)) # station i -> station j: cumulative waiting time
		for stop_id, stop in self.bus.controller.bus_stops.items():
			for passenger in stop.passengers_waiting:
				X[stop_id,passenger.destination] += [self.bus.controller.passenger.ticks - spawn_time]
		
		return _flatten(X)

	def get_state(self):

		state = []
		state.append(self.bus.capacity) # bus capacity

		state.extend(get_current_bus_position) # bus position (one-hot)

		state.extend(get_expected_station_capacity()) # expected station capacity

		state.extend(get_stations_waiting_times)

		state = np.array(state).reshape(-1,1)

		return state









		# state = np.zeros((N^2+N+1),1)

