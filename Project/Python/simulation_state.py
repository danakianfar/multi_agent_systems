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


def get_leftovers(bus, controller):
    expected_capacity = get_expected_station_capacity_vector(bus)
    passengers_waiting = controller.passengers_matrix.sum(axis=1)
    return passengers_waiting - expected_capacity

def get_capacity_contribution_vector(bus, controller):
    capacity_contribution = bus.capacity - get_leftovers(bus, controller)
    # laplacian smoothing
    capacity_contribution -= capacity_contribution.min() - 1
    return capacity_contribution / capacity_contribution.sum()


def get_station_relative_importance_projection_vector(bus, controller):
    adjacency_projection = np.zeros(len(controller.bus_stop_names))

    bus_x = bus.current_stop.x
    bus_y = bus.current_stop.y

    displacement_x = np.array([stop.x - bus_x for stop in controller.bus_stops.values()])
    displacement_y = np.array([stop.y - bus_y for stop in controller.bus_stops.values()])

    displacement = np.vstack((displacement_x, displacement_y)).astype(np.float32)
    displacement_norm = np.linalg.norm(displacement, axis=0)
    displacement[:, displacement_norm > 0] = displacement[:, displacement_norm > 0] / displacement_norm[displacement_norm > 0]

    waiting_time = controller.waiting_time_matrix[bus.current_stop.stop_id, :]

    for connection in controller.connections[bus.current_stop.stop_id]:
        stop_x = controller.bus_stops[connection].x
        stop_y = controller.bus_stops[connection].y

        bus_displacement = np.array([stop_x - bus_x, stop_y - bus_y]).astype(np.float32)
        bus_displacement = bus_displacement / np.linalg.norm(bus_displacement)
        projection = np.dot(bus_displacement.T, displacement)
        projection[projection < 0] = 0
        adjacency_projection[connection] = np.sum(waiting_time * projection)

        if adjacency_projection.sum() > 0:
            adjacency_projection = adjacency_projection / adjacency_projection.sum()
    return adjacency_projection

def get_waiting_time_vector(controller):
    return controller.waiting_time_matrix.sum(axis=1) / 1000000.

def get_similarity_vector(bus, controller):
    # laplacian smoothing
    station_population = controller.waiting_time_matrix[bus.current_stop.stop_id,:]

    similarity = np.dot(controller.waiting_time_matrix.T, station_population.T)

    connections = controller.connections[bus.current_stop.stop_id]
    connection_vector = np.zeros(len(controller.bus_stop_names))
    connection_vector[connections] = 1.0

    similarity *= connection_vector

    similarity -= similarity.min() - 1
    similarity /= similarity.sum()
    return similarity

def compute_state_vector(bus):

    # bus position (one-hot)
    position_vector = get_current_bus_position_vector(bus)
    # capacity contribution vector
    capacity_contribution_vector = get_capacity_contribution_vector(bus, bus.controller)
    # current station -> all other stations cumulative waiting time
    relative_importance_vector = get_station_relative_importance_projection_vector(bus, bus.controller)
    # total waiting time in all the other stations
    waiting_time = get_waiting_time_vector(bus.controller)
    # station similarity vector
    similarity_vector = get_similarity_vector(bus, bus.controller)

    state = np.array(position_vector)
    state = np.concatenate([state, capacity_contribution_vector], axis=0)
    state = np.concatenate([state, relative_importance_vector], axis=0)
    state = np.concatenate([state, waiting_time], axis=0)
    state = np.concatenate([state, similarity_vector], axis=0)
    state = state.reshape((1, -1))

    return state
