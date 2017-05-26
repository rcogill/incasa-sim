__author__ = 'maxbiggs'

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def time_varying_system_metrics(nurse_list,customer_list):
    """This function collates and reports on how the state of simulation changes with time
    Metrics reported: # customers waiting, # customers being served, # nurses idle, # nurses travelling
    These metrics are visualized in plot over time horizon

    inputs:
        nurse_list= (list of nurse objects)
        customer_list = (list of customer objects)
    """

    #extract event times from respective objects
    arrival_times=[cust.arrival_time for cust in customer_list]
    dispatch_times=[dispatch for nurse in nurse_list for dispatch in nurse.dispatch_time]
    service_begin_times=[start_service for nurse in nurse_list for start_service in nurse.time_start_service]
    finish_service_times=[cust.time_finish_service for cust in customer_list]

    # get sorted list of event times
    event_times=arrival_times+dispatch_times+service_begin_times+finish_service_times
    event_categories=["arrival"]*len(arrival_times)+["dispatch"]*len(dispatch_times)+\
                     ["service_begin_times"]*len(service_begin_times)+["finish_service_times"]*len(finish_service_times)
    d={'event_times': event_times}
    event_dataframe=pd.DataFrame(d)
    # need to sort by category for scenario where multiple events happen at same time (ie arrival occurs before dispatch, even if both occur simultaneously)
    event_dataframe['event_categories']=pd.Categorical(event_categories, ["arrival","finish_service_times","dispatch","service_begin_times"],ordered=True)
    event_dataframe.sort_values(by=['event_times','event_categories'],inplace=True)

    print("event_dataframe",event_dataframe)

    #store metrics at each event time
    customers_waiting=np.zeros([len(event_times)])
    nurses_idle=np.zeros([len(event_times)])
    customers_being_served=np.zeros([len(event_times)])
    nurses_travelling=np.zeros([len(event_times)])

    #Initial state has no customers and all nurses idle
    current_customers_waiting=0
    current_nurses_idle=len(nurse_list)
    current_customers_being_served=0
    current_nurses_travelling=0

    # loop through events and update the state of the system
    counter=0
    for index,row in event_dataframe.iterrows():

        if row['event_categories'] == "arrival":
            current_customers_waiting+=1
        elif row['event_categories'] == "dispatch":
            current_nurses_travelling+=1
            current_nurses_idle-=1
        elif row['event_categories'] == "service_begin_times":
            current_nurses_travelling-=1
            current_customers_being_served+=1
            current_customers_waiting-=1
        elif row['event_categories'] == "finish_service_times":
            current_customers_being_served-=1
            current_nurses_idle+=1

        #record snapshot
        customers_waiting[counter]=current_customers_waiting
        nurses_idle[counter]=current_nurses_idle
        customers_being_served[counter]=current_customers_being_served
        nurses_travelling[counter]=current_nurses_travelling

        counter+=1

    # visualise state of system as it changes
    plt.plot(event_dataframe.event_times,customers_waiting,label="customers waiting")
    plt.plot(event_dataframe.event_times,customers_being_served,label="customers being served")
    plt.plot(event_dataframe.event_times,nurses_idle,label="nurses idle")
    plt.plot(event_dataframe.event_times,nurses_travelling,label="nurses travelling")
    plt.ylabel("number in system")
    plt.xlabel("event time")
    plt.legend(loc='best')

    plt.savefig('results/number_in_system.png')
    plt.close()

    # calculate how the wait time changes as a function of customer arrival time + visulaise
    cust_wait_times=[cust.wait_time for cust in customer_list]
    cust_arrival_times=[cust.arrival_time for cust in customer_list]

    plt.plot(cust_arrival_times,cust_wait_times,'ro',cust_arrival_times,cust_wait_times,'k')
    plt.ylabel("wait time")
    plt.xlabel("arrival time")

    plt.savefig('results/cust_wait_times.png')
    plt.close()

    return


def aggregate_system_metrics(nurse_list,customer_list):
    """This function collates and reports on aggregate statistics once simulation has finished
    Metrics reported: see below
    TO DO: visualization

    inputs:
        nurse_list= (list of nurse objects)
        customer_list = (list of customer objects)
    """

    #extract relevant statistics
    customer_wait=[cust.wait_time for cust in customer_list]
    customer_service_time=[cust.service_time for cust in customer_list]
    nurse_idle_time=[wait_time for nurse in nurse_list for wait_time in nurse.wait_time]
    nurse_travel_time=[travel_time for nurse in nurse_list for travel_time in nurse.time_driving]
    nurse_service_time=[service_time for nurse in nurse_list for service_time in nurse.time_serving]

    print("average_idle_time_nurse",np.mean(nurse_idle_time))
    print("average_travel_time_nurse",np.mean(nurse_travel_time))
    print("average_nurse_service_time",np.mean(nurse_service_time))
    print("nurse_percentage_idle",100*np.sum(nurse_idle_time)/(np.sum(nurse_idle_time)+np.sum(nurse_travel_time)+np.sum(nurse_service_time)))
    print("nurse_percentage_travel_time",100*np.sum(nurse_travel_time)/(np.sum(nurse_idle_time)+np.sum(nurse_travel_time)+np.sum(nurse_service_time)))
    print("nurse_percentage_service_time",100*np.sum(nurse_service_time)/(np.sum(nurse_idle_time)+np.sum(nurse_travel_time)+np.sum(nurse_service_time)))
    print("average_customer_wait",np.mean(customer_wait))
    print("max_customer_wait",np.max(customer_wait))
    print("average_customer_service_time",np.mean(customer_service_time))

    return