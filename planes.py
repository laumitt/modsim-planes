import numpy as np
import csv


flight_time_array = []
airports = []

def read_csv(airports, flight_time_array):
    with open('flight_times.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            if airports == []:
                airports = (row[0].split(','))[1:]
            else:
                split = row[0].split(',')
                split_ints = []
                for i in split:
                    if i not in airports:
                        split_ints.append(int(i))
                flight_time_array.append(split_ints)
    airport_dict = {}
    for i in range(len(airports)):
        airport_dict[airports[i]] = i
    return airports, airport_dict

airports, airport_dict = read_csv(airports, flight_time_array)
print('dictionary: \n {}'.format(airport_dict))

#these global variables are parameters that can be changed
flying_prob = 2
break_prob = np.random.randint(0,1)

class ATC:
    def __init__(self, airports, flight_times, number_of_planes, schedule):
        self.airports = airports
        self.flight_times = flight_times
        self.number_of_planes = number_of_planes
        self.schedule = schedule
    def get_time

class Airport:
    def __init__(self, code, airport_schedule, planes_ready):
        self.code = code
        self.airport_schedule = airport_schedule
        self.planes_ready = planes_ready

class Plane:
    def __init__(self, number, location, destination, arrival_time):
        self.number = number
        self.location = location
        self.destination = destination
        self.arrival_time = arrival_time
    def assign_new_destination(destination, arrival_time):
        self.destination = destination
        self.arrival_time = arrival_time
    def update():
        #get time
        #compare time to arrival time
        #tell airport it has arrived

def create_airports():
    for i in range(len(airports)):
        destinations = np.delete(airports, i)
        name = airports[i]
        airports[i] = Airport(airports[i], destinations)
        print('airport {} created'.format(name))

def find_flight_time(port_one, port_two):
    '''returns the time from port one to port two'''
    return flight_time_array[airport_dict[port_one]][airport_dict[port_two]]

def create_schedule(airports,planes_per_port,total_time):
    ''' takes in list of airports, number of planes each start with, and simulation length
    returns a schedule listing the time of departure, the departure airport, and the arrival airport
    '''
    #sched: time leaving , departure airport, arrival airport
    sched = []
    #arrivals: time, destination
    arrivals = []
    planes_in_ports = []
    for i in airports:
        planes_in_ports.append([i,planes_per_port])
    for i in range(total_time):  #goes through each time to determine arrivals and departures for that time
        for x in planes_in_ports:     #figure out departures
            for individual_airplanes in range(x[-1]):  #this should go through and decide if each airplane available is flying
                if (x[-1] > 0) and (np.random.randint(0,flying_prob) > 0):   #PROBABLILITY HERE
                    x[-1] -= 1
                    time_to_dest = 0
                    while time_to_dest < 1:  #this is here to make sure that we dont send an airplane to an airport its already at
                        dest = np.random.randint(1,(len(planes_in_ports)))    #PROBABLILITY HERE
                        time_to_dest = flight_time_array[airport_dict[x[0]]][dest]
                    arrivalTime = int(i) + int(time_to_dest)
                    arrivals.append([arrivalTime,dest])
                    sched.append([i,x[0],airports[dest]])
            for x in arrivals:  #check for arrivals
                if x[0] == i:
                    planes_in_ports[x[1]][-1] += 1
    return sched

def run_simulation():
    #determine sched, and pass to airports
    print('planes :)')

print('airports: \n {}'.format(airports))
print('flight time array: \n {}'.format(flight_time_array))
print('flight time from JFK to SFO (should be 6): {}'.format(find_flight_time('JFK','SFO')))
print(create_schedule(airports,5,10))
create_airports()
