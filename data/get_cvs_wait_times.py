'''
This script opens files containing IDs of all MinuteClinics in a set of given states,
gets basic info about each clinic (location, hours, etc...),
then continually polls for wait times at all clinics.
Outputs are placed in two csv files, one for clinic info and one for wait times
'''

import urllib2
import json
import time
import datetime
import random
import csv

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def processAllClinicIDs(clinicIDsTmp,allStoreInfo):

  #-------------------------------
  # Set up the service URL and request header
  # Might need to periodically refresh the URL

  request_headers = {
  "Origin": "http://www.cvs.com",
  "Accept-Encoding": "gzip, deflate, br", 
  "Accept-Language": "en-US,en;q=0.8",
  "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
  "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
  "Accept": "application/json, text/javascript, */*; q=0.01",
  "Referer": "http://www.cvs.com/minuteclinic/clinic-locator/clinicdetails.jsp?storeId=2125",
  "Connection": "keep-alive"
  }

  url = 'https://services.cvs.com/minuteClinic/getStoreDetails?version=1.0&serviceName=getStoreDetails&appName=MCL_APP&apiSecret=4bcd4484-c9f5-4479-a5ac-9e8e2c8ad4b0&apiKey=c9c4a7d0-0a3c-4e88-ae30-ab24d2064e43&deviceID=device12345&deviceToken=12232434&deviceType=AND_MOBILE&lineOfBusiness=MINUTE_CLINIC&channelName=MOBILE&operationName=getStoreDetails&serviceCORS=FALSE'

  startTime = time.time()

  # Loop over all clinic IDs
  while len(clinicIDsTmp) > 0:

    #--------
    # Get 5 clinic IDs and build the API call

    clinicIDstring = ''
    for i in range(0,min(5,len(clinicIDsTmp))):
      clinicIDstring = clinicIDstring + '"%s",' % (clinicIDsTmp.pop(0))
    clinicIDstring = clinicIDstring[:-1]

    request_data = '{"request":{"destination":{"minuteClinicID":[%s]},"operation":["clinicInfo","waittime"],"services":["indicatorMinuteClinicService"]}}' % (clinicIDstring)

    print request_data
    print

    #--------
    # Parse the JSON response and take a timestamp

    try:
      request = urllib2.Request(url, data=request_data, headers=request_headers)
      contents = urllib2.urlopen(request).read()
      dictResult = json.loads(contents)
    except:
      print 'Error calling API/parsing response...'
      continue

    timeStamp = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')

    #--------
    # Build tuples containing the store and wait time results

    for loc in dictResult['response']['details']['locations']:
  
      mcID = loc['minuteClinicID']
      storeNum = loc['StoreNumber']
      address = loc['addressLine']
      city = loc['addressCityDescriptionText']
      zip = loc['addressZipCode']
      state = loc['addressState']
      lat = loc['geographicLatitudePoint']
      lon = loc['geographicLongitudePoint']
      #----
      mcHourDict = {}
      for d in loc['minuteClinicHours']['DayHours']:
        mcHourDict[d['Day']] = d['Hours']
      #----
      breakHourDict = {}
      for d in loc['minuteClinicNpBreakHours']['DayHours']:
        breakHourDict[d['Day']] = d['Hours']
      #----
      waitTime = loc['waittime']
  
      storeInfo = (mcID,storeNum,address,city,zip,state,lat,lon, 
        mcHourDict['MON'], mcHourDict['TUE'], mcHourDict['WED'], mcHourDict['THU'], 
        mcHourDict['FRI'], mcHourDict['SAT'], mcHourDict['SUN'], 
        breakHourDict['MON'], breakHourDict['TUE'], breakHourDict['WED'], breakHourDict['THU'], 
        breakHourDict['FRI'], breakHourDict['SAT'], breakHourDict['SUN'])
  
      # Only write the store info if we have not yet seen this store
      if storeInfo not in allStoreInfo:
        print storeInfo
        wr1.writerow(storeInfo)
        f1.flush()
        allStoreInfo.append(storeInfo)
    
      # Write the wait times
      print (mcID,timeStamp,waitTime)
      wr2.writerow((mcID,timeStamp,waitTime))
      f2.flush()
  
    time.sleep(1.0 + 3.0*random.random())
    
  # Ensure at least a 2 minute wait between sampling each clinic
  print '-------------------------------'
  sampleMinutes = 5
  print 'Waiting %f seconds...' % ( max(0.1,sampleMinutes*60 - (time.time()-startTime)) )
  time.sleep( max(0.1,sampleMinutes*60 - (time.time()-startTime)) )
  
  return allStoreInfo
  
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#-------------------------------
# Get all the IDs of all clinics to be crawled

clinicIDs = []
#--
f = open('MA_clinic_nums.txt','r')
for line in f:
  clinicIDs.append(line.strip())
f.close()
#--
f = open('GA_clinic_nums.txt','r')
for line in f:
  clinicIDs.append(line.strip())
f.close()
#--
f = open('TX_clinic_nums.txt','r')
for line in f:
  clinicIDs.append(line.strip())
f.close()
#--
f = open('AZ_clinic_nums.txt','r')
for line in f:
  clinicIDs.append(line.strip())
f.close()

#-------------------------------
# Write the headers of the two CSV files

storeHeaders = ('Clinic_ID','Store_Number','Store_Address','Store_City','Store_Zip','Store_State','Store_Lat','Store_Lon', 
        'Clinic_Hours_Mon', 'Clinic_Hours_Tue', 'Clinic_Hours_Wed', 'Clinic_Hours_Thu', 
        'Clinic_Hours_Fri', 'Clinic_Hours_Sat', 'Clinic_Hours_Sun', 
        'Break_Hours_Mon', 'Break_Hours_Tue', 'Break_Hours_Wed', 'Break_Hours_Thu', 
        'Break_Hours_Fri', 'Break_Hours_Sat', 'Break_Hours_Sun')

waitHeaders = ('Clinic_ID','Timestamp','Wait_Minutes')

f1 = open('storeInfo.csv','w')
f2 = open('waitTimes.csv','w')

wr1 = csv.writer(f1)
wr2 = csv.writer(f2)

wr1.writerow(storeHeaders)
wr2.writerow(waitHeaders)

#-------------------------------
# Loop forever...

allStoreInfo = []

#request_data = '{"request":{"destination":{"minuteClinicID":["445","1724","466","1755","476"]},"operation":["clinicInfo","waittime"],"services":["indicatorMinuteClinicService"]}}' 

while True:
  
  # Get a list of clinic IDs to pop from
  clinicIDsTmp = clinicIDs[:]
  clinicIDsTmp.sort(key=lambda x: random.random())
  
  # Calling function to manage exceptions, but have big mess of globals
  try:
    allStoreInfo = processAllClinicIDs(clinicIDsTmp,allStoreInfo)
  except:
    print 'Error processing clinic IDs...'



  