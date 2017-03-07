from controller import *

class BusMap:
    def __init__(self, controller):
        init_probability_distribution()
        self.route_table = {}
        self.controller = controller
        
        
    def init_probability_distribution(self):
        
        self._max_choices = 24
        self._avg_travel_time = 5
        
        # initialization of the m_support matrix, TODO replace with exact implementation
        S = len(controller.amsterdam_bus_stops_names)
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
                        dest = np.random.choice(controller.connections[s_prime])
                        aux_distro[dest] += 1
                distro = aux_distro
                P[t+1, :, s] = distro
        P /= B
        self._m_support = P / B 
        
    def compute_probability_distribution(self, bus_id):
        timestamp, bus_stop = self.route_table[bus_id]
        delta_t = controller.ticks - timestamp 
        
        if delta_t < 0:
            delta_t = 0
            
        choices = delta_t / avg_travel_time
        
        if choices > self._max_choices:
            choices = self._max_choices
            
        return self._m_support[choices, :, bus_stop.stop_id]
    
    def compute_entropy(self, bus_id):
        prob = self.compute_probability_distribution(bus_id)
        prob = np.array(prob)
        
        return - (np.log(prob)*prob).sum()
        
        
       
    
        