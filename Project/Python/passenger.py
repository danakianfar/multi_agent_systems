

class Passenger:
    def __init__(self, passenger_id, source, destination, spawn_time):
        self.passenger_id = passenger_id
        self.destination = destination
        self.source = source
        self.spawn_time = spawn_time
        
    def get_waiting_time(current_time):
        return current_time-self.spawn_time
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.passenger_id == other.passenger_id
        else:
            return False