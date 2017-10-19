from urllib.request import urlopen
import re
import sys
import operator
from datetime import datetime

# Config options
REMOTE_URL = 'https://s3.amazonaws.com/tcmg412-fall2016/http_access_log'
LOCAL_FILE = 'http_access_log.bak'
LOG_PATH = 'logs/'

# Initialize some variables
i = 0
requests_by_month = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}
requests_by_week = {}
requests_by_day = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
files = {}
counts = {'requests': 0, '300': 0, '400': 0}
errors = []

# Fetch the file from the remote server and save it to disk
print("\n\nDownloading log file from URI... ")
response = urlopen(REMOTE_URL)
with open(LOCAL_FILE, "wb") as local:
	local.write(response.read())
print("File retrieved and saved to disk ({}) \n\n".format(LOCAL_FILE))

# Prepare the regex...
regex = re.compile(".*\[(.*) \-[0-9]{4}\] \"([A-Z]+) (.+?)( HTTP.*\"|\") ([2-5]0[0-9]) (.*)")

# Loop through each line of the file on disk
for line in open(LOCAL_FILE, 'r'):

	# A simple progress meter
	i += 1
	if i % 1000 == 0:
		print(".", end= '')
	if i > 200000:
		break
	
	# Use Regex to split the line into parts
	parts = regex.split(line)
	#print(parts)

	# Sanity check the line -- capture the error and move on
	if not parts or len(parts) < 8:
		#print("Error parsing line! Log entry added to errors[] list...")
		print('*', end='')
		errors.append(line)
		continue
	else:
		counts['requests'] += 1

	# Parse the date from the second array element
	entry_date = datetime.strptime(parts[1], "%d/%b/%Y:%H:%M:%S")
	
	# 
	requests_by_day[entry_date.weekday()] += 1
	requests_by_month[entry_date.month] += 1
	
	# these keys don't exist so check first!
	if entry_date.strftime('%W') in requests_by_week:
		requests_by_week[entry_date.strftime("%W")] += 1
	else:
		requests_by_week[entry_date.strftime("%W")] = 1
		
	# Tracking files by file name
	file_name = parts[3]
	if file_name in files:
		files[file_name] += 1
	else:
		files[file_name] = 1	
		
		
	# detect the HTPP status code
	if parts[5][0] == '4':
		counts['400'] += 1
		
	if parts[5][0] == '3':
		counts['300'] += 1

	#getting the min and max of files
	
	sorted_counts = sorted(files.items(), key=operator.itemgetter(1))

print("\n")
print ('Total Requests:', counts['requests'])
print (' ')
print ('400 status:', counts['300'])
print (' ')
print ('300 status:', counts['400'])
print (' ')
print ('requests by day with 0 being sunday and 6 being saturday')
print (requests_by_day)
print (' ')
print ('requests by week starting in October 1994')
print (requests_by_week)
print (' ')
print ('requests by month:')
print (requests_by_month)
print (' ')
print ('Most-requested file:', sorted_counts.pop())

