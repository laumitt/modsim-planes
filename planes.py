import numpy as np
import csv
import string

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

airport_names = read_csv(airport_names, flight_time_array)
print('airport names: \n {}'.format(airport_names))

#these global variables are parameters that can be changed
flying_prob = 4
length_of_simulation = 10 # in hours
storm_threshold = 0.1
airport_size = 4 # number of planes
max_storm_length = 4

class ATC:
    def __init__(self):
        self.current_time = 0
    def get_time(self):
        '''tells whatever asked it what time it is''' # is this necessary?
        return self.current_time
    def update(self):
        '''updates time until end of simulation'''
        if self.current_time < length_of_simulation:
            self.current_time += 1
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

class Airport:
    def __init__(self, code, airport_schedule, planes_ready):
        self.code = code
        self.airport_schedule = airport_schedule
        self.planes_ready = planes_ready
        current_time = 0
        storm_happening = False
    def update(self):
        current_time = atc.get_time()
        storm_info = atc.storm()
    def departure_update(self):
        print('departures not updated') #send departing planes
    def arrival_update(self):
        print('arrivals not updated') #check for arriving planes

class Plane:
    def __init__(self, code, location, destination, arrival_time):
        self.number = code
        self.location = location
        self.destination = destination
        self.arrival_time = arrival_time
    def assign_new_destination(self, destination, arrival_time):
        self.destination = destination
        self.arrival_time = arrival_time
    def update(self):
        current_time = atc.get_time()
        if current_time == self.arrival_time:
            self.location = self.destination
    def give_info(self):
        print('code {}'.format(self.code))
        print('location {}'.format(self.location))
        print('destination {}'.format(self.destination))
        print('arrival time {}'.format(self.arrival_time))

def create_airports():
    airport_dict = {}
    for i in airport_names:
        name = i
        schedule = [] # PLACEHOLDER
        i = Airport(name, schedule, airport_size)
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

def find_flight_time(port_one, port_two):
    '''returns the time from port one to port two'''
    return flight_time_array[airport_dict[port_one]][airport_dict[port_two]]

def create_schedule(airport_names,airport_size,total_time,airport_dict):
    ''' takes in list of airports, number of planes each start with, and simulation length
    returns a schedule listing the time of departure, the departure airport, and the arrival airport
    '''
    #sched: time leaving , departure airport, arrival airport
    sched = []
    #arrivals: time, destination
    arrivals = []
    planes_in_ports = []
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
                        #while time_to_dest < 1:  #this is here to make sure that we dont send an airplane to an airport its already at
                            #dest = np.random.randint(1,(len(planes_in_ports)))    #PROBABLILITY HERE
                            #time_to_dest = flight_time_array[port_number][dest]
                        arrivalTime = int(i) + int(time_to_dest)
                        arrivals.append([arrivalTime,dest])
                        sched.append([i,port[0],airport_names[dest]])
                        print('destination: {}'.format(airport_names[dest]))
                        if len(destinations) == 1:
                            destinations = []
                        else:
                            destinations.remove(airport_names[dest])
                            print('removing a thing from destinations {}'.format(destinations))
                            print('airport names after removing from dest {}'.format(airport_names))
                        print(destinations)
            for x in arrivals:  #check for arrivals
                if x[0] == i:
                    planes_in_ports[x[1]][-1] += 1
    return sched

def run_simulation():
    #determine sched, and pass to airports
    airport_dict = create_airports()
    plane_dict = create_airplanes()
    schedule = create_schedule(airport_names,airport_size,length_of_simulation, airport_dict)
    print(schedule)
    print('schedule length {}'.format(len(schedule)))
    atc = ATC()

run_simulation()
# print('finding DEN: airport_dict key is {}, airport_names at that index is {}, airport object is {}, airport object code is {}'.format(airport_dict['DEN'], airport_names[airport_dict['DEN']], airports[airport_dict['DEN']], airports[airport_dict['DEN']].code))
