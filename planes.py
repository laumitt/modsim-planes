import numpy as np
import csv
import string
import matplotlib.pyplot as plt

#these global variables are parameters that can be changed
flying_prob = 4
length_of_simulation = 100 # in hours
airport_size = 10 # number of planes
max_storm_length = 4
length_of_schedule = 10

def read_csv(airport_names, flight_time_array):
    '''reads airport names and flight times from csv'''
    with open('flight_times.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            if airport_names == []: # the first row of the csv is the names of the airports
                airport_names = (row[0].split(','))[1:] # exclude the first cell because it's a label for humans
            else:
                split = row[0].split(',') # split rows to give each airport flight times to the others
                split_ints = []
                for i in split:
                    if i not in airport_names: # if it's not an airport name it's a flight time
                        split_ints.append(int(i))
                flight_time_array.append(split_ints)
    return airport_names

class ATC:
    def __init__(self):
        self.storm_time = -1
        self.storm_length = -1
        self.storm_location = None
        self.storm_info = []
    def update(self):
        '''updates time until end of simulation'''
        global current_time
        if current_time < length_of_simulation:
            current_time += 1 # keeping track of time
    def storm_schedule(self):
        '''generates information about storms'''
        global length_of_schedule
        self.storm_time = np.random.randint(1, (length_of_schedule/4))
        self.storm_length = np.random.randint(1, max_storm_length)
        self.storm_location = airport_names[np.random.randint(0, len(airport_names))]
        print('storm time {}, location {}, length {}'.format(self.storm_time, self.storm_location, self.storm_length))
    def get_storm_info(self):
        self.storm_info = [self.storm_time, self.storm_location, self.storm_length]
        return self.storm_info
    def divide_schedule(self, schedule, airport_dict):
        for step in schedule:
            airport_dict[step[1]].add_to_schedule(step) # tell each airport what its departures are

class Airport:
    def __init__(self, code, airport_schedule, planes_ready, planes_arriving):
        self.code = code
        self.airport_schedule = airport_schedule
        self.planes_ready = planes_ready
        self.planes_arriving = planes_arriving
        storm_happening = False
        self.planes_arriving_log = []
        self.planes_departing = []
        self.planes_departing_log = []
    def arriving_plane(self, plane):
        self.planes_arriving.append(plane)
    def departure_update(self, airport_dict, airport_names, plane_dict, storms):
        global current_time
        planes_departing = []
        delays = 0
        if storms == True:
            storm_info = atc.get_storm_info()
        for time_num in range(len(self.airport_schedule)):
            time = self.airport_schedule[time_num]
            if time[0] == current_time:
                if len(self.planes_ready) > 0:
                    plane_flying = self.planes_ready[0]
                    flight_time = find_flight_time(airport_dict, airport_names, self.code, time[2])
                    if storms == True:
                        if (storm_info[0] <= (current_time + flight_time) <= (storm_info[0] + storm_info[2])) and (time[2] == storm_info[1]):
                            flight_time += 1
                            delays += 1
                            print('{} delayed from {} to {} at time {}'.format(plane_flying, self.code, time[2], current_time))
                    plane_dict[plane_flying].assign_new_destination(time[2], flight_time, time[-1])
                    print('plane {} flying from {} to {} with flight number {}'.format(plane_flying, self.code, time[2], time[-1]))
                    self.planes_departing.append(plane_flying)
                    if len(self.planes_ready) == 1:
                        self.planes_ready = []
                    else:
                        self.planes_ready.remove(plane_flying)
                else: #we have no planes and have to delay done_flights
                    self.airport_schedule[time_num][0] += 1
                    delays +=1
                    print('delay without a plane')
        self.planes_departing_log.append(len(self.planes_departing))
        return delays
    def arrival_update(self):
        for plane in self.planes_arriving:
            self.planes_ready.append(plane)
        self.planes_arriving_now = len(self.planes_arriving)
        self.planes_arriving = []
    def add_to_schedule(self, step):
        self.airport_schedule.append(step)

class Plane:
    def __init__(self, code, location, destination, arrival_time):
        self.code = code
        self.location = location
        self.destination = destination
        self.arrival_time = arrival_time
        self.flying = False
        self.flight_number = 0
    def assign_new_destination(self, destination, arrival_time, flight_number):
        global planes_in_air
        global current_time
        self.destination = destination
        self.arrival_time = arrival_time + current_time
        self.flying = True
        self.flight_number = flight_number
        planes_in_air.append(self.code)
    def update(self,airport_dict):
        global current_time
        global planes_in_air
        global plane_tracking
        plane_tracking.append([current_time, self.code, self.location, self.destination, self.flight_number])
        if self.arrival_time == current_time:
            self.location = self.destination
            airport_dict[self.destination].arriving_plane(self.code)
            self.flying = False
            if current_time > 0:
                done_flights[self.flight_number] += 1
            if self.code in planes_in_air:
                if len(planes_in_air) == 1:
                    planes_in_air = []
                else:
                    planes_in_air.remove(self.code)
        # if (current_time == length_of_simulation - 2) and self.flying == True:
        #     print('I, {}, am flying at the end of the simulation'.format(self.code))
        # if current_time == length_of_simulation and self.flying == True:
        #     print('{} still flying at end of simulation'.format(self.code))

def create_airports():
    airport_dict = {}
    for i in airport_names:
        name = i
        schedule = [] # empty for initialization
        arrivals = [] # empty for initialization
        planes_ready = [] # empty for initialization
        i = Airport(name, schedule, planes_ready, arrivals)
        airport_dict[name] = i
    return airport_dict

def create_airplanes():
    '''creates airplanes and returns a dictionary with names and location'''
    plane_dict = {}
    names = []
    letters = []
    for i in range(len(string.ascii_lowercase)):
        letters.append(string.ascii_lowercase[i])
        i +=1
    current_letter = 0
    current_number = 0
    airplanes = []
    for i in range(len(airport_names)*airport_size):
        names.append(letters[current_letter]+str(current_number))
        current_number += 1
        if(current_number > 99):
            current_number = 0
            current_letter += 1
    plane_num = 0
    for i in range(len(airport_names)):
        for j in range(airport_size):
            name = names[plane_num]
            plane_names.append(name)
            names[plane_num] = Plane(name, airport_names[i], airport_names[i],-1)   # the -1 gives all the airports their planes at the same time
            plane_dict[name] = names[plane_num]
            plane_num += 1
    return plane_dict

def find_flight_time(airport_dict, airport_names, port_one, port_two):
    '''returns the time from port one to port two'''
    for i in range(len(airport_names)):
        if airport_names[i] == port_one:
            port_one = i
        if airport_names[i] == port_two:
            port_two = i
    return flight_time_array[port_one][port_two]

def create_schedule(airport_names, airport_size, total_time, airport_dict):
    '''
    takes in list of airports, number of planes each start with, and simulation length
    returns a schedule listing the time of departure, the departure airport, and the arrival airport
    '''
    sched = [] # sched: time leaving, departure airport, arrival airport
    arrivals = [] # arrivals: time, destination
    planes_in_ports = []
    for i in airport_names:
        planes_in_ports.append([i,airport_size])
    flight_number = 0
    for i in range(total_time):  #goes through each time to determine arrivals and departures for that time
        for port_number in range(len(planes_in_ports)):     #figure out departures
            destinations = airport_names.copy()
            port = planes_in_ports[port_number]
            destinations.remove(airport_names[port_number])
            if type(destinations) == None:
                return
            for individual_airplanes in range(port[-1]):  #this should go through and decide if each airplane available is flying
                if (port[-1] > 0) and (np.random.randint(0,flying_prob) > flying_prob - 2) and len(destinations) > 0:   #PROBABLILITY HERE
                    port[-1] -= 1
                    dest = np.random.randint(0,len(airport_names))
                    time_to_dest = flight_time_array[port_number][dest]
                    arrival_time = int(i) + int(time_to_dest) +1
                    if arrival_time < length_of_simulation:
                        if airport_names[dest] in destinations:
                            arrivals.append([arrival_time,dest])
                            sched.append([i,port[0],airport_names[dest], flight_number])
                            flight_number+=1
                            done_flights.append(0)
                            if len(destinations) == 1:
                                destinations = []
                            else:
                                destinations.remove(airport_names[dest])
            for x in arrivals:  #check for arrivals
                if x[0] == i:
                    planes_in_ports[x[1]][-1] += 1
    return sched

def run_simulation(storms):
    '''determine schedule, and pass to airports'''
    for airport in airport_names:
        print('airport {} schedule {}'.format(airport, airport_dict[airport].airport_schedule))
    planes_in_air_at_time = []
    for step in range(length_of_simulation):
        delays = 0
        atc.update()
        for airport in airport_names:
            airport_dict[airport].planes_departing = []
            delays += airport_dict[airport].departure_update(airport_dict, airport_names, plane_dict, storms) # update departing planes for each airport
        for plane in plane_names:
            plane_dict[plane].update(airport_dict) # update locations of planes
        for airport in airport_names:
            airport_dict[airport].arrival_update() # update arriving planes for each airport
            airport_dict[airport].planes_arriving_log.append(airport_dict[airport].planes_arriving_now) # log when planes arrive
        planes_in_air_at_time.append(len(planes_in_air)) # tracking how many planes are in the air at a given time
        delayed_per_hour.append(delays)
    i = 0
    plotting = ['b', 'g',
                'r', 'c',
                'm', 'k',
                'y', 'tab:pink',
                'darkkhaki', 'maroon',
                'gold', 'lawngreen',
                'lightseagreen', 'olive',
                'palevioletred', 'orchid',
                'peru', 'coral',
                'orangered', 'mediumspringgreen',
                'rebeccapurple', 'teal']
        # colors for plotting later
    for airport in airport_names: # graphing arrivals by airport over time
        # plt.plot(airport_dict[airport].planes_arriving_log, ':', color=plotting[i], label=str(airport) + ' arrivals')
        plt.plot(airport_dict[airport].planes_departing_log, ':', color=plotting[i+1], label=str(airport) + ' departures')
        i += 2
    if len(planes_in_air) == 0: # if there are no planes still flying at the end of the simulation
        print('all landed')
    else:
        print('got stuck')
    plt.plot(planes_in_air_at_time, color='k', label='planes in air')
    plt.plot(delayed_per_hour, color='deepskyblue', label='delays')
    plt.xlabel('time (hours)')
    plt.ylabel('number of planes')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    flight_time_array = []
    airport_names = []
    plane_names = []
    delayed_per_hour = []
    airport_names = read_csv(airport_names, flight_time_array)
    done_flights = [] # debug piece
    current_time = -2 # don't change this - atc will update it later
    planes_in_air = []
    plane_tracking = []
    airport_dict = create_airports()
    plane_dict = create_airplanes()
    schedule = create_schedule(airport_names, airport_size, length_of_schedule, airport_dict)
    atc = ATC()
    atc.storm_schedule()
    atc.divide_schedule(schedule, airport_dict)
    storms = False
    run_simulation(storms)
