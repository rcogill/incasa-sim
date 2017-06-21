__author__ = 'scaso'

import xml.etree.ElementTree as ET
from datetime import datetime
import math
import numpy as np


def read_file(clinicID):
    """Loads and reads the file of MinuteClinic wait time data.
    Inputs: xml file of data, MinuteClinic Store ID number
    Outputs: dictionary mapping the time of day (in units of minutes as timesteps) to wait time at a given MinuteClinic
    """
    # tested: works as intended
    tree = ET.parse('1week_waitTimes_2017.xml')
    root = tree.getroot()
    wait_dict = {}
    # find the clinic in the data using the ID number
    for i in range(4, 416851):
        if root[4][0][i][0][0].text == str(clinicID):
            start = i
            break

    for i in range(start, start + 10000): #unsure how many data points each clinic had, used 10,000 as a large upper bound
        if root[4][0][i][0][0].text != str(clinicID):
            stop = i
            break

    # need to get precise number of data points (rows)
    for i in range(start, stop):
        try:
            timestamp = root[4][0][i][1][0].text
            wait_time = root[4][0][i][2][0].text
            if wait_time == '180+':
                wait_time = 180
            if wait_time == "Closed":
                continue
            elif wait_time == "Unavailable":
                continue
            else:
                wait_dict[timestamp] = float(wait_time)
        except:
            break
    return wait_dict


def get_demand_at_clinic(clinic, time_start, time_stop):
    """Estimates the demand at a given MinuteClinic.
    Inputs: clinic ID, time range you are looking at (hours given in military time (ints 0-23))
    Outputs: a list of customer arrival times at that clinic (using units of minutes for the timesteps), and the corresponding minute they arrive at
    """
    # tested: works as intended
    # make time_start and time_stop into actual datetime objects
    # dates are 4/2 to 4/8/2017
    wait_dict = read_file(clinic)
    #print(wait_dict)
    new_wait_dict = {}
    dates = wait_dict.keys()
    for date in dates:
        original_date = date
        date = date.split('T')
        date[0] = date[0].split('-')
        y = int(date[0][0])
        m = int(date[0][1])
        d = int(date[0][2])
        date[1] = date[1].split(":")
        h = int(date[1][0])
        min = int(date[1][1])
        sec = int(float(date[1][2]))
        key_date = datetime(y, m, d, h, min, sec)
        for val in wait_dict.values():
            if wait_dict[original_date] == val:
                new_wait_dict[key_date] = val
    # create dates using start and stop values
    y = 2017
    m = 4
    min = 0
    sec = 0
    start_times = []
    stop_times = []
    for i in range(2,9):
        d = i
        h = time_start
        start = datetime(y, m, d, h, min, sec)
        start_times.append(start)
        h = time_stop
        stop = datetime(y, m, d, h, min, sec)
        stop_times.append(stop)
    all_wait_times = []
    all_arrivals = []
    all_customers = []
    # simulate each day you have data for
    for start in start_times:
        for stop in stop_times:
            if start.day == stop.day:
                wait_times = []
                arrivals = []
                for time in sorted(new_wait_dict.keys()):
                    if time.day == start.day:
                        if time > start:
                            if time < stop:
                                wait_times.append(new_wait_dict[time])
                                minute = time.minute
                                hour = time.hour
                                arrival = minute + 60*(hour - time_start)
                                arrivals.append(arrival)
                all_wait_times.append(wait_times)
                all_arrivals.append(arrivals)
                time_prior = 0
                customers = []
                for wait_time in wait_times:
                    add_cus = 0
                    if time_prior < wait_time:
                        add_cus = math.ceil((wait_time - time_prior)/18)
                        if time_prior == 0:
                            add_cus += 1
                    customers.append(add_cus)
                    time_prior = wait_time
                all_customers.append(customers)
    return all_customers, all_arrivals


def create_clinics():
    """Loads and reads the file of store info data.
    Returns a dictionary of MinuteClinic clinic ID numbers mapped to their zip codes, latitutde, longitude,
    state, and town."""
    # tested: works as intended
    tree = ET.parse('1week_storeInfo_2017.xml')
    root = tree.getroot()
    clinic_dict = {}
    for i in range(1,471):
        clinic = root[4][1][i][0][0].text
        if clinic not in clinic_dict.keys():
            zipcode = root[4][1][i][4][0].text
            lat = root[4][1][i][6][0].text
            long = root[4][1][i][7][0].text
            state = root[4][1][i][5][0].text
            town = root[4][1][i][3][0].text
            clinic_dict[clinic] = []
            clinic_dict[clinic] += [zipcode, lat, long, state, town]
    return clinic_dict


def estimate_demand_at_node(zipcode, time_start, time_stop):
    """Estimates the demand at a given node in a specified time interval based on the nearest minute clinic.
    Inputs: demand node zip code, list of clinics, time interval
    Outputs: a list of estimated customer arrival times at that node.
    """
    # tested: works as intended
    clinics = create_clinics()
    for key in clinics.keys():
        if clinics[key][0] == zipcode:
            clinicID = key
    customers, arrivals = get_demand_at_clinic(clinicID, time_start, time_stop)
    return customers, arrivals, clinics

def estimate_arrival_rate(zipcode, start, stop):
    '''Estimates the arrival rate of customers based on Minute Clinic Data.
    Inputs:
    Outputs: arrival rate, the estimated arrival rate based on wait times over a given time period
    '''
    customers, arrivals, clinics = estimate_demand_at_node(zipcode, start, stop)
    time_horizon = (stop - start) * 60
    arrival_rate = 0
    for customers_on_day in customers:
        arrival_rate_on_day = sum(customers_on_day) / time_horizon
        arrival_rate += arrival_rate_on_day
    arrival_rate = arrival_rate / 7
    return arrival_rate


#i, j = get_demand_at_clinic(1675,9,17)
#print(i)
#print(j)
#arrival_rate = estimate_arrival_rate('2138',10,17)
#print(arrival_rate)
#arrival_rate = estimate_arrival_rate('2140',10,17)
#print(arrival_rate)
#print(mean)
# locations = ['77056','77006','77025','77095','77079','77058','77069']
# customers_per_zip = []
# for loc in locations:
#     customers, arrivals = estimate_demand_at_node(loc,8, 19)
#     print(customers)
#     total_cus = 0
#     for customers_on_day in customers:
#         total_cus += sum(customers_on_day)
#     customers_per_zip.append(total_cus)
# print(customers_per_zip)
#customers, arrivals = get_demand_at_clinic('648',13,17)
#print(customers)
#arrival_rate = estimate_arrival_rate('2138',9,17)
#print(arrival_rate)
# arrival_rate = estimate_arrival_rate('77006',9,17)
# print(arrival_rate)