from bus import *
import numpy as np

class PositionBeliefs:

    def __init__(self, bus):
        self.internal_table = {} # what we know about other buses' positions
        self.external_table = {} # what we think other buses know about our position
        self.bus = bus

    def prepare_message(self):
        message = {k:v for k,v in self.internal_table.items()}

        destination = self.bus.next_stop 
        arrival_time = self.bus.arrival_time

        if not destination:
            arrival_time = self.bus.controller.ticks + 1
            destination = self.bus.current_stop

        message[self.bus.bus_id] = (arrival_time, destination.stop_id)

        return message

    def calculate_transmission_probability(self):
        normalizer = np.log(24)
        bus_ids = set(self.external_table.keys()).union(set(self.internal_table.keys()))
        return { b_id : self.compute_external_entropy(b_id) / normalizer for b_id in bus_ids} # {bus_id: [prob(station1), prob(station2), ..]}


    def update_beliefs(self, sender_id, received_table):

         for b_id , time_station in received_table.items():
            
            # update internal table
            if b_id != self.bus.bus_id: # for all buses thats not us

                # If bus is not in internal table, add it 
                if b_id not in self.internal_table:
                    self.internal_table[b_id] = time_station
                
                elif time_station[0] > self.internal_table[b_id][0]: # if received entry is more up-to-date, update beliefs
                    self.internal_table[b_id] = time_station   

            # update external table
            else:
                # If bus is not in external table, add it 
                if sender_id not in self.external_table:
                    self.external_table[sender_id] = time_station # they received info about us from someone else
                
                elif time_station[0] > self.external_table[sender_id][0]: # if received entry is more up-to-date, update beliefs
                    self.external_table[sender_id] = time_station  
            
    def update_external_table(self, bus_id):
        destination = self.bus.next_stop
        arrival_time = self.bus.arrival_time
        if not destination:
            arrival_time = self.bus.controller.ticks + 1
            destination = self.bus.current_stop

        self.external_table[bus_id] = (self.bus.arrival_time, destination.stop_id)
        
    def compute_internal_probability(self, bus_id):
        return self.compute_probability_distribution(bus_id, self.internal_table)

    def compute_external_probability(self, bus_id):
        return self.compute_probability_distribution(bus_id, self.external_table)

    def compute_probability_distribution(self, bus_id, table):
        if bus_id in table:

            _avg_travel_time = 5

            timestamp, stop_id = table[bus_id]
            delta_t = self.bus.controller.ticks - timestamp 
            
            if delta_t < 0:
                delta_t = 0
                
            choices = min(int(delta_t / _avg_travel_time ), 10)
            # print(table, choices, stop_id)
            return self.bus.controller._m_support[choices, :, stop_id]
        else:
            return np.ones(24) / 24 # without information about the bus, return uniform prob. dist.
    
    def compute_internal_entropy(self, bus_id):
        return self.compute_entropy(bus_id, self.internal_table)

    def compute_external_entropy(self, bus_id):
        return self.compute_entropy(bus_id, self.external_table)

    def compute_entropy(self, bus_id, table):
        prob = np.array(self.compute_probability_distribution(bus_id, table))
        
        sum = 0
        
        for p in prob:
            if p > 0:
                sum += p*np.log(p)
                
        return -sum