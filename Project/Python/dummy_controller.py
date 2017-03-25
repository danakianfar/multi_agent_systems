from action import *
from bus_stop import *
from passenger import *
import re
from logger import *
from destination_model import * 
import pyparsing
import json
from controller import Controller as MainController 

class NetLogoAction: # wrapper around commands send to netlogo

    # NetLogo parsing params
    ACT_TYPE_TRAVELTO = 'TRAVEL_TO' # station_id
    ACT_TYPE_MESSAGE = 'MESSAGE' # (tick, recipient, message)
    ACT_TYPE_PICKUP = 'PICK_UP' # passenger_id
    ACT_TYPE_DROPOFF = 'DROP_OFF' # passenger_id
    ACT_TYPE_ADDBUS = 'ADD_BUS' # bus type
    ACT_TYPE_MESSAGE_DELIM = '===' # split delimiters for messages
    ACT_TYPE_CMD_DELIM = '&&' # delimiter between commands
    ACT_TYPE_ACTION_DELIM = ':=:' # delimiter within each command

    def __init__(self, action_type, action_specification):
        self.action_type = action_type # one of the above types
        self.action_specification = action_specification # string representation of action (can be delimited)

    def __str__(self):
        return "%s%s%s"% (self.action_type, 
            NetLogoAction.ACT_TYPE_ACTION_DELIM,
            self.action_specification)

class Controller(MainController):

    bus_stop_names = {'Amstel': 0, 'Amstelveenseweg': 1, 'Buikslotermeer': 2, 'Centraal': 3,
                        'Dam': 4, 'Evertsenstraat': 5, 'Floradorp': 6, 'Haarlemmermeerstation': 7, 'Hasseltweg': 8,
                        'Hendrikkade': 9, 'Leidseplein': 10, 'Lelylaan': 11, 'Muiderpoort': 12, 'Museumplein': 13,
                        'RAI': 14, 'SciencePark': 15, 'Sloterdijk': 16, 'Surinameplein': 17, 'UvA': 18,
                        'VU': 19, 'Waterlooplein': 20, 'Weesperplein': 21,'Wibautstraat': 22, 'Zuid': 23}

    _COST_K = 1e-1

    def __init__(self, bus_class, loggers=[]):
        print('Initializing NetLogo Controller...')
        super(Controller, self).__init__(bus_class=bus_class, loggers=loggers)
        
        # NetLogo I/O parsing
        self.calling_bus_id = -1 # bus who called the controller
        self.commands = []
        self.nested_parser =  pyparsing.nestedExpr('[',']') #.parseString('[[1.0, 24.0, {hello:hello}],[1.0, 24.0, {hello:hello}]]'.replace(',',' ') ).asList()[0]
        self.bracket_parser = re.compile(r'([^\[\]]+)')

    # API for receiving form NetLogo
    def tick(self, netlogo_table):
        
        self.parse_netlogo_input(netlogo_table) # parse info from NetLogo

        self.buses[self.calling_bus_id].update()

        cmds = [i for i in self.commands] # commands
        self.commands.clear()

        return cmds

    ## Commands to NetLogo
    def add_bus(self, vehicle_type, genome=[]):
        self.commands.append(NetLogoAction(NetLogoAction.ACT_TYPE_ADDBUS, 
            vehicle_type))

    def travel_to(self, bus, bus_stop_id):
        # assert bus.current_stop
        # assert bus_stop_id in self.connections[bus.current_stop.stop_id]

        bus.next_stop = self.bus_stops[bus_stop_id]
        bus.previous_stop = bus.current_stop

        self.commands.append(NetLogoAction(NetLogoAction.ACT_TYPE_TRAVELTO, 
            bus_stop_id))

    def get_distance(self, from_station, to_station):
        return self.adj_matrix[from_station,to_station]
        
    def pick_up_passenger(self, bus, passenger_id):
        # assert bus.current_stop == self.passengers[passenger_id].current_stop 
        self.commands.append(NetLogoAction(NetLogoAction.ACT_TYPE_PICKUP, 
            passenger_id))

    def drop_off_passenger(self, bus, passenger_id):
        # assert passenger_id in [p[0] for p in bus.bus_passengers]
        self.commands.append(NetLogoAction(NetLogoAction.ACT_TYPE_DROPOFF,
            passenger_id))

    def send_message(self, sender, bus_id, message):

        self.commands.append(NetLogoAction(NetLogoAction.ACT_TYPE_MESSAGE,
            NetLogoAction.ACT_TYPE_MESSAGE_DELIM.join(list(map(str, [bus_id, json.dumps(message)])))))


    ## NetLogo Parsing

    # Parse HTTP POST input from NetLogo. Type is ImmutableDictionary
    def parse_netlogo_input(self, netlogo_table):

        self.ticks = dumb_int_cast(netlogo_table['ticks'])
        bus_id = dumb_int_cast(netlogo_table['bus_id']) # current bus
        self.calling_bus_id = bus_id
        bus_type = dumb_int_cast(netlogo_table['bus_type'])
        
        if bus_id not in self.buses:
            self.buses[bus_id] = self.bus_class(bus_id, bus_type, self.bus_stops[3], self)
        
        self.buses[bus_id].current_stop = self.parse_bus_stop(netlogo_table['current_stop'])
        self.buses[bus_id].next_stop = self.parse_bus_stop(netlogo_table['next_stop'])
        self.buses[bus_id].previous_stop = self.parse_bus_stop(netlogo_table['previous_stop'])
        self.buses[bus_id].bus_passengers = self.parse_bus_passengers(netlogo_table['bus_passengers'])
        self.buses[bus_id].inbox = self.parse_inbox(netlogo_table['inbox'])

        if 'stops' in netlogo_table:
            self.parse_stops(netlogo_table['stops'])

    # Parses inbox
    # Sample input # inbox <class 'str'> [1.0, 24.0, {hello:hello}]
    def parse_inbox(self, input):
        inbox = []

        if len(input) > 0 and input != '[]':
            inbox =eval(input) # self.nested_parser.parseString(input.replace(',',' ')).asList()

            if not isinstance(inbox[0],list):
                inbox = [inbox]

            for i, msg in enumerate(inbox):
                new_content = {}
                for key, value in msg[2]['content'].items():
                    new_content[int(key)] = value

                inbox[i][2]['content'] = new_content
            # for i, msg in enumerate(inbox):
            #     inbox[i][2] = json.loads(inbox[i][2])

        return inbox



    # Convert NetLogo strings such as "01:15" to ticks ranging 1-96
    def parse_str_spawn_time(self, input):
         hours_mins = list(map(float, input.split(":")))
         arrival_num = int((hours_mins[1]/15) +  ( 4 * hours_mins[0]))
         if arrival_num == 0:
             return 1
         else:
             return 15*arrival_num
    

    # Parses passenger info (passenger_id, destination, spawn time)
    def parse_passenger(self, input):
        try:
            passenger_id, spawn_time_str, destination_id = list(map(str.strip, input.split(',')))
        except ValueError:
            print('Err')
            raise ValueError

        passenger_id, destination_id = list(map(float,[passenger_id, destination_id]))
        spawn_time = self.parse_str_spawn_time(spawn_time_str)
        return Passenger(passenger_id, self.buses[self.calling_bus_id].current_stop, self.bus_stops[destination_id], spawn_time, self)
        
    def parse_bus_stop(self, input):
        stop_id = dumb_int_cast(input)
        return self.bus_stops[stop_id] if stop_id in self.bus_stops else None

    # Parses information about passengers on the bus
    # Sample input # bus_passengers <class 'str'> [5460.0, 7.0][5461.0, 13.0]
    def parse_bus_passengers(self, input):
         
        passengers = []
        for item in self.bracket_parser.findall(input):
            if len(item.strip()) == 0: continue

            passenger = self.parse_passenger(item)

            if passenger.passenger_id not in self.passengers:
                self.passengers[passenger.passenger_id] = passenger

            passengers.append((passenger.passenger_id, passenger.destination))
        return passengers

    # Parses information about stations (station id, passengers)
    # Sample input: # stops <class 'str'> [0.0, [[0.0, 13.0]]][1.0, [[1781.0, 3.0], [1782.0, 4.0], [1783.0, 7.0]]][2.0, [[3587.0, 7.0], [3588.0, 16.0]]][3.0, []][4.0, []][5.0, [[8822.0, 3.0]]][6.0, []][7.0, [[12412.0, 3.0], [12413.0, 10.0], [12414.0, 13.0], [12415.0, 16.0]]][8.0, [[14154.0, 3.0], [14155.0, 13.0]]][9.0, [[15918.0, 4.0], [15919.0, 15.0], [15920.0, 16.0]]][10.0, [[17781.0, 3.0]]][11.0, [[19497.0, 3.0], [19498.0, 19.0]]][12.0, [[21283.0, 10.0], [21284.0, 13.0], [21285.0, 19.0]]][13.0, [[23038.0, 3.0], [23039.0, 4.0]]][14.0, [[24813.0, 3.0], [24814.0, 4.0], [24815.0, 13.0], [24816.0, 23.0]]][15.0, [[26614.0, 7.0], [26615.0, 10.0], [26616.0, 13.0], [26617.0, 23.0]]][16.0, [[28404.0, 3.0], [28405.0, 4.0]]][17.0, [[30199.0, 18.0]]][18.0, [[32012.0, 3.0]]][19.0, [[33752.0, 10.0], [33753.0, 13.0], [33754.0, 23.0]]][20.0, [[35518.0, 4.0], [35519.0, 7.0]]][21.0, [[37342.0, 3.0], [37343.0, 12.0], [37344.0, 18.0]]][22.0, [[39205.0, 13.0]]][23.0, [[40994.0, 3.0], [40995.0, 14.0], [40996.0, 15.0]]]
    def parse_stops(self, input):
        # if the stop is empty, abort
        if len(input.strip()) == 0: return []

        # For each station
        for station_info in input[1:-1].split(']['):
            
            # Format: [1.0, [[1781.0, 3.0], [1782.0, 4.0]]]
            # [station_id, [[passenger_id, destination], ...]] 
            station_id, passenger_info = station_info.split(',', 1)
            station_id = dumb_int_cast(station_id)

            # empty passengers in bus stops
            self.bus_stops[station_id].reset()

            # parse each passenger info
            for passenger_destination in self.bracket_parser.findall(passenger_info.strip()):
                if len(passenger_destination.strip()) == 0 or passenger_destination.strip() == ',':
                    continue

                # Parse passenger
                passenger = self.parse_passenger(passenger_destination)

                # If new passenger in system, add
                if passenger.passenger_id not in self.passengers:
                    self.passengers[passenger.passenger_id] = passenger
                
                # Add to waiting passengers at station
                self.bus_stops[station_id].add_waiting_passenger(passenger)

    def __str__(self):
        return "Num Stops %d, Num buses %d, Num passengers %d" % (len(self.bus_stops), len(self.buses), len(self.passengers))

    def __repr__(self):
        return self.__str__()


def dumb_int_cast(stupid_int_string):
    return int(float(stupid_int_string))
