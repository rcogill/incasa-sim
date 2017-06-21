'''
This script continually fetches a travel time matrix from a collection of 
origin and destination lat-lon pairs.
Timestamped estimates of traveltime between each lat-lon pair are written to a CSV file
Requires you to supply your own Google Maps API key
'''

import urllib.request, urllib.error, urllib.parse
import time
import csv
import json

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def getTravelTime(oLat,oLon,dLat,dLon):

  apiKey = 'AIzaSyAUeHQtEglYtNTmmWsda107Cv2mvypn7Pw' # Include your API key here...

  url = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=%f,%f&destinations=%f,%f&key=%s' % (oLat,oLon,dLat,dLon,apiKey)

  request = urllib.request.Request(url)
  source = urllib.request.urlopen(request).read()

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
  (29.73959, -95.47121),
  (29.73376, -95.39147),
  (29.70538, -95.44058),
  (29.91015, -95.62942),
  (29.77876, -95.6188),
  (29.5728, -95.10988),
  (29.97871, -95.51367)
  ]

dest = origin
#---

#dest = [
 # (29.760427, -95.369803),
 # (29.705611, -95.181427),
 # (29.924849, -95.560455),
  #(29.530114, -95.131989),
  #(29.972446, -95.318756),
  #(29.642372, -95.049591),
  #(29.730657, -95.796661),
  #(30.088962, -95.515137),
  #(29.848647, -95.454712),
  #(29.770003, -94.901276)
  #] #commented out because the only nodes we're using are the origin nodes for now

#------------------------


def write_file(origin,dest):
  """Writes the drive times into a CSV file to be parsed by a distance matrix function."""
  file_name = 'traveltimes.csv'
  f = open('traveltimes.csv','w') #changed from 'wb' to 'w'
  wr = csv.writer(f)

  wr.writerow( ('Timestamp','Origin_Lat','Origin_Lon','Dest_Lat','Dest_Lon','Travel_Time_Str','Travel_Time_Sec','Distance_Str','Distance_M') )

  while True:

    start = time.time()

    for node_o in origin:
      for node_d in dest:

        try:
          timeStamp = int(time.time())
          (timeStr,timeSec,distStr,distM) = getTravelTime(node_o.lat,node_o.lon,node_d.lat,node_d.lon)
          print((timeStamp,node_o.lat,node_o.lon,node_d.lat,node_d.lon,timeStr,timeSec,distStr,distM))
          wr.writerow( (timeStamp,node_o.lat,node_o.lon,node_d.lat,node_d.lon,timeStr,timeSec,distStr,distM) )
        except:
          print ('No response received...') #added parentheses
          continue
      
        time.sleep(1)
      
    while time.time() - start < 3600:
      time.sleep(2)
      print(('Waiting: %f') % ((time.time() - start)/60)) #added parentheses'''
      break
    break
  return file_name
