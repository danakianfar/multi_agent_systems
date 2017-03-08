from functools import partial
import numpy as np
import pandas as pd
from bus import Bus, TestBus
from action import *
from bus_stop import *
from passenger import *


class Controller:

    bus_stop_names = {'Amstel': 0, 'Amstelveenseweg': 1, 'Buikslotermeer': 2, 'Centraal': 3,
     'Dam': 4, 'Evertsenstraat': 5, 'Floradorp': 6, 'Haarlemmermeerstation': 7, 'Hasseltweg': 8,
     'Hendrikkade': 9, 'Leidseplein': 10, 'Lelylaan': 11, 'Muiderpoort': 12, 'Museumplein': 13,
     'RAI': 14, 'SciencePark': 15, 'Sloterdijk': 16, 'Surinameplein': 17, 'UvA': 18,
     'VU': 19, 'Waterlooplein': 20, 'Weesperplein': 21,'Wibautstraat': 22, 'Zuid': 23}
    
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
        self.passengers = {}
        self.passenger_count = 0

        self.init_map()
        
        self.actions = ActionHeap()
        self.passenger_actions = ActionHeap()
        
    def setup(self):
        self.add_bus(1)
        self.init_daily_ridership()
                
    def init_daily_ridership(self):

        def passengers_arrival_at_tick(row):
            
            def passengers_arrival(passengers):
                
                for passenger in passengers: 
                    passenger.source.add_waiting_passenger(passenger)
                    
                    
            tick = row['Ticks']  # When the passengers arrive (every 15 ticks)
            source_name = row['FROM'] # source station
            destination_names_counts = row[Controller.bus_stop_names.keys()][row[Controller.bus_stop_names.keys()] > 0] # Get destination-passenger_count tuples where passenger_count > 0
            
            # For each destination-passenger tuple
            passengers = []

            for destination_name, passenger_count in destination_names_counts.items():
                source = self.bus_stops[Controller.bus_stop_names[source_name]]
                destination = self.bus_stops[Controller.bus_stop_names[destination_name]]
                
                
                for i in range(passenger_count): 
                    passenger = Passenger(self.passenger_count , source, destination, tick)
                    self.passengers[passenger.passenger_id] = passenger
                    self.passenger_count +=1 
                    passengers.append(passenger)


            passengers_arrival_action = Action(tick, partial(passengers_arrival, passengers))
            self.passenger_actions.push(passengers_arrival_action)

        df = pd.read_pickle('./passengers.dataframe')

        # Map to each row in dataframe (each arrival)
        df.apply(passengers_arrival_at_tick, axis=1)

    
    def init_map(self):

        xs = [27, 11, 31, 22, 21, 11, 25, 11, 26, 25, 17, 4, 31, 17, 19, 35, 6, 10, 38, 14, 23, 24, 25, 15]
        ys = [7, 4, 30, 21, 18, 18, 30, 9, 24, 18, 14, 12, 13, 11, 3, 10, 26, 13, 11, 1, 16, 13, 11, 4]

        self.connections = [[14, 15, 22], [7, 11, 19, 23], [8], [4, 9, 16, 20], [3, 5, 10], [4, 10, 16, 17], 
                            [8], [1, 13, 17], [2, 6, 9], [3, 8, 20], [4, 5, 13, 17, 21], [1, 16, 17], 
                            [15, 20, 22], [7, 10, 22, 23], [0, 23], [0, 12, 18], [3, 5, 11], [5, 7, 10, 11], 
                            [15], [1, 23], [3, 9, 12, 21], [10, 20, 22], [0, 12, 13, 21], [1, 13, 14, 19]] 

        self.adj_matrix = np.ones((len(xs), len(xs)))*-np.inf
        
        for stop_name, i in Controller.bus_stop_names.items():
            # Creates bus stop and appends it to the list
            self.bus_stops[i] = BusStop(i, stop_name, xs[i], ys[i])
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
            new_bus.current_stop = self.bus_stops[3] # everyone starts at Amsterdam Centraal
            # add it to the fleet
            self.buses[self.last_bus_id] =  new_bus
        
        bus_creation_action = Action(self.ticks + 1, partial(bus_creation, vehicle_type))
        
        self.actions.push(bus_creation_action)
        
    def travel_to(self, bus, bus_stop):
        assert bus.current_stop
        assert bus_stop in self.connections[bus.current_stop.stop_id]
        
        bus.previous_stop = bus.current_stop
        bus.next_stop = self.bus_stops[bus_stop]

        def start(bus):
            bus.current_stop = None
            bus.progress = 0.3
            
        def arrive(bus):
            bus.current_stop = bus.next_stop
            bus.next_stop = None
            bus.progress = 0
            
        start_action = Action(self.ticks+0.5, partial(start, bus))
        arrive_action = Action(self.ticks + self.adj_matrix[bus.previous_stop.stop_id , bus.next_stop.stop_id], partial(arrive, bus))
        
        self.actions.push(start_action)
        self.actions.push(arrive_action)

    def get_distance(self, from_station, to_station):
        return self.adj_matrix[from_station,to_station]
        
    def pick_up_passenger(self, bus, passenger_id):
        assert bus.current_stop == self.passengers[passenger_id].current_stop

        # def pick_up(bus, passenger):
            # unload from station
        self.bus_stops[bus.current_stop.stop_id].remove_waiting_passenger(self.passengers[passenger_id])

        # print('Picking up %s, at %s, capacity %s' % (passenger_id, bus.current_stop.stop_id, len(bus.bus_passengers)))

        # load to bus
        bus.bus_passengers.append((passenger_id, self.passengers[passenger_id].destination.stop_id))
        self.passengers[passenger_id].current_stop = None
            
        # pick_up(bus, self.passengers[passenger_id])
        # pick_up_action = Action(self.ticks, partial(pick_up,  bus, self.passengers[passenger_id]))
        # self.actions.push(pick_up_action)


    def drop_off_passenger(self, bus, passenger_id):
        assert passenger_id in [p[0] for p in bus.bus_passengers]

        # def drop_off(bus, passenger):
            # unload from bus
        bus.bus_passengers.remove((passenger_id, self.passengers[passenger_id].destination.stop_id))

        # print('Dropping off %s, at %s, capacity %s' % (passenger_id, bus.current_stop.stop_id, len(bus.bus_passengers)))
            
        if self.passengers[passenger_id].destination == bus.current_stop:
            # print('Passenger %s delivered at %s' % (passenger_id, bus.current_stop))
            self.deliver_passenger(self.passengers[passenger_id])
        else: 
            # load to station
            self.bus_stops[bus.current_stop.stop_id].add_waiting_passenger(self.passengers[passenger_id])
                                                                                
        # drop_off(bus, self.passengers[passenger_id])
        # drop_off_action = Action(self.ticks, partial(drop_off, bus, self.passengers[passenger_id]))
        # self.actions.push(drop_off_action)

    def deliver_passenger(self, passenger):
        pass 
        # print('Passenger delivered %s' % passenger.passenger_id)
        
    def send_message(self, sender, bus_id, message):
        
        def send_message(receiver, time, sender_id, message):
            receiver.inbox.append((time, sender_id, message))
         
        send_action = Action(self.ticks, partial(send_message, self.buses[bus_id], self.ticks, sender.bus_id ,message))
        
        self.actions.push(send_action)

            
    def step(self):

        while self.passenger_actions.peek() <= self.ticks and self.passenger_actions.peek() != -1:
            action = self.passenger_actions.pop()
            action() 

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
            self.actions.debug_print()
            print('Size of Passenger actions heap %d' % len(self.passenger_actions._data))
            print('\n\n')
        
        self.ticks += 1
