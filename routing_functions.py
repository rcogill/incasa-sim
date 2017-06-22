__author__ = 'maxbiggs'

import numpy as np
import xml.etree.ElementTree as ET
from gmaps_drive_times import getTravelTime
from demand_generation import generate_demand_nodes_in_zip, generate_demand_nodes_from_data


def distance_between_nodes_api(demand_node_list):
    """
    Fetches travel time data real-time using the Google API and the script gmaps_drive_times. Works with demand nodes
    generated by the functions generate_demand_nodes_from_data and generate_demand_nodes_from_zip.

    Inputs:
        demand_node_list = list of demand node objects based on real locations
    Outputs:
        travel_time_matrix = (num_demand_nodes x num_demand_nodes) numpy array with distances between demand nodes
    """

    num_demand_nodes = len(demand_node_list)
    travel_time_matrix = np.zeros([num_demand_nodes, num_demand_nodes])

    for a, node_a in enumerate(demand_node_list):
        for b, node_b in enumerate(demand_node_list):
            if not(a==b):
                (travelTimeText, travelTimeSec, distanceText, distanceM) = getTravelTime(float(node_a.lat), float(node_a.lon), float(node_b.lat), float(node_b.lon))
                travel_time_matrix[a, b] = travelTimeSec/60
    return travel_time_matrix


def distance_between_fake_nodes(demand_node_list):
    """
    Calculates the pairwise euclidean distance between pretend, randomly generated demand nodes.

    Inputs:
        demand_node_list = list of demand node objects
    Outputs:
        distance_matrix = (num_demand_nodes x num_demand_nodes) numpy array with the distances between demand nodes
    """
    num_demand_nodes = len(demand_node_list)
    distance_matrix=np.zeros([num_demand_nodes,num_demand_nodes])
    for a,node_a in enumerate(demand_node_list):
        for b,node_b in enumerate(demand_node_list):
            if not(a == b):
                distance_matrix[a,b]=np.sqrt((node_a.lat-node_b.lat)**2+(node_a.lon-node_b.lon)**2)*10

    return distance_matrix


def distance_between_nodes_csv(demand_node_list, file_name):
    """
    Calculates the distance between nodes based on google maps travel time data previously fetched from the API and
    saved in an XML file.

    Inputs:
        demand_node_list: list of demand node objects based on real locations
        file_name: name of the file with the drive time data between these nodes (created by the function gmaps_drive_times)

    Outputs:
        travel_time_matrix = (num_demand_nodes x num_demand_nodes) numpy array with distances between demand nodes
    """
    tree = ET.parse(file_name)
    root = tree.getroot()
    num_demand_nodes = len(demand_node_list)
    travel_time_matrix = np.zeros([num_demand_nodes, num_demand_nodes])
    for a, node_a in enumerate(demand_node_list):
        for b, node_b in enumerate(demand_node_list):
            for i in range(1, num_demand_nodes ** 2):
                if root[4][0][i][1][0].text == node_a.lat and root[4][0][i][2][0].text == node_a.lon and \
                    root[4][0][i][3][0].text == node_b.lat and root[4][0][i][4][0].text == node_b.lon:
                    travel_time = root[4][0][i][5][0].text
                    if travel_time == '1 min':
                        travel_time = travel_time.strip(' min')
                    else:
                        travel_time = travel_time.strip(' mins')
                    travel_time_num = float(travel_time)
                    travel_time_matrix[a, b] = travel_time_num
    return travel_time_matrix


def distance_matrix_with_restrictions(nurse, node_list, distance_matrix):
    """Calculates the distance matrix for a given nurse, taking into consideration areas (for now, these areas are just
    zip codes. This function can be modified to support more specific restrictions.) she is restricted from driving.

     Inputs: nurse object, list of demand node objects based on real locations
     Outputs: distance matrix specifically for that nurse
     """
    for loc in nurse.restrictions:
        for i, node_i in enumerate(node_list):
            if node_i.id_number == loc:
                distance_matrix[i,0:] = inf
                distance_matrix[0:,i] = inf
    return distance_matrix


def dispatch_nurse(nurse_list,customer,current_time,distance_matrix,service_time):
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
    nurse_to_dispatch = nurse_list[closest_avail_nurse_index]

    # If no nurse is available, send the nurse which finishes first
    if closest_avail_nurse_index==-1:
        nurse_to_dispatch=min(nurse_list, key=lambda x: x.customer_finish_time)
        # advance time to when next nurse finishes
        current_time = nurse_to_dispatch.customer_finish_time

    return nurse_to_dispatch, current_time


def updated_dispatch_nurse(nurse_list, customer, current_time, distance_matrix, service_time, time_horizon):
    """
    This function finds the best nurse for a customer who just arrived, based on the criteria of finding the nurse
    who can serve them the fastest, whether or not they are currently available or on shift.
    (This function has commented code for the future, when shifts are incorporated into the simulations)

    Inputs:
        nurse_list= (list of nurse objects) nurses to be considered for routing
        customer = (object) customer to be routed (TO DO: make decision based on all customers that are currently available)
        current_time = (float) time at which dispatch decision is made
        distance_matrix = (num_demand_nodes x num_demand_nodes) numpy array with distances between demand nodes
        time_horizon = the total time period of the simulation
    Outputs:
        The best available nurse for the customer, the dispatch time, and a list of nurses currently working
    """
    nurses_not_working = []
    nurses_working = []
    for nurse in nurse_list:
        nurse.check_is_on_shift(current_time, service_time)
        nurse.check_availability(current_time)
        if nurse.working is False:
            nurses_not_working.append(nurse)
        else:
            nurses_working.append(nurse)
    # best_other_time = time_horizon
    #new_current_time = time_horizon
    best_nurse, dispatch_time = dispatch_nurse(nurse_list,customer,current_time,distance_matrix,service_time)
    if best_nurse.busy is True:
        best_service_begins = best_nurse.customer_finish_time + int(distance_matrix[customer.location, nurse.location])
    else:
        best_service_begins = current_time + int(distance_matrix[customer.location, nurse.location])
    service_begins = time_horizon*10
    for nurse in nurses_working:
        if nurse.busy is True:
            service_begins = nurse.customer_finish_time + int(distance_matrix[customer.location, nurse.location])
            dispatch = nurse.customer_finish_time
        elif nurse.busy is False:
            service_begins = current_time + int(distance_matrix[customer.location, nurse.location])
            dispatch = current_time
        if service_begins < best_service_begins or best_service_begins is None:
            best_service_begins = service_begins
            best_nurse = nurse
            dispatch_time = dispatch
        #if new_current_time > dispatch:
         #   new_current_time = dispatch
    # for nurse in nurses_not_working:
    #     other_time = nurse.start_time - current_time + nurse.customer_finish_time
    #     if nurse.customer_finish_time == 0:
    #         dispatch = nurse.start_time
    #     else:
    #         dispatch = nurse.customer_finish_time
    #     if other_time < best_other_time:
    #         best_other_time = other_time
    #         best_other_nurse = nurse
    #         other_dispatch_time = dispatch
    # if best_time <= best_other_time:
    #     nurse_to_dispatch = best_nurse
    # else:
    #     nurse_to_dispatch = best_other_nurse
    #     dispatch_time = other_dispatch_time
    #current_time = dispatch_time #originally was new_current_time
    nurse_to_dispatch = best_nurse
    return nurse_to_dispatch, dispatch_time, nurses_working


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
    for i,nurse in enumerate(nurse_list): #this needs to be the list of working nurses only to get the correct index
        #update nurse availability
        nurse.check_availability(current_time)
        if nurse.busy==False:
            if distance_matrix[customer.location, nurse.location] < closest_avail_nurse_distance:
                closest_avail_nurse_index=i
                closest_avail_nurse_distance=distance_matrix[customer.location,nurse.location]

    return  closest_avail_nurse_index


def serve_customer(nurse,customer,distance_matrix,current_time):
    """Update metrics once nurse chosen. Compatible with the dispatch_nurse function.

    Inputs:
        nurse= (object) nurse selected to service the given customer
        customer = (object) customer to be routed (TO DO: make decision based on all customers that are currently available)
        current_time = (float) time at which dispatch decision is made
        distance_matrix = (num_demand_nodes x num_demand_nodes) numpy array with distances between demand nodes
    """

    travel_time=int(distance_matrix[nurse.location,customer.location])

    nurse.time_driving.append(travel_time)
    nurse.time_serving.append(customer.service_time)
    nurse.customers_served+=1
    nurse.busy=True
    nurse.dispatch_time.append(current_time)
    nurse.time_start_service.append(current_time+travel_time)
    if nurse.working is True:
        nurse.wait_time.append(current_time-nurse.customer_finish_time)
        nurse.customer_finish_time = current_time + travel_time + customer.service_time
    else:
        nurse.wait_time.append(0)
        nurse.customer_finish_time = nurse.start_time + travel_time + customer.service_time
        # because if the nurse is not working and is being queued to serve customers,
        # the wait time between queues will be zero
    # update nurse location, can't find where in the code this has been done already
    nurse.location = customer.location
    nurse.locs_visited.append(nurse.location)

    customer.wait_time = current_time+travel_time-customer.arrival_time
    customer.time_nurse_arrival = current_time+travel_time
    customer.time_finish_service = current_time+travel_time+customer.service_time

    return


def updated_serve_customer(nurse,customer,distance_matrix,dispatch_time,nurses_working):
    """Update metrics once nurse chosen. Compatible with the updated_dispatch_nurse function.

    Inputs:
        nurse= (object) nurse selected to serve given customer
        customer = (object) customer to be routed (TO DO: make decision based on all customers that are currently available)
        dispatch_time  = (float) time at which the nurse is dispatched
        distance_matrix = (num_demand_nodes x num_demand_nodes) numpy array with distances between demand nodes
        nurses_working = list of nurse objects who are currently on their shift

    Output:
        current_time = time (float) for the next routing decision to be considered
    """

    travel_time = int(distance_matrix[nurse.location, customer.location])

    nurse.time_driving.append(travel_time)
    nurse.time_serving.append(customer.service_time)
    nurse.customers_served += 1
    nurse.busy = True
    nurse.dispatch_time.append(dispatch_time)
    nurse.time_start_service.append(dispatch_time + travel_time)
    if nurse.working is True:
        nurse.wait_time.append(dispatch_time - nurse.customer_finish_time)
        nurse.customer_finish_time = dispatch_time + travel_time + customer.service_time
    else:
        nurse.wait_time.append(0)
        nurse.customer_finish_time = nurse.start_time + travel_time + customer.service_time
        # because if the nurse is not working and is being queued to serve customers,
        # the wait time between queues will be zero
    # update nurse location, can't find where in the code this has been done already
    nurse.location = customer.location
    nurse.locs_visited.append(nurse.location)

    customer.wait_time = dispatch_time + travel_time - customer.arrival_time
    customer.time_nurse_arrival = dispatch_time + travel_time
    customer.time_finish_service = dispatch_time + travel_time + customer.service_time

    # sort working nurses and find one that finishes first
    nurses_working.sort(key=lambda x: x.customer_finish_time)
    current_time = nurses_working[0].customer_finish_time

    return current_time

def distance_matrix_adjacent_nodes_only(demand_node_list):
    # make a weighted undirected graph, where adjacent nodes are ones that share an edge
    digraph = Digraph(demand_node_list)
    for node in demand_node_list:
        for other_node in demand_node_list:
            if digraph.determine_if_edge(node,other_node):
                digraph.addEdge(node,other_node)
    # make a distance matrix by adding the weighted edges together


class Digraph(object):

    def __init__(self, node_list):
        self.nodes = node_list
        self.edges = {} #dictionary mapping source nodes to dest nodes
        self.weighted_edges = [] #list of WeightedEdge objects

    def determine_if_edge(self, src, dest):
        # for now, my criteria is to find the 2 nearest nodes to it. I'll see what Max says about finding adjacent nodes
        dist_dict = {}
        adjacent_nodes = []
        for node in self.nodes:
            # calculate the euclidean distance between this node and each node:
            if src != node:
                euc_dist = math.sqrt((src.lat - node.lat) ** 2 + (src.lon - node.lon) ** 2)
                dist_dict[node] = euc_dist
        #adjacent_nodes.append(min(dist_dict.keys(), key=lambda x, dist_dict[x]))
        #dist_dict.del (adjacent_nodes[0])
        #adjacent_nodes.append(min(dist_dict.keys(), key=lambda x, dist_dict[x]))
        return dest in adjacent_nodes

    def addEdge(self, src, dest):
        """This method checks if the destination node is adjacent to the source node, fetches the travel time
        between the two, and then creates a weighted edge out of the two nodes."""
        if WeightedEdge.determine_if_edge():
            length = math.sqrt((src.lat - dest.lat) ** 2 + (src.lon - dest.lon) ** 2)
            drivetime = getTravelTime(src.lat, src.lon, dest.lat, dest.lon)
            if src in self.edges.keys():
                self.edges[src].append(dest)
                edge = WeightedEdge(src,dest,length,drivetime)
                self.weighted_edges.append(edge)
            else:
                self.edges[src] = []
                self.edges[src].append(dest)
                edge= WeightedEdge(src,dest,length,drivetime)
                self.weighted_edges.append(edge)
            return
        else:
            return

class WeightedEdge(Digraph):
    def __init__(self, src, dest,length,drivetime):
        self.drivetime = drivetime
        self.src = src
        self.dest = dest
        self.length = length

    def __str__(self):
        return '(' + str(self.src.id_number) + ', ' + str(self.dest.id_number) + ', traveltime = ' + str(self.traveltime) + ', distance = ' + str(self.length) + ')'

#node_list = generate_demand_nodes_in_zip(['77006'], 10, 5)
#travel_time_matrix = distance_between_nodes(node_list)
#print(travel_time_matrix)

# demand_node_list = generate_demand_nodes_from_data(['77056','77006','77025','77095','77079','77058','77069'])
# travel_time_matrix = distance_between_nodes(demand_node_list)
# print(travel_time_matrix)

# Extra code:
# busy_nurses = []
#     if nurse.busy is True:
#         for nurse in nurses_working:
#             if nurse.busy is True:
#                 busy_nurses.append(nurse)
#             if nurse.busy is False:
#                 break
#             else: