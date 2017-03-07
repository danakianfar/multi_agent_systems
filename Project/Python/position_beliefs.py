from bus import *

class PositionBeliefs:

    _m_support = None

    def __init__(self, bus):
        self.internal_table = {} # what we know about other buses' positions
        self.external_table = {} # what we think other buses know about our position
        self.bus = bus

        if PositionBeliefs._m_support is None:
            self.init_probability_distribution()

    def prepare_message(self):
        message = {k:v for k,v in self.internal_table.items()}
        message[self.bus.bus_id] = (self.bus.arrival_time, self.bus.next_stop)

        return message

    def calculate_transmission_probability(self):
        normalizer = np.log(24)
        bus_ids = set(self.external_table.keys()).union(set(self.internal_table.keys()))
        return {b_id:self.compute_external_entropy(b_id)/normalizer for b_id in bus_ids} # {bus_id: [prob(station1), prob(station2), ..]}


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
        self.external_table[bus_id] = (self.bus.arrival_time, self.bus.next_stop)

    def init_probability_distribution(self):
        
        self._max_choices = 24
        self._avg_travel_time = 5
        
        # initialization of the m_support matrix, TODO replace with exact implementation
        S = len(self.bus.controller.bus_stop_names)
        T = self._max_choices
        P = np.zeros((T+1, S, S))
        B = 1000

        for s in range(S):    
            distro = np.zeros(S)
            distro[s] = B
            P[0, :, s] = distro

            for t in range(T):
                aux_distro = np.zeros(S)
                for s_prime in range(S):
                    for b in range(int(distro[s_prime])):
                        dest = np.random.choice(self.bus.controller.connections[s_prime])
                        aux_distro[dest] += 1
                distro = aux_distro
                P[t+1, :, s] = distro
        PositionBeliefs._m_support = P / B 
        
    def compute_internal_probability(self, bus_id):
        self.compute_probability_distribution(bus_id, self.internal_table)

    def compute_external_probability(self, bus_id):
        self.compute_probability_distribution(bus_id, self.external_table)

    def compute_probability_distribution(self, bus_id, table):
        if bus_id in table:

            timestamp, bus_stop = table[bus_id]
            delta_t = self.bus.controller.ticks - timestamp 
            
            if delta_t < 0:
                delta_t = 0
                
            choices = int(delta_t / self._avg_travel_time )
            
            if choices > self._max_choices:
                choices = self._max_choices
                
            return self._m_support[choices, :, bus_stop.stop_id]
        else:
            return np.ones(24) / 24 # without information about the bus, return uniform prob. dist.
    
    def compute_internal_entropy(self, bus_id):
        self.compute_entropy(bus_id, self.internal_table)

    def compute_external_entropy(self, bus_id):
        self.compute_entropy(bus_id, self.external_table)

    def compute_entropy(self, bus_id, table):
        prob = self.compute_probability_distribution(bus_id, table)
        prob = np.array(prob)
        
        sum = 0
        
        for p in prob:
            if p > 0:
                sum += p*np.log(p)
                
        return -sum