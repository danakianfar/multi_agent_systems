from controller import *

class Bus:

    _bus_type_capacity = {1:12, 2:60, 3:150}

    def __init__(self, bus_id, bus_type, init_stop, controller):
        self.bus_id = bus_id
        self.bus_type = bus_type
        self.capacity = Bus._bus_type_capacity[self.bus_type]
        
        self.inbox = [] # (tick, sender, message)
        self.bus_passengers = [] # (passenger_id, destination_bus_stop)
        self.previous_stop = None
        self.current_stop = init_stop # central station has to be setted as init_stop
        self.next_stop = None
        
        self.x = init_stop.x
        self.y = init_stop.y
        
        self.progress = 0
        
        self.controller = controller
        
        self.connections = controller.connections
        
        self.init_bus()
    
    def update(self):
        if self.previous_stop and self.next_stop:
            distance = self.controller.adj_matrix[self.previous_stop.stop_id, self.next_stop.stop_id]
            self.x = self.previous_stop.x + (self.next_stop.x - self.previous_stop.x) * self.progress
            self.y = self.previous_stop.y + (self.next_stop.y - self.previous_stop.y) * self.progress
        else:
            self.x = self.current_stop.x
            self.y = self.current_stop.y
            
        self.execute_action()
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.bus_id == other.bus_id
        else:
            return False
    
    def add_bus(self, vehicle_type):
        self.controller.add_bus(vehicle_type)
        
    def travel_to(self, bus_stop):
        self.controller.travel_to(self, bus_stop)
        
    def pick_up_passenger(self, passenger_id):
        self.controller.pick_up_passenger(self, passenger_id)

    def drop_off_passenger(self, passenger_id):
        self.controller.drop_off_passenger(self, passenger_id)
        
    def get_passengers_at_stop(self, stop_id):
        return [i for i in self.controller.bus_stops[stop_id].passengers_waiting] # copy

    def send_message(self, bus_id, message):
        self.controller.send_message(self, bus_id, message)
        
    def init_bus(self):
        raise NotImplementedError
    
    def execute_action(self):
        raise NotImplementedError


class TestBus(Bus):
    
    def init_bus(self):
        pass
    
    def execute_action(self):
        if self.current_stop:
            self.travel_to(np.random.choice(self.connections[self.current_stop.stop_id]))
            
#        if len(self.inbox)>0:
#            print('INBOX:{}'.format(self.inbox))
#            self.inbox = []
            
        if self.controller.ticks %5 == 0 and self.bus_id == 24 :
            self.add_bus(1)
            
            
class AmsterdamBus(Bus):
    
    fixed_routes = [[3,16,11,1,19,23,13,10,4,3],
                [3,4,5,17,7,1,23,14,0,22,21,20,3],
                [3,9,8,6,8,2,8,9,3],
                [3,9,20,12,15,18,15,0,22,21,20,3]]

    
    def init_bus(self): # [id1, id2, ... idn] id's of stations to visit in route
        self.fixed_route = np.random.choice(AmsterdamBus.fixed_routes)
        self.current_station_idx = 0
        
    def next_station(self):
        if self.current_station_idx >= len(self.fixed_route)-1:
            print('eh')
            self.current_station_idx = 0
        self.current_station_idx +=1
        return self.fixed_route[self.current_station_idx]
    
    def execute_action(self):
        if self.current_stop:
            self.travel_to(self.next_station())
        
        
    