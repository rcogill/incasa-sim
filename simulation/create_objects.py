__author__ = 'maxbiggs'

import numpy as np
import random

class Customer(object):
    """A customer wanting to be served by a nurse practitioner. Customers have the
    following properties:

    Attributes:
        id_number: (integer) An id representing the customer.
        location: (integer) An integer representing the discrete demand node a customer arrives at
        arrival_time: (float) The time the customer requests service
        service_time: (float) How long the customer will take to be served (constant for now)
        wait_time: (float) How long did the customer wait? (variable)
        time_nurse_arrival: (float) Time the nurse arrives (variable)
        time_finish_service: (float) Time customer finishes service
    """

    def __init__(self, id_number, location,arrival_time,service_time,wait_time=0,time_nurse_arrival=0,time_finish_service=0):
        """Return a Customer object"""
        self.id_number = id_number
        self.location = location
        self.arrival_time = arrival_time
        self.service_time = service_time
        self.wait_time = wait_time
        self.time_nurse_arrival=time_nurse_arrival
        self.time_finish_service=time_finish_service

    def __str__(self):
        "if print is called, we print out state of customer"
        return("\n id_number " + str(self.id_number) + "\n location " + str(self.location) + "\n arrival_time " + str(self.arrival_time)
               + "\n service_time " + str(self.service_time)+ "\n wait_time " + str(self.wait_time)+"\n time_nurse_arrival " + str(self.time_nurse_arrival) )


class Nurse(object):
    """A nurse available for service customers. Nurses have the
    following properties:

    Attributes:
        id_number: (integer) An id representing the nurse.
        location: (integer) An integer representing the discrete demand node a nurse is currently at (variable)
        busy: (boolean) whether the nurse is currently busy (variable)
        customer_finish_time: (float) what time will the current customer finish at?
        customers_served: (integer) How many customers has  the nurse served? (variable)
        wait_time: (list of float) How long has the nurse wait for each customer? updated throughout simulation (variable)
        time_driving: (list of float) How long did the nurse drive for each customer? updated throughout simulation (variable)
        time_serving: (list of float) How long has the nurse serving each customer? updated throughout simulation (variable)
        dispatch_time: (list of float) When was nurse dispatched for current customer
        time_start_service: (list of float) When did nurse start serving current customer
        To add?
        start_time: (float) what time a nurse practitioner starts shift
        end_time: (float) what time a nurse practitioner ends shift
    """

    def __init__(self,id_number, location, start_time, end_time, restrictions=None, working=True, busy=False,customer_finish_time=0,customers_served=0):
        """Return a Nurse object"""
        self.id_number = id_number
        self.location = location
        self.busy = busy
        self.customer_finish_time=customer_finish_time
        self.customers_served = customers_served
        self.wait_time = []
        self.time_driving = []
        self.time_serving = []
        self.dispatch_time = []
        self.time_start_service = []
        self.locs_visited = []
        self.start_time = start_time
        self.end_time = end_time
        self.working = working
        self.restrictions = restrictions

    def check_availability(self,current_time):
        """Check if nurse has finished serving current customer"""
        if self.busy==True:
            if current_time>self.customer_finish_time:
                self.busy=False
        return

    def check_is_on_shift(self,current_time,service_time):
        if self.start_time > current_time:
            self.working = False
        elif self.end_time < current_time + service_time:
            self.working = False
        else:
            self.working = True
        return

    def __str__(self):
        return("\n id_number " + str(self.id_number) + "\n location " + str(self.location) + "\n busy " + str(self.busy)
               + "\n customer_finish_time " + str(self.customer_finish_time) +"\n customers_served " + str(self.customers_served) +
                "\n wait_time " + str(self.wait_time) + "\n time_driving " + str(self.time_driving) + "\n time_serving " + str(self.time_serving))

class Demand_node(object):
    """A geographic node where customers arrive. Demand nodes have the
    following properties:

    Attributes:
        id_number: (integer) An id representing the demand node (1...num_nodes)
        lon: (float) latitude of demand node
        lat: (float) longitude of demand node
        arrival_rate: (float) rate at which customers arrive to the node
        customer_list: (float) a list of customer (ids) which are generated at that

    """

    def __init__(self, id_number, lon, lat, zip, arrival_rate):
        """Return a Demand node object with required attributes"""
        self.id_number = id_number
        self.lon = lon
        self.lat = lat
        self.zip = zip
        self.arrival_rate = arrival_rate
        #self.customer_list= []

    def __str__(self):
        return("\n id_number " + str(self.id_number) + "\n lon " + str(self.lon) + "\n lat " + str(self.lat) + "\n arrival_rate " + str(self.arrival_rate) )

