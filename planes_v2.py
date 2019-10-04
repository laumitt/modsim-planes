import numpy as np
import csv
import string
import matplotlib.pyplot as plt

'''these global constants are parameters that can be varied as desired'''
flying_prob = .95  # probability of a flight being scheduled at a particular time
length_of_simulation = 125 # in hours
airport_size = 10 # number of airplanes distributed to each airport at the beginning
max_storm_length = 7 # max and min storm length
min_storm_length = 3
length_of_schedule = 100 # in hours, the simulation will continue to run after the schedule ends to finish out flights started
plot_arrivals = True # if True, will plot arrivals at the end; if False, will plot departures

'''these things are all to be plotted at the end'''
storm_planes_arriving = []
storm_planes_departing= []
storm_flights = []
storm_delays= []
no_storm_planes_arriving= []
no_storm_planes_departing = []
no_storm_flights= []
no_storm_delays= []

def read_csv(flight_time_array):
    '''reads airport names and flight times from csv'''
    airport_names = []
    with open('flight_times.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            if airport_names == []: # the first row of the csv is the names of the airports
                airport_names = (row[0].split(','))[1:] # exclude the first cell because it's a label for humans
            else: # the rest of the file is flight times to be separated out
                split = row[0].split(',') # split rows to give each airport flight times to the others
                split_ints = []
                for i in split:
                    if i not in airport_names: # if it's not an airport name it's a flight time
                        split_ints.append(int(i))
                flight_time_array.append(split_ints)
    return airport_names

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

class ATC:
    def __init__(self):
        self.storm_time = -1
        self.storm_length = -1
        self.storm_location = None
        self.storm_info = [self.storm_time, self.storm_location, self.storm_length]
    def update(self):
        '''updates time until end of simulation'''
        global current_time
        if current_time < length_of_simulation:
            current_time += 1 # keeping track of time for the entire system
    def divide_schedule(self, schedule, airport_dict):
        '''takes the schedule and distributes between each airport so they know their own departures'''
        for step in schedule:
            airport_dict[step[1]].add_to_schedule(step)
    def storm_schedule(self):
        '''generates information about storms'''
        global length_of_schedule
        self.storm_length = np.random.randint(min_storm_length, max_storm_length)  # randomly determines storm length
        if(self.storm_length < round(length_of_schedule/4)): # keeps time at the beginning of the model length for a full prestorm
            self.storm_time = np.random.randint(self.storm_length, (round(length_of_schedule/4)))
        else:
            self.storm_time = self.storm_length # because we want the storm at the beginning to be able to see the effects later
        self.storm_location = airport_names[np.random.randint(0, len(airport_names))]
        self.storm_info = [self.storm_time, self.storm_location, self.storm_length]

class Airport:
    '''handles the departures of each airplane, as well as reciving airplanes from other airports'''
    def __init__(self, code, airport_schedule, planes_ready, planes_arriving):
        self.code = code
        self.airport_schedule = airport_schedule
        self.planes_ready = planes_ready
        self.planes_arriving = planes_arriving
        self.planes_arriving_log = []
        self.planes_departing = []
        self.planes_departing_log = []
        self.storm_delays = 0
        self.delays = 0
    def add_to_schedule(self, step):
        '''takes info from the schedule distribution by the atc and compiles own schedule'''
        self.airport_schedule.append(step)
    def arriving_plane(self, plane):
        '''keep track of arriving planes and bring them in next time cycle after wait period'''
        self.planes_arriving.append(plane)
    def storm_check(self):
        '''checks storm info and update airport schedule with delays'''
        storm_info = atc.storm_info
        self.storm_delays = 0
        for time_step in range(len(self.airport_schedule)):
            schedule_step = self.airport_schedule[time_step]
            if schedule_step[0] == current_time:
                flight_time = find_flight_time(airport_dict, airport_names, self.code, schedule_step[2])
                # storm_info is formatted as storm_time, storm_location, storm_length
                if (storm_info[0] <= (current_time + flight_time)) and ((current_time + flight_time) <= (storm_info[0] + storm_info[2])) and (schedule_step[2] == storm_info[1]): # if the destination is under a storm
                    self.airport_schedule[time_step][0] += 1
                    self.storm_delays += 1
                elif (storm_info[0] <= current_time <= (storm_info[0] + storm_info[2])) and (self.code == storm_info[1]): # if the current airport is under a storm
                    self.airport_schedule[time_step][0] += 1
                    self.storm_delays += 1
        return self.storm_delays
    def departure_update(self):
        '''tells planes when to leave and for where'''
        global current_time
        planes_departing = [] # log what planes leave in this update
        self.delays = 0
        for time_step in range(len(self.airport_schedule)):
            schedule_step = self.airport_schedule[time_step]
            if schedule_step[0] == current_time: # if there is a flight scheduled now
                if len(self.planes_ready) > 0: # if we have planes available
                    plane_flying = self.planes_ready[0] # send out the next available plane
                    flight_time = find_flight_time(airport_dict, airport_names, self.code, schedule_step[2])
                    plane_dict[plane_flying].assign_new_destination(schedule_step[2], flight_time, schedule_step[-1])
                    self.planes_departing.append(plane_flying)
                    if len(self.planes_ready) == 1: # if that was the last available plane, the list becomes empty
                        self.planes_ready = []
                    else: # otherwise just remove the plane from the list
                        self.planes_ready.remove(plane_flying)
                else: # if we don't have planes available
                    self.airport_schedule[time_step][0] += 1 # push back that flight
                    self.delays +=1 # add an hour of delay
        self.planes_departing_log.append(len(self.planes_departing)) # track how many planes left in this update
        return self.delays
    def arrival_update(self):
        '''takes planes that have arrived and processes them to ready to fly'''
        for plane in self.planes_arriving:
            self.planes_ready.append(plane)
        self.planes_arriving_log.append(len(self.planes_arriving))
        self.planes_arriving = []

class Plane:
    def __init__(self, code, location, destination, arrival_time):
        self.code = code
        self.location = location
        self.destination = destination
        self.arrival_time = arrival_time
        self.flying = False
        self.flight_number = 0
    def assign_new_destination(self, destination, arrival_time, flight_number):
        '''assigns plane destination when airport tells it to take off'''
        global current_time
        self.destination = destination
        self.arrival_time = arrival_time + current_time
        self.flying = True
        self.flight_number = flight_number
    def update(self,airport_dict):
        '''logs plane info per time and checks if it's arrived at its destination yet'''
        global current_time
        global planes_in_air
        global plane_tracking
        plane_tracking.append([current_time, self.code, self.location, self.destination, self.flight_number])
        if self.arrival_time == current_time: # if the plane has arrived
            self.location = self.destination
            airport_dict[self.destination].arriving_plane(self.code) # tell the destination airport the plane has arrived
            self.flying = False # remove itself from the list of planes in flight

def create_airports():
    '''loops through each airport name and creates an object based on that list'''
    airport_dict = {}
    for i in airport_names:
        name = i # the name is the airport code as a string
        schedule = [] # empty for initialization
        arrivals = [] # empty for initialization
        planes_ready = [] # empty for initialization
        i = Airport(name, schedule, planes_ready, arrivals)
        airport_dict[name] = i  # dictionary to make it easier to refer to airport objects
    return airport_dict

def create_airplanes():
    '''creates airplanes and returns a dictionary with names and location'''
    plane_dict = {}
    names = []
    for i in range(len(airport_names) * airport_size): # creates a series of names, a0, a1, a2, etc, as many as necessary
        names.append('a'+ str(i))
    plane_num = 0
    for i in range(len(airport_names)):
        for j in range(airport_size): # evenly distributes planes to airports
            name = names[plane_num]
            plane_names.append(name)
            names[plane_num] = Plane(name, airport_names[i], airport_names[i],-1)   # the -1 gives all the airports their planes at the same time
            plane_dict[name] = names[plane_num]
            plane_num += 1
    return plane_dict

def find_flight_time(airport_dict, airport_names, port_one, port_two):
    '''returns the time from port one to port two'''
    for i in range(len(airport_names)):
        if airport_names[i] == port_one: # find the first airport
            port_one = i
        if airport_names[i] == port_two: # find the second airport
            port_two = i
    return flight_time_array[port_one][port_two] # consult the flight time array for flight time

def run_simulation(storms):
    '''storm global variables'''
    global storm_delays
    global storm_flights
    global storm_planes_arriving
    global storm_planes_departing
    '''no storm global variables'''
    global no_storm_delays
    global no_storm_flights
    global no_storm_planes_arriving
    global no_storm_planes_departing
    '''loops through an entire simulation, takes in if there are storms or not'''
    #first, set up an array to keep track of how many planes are flying at each time and how many delays occur
    planes_in_air_at_time = []
    delayed_per_hour = []
    total_delays = 0
    delays = 0
    #then, step through each time in the run_simulation
    for step in range(length_of_simulation):
        delays = 0 #reset the number of delays for time step
        atc.update() #update the time each step
        for airport in airport_names:
            #run through each airport and check if there are any storms which affect the current flights and update accordingly, also add any delays caused by this
            if storms:
                delays += airport_dict[airport].storm_check()
            #send any flights, and if there arent enough airplanes then add that into our calculated delays too
            delays += airport_dict[airport].departure_update()
        for plane in plane_names:
            #have plane check if it should be arriving somewhere
            plane_dict[plane].update(airport_dict)
        for airport in airport_names:
            #then process the arriving planes in the airports
            airport_dict[airport].arrival_update()
        #determine how many planes are currently flying
        planes_currently_flying = 0
        for plane in plane_names:
            if plane_dict[plane].flying == True:
                planes_currently_flying += 1
        planes_in_air_at_time.append(planes_currently_flying)
        delayed_per_hour.append(delays)
        total_delays += delays
    #keeping track of metrics about how many storms and delays there were
    if storms:
        storm_flights = planes_in_air_at_time
        storm_delays = delayed_per_hour
        for airport in airport_names:
            storm_planes_arriving.append(airport_dict[airport].planes_arriving_log)
            storm_planes_departing.append(airport_dict[airport].planes_departing_log)
    else:
        no_storm_flights = planes_in_air_at_time
        no_storm_delays = delayed_per_hour
        for airport in airport_names:
            no_storm_planes_arriving.append(airport_dict[airport].planes_arriving_log)
            no_storm_planes_departing.append(airport_dict[airport].planes_departing_log)

if __name__ == '__main__':
    '''allows us to run through the simulation twice with the same schedule to see how storms affect the pattern'''
    '''these global variable are changed throughout the simulation'''
    current_time = -2
    flight_time_array = []
    plane_names = []
    airport_names = read_csv(flight_time_array)
    '''setting up the airports, planes, and schedule by initializing classes'''
    airport_dict = create_airports()
    plane_dict = create_airplanes()
    schedule = create_schedule(airport_names, airport_size, length_of_schedule, airport_dict)
    storm_planes = schedule.copy()
    atc = ATC()
    atc.storm_schedule()
    '''looping through the same schedule with and without a stom'''
    for storm in range(2):
        #resetting the airports and planes so each time they start from their initial values
        airport_dict = {}
        plane_dict = {}
        plane_names = []
        airport_dict = create_airports()
        plane_dict = create_airplanes()
        plane_tracking = []
        current_time = -2
        if storm == 0:
            atc.divide_schedule(schedule, airport_dict)
            run_simulation(False)
        else:
            atc.divide_schedule(storm_planes, airport_dict)
            run_simulation(True)
    '''Plotting'''
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
    plt.figure(0)
    plt.title("Flights Under No Storm Condition")
    plt.plot(no_storm_flights, label = 'Flights')
    plt.plot(no_storm_delays, label = 'Delays')
    i = 0
    for airport_num in range(len(airport_names)): # graphing arrivals by airport over time
        airport = airport_names[airport_num]
        if plot_arrivals == True:
            plt.plot(no_storm_planes_arriving[airport_num], ':', color=plotting[i], label=str(airport) + ' Arrivals')
        else:
            plt.plot(no_storm_planes_departing[airport_num], ':', color=plotting[i+1], label=str(airport) + ' Departures')
        i += 2
    plt.xlabel('Time (Hours)')
    plt.ylabel('Number of Planes')
    plt.legend()
    plt.figure(1)
    plt.title('Flights Under Storm Condition')
    plt.plot(storm_flights, label = 'Flights')
    plt.plot(storm_delays, label = 'Delays')
    i = 0
    for airport_num in range(len(airport_names)): # graphing arrivals by airport over time
        airport = airport_names[airport_num]
        if plot_arrivals == True:
            plt.plot(storm_planes_arriving[airport_num], ':', color=plotting[i], label=str(airport) + ' Arrivals')
        else:
            plt.plot(storm_planes_departing[airport_num], ':', color=plotting[i+1], label=str(airport) + ' Departures')
        i += 2
    plt.xlabel('Time (Hours)')
    plt.ylabel('Number of Planes')
    plt.legend()
    plt.figure(2)
    plt.title('Number of Flights, Storm vs No Storm Condition')
    plt.plot(storm_flights, label = 'Flights with Storm')
    plt.plot(no_storm_flights, label = 'Flights without Storm')
    plt.plot(storm_delays, label = 'Delays caused by Storm')
    plt.legend()
    print('PLANE INCREASE')
    print('Storm time {}, location {}, length {}'.format(atc.storm_time, atc.storm_location, atc.storm_length))
    print('Flying probability {}%, length of simulation {}, length of schedule {}, airport size {}'.format((flying_prob*100), length_of_simulation, length_of_schedule, airport_size))
    plt.show()
