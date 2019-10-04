import numpy as np
import csv
import string
import matplotlib.pyplot as plt

'''these global variables are parameters that can be changed'''

flying_prob = .95   #probably of flying
length_of_simulation = 17 # in hours
airport_size = 3  #number of airplanes distributed to airports at the beginning
max_storm_length = 3    #max and min storm length
min_storm_length = 1
length_of_schedule = 10 #in hours, the simulation will continue to run after the schedule ends to finish out flights started

#thing that will be plotted at the end
storm_planes_arriving = []
storm_planes_departing= []
storm_flights = []
storm_delays= []
no_storm_planes_arriving= []
no_storm_planes_departing = []
no_storm_flights= []
no_storm_delays= []

def read_csv(airport_names, flight_time_array):
    '''reads airport names and flight times from csv'''
    with open('modsim-planes-master\\flight_timestest.csv', newline='') as csvfile:
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
    '''controls the time updating as well as storms throughout the model'''
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
        self.storm_length = np.random.randint(min_storm_length, max_storm_length)  #randomly determines storm length
        if(self.storm_length < round(length_of_schedule/4)):    #keeps time at the beginning of the model length
            self.storm_time = np.random.randint(self.storm_length, (round(length_of_schedule/4)))
        else:
            self.storm_time = self.storm_length
        self.storm_location = airport_names[np.random.randint(0, len(airport_names))]
        print('storm time {}, location {}, length {}'.format(self.storm_time, self.storm_location, self.storm_length))
    def get_storm_info(self):
        '''returns the time, location, and length of storm'''
        self.storm_info = [self.storm_time, self.storm_location, self.storm_length]
        return self.storm_info
    def divide_schedule(self, schedule, airport_dict):
        '''takes the schedule and distributes between each airport so they know their own departures'''
        for step in schedule:
            airport_dict[step[1]].add_to_schedule(step)

class Airport:
    '''handles the departures of each airplane, as well as reciving airplanes from other airports'''
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
        '''keep track of arriving planes and bring them in next time cycle after wait period'''
        self.planes_arriving.append(plane)
    def departure_update(self, airport_dict, airport_names, plane_dict, storms):
        '''checks schedule, and sees if there is a storm that could cause flights to not depart
           if there is a storm, then push the flight back and also keep track of the delay
           then check if there are any flights that can depart, and send each airplane off into the blue yonder
        '''
        global current_time
        planes_departing = []
        delays = 0
        if storms == True:
            storm_info = atc.get_storm_info()
        for time_num in range(len(self.airport_schedule)):
            time = self.airport_schedule[time_num]
            if time[0] == current_time:
                if storms == True:
                    flight_time = find_flight_time(airport_dict, airport_names, self.code, time[2])
                    # storm_info is formatted as storm_time, storm_location, storm_length
                    if (storm_info[0] <= (current_time + flight_time)) and ((current_time + flight_time) <= (storm_info[0] + storm_info[2])) and (time[2] == storm_info[1]):
                        # ^if the destination
                        self.airport_schedule[time_num][0] += 1
                        delays += 1
                    elif (storm_info[0] <= current_time <= (storm_info[0] + storm_info[2])) and (self.code == storm_info[1]): #current = storm
                        self.airport_schedule[time_num][0] += 1
                        delays += 1
            time = self.airport_schedule[time_num] # update after potentially changing time
            if time[0] == current_time:
                if len(self.planes_ready) > 0:
                    plane_flying = self.planes_ready[0]
                    flight_time = find_flight_time(airport_dict, airport_names, self.code, time[2])
                    plane_dict[plane_flying].assign_new_destination(time[2], flight_time, time[-1])
                    self.planes_departing.append(plane_flying)
                    if len(self.planes_ready) == 1:
                        self.planes_ready = []
                    else:
                        self.planes_ready.remove(plane_flying)
                else: #we have no planes
                    self.airport_schedule[time_num][0] += 1
                    delays +=1
        self.planes_departing_log.append(len(self.planes_departing))
        return delays
    def arrival_update(self):
        '''takes planes that have arrived and processes them to ready to fly'''
        for plane in self.planes_arriving:
            self.planes_ready.append(plane)
        self.planes_arriving_now = len(self.planes_arriving)
        self.planes_arriving = []
    def add_to_schedule(self, step):
        '''takes info from the schedule distribution by the atc and compiles own schedule'''
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
        if self.flying:
            print('i, {}, and flying at time {} and should land at {}'.format(self.code,current_time,self.arrival_time))
        if self.arrival_time == current_time:
            self.location = self.destination
            airport_dict[self.destination].arriving_plane(self.code)
            self.flying = False
            if self.code in planes_in_air:
                if len(planes_in_air) == 1:
                    planes_in_air = []
                else:
                    planes_in_air.remove(self.code)

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
            for individual_airplanes in range(planes_in_ports[port_number][1]):  #this should go through and decide if each airplane available is flying
                if (planes_in_ports[port_number][1] > 0) and (np.random.random() > 1- flying_prob) and len(destinations) > 0:   #PROBABLILITY HERE
                    planes_in_ports[port_number][1] -= 1
                    dest = np.random.randint(0,len(airport_names))
                    time_to_dest = flight_time_array[port_number][dest]
                    arrival_time = int(i) + int(time_to_dest) + 1
                    if airport_names[dest] in destinations:
                        arrivals.append([arrival_time,dest])
                        sched.append([i,port[0],airport_names[dest], flight_number])
                        flight_number+=1
                        if len(destinations) == 1:
                            destinations = []
                        else:
                            destinations.remove(airport_names[dest])
        for x in arrivals:  #check for arrivals
            if x[0] == i:   #if the time the arrival specifies is now
                for plane_num in range(len(planes_in_ports)):
                    if planes_in_ports[plane_num][0] == airport_names[x[1]]:
                        planes_in_ports[plane_num][1] += 1
    return sched

def run_simulation(storms):
    global storm_delays
    global storm_flights
    global storm_planes_arriving
    global storm_planes_departing

    global no_storm_delays
    global no_storm_flights
    global no_storm_planes_arriving
    global no_storm_planes_departing

    total_delays = 0
    '''determine schedule, and pass to airports'''
    planes_in_air_at_time = []
    global planes_in_air
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
        total_delays += delays
    for airport in airport_names: # graphing arrivals by airport over time
        if storms:
            for airport in airport_names: # graphing arrivals by airport over time
                storm_planes_arriving.append(airport_dict[airport].planes_arriving_log)
                storm_planes_departing.append(airport_dict[airport].planes_departing_log)
        else:
            for airport in airport_names: # graphing arrivals by airport over time
                no_storm_planes_arriving.append(airport_dict[airport].planes_arriving_log)
                no_storm_planes_departing.append(airport_dict[airport].planes_departing_log)
    print('total delays {}'.format(total_delays))
    if storms:
        storm_flights = planes_in_air_at_time
        storm_delays = delayed_per_hour
    else:
        no_storm_flights = planes_in_air_at_time
        no_storm_delays = delayed_per_hour

if __name__ == '__main__':
    flight_time_array = []
    plane_names = []
    airport_names = []
    airport_names = read_csv(airport_names, flight_time_array)
    airport_dict = create_airports()
    plane_dict = create_airplanes()
    schedule = create_schedule(airport_names, airport_size, length_of_schedule, airport_dict)
    atc = ATC()
    atc.storm_schedule()
    plotting = ['b', 'g', # colors for plotting later
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
    for i in range(0,2):
        current_time = -2 # don't change this - atc will update it later
        planes_in_air = []
        plane_tracking = []
        delayed_per_hour = []
        airport_dict = create_airports()
        plane_dict = create_airplanes()
        atc.divide_schedule(schedule, airport_dict)
        delayed_per_hour = []
        if i == 0:
            run_simulation(False)
        else:
            run_simulation(True)
    plt.figure(0)
    plt.title("NO STORM")
    plt.plot(no_storm_flights, label = 'flights')
    plt.plot(no_storm_delays, label = 'delays')
    i = 0
    i = 0
    for airport_num in range(len(airport_names)): # graphing arrivals by airport over time
        airport = airport_names[airport_num]
        #plt.plot(no_storm_planes_arriving[airport_num], ':', color=plotting[i], label=str(airport) + ' arrivals')
        plt.plot(no_storm_planes_departing[airport_num], ':', color=plotting[i+1], label=str(airport) + ' departures')
        i += 2
    plt.xlabel('time (hours)')
    plt.ylabel('number of planes')
    plt.legend()
    plt.figure(1)
    plt.title('STORM')
    plt.plot(storm_flights, label = 'flights')
    plt.plot(storm_delays, label = 'delays')
    i = 0
    for airport_num in range(len(airport_names)): # graphing arrivals by airport over time
        airport = airport_names[airport_num]
        #plt.plot(storm_planes_arriving[airport_num], ':', color=plotting[i], label=str(airport) + ' arrivals')
        plt.plot(storm_planes_departing[airport_num], ':', color=plotting[i+1], label=str(airport) + ' departures')
        i += 2
    plt.xlabel('time (hours)')
    plt.ylabel('number of planes')
    plt.legend()
    plt.figure(2)
    plt.title('number of flights, storm vs no storm')
    plt.plot(storm_flights, label = 'flights with storm')
    plt.plot(no_storm_flights, label = 'flights without storm')
    plt.plot(storm_delays, label = 'delays caused by storm')
    print(storm_flights)
    print(no_storm_flights)
    plt.legend()
    plt.plot()
    plt.show()
