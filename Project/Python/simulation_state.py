import numpy as np
from scipy.special import expit

def get_current_bus_position_vector(bus):
    N = len(bus.controller.bus_stop_names)
    return np.eye(N)[bus.current_stop.stop_id, :]

def get_expected_station_capacity_vector(bus):
    bus_ids = bus.beliefs.internal_table.keys()
    bus_capacities = np.array([bus.beliefs.internal_table[bus_id]['capacity'] for bus_id in bus_ids]).reshape((-1, 1))

    N = len(bus.controller.bus_stop_names)
    K = len(bus_ids)  # num of other buses we know about
    M = np.zeros((K, N))  # station-bus presence distribution

    # for each bus, get its station (future) presence distribution
    for i, bus_id in enumerate(bus_ids):
        M[i, :] = bus.beliefs.compute_internal_probability(bus_id)

    return M.T.dot(bus_capacities).reshape(-1)  # (NxK) x (Kx1)


def get_leftovers(bus, controller):
    expected_capacity = get_expected_station_capacity_vector(bus)
    passengers_waiting = controller.passengers_matrix.sum(axis=1)
    return passengers_waiting - expected_capacity

def expected_capacity_contribution(bus, controller):
    fill_percentage = get_leftovers(bus, controller)/bus.capacity
    connections = np.zeros(len(controller.bus_stop_names))
    connections[controller.connections[bus.current_stop.stop_id]] = 1
    scores = (expit(fill_percentage * connections)-0.5)*2.0
    return scores


def get_station_relative_importance_projection_vector(bus, controller):
    stop_id = bus.current_stop.stop_id
    #
    # for adj_id in controller.connections[stop_id]:
    #     for passenger_id in controller.bus_stops[stop_id].passengers_waiting:
    #         scores[adj_id] += controller.passengers[passenger_id].get_attractivity(adj_id)
    urgency = controller.waiting_time_matrix[stop_id]
    urgency += controller.passengers_matrix[stop_id] * controller.average_minumum_delivery_time

    attractivity = controller.attractivity[stop_id]
    scores = urgency.dot(attractivity)
    s = scores.sum()
    if s > 0:
        scores /= s

    return scores

def get_waiting_time_distribution_vector(bus, controller):
    stop_id = bus.current_stop.stop_id
    waiting_time = controller.waiting_time_matrix.sum(axis=1)
    attractivity = controller.attractivity[stop_id]
    scores = waiting_time.dot(attractivity)
    s = scores.sum()
    if s > 0:
        scores /= s
    return scores

def get_similarity_vector(bus, controller):
    similarity = controller.passengers_matrix[bus.current_stop.stop_id].dot(controller.similarity_matrix)
    connections = np.zeros(len(controller.bus_stop_names))
    connections[controller.connections[bus.current_stop.stop_id]] = 1
    similarity = similarity
    scores = similarity.dot(controller.passengers_matrix.T)
    scores = scores * connections
    s = scores.sum()
    if s > 0:
        scores /= s
    return scores

def compute_state_vector(bus):

    # bus position (one-hot)
    position_vector = get_current_bus_position_vector(bus)
    # capacity contribution vector
    capacity_contribution_vector = expected_capacity_contribution(bus, bus.controller)
    # current station -> all other stations cumulative waiting time
    relative_importance_vector = get_station_relative_importance_projection_vector(bus, bus.controller)
    # total waiting time in all the other stations
    waiting_time = get_waiting_time_distribution_vector(bus, bus.controller)
    # station similarity vector
    similarity_vector = get_similarity_vector(bus, bus.controller)

    state = np.array(position_vector)
    state = np.concatenate([state, capacity_contribution_vector], axis=0)
    state = np.concatenate([state, relative_importance_vector], axis=0)
    state = np.concatenate([state, waiting_time], axis=0)
    state = np.concatenate([state, similarity_vector], axis=0)
    state = state.reshape((1, -1))

    return state
