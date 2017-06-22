__author__ = 'maxbiggs'

from demand_generation import randomly_generate_uniform_demand_nodes, generate_customers,generate_nurses, \
    generate_demand_nodes_from_data, generate_customers_from_data, generate_demand_nodes_in_zip,\
    generate_nurses_with_restrictions
from routing_functions import dispatch_nurse,distance_between_fake_nodes, distance_between_nodes_csv, \
    distance_matrix_with_restrictions, find_closest_available_nurse, serve_customer, updated_dispatch_nurse, \
    updated_serve_customer, distance_between_nodes_api
from create_objects import Demand_node,Nurse,Customer
from reporting_functions import aggregate_system_metrics, time_varying_system_metrics
from gmaps_drive_times import write_file
from pprint import pprint
import csv
import numpy as np
import random


def simulation_run_v1(num_demand_nodes,num_nurses,time_horizon,arrival_rate,fixed_service_time=True,shifts=False,restrictions=False):
    """This function runs one simulation trial using the old routing function.
    Returns the lists of nurses and nodes generated for visualization purposes.
    Demand nodes are fake and randomly generated
    The user can decide if the nurses should have restrictions or shifts based on boolean inputs.
    Asks for user input to decide other parameters.
    """

    # generate demand nodes, customers and nurses
    node = False
    demand_node_list=randomly_generate_uniform_demand_nodes(num_demand_nodes,arrival_rate)
    distance_matrix=distance_between_fake_nodes(demand_node_list)
    customer_list=generate_customers(demand_node_list,time_horizon,fixed_service_time)
    if shifts is True:
        shift_lower_bound = input('Input the minimum shift length: ')
        shift_upper_bound = input('Input the maximum shift length: ')
    else:
        shift_lower_bound = 0
        shift_upper_bound = time_horizon
    if restrictions is True:
        # build probabilities dictionary
        probabilities = {}
        for node in demand_node_list:
            print("Latitude: " %s) %node.lat
            print("Longitude: " %s) %node.lon
            prob = input('Input the probability of a nurse being restricted from this node: ')
            probabilites[node.id_number] = prob
        nurse_list = generate_nurses_with_restrictions(probabilities, node_list,num_nurses, time_horizon,
                                                       shift_lower_bound, shift_upper_bound, node)
    else:
        nurse_list=generate_nurses(num_nurses,num_demand_nodes, demand_node_list, time_horizon, shift_lower_bound, shift_upper_bound)

    # customers are served in the order they arrive (at the moment)
    current_time=0
    for customer in customer_list:

        #next event dispatch after a customer arrives and at least one nurse is available
        current_time=max(current_time,customer.arrival_time)
        # choose which nurse to dispatch
        nurse_to_dispatch,dispatch_time=dispatch_nurse(nurse_list,customer,current_time,distance_matrix,fixed_service_time)
        # serve customer and update metrics
        serve_customer(nurse_to_dispatch,customer,current_time,distance_matrix,dispatch_time)
    #report on simulation
    time_varying_system_metrics(nurse_list,customer_list,fixed_service_time, time_horizon)
    aggregate_system_metrics(nurse_list,customer_list)
    return nurse_list, demand_node_list


def simulation_run_v2(num_demand_nodes,num_nurses,time_horizon,arrival_rate,fixed_service_time=True, shifts=False, restrictions=False):
    """This function runs one simulation trial using the new routing function.
    Returns the lists of nurses and nodes generated for visualization purposes.
    Demand nodes are fake and randomly generated
    The user can decide if the nurses should have restrictions or shifts based on boolean inputs.
    Asks for user input to decide other parameters."""

    # generate demand nodes, customers and nurses
    node = False
    demand_node_list = randomly_generate_uniform_demand_nodes(num_demand_nodes, arrival_rate)
    distance_matrix = distance_between_fake_nodes(demand_node_list)
    customer_list = generate_customers(demand_node_list, time_horizon, fixed_service_time)
    if shifts is True:
        shift_lower_bound = input('Input the minimum shift length: ')
        shift_upper_bound = input('Input the maximum shift length: ')
    else:
        shift_lower_bound = 0
        shift_upper_bound = time_horizon
    if restrictions is True:
        # build probabilities dictionary
        probabilities = {}
        for node in demand_node_list:
            print("Latitude: " % s) % node.lat
            print("Longitude: " % s) % node.lon
            prob = input('Input the probability of a nurse being restricted from this node: ')
            probabilites[node.id_number] = prob
        nurse_list = generate_nurses_with_restrictions(probabilities, node_list,num_nurses, time_horizon,
                                                       shift_lower_bound, shift_upper_bound, node)
    else:
        nurse_list = generate_nurses(num_nurses, num_demand_nodes, demand_node_list, time_horizon, shift_lower_bound, shift_upper_bound)

    # customers are served in the order they arrive (at the moment)
    current_time = 0
    for customer in customer_list:
        # next event dispatch after a customer arrives and at least one nurse is available
        current_time = max(current_time, customer.arrival_time)
        # choose which nurse to dispatch
        nurse_to_dispatch, dispatch_time, nurses_working = updated_dispatch_nurse(nurse_list, customer,
                                                                                          current_time, distance_matrix,
                                                                                          fixed_service_time,
                                                                                          time_horizon)
        # serve customer and update metrics
        current_time = updated_serve_customer(nurse_to_dispatch, customer, distance_matrix, dispatch_time,
                                      nurses_working)
    # report on simulation
    time_varying_system_metrics(nurse_list, customer_list, fixed_service_time, time_horizon)
    aggregate_system_metrics(nurse_list, customer_list)
    return nurse_list, demand_node_list


def simulation_run_v3(num_demand_nodes, num_nurses, time_horizon, locations, fixed_service_time=True, shifts=False, restrictions=False):
    """This function runs on simulation trial using the old routing function.
    Returns the lists of nurses and nodes generated for visualization purposes.
    Demand nodes are generated from real GPS coordinates.
    The user can decide if the nurses should have restrictions or shifts based on boolean inputs.
    Asks for user input to decide other parameters.
    Fetches travel times from an API.
    """

    # generate demand nodes, customers, and nurses
    node = True
    node_type = input(
        'Input "actual" for nodes to be actual locations, "random" for nodes to be randomly generated locations: ')
    customer_type = input('Input "random" for random arrival rate, "rate from data", or "actual" for actual data: ')
    if node_type == "actual":
        demand_node_list = generate_demand_nodes_from_data(locations, customer_type)
    elif node_type == "random":
        radius = float(input("Input a radius for the demand nodes: "))
        demand_node_list = generate_demand_nodes_in_zip(locations, num_demand_nodes, radius, customer_type)
    else:
        raise InputError
    file_name = write_file(demand_node_list, demand_node_list)
    distance_matrix = distance_between_nodes_api(demand_node_list)
    if customer_type == "random" or "random from data":
        customer_list = generate_customers(demand_node_list, time_horizon, fixed_service_time)
    elif customer_type == "actual":
        start = input("Input a start time (hour in military time): ")
        stop = start + (time_horizon / 60)
        customer_list = generate_customers_from_data(node_list, fixed_service_time, start, stop)
        day = input("Input a number 0-6 corresponding to a day Sun-Sat: ")
        customer_list = customer_list[day]
    if shifts is True:
        shift_lower_bound = input('Input the minimum shift length: ')
        shift_upper_bound = input('Input the maximum shift length: ')
    else:
        shift_lower_bound = 0
        shift_upper_bound = time_horizon
    if restrictions is True:
        # build probabilities dictionary
        probabilities = {}
        for node in demand_node_list:
            print("Latitude: " % s) % node.lat
            print("Longitude: " % s) % node.lon
            prob = input('Input the probability of a nurse being restricted from this node: ')
            probabilites[node.id_number] = prob
        nurse_list = generate_nurses_with_restrictions(probabilities, node_list, num_nurses, time_horizon,
                                                       shift_lower_bound, shift_upper_bound, node)
    else:
        nurse_list = generate_nurses(num_nurses, num_demand_nodes, demand_node_list, time_horizon, shift_lower_bound, shift_upper_bound)

    # customers are served in the order they arrive (at the moment)
    current_time = 0
    for customer in customer_list:
        # next event dispatch after a customer arrives and at least one nurse is available
        current_time = max(current_time, customer.arrival_time)
        # choose which nurse to dispatch
        nurse_to_dispatch, dispatch_time = dispatch_nurse(nurse_list, customer, current_time, distance_matrix,
                                                              fixed_service_time)
        # serve customer and update metrics
        serve_customer(nurse_to_dispatch, customer, current_time, distance_matrix, dispatch_time)
    # report on simulation
    time_varying_system_metrics(nurse_list, customer_list, fixed_service_time, time_horizon)
    aggregate_system_metrics(nurse_list, customer_list)
    return nurse_list, demand_node_list

def simulation_run_v4(num_demand_nodes,num_nurses,time_horizon, locations, fixed_service_time=True, shifts=False, restrictions=False):
    """This function runs one simulation trial using the new routing function.
    Returns the lists of nurses and nodes generated for visualization purposes.
    Demand nodes are generated from GPS coordinates.
    The user can decide if the nurses should have restrictions or shifts based on boolean inputs.
    Asks for user input to decide other parameters.
    Fetches travel times from an API."""

    # generate demand nodes, customers, and nurses
    node = True
    node_type = input('Input "actual" for nodes to be actual locations, "random" for nodes to be randomly generated locations: ')
    customer_type = input('Input "random" for random arrival rate, "rate from data", or "actual" for actual data: ')
    if node_type == "actual":
        demand_node_list = generate_demand_nodes_from_data(locations, customer_type)
    elif node_type == "random":
        radius = float(input("Input a radius for the demand nodes: "))
        demand_node_list = generate_demand_nodes_in_zip(locations, num_demand_nodes, radius, customer_type)
    else:
        raise InputError
    file_name = write_file(demand_node_list,demand_node_list)
    distance_matrix = distance_between_nodes_api(demand_node_list)
    if customer_type == "random" or "random from data":
        customer_list = generate_customers(demand_node_list, time_horizon, fixed_service_time)
    elif customer_type == "actual":
        start = input("Input a start time (hour in military time): ")
        stop = start+(time_horizon/60)
        customer_list = generate_customers_from_data(node_list, fixed_service_time, start, stop)
        day = input("Input a number 0-6 corresponding to a day Sun-Sat: ")
        customer_list = customer_list[day]
    if shifts is True:
        shift_lower_bound = input('Input the minimum shift length: ')
        shift_upper_bound = input('Input the maximum shift length: ')
    else:
        shift_lower_bound = 0
        shift_upper_bound = time_horizon
    if restrictions is True:
        # build probabilities dictionary
        probabilities = {}
        for node in demand_node_list:
            print("Latitude: " % s) % node.lat
            print("Longitude: " % s) % node.lon
            prob = input('Input the probability of a nurse being restricted from this node: ')
            probabilites[node.id_number] = prob
        nurse_list = generate_nurses_with_restrictions(probabilities, node_list,num_nurses, time_horizon,
                                                       shift_lower_bound, shift_upper_bound, node)
    else:
        nurse_list = generate_nurses(num_nurses, num_demand_nodes, demand_node_list, time_horizon, shift_lower_bound, shift_upper_bound,node)

    # customers are served in the order they arrive (at the moment)
    current_time = 0
    for customer in customer_list:
        # next event dispatch after a customer arrives and at least one nurse is available
        current_time = max(current_time, customer.arrival_time)
        # choose which nurse to dispatch
        nurse_to_dispatch, dispatch_time, nurses_working = updated_dispatch_nurse(nurse_list, customer,
                                                                                      current_time, distance_matrix,
                                                                                      fixed_service_time,
                                                                                      time_horizon)
        # serve customer and update metrics
        current_time = updated_serve_customer(nurse_to_dispatch, customer, distance_matrix, dispatch_time,
                                                  nurses_working)
    # report on simulation
    time_varying_system_metrics(nurse_list, customer_list, fixed_service_time, time_horizon)
    aggregate_system_metrics(nurse_list, customer_list)
    return nurse_list, demand_node_list

def simulation_run_real_nodes_part_one(num_demand_nodes,locations):
    """First part of simulation version 4. Uses a CSV file from API data downloaded in this part."""
    # generate demand nodes, customers, and nurses
    node_type = input(
        'Input "actual" for nodes to be actual locations, "random" for nodes to be randomly generated locations: ')
    customer_type = input('Input "random" for random arrival rate, "rate from data", or "actual" for actual data: ')
    if node_type == "actual":
        demand_node_list = generate_demand_nodes_from_data(locations, customer_type)
        print(demand_node_list)
    elif node_type == "random":
        radius = float(input("Input a radius for the demand nodes: "))
        demand_node_list = generate_demand_nodes_in_zip(locations, num_demand_nodes, radius, customer_type)
        print(demand_node_list)
    else:
        raise InputError
    file_name = write_file(demand_node_list, demand_node_list)
    return file_name, customer_type

def simulation_run_real_nodes_part_two(num_demand_nodes,num_nurses,demand_node_list,time_horizon,file_name, customer_type, fixed_service_time=True, shifts=False, restrictions=False):
    """Second part of simulation version 4. Uses a CSV of travel time data downloaded from part one."""
    node = True
    distance_matrix = distance_between_nodes_csv(demand_node_list, file_name)
    if customer_type == "random" or "random from data":
        customer_list = generate_customers(demand_node_list, time_horizon, fixed_service_time)
    elif customer_type == "actual":
        start = input("Input a start time (hour in military time): ")
        stop = start + (time_horizon / 60)
        customer_list = generate_customers_from_data(node_list, fixed_service_time, start, stop)
    if shifts is True:
        shift_lower_bound = input('Input the minimum shift length: ')
        shift_upper_bound = input('Input the maximum shift length: ')
    else:
        shift_lower_bound = 0
        shift_upper_bound = time_horizon
    if restrictions is True:
        # build probabilities dictionary
        probabilities = {}
        for node in demand_node_list:
            print("Latitude: " % s) % node.lat
            print("Longitude: " % s) % node.lon
            prob = input('Input the probability of a nurse being restricted from this node: ')
            probabilites[node.id_number] = prob
        nurse_list = generate_nurses_with_restrictions(probabilities, node_list, num_nurses, time_horizon,
                                                       shift_lower_bound, shift_upper_bound, node)
    else:
        nurse_list = generate_nurses(num_nurses, num_demand_nodes, demand_node_list, time_horizon, shift_lower_bound, shift_upper_bound,node)

    # customers are served in the order they arrive (at the moment)
    current_time = 0
    for customer in customer_list:
        # next event dispatch after a customer arrives and at least one nurse is available
        current_time = max(current_time, customer.arrival_time)
        # choose which nurse to dispatch
        nurse_to_dispatch, dispatch_time, nurses_working = updated_dispatch_nurse(nurse_list, customer,
                                                                                  current_time, distance_matrix,
                                                                                  fixed_service_time,
                                                                                  time_horizon)
        # serve customer and update metrics
        current_time = updated_serve_customer(nurse_to_dispatch, customer, distance_matrix, dispatch_time,
                                              nurses_working)
    # report on simulation
    time_varying_system_metrics(nurse_list, customer_list, fixed_service_time, time_horizon)
    aggregate_system_metrics(nurse_list, customer_list)
    return nurse_list, demand_node_list

def track_nurses_paths(nurse_list,demand_node_list):
    '''Stores all the locations each nurse visited into a CSV file for visualization later.'''
    f = open('nurses_at_timestep.csv', 'w')
    wr = csv.writer(f)
    wr.writerow(('longitude', 'latitude', 'nurse','timestep'))
    for nurse in nurse_list:
        for time in range(len(nurse.time_start_service)):
            for node in demand_node_list:
                if nurse.locs_visited[time] == node.id_number:
                    wr.writerow((node.lon, node.lat, nurse.id_number, nurse.time_start_service[time]))
    return


def optimize_nurses_simulation_run():
    '''Same simulation as above, just optimizes the amount of nurses based on certain metrics being met.'''
    # set simulation parameters

    locations = ['77056','77006','77025','77095','77079','77069']
    num_demand_nodes = len(locations)
    num_nurses = 22
    time_horizon = 60 * 8
    fixed_service_time = 18
    start = 9
    # stop = int(start + (time_horizon/60))
    stop = 17

    # generate demand nodes, customers, and nurses:
    demand_node_list = generate_demand_nodes_from_data(locations)
    #demand_node_list = generate_demand_nodes_in_zip(locations, 25, 5)
    distance_matrix = distance_between_nodes(demand_node_list)
    customer_list = generate_customers_from_data(demand_node_list, fixed_service_time, start, stop)
    #customer_list = generate_customers(demand_node_list, fixed_service_time, time_horizon)
    #nurse_list = generate_nurses_from_real_nodes(num_nurses, demand_node_list)

    for n in range(1,num_nurses):
        nurse_list = generate_nurses_from_real_nodes(n, demand_node_list,time_horizon)


        # customers are served in the order they arrive (at the moment)
        current_time = 0
        for customer in customer_list[2]:  # will have to change to customer_list[i] if using customers from data

            # next event dispatch after a customer arrives and at least one nurse is available
            current_time = max(current_time, customer.arrival_time)
            # choose which nurse to dispatch
            nurse_to_dispatch, current_time = dispatch_nurse(nurse_list, customer, current_time, distance_matrix,fixed_service_time)
            # serve customer and update metrics
            serve_customer(nurse_to_dispatch, customer, current_time, distance_matrix)

        # report on simulation
        time_varying_system_metrics(nurse_list, customer_list[2],fixed_service_time, time_horizon)
        customer_wait = aggregate_system_metrics(nurse_list, customer_list[2])
            # to find optimal num of nurses, made a for loop iterating through possible numbers of nurses
        if customer_wait < 60.0:
            return n
            break

locations = ['77056','77006','77025','77095','77079','77069']
#nurse_list, demand_node_list = simulation_run_v4(3,5,90,20,locations)
#file_name = simulation_run_real_nodes_part_one(3,locations)
#file_name = 'traveltimes.xml'
#customer_type = 'random'
#demand_node_list = generate_demand_nodes_from_data(locations,customer_type)
#nurse_list, demand_node_list = simulation_run_real_nodes_part_two(3,5,demand_node_list,90,20,file_name,customer_type)
#track_nurses_paths(nurse_list, demand_node_list)

nurse, demand = simulation_run_v4(3,5,60, locations)