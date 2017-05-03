'''
This script will get the IDs of all MinuteClinics in a given state,
then place these IDs in a text file
'''

import urllib2
import json
import re
import time

request_headers = {
"Accept-Encoding": "gzip, deflate, br", 
"Accept-Language": "en-US,en;q=0.8",
"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Connection": "keep-alive"
}

#url = 'http://www.cvs.com/minuteclinic/clinics/Massachusetts'
#url = 'http://www.cvs.com/minuteclinic/clinics/Georgia'
#url = 'http://www.cvs.com/minuteclinic/clinics/Texas'
url = 'http://www.cvs.com/minuteclinic/clinics/Arizona'

#-----------------------

request = urllib2.Request(url, headers=request_headers)
contents = urllib2.urlopen(request).read()

clinicURLs = re.findall('href="(/minuteclinic/clinics/[^;]+);',contents)
clinicURLs = ['http://www.cvs.com'+x for x in clinicURLs]

print len(clinicURLs)

#------------------------------------------

allClinicNums = []

for url2 in clinicURLs:

  request = urllib2.Request(url2, headers=request_headers)
  contents = urllib2.urlopen(request).read()

  tmp = re.findall('getWaitTimeBrowseByState([^;]+);',contents)
  clinicNums = []
  for t in tmp:
    clinicNums = clinicNums + re.findall('([0-9]+)',t)

  allClinicNums = allClinicNums + clinicNums
  print clinicNums
  
  time.sleep(1.3)

print allClinicNums
print len(allClinicNums)

f = open('AZ_clinic_nums.txt','w')
for cn in allClinicNums:
  f.write( cn + '\n' )
f.close()