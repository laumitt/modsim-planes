import numpy as np
import csv
import string
import matplotlib.pyplot as plt

flight_time_array = []
airport_names = []
plane_names = []

def read_csv(airport_names, flight_time_array):
    with open('flight_times.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            if airport_names == []:
                airport_names = (row[0].split(','))[1:]
            else:
                split = row[0].split(',')
                split_ints = []
                for i in split:
                    if i not in airport_names:
                        split_ints.append(int(i))
                flight_time_array.append(split_ints)
    return airport_names

#these global variables are parameters that can be changed
flying_prob = 4
length_of_simulation = 15 # in hours
storm_threshold = 0.1
airport_size = 4 # number of planes
max_storm_length = 4
shorten_schedule_by = 10

# don't change this - atc will update it later
current_time = -2
planes_in_air = []

class ATC:
    def get_time(self):
        '''tells whatever asked it what time it is''' # is this necessary?
        return self.current_time
    def update(self):
        '''updates time until end of simulation'''
        global current_time
        if current_time < length_of_simulation:
            current_time += 1
    def storm(self):
        '''generates information about storms'''
        if np.random.random() < storm_threshold:
            is_stormy = True
        else:
            is_stormy = False
        storm_location = airport_names[np.random.randint(0,len(airport_names))]
        storm_length = np.random.randint(0,max_storm_length)
        storm_info = [is_stormy, storm_location, storm_length]
        print(storm_info)
        return storm_info
    def divide_schedule(self, schedule, airport_dict):
        for step in schedule:
            airport_dict[step[1]].add_to_schedule(step)

class Airport:
    def __init__(self, code, airport_schedule, planes_ready, planes_arriving):
        self.code = code
        self.airport_schedule = airport_schedule
        self.planes_ready = planes_ready
        self.planes_arriving = planes_arriving
        storm_happening = False
        self.planes_arriving_log = []
    def update(self):
        print('updated')
        # storm_info = atc.storm()
    def arriving_plane(self, plane):
        self.planes_arriving.append(plane)
        print('{} has arrived at {}'.format(plane, self.code))
    def departure_update(self, airport_dict, airport_names, plane_dict):
        global current_time
        for time in self.airport_schedule:
            if time[0] == current_time:
                if len(self.planes_ready) > 0:
                    plane_flying = self.planes_ready[0]
                    plane_dict[plane_flying].assign_new_destination(time[2], find_flight_time(airport_dict, airport_names, self.code, time[2]))
                    print('plane {} flying from {} to {}'.format(plane_flying, self.code, time[2]))
                    if len(self.planes_ready) == 1:
                        self.planes_ready = []
                    else:
                        self.planes_ready.remove(plane_flying)
    def arrival_update(self):
        print('planes arriving at {} are {}'.format(self.code, self.planes_arriving))
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
    def assign_new_destination(self, destination, arrival_time):
        global planes_in_air
        self.destination = destination
        self.arrival_time = arrival_time
        self.flying = True
        planes_in_air.append(self.code)
        print('added {} to planes_in_air'.format(self.code))
    def update(self,airport_dict):
        global current_time
        global planes_in_air
        if self.arrival_time == current_time:
            self.location = self.destination
            airport_dict[self.destination].arriving_plane(self.code)
            self.flying = False
            if self.code in planes_in_air:
                if len(planes_in_air) == 1:
                    planes_in_air = []
                else:
                    planes_in_air.remove(self.code)
                    print('removed {} from planes_in_air'.format(self.code))

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
            names[plane_num] = Plane(name, airport_names[i], airport_names[i],-1)   #THE -1 IS IMPORTANT FOR SETUP OF THE AIRPORTS
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

def create_schedule(airport_names,airport_size,total_time,airport_dict):
    ''' takes in list of airports, number of planes each start with, and simulation length
    returns a schedule listing the time of departure, the departure airport, and the arrival airport
    '''
    #sched: time leaving, departure airport, arrival airport
    sched = []
    #arrivals: time, destination
    arrivals = []
    planes_in_ports = []
    total_time -= shorten_schedule_by
    for i in airport_names:
        planes_in_ports.append([i,airport_size])
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
                    time_to_dest = 0
                    dest = np.random.randint(0,len(airport_names))
                    if airport_names[dest] in destinations:
                        time_to_dest = flight_time_array[port_number][dest]
                        arrival_time = int(i) + int(time_to_dest)
                        arrivals.append([arrival_time,dest])
                        sched.append([i,port[0],airport_names[dest]])
                        if len(destinations) == 1:
                            destinations = []
                        else:
                            destinations.remove(airport_names[dest])
            for x in arrivals:  #check for arrivals
                if x[0] == i:
                    planes_in_ports[x[1]][-1] += 1
    return sched

def run_simulation():
    #determine sched, and pass to airports
    airport_dict = create_airports()
    plane_dict = create_airplanes()
    schedule = create_schedule(airport_names,airport_size, length_of_simulation, airport_dict)
    atc = ATC()
    atc.divide_schedule(schedule,airport_dict)
    planes_in_air_at_time = []
    print(len(schedule))
    for step in range(length_of_simulation):
        atc.update()
        for airport in airport_names:
            airport_dict[airport].update()
            airport_dict[airport].departure_update(airport_dict, airport_names, plane_dict)
        print('first for loop done')
        for plane in plane_names:
            plane_dict[plane].update(airport_dict)
        print('second for loop done')
        for airport in airport_names:
            airport_dict[airport].arrival_update()
            airport_dict[airport].planes_arriving_log.append(airport_dict[airport].planes_arriving_now)
        print('third for loop done')
        for plane in planes_in_air:
            print('plane {} flying from {} to {}, landing at {}'.format(plane, plane_dict[plane].location, plane_dict[plane].destination, plane_dict[plane].arrival_time))
        planes_in_air_at_time.append(len(planes_in_air))
    for airport in airport_names:
        plt.plot(airport_dict[airport].planes_arriving_log, label=airport)
    plt.plot(planes_in_air_at_time, color='b', label='planes in air')
    plt.xlabel('time (hours)')
    plt.ylabel('number of planes')
    plt.legend()
    plt.show()
airport_names = read_csv(airport_names, flight_time_array)
run_simulation()
