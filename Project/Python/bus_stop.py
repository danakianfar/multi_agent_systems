import numpy as np

class BusStop:
    def __init__(self, stop_id, name, x, y):
        self.stop_id = stop_id
        self.name = name
        self.passengers_waiting = []
        self.x = x
        self.y = y
        # self.passengers_that_arrived = [] 
        
    def add_waiting_passenger(self, passenger):
        self.passengers_waiting.append(passenger)
        
    def remove_waiting_passenger(self, passenger):
        assert passenger in self.passengers_waiting 
        self.passengers_waiting.remove(passenger)
        
    def distance(self, other):
        return np.sqrt((self.x-other.x)**2 + (self.y-other.y)**2)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.stop_id == other.stop_id
        else:
            return False