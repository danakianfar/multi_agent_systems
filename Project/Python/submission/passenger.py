

class Passenger:
    def __init__(self, passenger_id, source, destination, spawn_time, controller):
        self.passenger_id = passenger_id
        self.destination = destination
        self.source = source
        self.spawn_time = spawn_time
        self.current_stop = source
        self.controller = controller
        
    def get_waiting_time(self):
        return self.controller.ticks-self.spawn_time

    def get_attractivity(self, next_stop):
        urgency = self.controller.average_minumum_delivery_time + self.get_waiting_time()
        attractivity = self.controller.attractivity[self.current_stop.stop_id, self.destination.stop_id, next_stop]
        return urgency * attractivity

    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.passenger_id == other.passenger_id
        else:
            return False