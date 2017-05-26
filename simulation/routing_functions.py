__author__ = 'maxbiggs'

import numpy as np


def distance_between_nodes(demand_node_list):
    """
    Calculate the pairwise euclidean distance between demand nodes

    inputs:
        num_demand_nodes= (int) number of demand nodes
    outputs:
        distance_matrix = (num_demand_nodes x num_demand_nodes) numpy array with distances between demand nodes
    """

    num_demand_nodes=len(demand_node_list)

    distance_matrix=np.zeros([num_demand_nodes,num_demand_nodes])
    for a,node_a in enumerate(demand_node_list):
        for b,node_b in enumerate(demand_node_list):
            if not(a == b):
                distance_matrix[a,b]=np.sqrt((node_a.lat-node_b.lat)**2+(node_a.lon-node_b.lon)**2)

    return distance_matrix

def dispatch_nurse(nurse_list,customer,current_time,distance_matrix):
    """
    This function chooses and dispatches the next nurse
    If there is no nurse available when a customer arrives, the next available nurse is dispatched

    inputs:
        nurse_list= (list of nurse objects) nurses to be considered for routing
        customer = (object) customer to be routed (TO DO: make decision based on all customers that are currently available)
        current_time = (float) time at which dispatch decision is made
        distance_matrix = (num_demand_nodes x num_demand_nodes) numpy array with distances between demand nodes
    outputs:
        nurse_to_dispatch= (int) index of nurse to dispatch
        current_time = time at which customer is dispatched
    """

    # find closest available nurse
    closest_avail_nurse_index=find_closest_available_nurse(nurse_list,customer,current_time,distance_matrix)
    nurse_to_dispatch=nurse_list[closest_avail_nurse_index]

    # If no nurse is available, send the nurse which finishes first
    if closest_avail_nurse_index==-1:
        nurse_to_dispatch=min(nurse_list, key=lambda x: x.customer_finish_time)
        # advance time to when next nurse finishes
        current_time=nurse_to_dispatch.customer_finish_time

    return nurse_to_dispatch,current_time

def find_closest_available_nurse(nurse_list,customer,current_time,distance_matrix):
    """
    This function finds the closest available nurse

    inputs:
        nurse_list= (list of nurse objects) nurses to be considered for routing
        customer = (object) customer to be routed (TO DO: make decision based on all customers that are currently available)
        current_time = (float) time at which dispatch decision is made
        distance_matrix = (num_demand_nodes x num_demand_nodes) numpy array with distances between demand nodes
    outputs:
        closest_avail_nurse_index= (int) index of closest nurse
    """

    # initialize to large value
    closest_avail_nurse_distance=np.amax(distance_matrix)+1
    # default value -1 if no nurse is available
    closest_avail_nurse_index=-1
    #find closest available nurse
    for i,nurse in enumerate(nurse_list):
        #update nurse availability
        nurse.check_availability(current_time)
        if nurse.busy==False:
            if distance_matrix[customer.location,nurse.location] < closest_avail_nurse_distance:
                closest_avail_nurse_index=i
                closest_avail_nurse_distance=distance_matrix[customer.location,nurse.location]

    return  closest_avail_nurse_index

def serve_customer(nurse,customer,current_time,distance_matrix):

    """Update metrics once nurse chosen

    inputs:
        nurse_list= (list of nurse objects) nurses to be considered for routing
        customer = (object) customer to be routed (TO DO: make decision based on all customers that are currently available)
        current_time = (float) time at which dispatch decision is made
        distance_matrix = (num_demand_nodes x num_demand_nodes) numpy array with distances between demand nodes
    """

    travel_time=distance_matrix[nurse.location,customer.location]

    nurse.time_driving.append(travel_time)
    nurse.time_serving.append(customer.service_time)
    nurse.wait_time.append(current_time-nurse.customer_finish_time)
    nurse.customers_served+=1
    nurse.customer_finish_time=current_time+travel_time+customer.service_time
    nurse.busy=True
    nurse.dispatch_time.append(current_time)
    nurse.time_start_service.append(current_time+travel_time)

    customer.wait_time=current_time+travel_time-customer.arrival_time
    customer.time_nurse_arrival=current_time+travel_time
    customer.time_finish_service=current_time+travel_time+customer.service_time
    return
