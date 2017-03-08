
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
                    return controller.buses[bus_id].next_stop.stop_id
                else:
                    return False
            Logger.__init__(self, "bus {} logger".format(bus_id), log_one_position, save_every=save_every)
        else:
            def log_all_positions(controller):
                return {bus.bus_id:bus.next_stop.stop_id for bus in controller.buses.values()}
            Logger.__init__(self, "all bus logger", log_all_positions, save_every=save_every)