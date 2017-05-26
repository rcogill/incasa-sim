__author__ = 'maxbiggs'

from demand_generation import randomly_generate_uniform_demand_nodes,generate_customers,generate_nurses
from routing_functions import dispatch_nurse,distance_between_nodes,find_closest_available_nurse,serve_customer
from create_objects import Demand_node,Nurse,Customer
from reporting_functions import aggregate_system_metrics, time_varying_system_metrics
from pprint import pprint

def simulation_run():
    """This function runs one simulation trial.
    """

    #set simulation parameters
    num_demand_nodes=10
    num_nurses=10
    time_horizon=10
    fixed_service_time=1

    # generate demand nodes, customers and nurses
    demand_node_list=randomly_generate_uniform_demand_nodes(num_demand_nodes,fixed_service_time)
    distance_matrix=distance_between_nodes(demand_node_list)
    customer_list=generate_customers(demand_node_list,fixed_service_time,time_horizon)
    nurse_list=generate_nurses(num_nurses,num_demand_nodes)


    # customers are served in the order they arrive (at the moment)
    current_time=0
    for customer in customer_list:

        #next event dispatch after a customer arrives and at least one nurse is available
        current_time=max(current_time,customer.arrival_time)
        # choose which nurse to dispatch
        nurse_to_dispatch,current_time=dispatch_nurse(nurse_list,customer,current_time,distance_matrix)
        # serve customer and update metrics
        serve_customer(nurse_to_dispatch,customer,current_time,distance_matrix)

    #report on simulation
    time_varying_system_metrics(nurse_list,customer_list)
    aggregate_system_metrics(nurse_list,customer_list)

    return

simulation_run()