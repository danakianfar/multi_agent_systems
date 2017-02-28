from functools import partial
import numpy as np

from bus import Bus, TestBus
from action import *
from bus_stop import *
from passenger import *


class Controller:
    
    def __init__(self, bus_class=Bus , debug=False):
        self.ticks = 0
        self.buses = {}
        self.last_bus_id = 23
        self.bus_class = bus_class
        
        self.total_cost = 0
        self.total_travel_time = 0
        self.communication_cost = 0
        
        self.debug = debug
        
        self.bus_stops = {}

        self.init_map()
        
        self.actions = ActionHeap()
        
    def setup(self):
        self.add_bus(1)
                
    
    def init_map(self):
        amsterdam_bus_stops_names = ["Amstel", "Amstelveenseweg", "Buikslotermeer","Centraal","Dam",
                                     "Evertsenstraat","Floradorp","Haarlemmermeerstation","Hasseltweg",
                                     "Hendrikkade","Leidseplein","Lelylaan","Muiderpoort","Museumplein",
                                     "RAI","SciencePark","Sloterdijk","Surinameplein","UvA","VU","Waterlooplein",
                                     "Weesperplein","Wibautstraat","Zuid"]

        xs = [27, 11, 31, 22, 21, 11, 25, 11, 26, 25, 17, 4, 31, 17, 19, 35, 6, 10, 38, 14, 23, 24, 25, 15]
        ys = [7, 4, 30, 21, 18, 18, 30, 9, 24, 18, 14, 12, 13, 11, 3, 10, 26, 13, 11, 1, 16, 13, 11, 4]

        self.connections = [[14, 15, 22], [7, 11, 19, 23], [8], [4, 9, 16, 20], [3, 5, 10], [4, 10, 16, 17], 
                            [8], [1, 13, 17], [2, 6, 9], [3, 8, 20], [4, 5, 13, 17, 21], [1, 16, 17], 
                            [15, 20, 22], [7, 10, 22, 23], [0, 23], [0, 12, 18], [3, 5, 11], [5, 7, 10, 11], 
                            [15], [1, 23], [3, 9, 12, 21], [10, 20, 22], [0, 12, 13, 21], [1, 13, 14, 19]] 

        self.adj_matrix = np.ones((len(xs), len(xs)))*-np.inf
        
        for i in range(len(self.connections)):
            # Creates bus stop and appends it to the list
            self.bus_stops[i] = BusStop(i, amsterdam_bus_stops_names[i], xs[i], ys[i])
            orig = i
            # Creates the bidirectional connection between stop orig and stop dest
            for dest in self.connections[i]:
                self.adj_matrix[orig, dest] = np.sqrt((xs[orig] - xs[dest])**2 + (ys[orig] - ys[dest])**2)
        
    
    def add_bus(self, vehicle_type):
        def bus_creation(vehicle_type):
            # increment the id
            self.last_bus_id += 1 
            # create the bus
            new_bus = self.bus_class(self.last_bus_id, vehicle_type,  self.bus_stops[3], self)
            # add it to the fleet
            self.buses[self.last_bus_id] =  new_bus
        
        bus_creation_action = Action(self.ticks + 1, partial(bus_creation, vehicle_type))
        
        self.actions.push(bus_creation_action)
        
    def travel_to(self, bus, bus_stop):
        assert bus.current_stop
        assert bus_stop in self.connections[bus.current_stop.stop_id]
        
        def start(bus):
            bus.previous_stop = bus.current_stop
            bus.current_stop = None
            bus.next_stop = self.bus_stops[bus_stop]
            bus.progress = 0.3
            
        def arrive(bus):
            bus.current_stop = bus.next_stop
            bus.next_stop = None
            bus.progress = 0
            
        start_action = Action(self.ticks, partial(start, bus))
        arrive_action = Action(self.ticks + self.adj_matrix[bus.current_stop.stop_id][bus_stop], partial(arrive, bus))
        
        self.actions.push(start_action)
        self.actions.push(arrive_action)
        
    def pick_up_passenger(self, bus, passenger_id):
        def pick_up():
            print("TO IMPLEMENT PASS")
            
        pick_up_action = Action(self.ticks, pick_up)
        
        self.actions.push(action)
        
    def send_message(self, sender, bus_id, message):
        
        def send_message(receiver, time, sender_id, message):
            receiver.inbox.append((time, sender_id, message))
         
        send_action = Action(self.ticks, partial(send_message, self.buses[bus_id], self.ticks, sender.bus_id ,message))
        
        self.actions.push(send_action)
        
            
    def step(self):
        while self.actions.peek() <= self.ticks and self.actions.peek() != -1:
            action = self.actions.pop()
            action()   
        
        for bus in self.buses.values():
            bus.update()
            
        while self.actions.peek() == self.ticks and self.actions.peek() != -1:
            action = self.actions.pop()
            action()
          
        if self.debug:
            print('ticks:{}'.format(self.ticks))
            self.actions.plot()
            print('\n\n')
        
        self.ticks += 1
