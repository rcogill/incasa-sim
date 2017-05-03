'''
This script continually fetches a travel time matrix from a collection of 
origin and destination lat-lon pairs.
Timestamped estimates of traveltime between each lat-lon pair are written to a CSV file
Requires you to supply your own Google Maps API key
'''

import urllib2
import time
import csv
import json

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def getTravelTime(oLat,oLon,dLat,dLon):

  apiKey = 'XXXX' # Include your API key here...

  url = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=%f,%f&destinations=%f,%f&key=%s' % (oLat,oLon,dLat,dLon,apiKey)

  request = urllib2.Request(url)
  source = urllib2.urlopen(request).read()

  responseDict = json.loads(source)

  travelTimeText = responseDict['rows'][0]['elements'][0]['duration']['text']
  travelTimeSec = responseDict['rows'][0]['elements'][0]['duration']['value']
  distanceText = responseDict['rows'][0]['elements'][0]['distance']['text']
  distanceM = responseDict['rows'][0]['elements'][0]['distance']['value']

  return (travelTimeText,travelTimeSec,distanceText,distanceM)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#------------------------
# List of origins and destinations for computing travel time matrix

origin = [
  (29.681752, -95.234985),
  (29.996236, -95.501404),
  (29.996236, -95.501404),
  (29.503823, -95.088043),
  (29.687717, -95.688171),
  (29.992668, -95.162201),
  (29.762850, -94.935608),
  (29.910566, -95.619507),
  (29.902233, -95.333862),
  (29.814099, -95.096283)
  ]
  
#---

dest = [
  (29.760427, -95.369803),
  (29.705611, -95.181427),
  (29.924849, -95.560455),
  (29.530114, -95.131989),
  (29.972446, -95.318756),
  (29.642372, -95.049591),
  (29.730657, -95.796661),
  (30.088962, -95.515137),
  (29.848647, -95.454712),
  (29.770003, -94.901276)
  ]

#------------------------

f = open('houston_traveltimes.csv','wb')
wr = csv.writer(f)

wr.writerow( ('Timestamp','Origin_Lat','Origin_Lon','Dest_Lat','Dest_Lon','Travel_Time_Str','Travel_Time_Sec','Distance_Str','Distance_M') )

while True:

  start = time.time()

  for (o_Lat,o_Lon) in origin:
    for (d_Lat,d_Lon) in dest:

      try:
        timeStamp = int(time.time())
        (timeStr,timeSec,distStr,distM) = getTravelTime(o_Lat,o_Lon,d_Lat,d_Lon)
        print (timeStamp,o_Lat,o_Lon,d_Lat,d_Lon,timeStr,timeSec,distStr,distM)
        wr.writerow( (timeStamp,o_Lat,o_Lon,d_Lat,d_Lon,timeStr,timeSec,distStr,distM) )
      except:
        print 'No response received...'
        continue
      
      time.sleep(1)
      
  while time.time() - start < 3600:
    time.sleep(2)    
    print 'Waiting: %f' % ((time.time() - start)/60)
