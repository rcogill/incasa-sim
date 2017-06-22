__author__ = 'maxbiggs'

import numpy as np
import random
from random import randint
from create_objects import Demand_node,Nurse,Customer
from estimating_demand import create_clinics, get_demand_at_clinic, estimate_demand_at_node, estimate_arrival_rate
import xml.etree.ElementTree as ET


def randomly_generate_uniform_demand_nodes(num_demand_nodes,rate):
    """
    Randomly generate demand nodes uniformly on the unit square (0 to 1) in the 2D plane
    Arrival rates at each demand node also randomly uniformly generated between 0 and 0.1 customers/min

    inputs:
        num_demand_nodes= number of demand nodes to generate
        rate = upper bound of arrival rate
    outputs:
        demand_node_list=list of demand node objects
    """
    longitudes=np.random.uniform(0,1,num_demand_nodes)
    latitudes=np.random.uniform(0,1,num_demand_nodes)
    arrival_rate=np.random.uniform(0,rate,num_demand_nodes)
    demand_node_list=[]
    zip = None
    for i in range(num_demand_nodes):
        for i in range(num_demand_nodes):
            demand_node_list.append(Demand_node(i, longitudes[i], latitudes[i], zip, arrival_rate[i]))
    return demand_node_list


def generate_customers(demand_node_list,time_horizon,fixed_service_time):
    """
    Randomly generate customers according to homogenous poisson arrival process, defined by arrival rate at demand nodes
    input:
        demand_node_list= list of demand_node objects
        fixed_service_time= service time for each customer (assumed constant at the moment)
        time_horizon= time over which the simulation occurs
    output:
        customer_list= a list of customer objects ordered by arrival time

    Updated by Sarah (made num_arrivals deterministic, made arrival times uniformly distributed)
    """

    customer_list=[]
    if fixed_service_time:
        service_time = 20
    else:
        # make a dictionary of service times that maps the time to its percent probability
        service_time_dict = {'20': 50, '15': 50}
        times = []
        # might have to write a function that creates a dict, or just manually input like I am right now
        for time in service_time_dict.keys():
            for j in range(service_time_dict[time]):
                times.append(int(time))
    # create customers for each node
    for demand_node in demand_node_list:
        #num_arrivals=np.random.poisson(demand_node.arrival_rate*time_horizon)
        num_arrivals=demand_node.arrival_rate*time_horizon
        num_arrivals = int(num_arrivals)
        #arrival times of poisson proccess uniformly distributed
        #arrival_times=np.sort(np.random.random(num_arrivals))*(time_horizon)
        arrival_times = np.sort(np.random.uniform(0,time_horizon,num_arrivals))

        for i in range(num_arrivals):
            id=random.getrandbits(32)
            if fixed_service_time:
                customer_list.append(Customer(id,demand_node.id_number, int(arrival_times[i]),service_time))
            else:
                service_time = random.choice(times)
                customer_list.append(Customer(id,demand_node.id_number, int(arrival_times[i],service_time)))

    # sort customers according to arrival time
    customer_list.sort(key=lambda x: x.arrival_time, reverse=False)

    return customer_list


def generate_nurses(num_nurses,num_demand_nodes, node_list, time_horizon, shift_lower_bound, shift_upper_bound, node):
    """
    Randomly generate nurses starting at random, pretend demand nodes
    input:
        num_nurses= number of nurses
        num_demand_nodes= number of demand nodes
    output:
        nurse_list= a list of nurse objects
    """
    nurse_list=[]
    # scenario for no shifts
    if shift_lower_bound == 0 and shift_upper_bound == time_horizon:
        for i in range(num_nurses):
            start_time = 0
            end_time = time_horizon*100 # made the end_time a much larger number than it possibly could be
            if node is False:
                nurse_list.append(Nurse(i, randint(0,num_demand_nodes-1), start_time, end_time))
            if node is True:
                nurse_list.append(Nurse(i, (random.choice(node_list)).id_number, start_time,end_time))

    # scenario with shifts
    else:
        for i in range(num_nurses):
            shift_length = random.randint(shift_lower_bound, shift_upper_bound)
            start_time = random.randint(0, time_horizon)
            end_time = start_time + shift_length * 60
            if node is False:
                nurse_list.append(Nurse(i, randint(0, num_demand_nodes - 1), start_time, end_time))
            if node is True:
                nurse_list.append(Nurse(i, (random.choice(node_list)).id_number, start_time, end_time))

    return nurse_list


def generate_demand_nodes_from_data(locations, customer_type):
    """
    Generates demand nodes based on locations (a list of zip codes) from Minute Clinic data. Can be modified to generate demand nodes based on state, city, lat, or long.
    Inputs: locations of demand nodes to generate
    Outputs: demand_node_list (list of demand node objects)
    """
    clinic_dict = create_clinics()
    node_list = []
    l = 0
    for loc in locations:
        for key in clinic_dict.keys():
            # a key in this dictionary represents the clinic ID#
            zip = clinic_dict[key][0]
            # change the zero to find location based on other parameters (city, state, etc.)
            if zip == loc:
                lat = float(clinic_dict[key][1])
                long = float(clinic_dict[key][2])
                if customer_type == "random":
                    arrival_rate = random.random()
                elif customer_type == "rate from data":
                    # hard coded in 9 to 5, can change if needed
                    start = 10
                    stop = 17
                    arrival_rate = estimate_arrival_rate(zip,start,stop)
                elif customer_type == "actual":
                    arrival_rate == None
                node_list.append(Demand_node(l,long,lat,zip,arrival_rate))
                l += 1
    return node_list


def generate_demand_nodes_in_zip(locations, num_nodes, radius, customer_type):
    """Generates num_nodes demand nodes per zip code randomly based on GPS data.
    Inputs: locations (a list of zip codes), num_nodes (number of desired nodes per zip code, and radius (mi radius from
    central GPS point that is considered to be the boundary of the zip code)
    Outputs: node_list (a list of nodes)
    """
    # tested: works as intended
    node_list = []
    # read the xml file of zipcodes and their lat and long points
    tree = ET.parse('free-zipcode-database-Primary.xml')
    root = tree.getroot()
    loc_dict = {}
    for i in range(1,42524):
        try:
            zip = root[4][0][i][0][0].text
            lat = root[4][0][i][5][0].text
            lon = root[4][0][i][6][0].text
            lat = float(lat)
            lon = float(lon)
            loc_dict[zip] = []
            loc_dict[zip].extend([lat, lon])
        except:
            pass
    # go through and set the lat and long points as a list of values in a dict of zip codes
    num = 0
    # 1 degree is about 62 miles
    deg_radius = radius/62
    for loc in locations:
        for zip in loc_dict.keys():
            if loc == zip:
                lat = loc_dict[zip][0]
                lon = loc_dict[zip][1]
                UB_lat = lat + deg_radius
                LB_lat = lat - deg_radius
                UB_lon = lon + deg_radius
                LB_lon = lon - deg_radius
                # generate a random longitude and latitude between their upper and lower bounds
                for i in range(0, num_nodes):
                    rand_lat = random.uniform(LB_lat,UB_lat)
                    rand_lon = random.uniform(LB_lon, UB_lon)
                    if customer_type == "random":
                        arrival_rate = random.random()
                    elif customer_type == "rate from data":
                        # hard coded in 9 to 5, can change if needed
                        start = 10
                        stop = 17
                        arrival_rate = estimate_arrival_rate(zip, start, stop)
                        arrival_rate = arrival_rate/num_nodes
                    elif customer_type == "actual":
                        arrival_rate == None
                    node_list.append(Demand_node(num,rand_lon,rand_lat,zip,arrival_rate))
                    num += 1
    return node_list


def generate_customers_from_data(node_list, fixed_service_time, start, stop):
    """
    Uses the demand nodes (zip codes) to generate customer objects who demand the service at a given time, based on the data
    Inputs: demand node list, fixed service time, start and stop times of time horizon
    Outputs: customer list (a list of customer objects ordered by arrival time, for each given day during the time horizon)
    """
    # tested: worked as intended
    customer_data = []
    arrival_data = []
    # create a customer from each demand node
    for node in node_list:
        # creates a list of customers and their arrivals at that node, from 4/2 to 4/8
        customers, arrivals = estimate_demand_at_node(node.zip, start, stop)
        customer_data.append(customers)
        arrival_data.append(arrivals)
        # in this list, customer_data[1] = customer data from node 1
    num_days = len(customers)
    # make a list of customers for each day, save in a larger list
    all_days = []
    ID = 0
    # get data for a given day
    for d in range(num_days):
        day = []
        # get customer data from each node individually
        for i in range(len(customer_data)):
            customers = customer_data[i]
            # get customer data from a node on a given day
            for j in range(len(customers[d])):
                cus = customers[d][j]
                node = node_list[i]
                if cus > 0:
                    for c in range(cus):
                        ID += 1
                        day.append(Customer(ID, node.id_number, arrival_data[i][d][j], fixed_service_time))
        all_days.append(day)
    for customer_list in all_days:
        # sort customers according to arrival time
        customer_list.sort(key=lambda x: x.arrival_time, reverse=False)
    return all_days


def generate_nurses_with_restrictions(probabilities, node_list,num_nurses, time_horizon, shift_lower_bound, shift_upper_bound, node):
    """Generates nurses working during the simulation, some with restrictions on neighborhoods they can drive to.
    Inputs:
    probabilites: a dictionary based on user input of the probability a nurse may be restricted from this location (locations are tagged by their ID numbers)
    node_list: a list of nodes
    num_nurses: the number of nurses
    Outputs:
    nurse_list: a list of nurse objects"""
    nurse_list = []
    restrictions = [[]*num_nurses]
    # creates a list of restricted areas for each nurse based on probabilities
    for i in range(num_nurses):
        for loc in probabilities.keys():
            if probabilities[loc] > random.random():
                restrictions[i].append(loc)
    if shift_lower_bound == 0 and shift_upper_bound == time_horizon: # no shifts
        for i in range(num_nurses):
            start_time = 0
            end_time = time_horizon * 100
            if node is False:
                location = randint(0,num_demand_nodes-1)
                while location in restrictions[i]:
                    location = randint(0,num_demand_nodes)
                nurse_list.append(Nurse(i, location, start_time, end_time))
            if node is True:
                location = random.choice(node_list)
                while location in restrictions[i]:
                    location = random.choice(node_list)
                nurse_list.append(Nurse(i, (random.choice(node_list)).id_number, start_time,end_time))
    else:
        for i in range(num_nurses):
            shift_length = random.randint(shift_lower_bound, shift_upper_bound)
            start_time = random.randint(0, time_horizon)
            end_time = start_time + shift_length * 60
            if node is False:
                location = randint(0, num_demand_nodes - 1)
                while location in restrictions[i]:
                    location = randint(0, num_demand_nodes)
                nurse_list.append(Nurse(i, location, start_time, end_time))
            if node is True:
                location = random.choice(node_list)
                while location in restrictions[i]:
                    location = random.choice(node_list)
                nurse_list.append(Nurse(i, (random.choice(node_list)).id_number, start_time, end_time))

    return nurse_list


#locations = ['77006']
#node_list = generate_demand_nodes_from_data(locations)
#nurse_list = generate_nurses_from_real_nodes(10,node_list,240)
#print([nurse.start_time for nurse in nurse_list])
#print([nurse.end_time for nurse in nurse_list])
#all_days = generate_customers_from_data(node_list,10,9,17)
#print(node_list)
#print(all_days)

#node_list = generate_demand_nodes_in_zip(['77006'], 10, 5)
#for node in node_list:
 #   print(node.lat, node.lon)
# locations = ['77056','77006','77025','77095','77079','77058','77069']
# demand_node_list = generate_demand_nodes_from_data(locations)
# for node in demand_node_list:
#     print(node.lat, node.lon)

#Some code to generate demand nodes from example points in gmaps_drive_times:
# origin = np.array([
#     [29.681752, -95.234985],
#     [29.996236, -95.501404],
#     [29.996236, -95.501404],
#     [29.503823, -95.088043],
#     [29.687717, -95.688171],
#     [29.992668, -95.162201],
#     [29.762850, -94.935608],
#     [29.910566, -95.619507],
#     [29.902233, -95.333862],
#     [29.814099, -95.096283]])
# longitudes = np.zeros(len(origin))
# for i in range(len(origin)):
#     longitudes[i] = origin[i][1]
# latitudes = np.zeros(len(origin))
# for i in range(len(origin)):
#     latitudes[i] = origin[i][0]