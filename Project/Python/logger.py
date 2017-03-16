
class Logger:
    def __init__(self, name, function, save_every=1):
        self.name = name
        self.function = function
        self.save_every = save_every


class BusPositionLogger(Logger):
    def __init__(self, bus_id=None, save_every=1):

        if bus_id:
            def log_one_position(controller):
                if bus_id in controller.buses:
                    return controller.buses[bus_id].next_stop
                else:
                    return False
            Logger.__init__(self, 'Bus {} Logger'.format(bus_id), log_one_position, save_every=save_every)
        else:
            def log_all_positions(controller):
                return {bus.bus_id:bus.next_stop for bus in controller.buses.values()}
            Logger.__init__(self, 'All Buses Logger', log_all_positions, save_every=save_every)

class ExecutionCostLogger(Logger):

    def __init__(self, save_every=1):

        def get_execution_cost(controller):
            return controller.get_execution_cost()

        Logger.__init__(self, 'Execution Cost Logger', get_execution_cost, save_every=save_every)

class TotalWaitingCostLogger(Logger):

    def __init__(self, save_every=1):

        def get_waiting_cost(controller):
            return controller.get_waiting_cost()

        Logger.__init__(self, 'Total Waiting Cost Logger', get_waiting_cost, save_every=save_every)


class AverageWaitingCostLogger(Logger):
    def __init__(self, save_every=1):

        def get_average_waiting_cost(controller):
            n_passengers = controller.get_number_of_passengers()
            if n_passengers > 0:
                return controller.get_waiting_cost() / n_passengers
            else :
                return 0

        Logger.__init__(self, 'Average Waiting Cost Logger', get_average_waiting_cost, save_every=save_every)


class NPassengersLogger(Logger):
    def __init__(self, save_every=1):

        def get_n_passengers(controller):
            n_passengers = controller.get_number_of_passengers()
            return n_passengers

        Logger.__init__(self, 'Number of Passengers Logger', get_n_passengers, save_every=save_every)


class TotalCostLogger(Logger):
    def __init__(self, save_every=1):
        Logger.__init__(self, 'Total Cost Logger', lambda c: c.get_total_cost(), save_every=save_every)

class StateLogger(Logger):
    def __init__(self, bus_id=None, save_every=1):

        if bus_id:
            def log_one_state(controller):
                if bus_id in controller.buses:
                    bus = controller.buses[bus_id]
                    if bus.current_stop:
                        return bus.generate_state()
                    else:
                        return False
                else:
                    return False

            Logger.__init__(self, 'Bus {} State Logger'.format(bus_id), log_one_state, save_every=save_every)