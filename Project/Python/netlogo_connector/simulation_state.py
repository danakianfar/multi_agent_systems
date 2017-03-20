import numpy as np

def get_current_bus_position_vector(bus):
    N = len(bus.controller.bus_stop_names)
    return np.eye(N)[bus.current_stop.stop_id, :]


def get_expected_station_capacity_vector(bus):
    bus_ids = bus.position_beliefs.internal_table.keys()
    bus_capacities = np.array([bus.controller.buses[bus_id].capacity for bus_id in bus_ids]).reshape((-1, 1))

    N = len(bus.controller.bus_stop_names)
    K = len(bus_ids)  # num of other buses we know about
    M = np.zeros((K, N))  # station-bus presence distribution

    # for each bus, get its station (future) presence distribution
    # TODO do all in one step
    for i, bus_id in enumerate(bus_ids):
        M[i, :] = bus.position_beliefs.compute_internal_probability(bus_id)

    return M.T.dot(bus_capacities).reshape(-1)  # (NxK) x (Kx1)


def get_stations_waiting_times_vector(controller):
    return controller.waiting_time_matrix.reshape(-1)


def compute_state_vector(bus):
    # bus capacity
    state = np.array([bus.capacity])
    # bus position (one-hot)
    position_vector = get_current_bus_position_vector(bus)
    # expected station capacity
    expected_capacity_vector = get_expected_station_capacity_vector(bus)
    # station i -> station j cumulative waiting time
    waiting_vector = get_stations_waiting_times_vector(bus.controller)

    state = np.concatenate([state, position_vector], axis=0)
    state = np.concatenate([state, expected_capacity_vector], axis=0)
    state = np.concatenate([state, waiting_vector], axis=0)
    state = state.reshape((1, -1))

    return state
