import datetime
import rec

### Constants for use in ReADY API Code

DEBUG = True
# Server/Client Config
api_uname, api_pw = 'readyProdReportingAgent', rec.axfdfsavca()
endpoint_url = f'https://uwiscprod.assetworks.cloud/ready/api/reporting/request?'
start_request_num = 2562 #The 1st request submitted after go live
end_request_num = 140844 #as of 9/25/23 in readytest, dummy value for now

# Controls for generating date range of requests to query
default_date_format = '%Y-%m-%d'
default_long_date_format = '%Y%m%d%H%M%S'
orig_start_date = '2019-07-01' #start of the first FY in which we used ReADY to captures work requests
debug_end_date = '2019-07-10' # a useful date for testing data extraction
today = datetime.date.today().strftime(default_date_format)
end_date = today # Default control value for queryable ReADY Reqeust date range.

# Data output files, first file is request data, second file is for 
# metadata about the requests, e.g., performance data of API calls etc...
request_data_csv_file_path = 'reqeust_data-{}.csv'
performance_data_csv_file_path = 'performance_data-{}.csv'

# Integer Codes
HTTP_SUCCESS_CODE = 200
HTTP_TIMEOUT_TOLERANCE = 60 #UOM = seconds
INTER_RETRY_WAIT = 2 #UMO = seconds