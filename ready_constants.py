import datetime
import rec
import socket as sock
import subprocess
import sqlite3
### Constants for use in ReADY API Code

DEBUG = True
api_uname, api_pw = 'readyProdReportingAgent', rec.axfdfsavca()

# Comment out static_rest_params if you only want to filter
# API result sets by dates
static_rest_params = 'template=Customer%20Request&'
static_rest_params = ''
endpoint_url = f'https://uwiscprod.assetworks.cloud/ready/api/reporting/request?{static_rest_params}'

start_request_num = 2562 #The 1st request submitted after go live
end_request_num = 140844 #as of 9/25/23 in readytest, dummy value for now

# Control variable to help weed out anything we don't want.
# The dot notation goes as deep as you want, also, so you
# can preserve or prune variables at the same level.
# fields_to_strip = ['values','additionalFieldsValues','aimStatusHistory.primaryKey', 'workflowStates', 'respondents', 'workflowResponses']
fields_to_strip = []

### This is basically our SELECT statement
## School-agnostic Data
fields_to_include = [\
'template',\
'title',\
'closed',\
'dateCreated',
'requestor',
'requestId']
## UW - Madison Specific Data:
values_to_include = [\
'propertyType',\
'woDescr',\
'buildingFloorRoom|Property|bldg',\
'buildingFloorRoom|Floor|flrId',\
'buildingFloorRoom|Location|locId',\
'locDetails',\
'processTitle',\
'costCenter',\
'contactName',\
'contactPhone',\
'contactEmail'\
]
additional_fields_to_include = [\
'buildingFloorRoom|Property|descr'\
]

# Controls for generating date range of requests to query
default_date_format = '%Y-%m-%d'
default_long_date_format = '%Y%m%d%H%M%S'
orig_start_date = '2019-07-01' #start of the first Fiscal Year in which we used ReADY to captures work requests
debug_end_date = '2019-07-10' # a useful date for testing data extraction
today = datetime.date.today().strftime(default_date_format)
end_date = '2023-06-30' # Default control value for queryable ReADY Reqeust date range.

# Data output files, first file is request data, second file is for
# metadata about the API calls, e.g., performance data of API calls etc...
request_data_csv_file_path = 'request_data/reqeust_data-{}.csv'
performance_data_csv_file_path = 'request_data/performance_data-{}.csv'

# Integer Codes
HTTP_SUCCESS_CODE = 200
HTTP_TIMEOUT_TOLERANCE = 6000 #UOM = seconds
INTER_RETRY_WAIT = 2 #UOM = seconds

### Tshark globals
# Temp tshark performance metrics dump file
ready_tshark_tmp_file = 'ready_tshark_tmp.pcap'
ready_host_ip_addr = sock.gethostbyname('uwiscprod.assetworks.cloud')
# Getting the wifi index can cost about .25 secs which can add up so we'll pregame it here
# Basically we get a dump of all interfaces, one per line, in a text file, so we find the
# line with the wifi index and the first char of that line is the index itself
wifi_interface_index = \
[line for line in subprocess.check_output("tshark -D", shell=True, text=True, stderr=subprocess.STDOUT).split('\n') if 'Wi-Fi' in line][0][0]