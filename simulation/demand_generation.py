__author__ = 'maxbiggs'

import numpy as np
import random
from random import randint
from create_objects import Demand_node,Nurse,Customer


def randomly_generate_uniform_demand_nodes(num_demand_nodes,fixed_service_time):
    """
    Randomly generate demand nodes uniformly on the unit square (0 to 1) in the 2D plane
    Arrival rates at each demand node also randomly uniformly generated between 0 and 1

    inputs:
        num_demand_nodes= number of demand nodes to generate
    outputs:
        demand_node_list=list of demand node objects

    """
    longitudes=np.random.uniform(0,1,num_demand_nodes)
    latitudes=np.random.uniform(0,1,num_demand_nodes)
    arrival_rate=np.random.uniform(0,1,num_demand_nodes)
    demand_node_list=[]
    for i in range(num_demand_nodes):
        demand_node_list.append(Demand_node(i,longitudes[i],latitudes[i],arrival_rate[i]))
    return demand_node_list


def generate_customers(demand_node_list,fixed_service_time,time_horizon):
    """
    Randomly generate customers according to homogenous poisson arrival process, defined by arrival rate at demand nodes
    input:
        demand_node_list= list of demand_node objects
        fixed_service_time= service time for each customer (assumed constant at the moment)
        time_horizon= service time for each customer (assumed constant at the moment)
    output:
        customer_list= a list of customer objects ordered by arrival time
    """

    customer_list=[]
    # create customers for each node
    for demand_node in demand_node_list:
        num_arrivals=np.random.poisson(demand_node.arrival_rate*time_horizon)
        #arrival times of poisson proccess uniformly distributed
        arrival_times=np.sort(np.random.random(num_arrivals))*time_horizon

        for i in range(num_arrivals):
            id=random.getrandbits(32)
            customer_list.append(Customer(id,demand_node.id_number,arrival_times[i],fixed_service_time))

    # sort customers according to arrival time
    customer_list.sort(key=lambda x: x.arrival_time, reverse=False)

    return customer_list


def generate_nurses(num_nurses,num_demand_nodes):
    """
    Randomly generate nurses starting at random demand nodes
    input:
        num_nurses= number of nurses
        num_demand_nodes= number of demand nodes
    output:
        nurse_list= a list of nurse objects
    """
    nurse_list=[]
    for i in range(num_nurses):
        nurse_list.append(Nurse(i, randint(0,num_demand_nodes-1)))

    return nurse_list



