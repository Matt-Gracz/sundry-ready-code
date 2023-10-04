import requests
import json
import csv
import time

date_range_file_name = 'random_date_ranges.csv'
api_call_data = 'api_call_data.csv'
api_uname, api_pw = 'readyProdReportingAgent','GCtQkq6lZkdoOsm7wb6l' #replace with values at runtime
request_timeout_tolerance = 20

### 2023-09-15 mgracz: I used this code to figure out the best way to write the actual ETL code.
### so consider this research, essentially, on how many days' worth of ReADY requests I could get
### with 1 REST request.  The answer is : 1 ReADY request per REST request.

# def load_random_date_ranges():
#     # Load in list of random date ranges, 30 each of 1, 2, and 3-day ranges for a total of 90 random date ranges

#     # Initialize an empty dictionary to store the date ranges read from the CSV file
#     random_date_ranges = {
#         '1_days': [],
#         '2_days': [],
#         '3_days': []
#     }

#     # Simulate reading the CSV file
#     csv_file_path = date_range_file_name  # Replace with the path to your actual CSV file

#     with open(csv_file_path, 'r', newline='') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             range_size = row['range_size']
#             start_date = row['start_date']
#             end_date = row['end_date']
            
#             # Append the date range to the appropriate list in the dictionary
#             random_date_ranges[range_size].append((start_date, end_date))

#     # Show first 5 samples of each to verify
#     print(random_date_ranges['1_days'][:5], random_date_ranges['2_days'][:5], random_date_ranges['3_days'][:5])
#     return random_date_ranges

# def run_ready_api_performance_sampling():

#     random_date_ranges = load_random_date_ranges()

#     flattened_date_ranges = []
#     for range_list in random_date_ranges.values():
#         flattened_date_ranges.extend(range_list)

#     # Initialize CSV file to store results
#     with open(api_call_data, 'w', newline='') as csvfile:
#         fieldnames = ['start_date', 'end_date', 'time_taken', 'outcome', 'json_size']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()

#         # Loop over date ranges
#         for start_date, end_date in flattened_date_ranges:  
#             # Make API call
#             url = f"https://uwisctest.assetworks.cloud/ready/api/reporting/request?startDate={start_date}&endDate={end_date}"  # Replace with actual API URL
            
#             start_time = time.time()
#             outcome = 'Success'  # Initialize as 'Success' and update if an exception occurs
#             try:
#                 print(f'Trying {url}')
#                 response = requests.get(url, auth=(api_uname, api_pw), timeout=request_timeout_tolerance)
#                 response.raise_for_status()  # Raise an HTTPError for bad responses

#                 # Record data if the status code indicates success
#                 elapsed_time = time.time() - start_time
#                 json_size = len(json.dumps(response.json()))
#             except requests.Timeout:
#                 elapsed_time = time.time() - start_time
#                 json_size = None
#                 outcome = 'Local Timeout'
#             except requests.RequestException as e:
#                 elapsed_time = time.time() - start_time
#                 json_size = None
#                 outcome = 'Response Failure'

#             # Write data to CSV
#             data_entry_dict = {'start_date': start_date, 'end_date': end_date, 'time_taken': elapsed_time, 'outcome': outcome, 'json_size': json_size}
#             print(data_entry_dict)
#             writer.writerow(data_entry_dict)


#Code for actual ETL
import datetime
import json
import pandas as pd
from time import sleep, time
import requests

start_date = '2019-07-01' #start of the first FY in which we used ReADY to captures work requests
today = datetime.date.today().strftime("%Y-%m-%d")

request_data_csv_file_path = 'reqeust_data-{}.csv'
performance_data_csv_file_path = 'performance_data-{}.csv'

#control for queryable date range.
end_date = today

#replace with values at runtime
api_uname, api_pw = 'readyProdReportingAgent','GCtQkq6lZkdoOsm7wb6l' 


# Function to generate dates between a start date and an end date
def daterange(start_date_str, end_date_str):
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
    
    for n in range(int((end_date - start_date).days) + 1):
        yield (start_date + datetime.timedelta(n)).strftime('%Y-%m-%d')

def test_daterange():
    # Generate the dates
    generated_dates = [single_date for single_date in daterange(start_date, end_date)]

    # Show first 5 and last 5 dates to verify
    print(f'first dates: {generated_dates[:5]}\nlast dates: {generated_dates[-5:]}')

def parse_json_response(json_response):

    # Initialize an empty list to store the parsed request objects
    parsed_requests = []
    # Loop through each request object in the JSON response list
    for request in json_response:
        # Remove stuff we don't care about
        fields_to_strip = ['values','additionalFieldsValues','aimStatusHistory.primaryKey', 'workflowStates', 'respondents', 'workflowResponses']
        for field in fields_to_strip:
            request.pop(field, None)
        
        # Append the modified request object to the list
        parsed_requests.append(request)
        
    # Convert the list of parsed request objects to a DataFrame
    parsed_requests_df = pd.DataFrame(parsed_requests)
    
    return parsed_requests_df

#ask bill about how to handle workflow responses


# Define a function to make the API call
def make_api_call(date):
    # Insert your API endpoint and parameters here
    # For demonstration purposes, using a placeholder URL
    url = f"https://uwisctest.assetworks.cloud/ready/api/reporting/request?startDate={date}&endDate={date}"
    print(url)
    # Initialize variables for retry mechanism
    max_retries = 3
    retries = 0

    this_call_metrics = {}
    this_call_data = {}
    
    while retries <= max_retries:
        # Capture the start time
        start_time = time()
        
        try:
            # Make the API call
            response = requests.get(url, timeout=10, auth=(api_uname, api_pw))  # 10-second timeout
            
            # Capture the elapsed time
            elapsed_time = time() - start_time
            
            # Check for successful status code
            if response.status_code == 200:
                # Parse the JSON response and store it
                parsed_requests = parse_json_response(response.json())
                this_call_data = parsed_requests.to_dict(orient='records')

                # Record performance metrics
                this_call_metrics = {
                    'api_date_request' : today,
                    'ready_request_date': date,
                    'elapsed_time': elapsed_time,
                    'outcome': 'Success',
                    'json_size': len(response.content),
                    'num_retries': retries
                }

                # Exit the loop
                break
            else:
                # Record performance metrics for failed attempt
                this_call_metrics = {
                    'api_date_request' : today,
                    'ready_request_date': date,
                    'elapsed_time': elapsed_time,
                    'outcome': 'Failure',
                    'json_size': 0,
                    'num_retries': retries
                }
                retries += 1
                sleep(2)  # Sleep for 2 seconds before retrying
        except requests.exceptions.RequestException as e:
            # Capture the elapsed time
            elapsed_time = time() - start_time
            
            # Record performance metrics for failed attempt
            this_call_metrics = {
                'api_date_request' : today,
                'ready_request_date': date,
                'elapsed_time': elapsed_time,
                'outcome': 'Local Timeout',
                'json_size': 0,
                'num_retries': retries
            }
            retries += 1
            sleep(2)  # Sleep for 2 seconds before retrying

    return this_call_metrics, this_call_data

# Set DEBUG to true so accidental calls to this don't kick off
# the entire ETL process, which takes a few minutes.
def extract_data_from_date_range(api_start_date=start_date, api_end_date=end_date, DEBUG=True):

    # List of performance metrics
    performance_metrics = []

    # List of request objects
    all_parsed_requests = []

    # Generate dates to call the API on
    date_ranges = daterange('2019-07-01' if DEBUG else api_start_date, '2019-07-10' if DEBUG else api_end_date)

    # Loop through each date and make the API call
    for date in date_ranges:
        this_call_metrics, this_call_data = make_api_call(date)
        performance_metrics.append(this_call_metrics)
        all_parsed_requests.extend(this_call_data)
        
    # Convert performance metrics and all_parsed_requests to DataFrames
    performance_metrics_df = pd.DataFrame(performance_metrics)
    all_parsed_requests_df = pd.DataFrame(all_parsed_requests)

    if(DEBUG):
        # Show some performance metrics and a few parsed requests
        print(performance_metrics_df.head(), all_parsed_requests_df.head())


    #Persistence
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    # For performance_metrics_df
    performance_metrics_df.to_csv(performance_data_csv_file_path.format(now), index=False)

    # For all_parsed_requests_df
    all_parsed_requests_df.to_csv(request_data_csv_file_path.format(now), index=False)

    return performance_metrics, all_parsed_requests

    #9/15/23 IDEA run thi over and over and save the perfor metrics at least,
    #maybe run it 100 times overnight, 100 times during the day, 100 times on a weekend
    #for each day, take the max payload and count that JSON's # of requets and store a
    #date --> int map that when we run future requests, we can use to check the payload
    #for retries.  I can't belive I'm doing that, if I do.
    #9/25/23 THAT doesn't even work b/c old requests' sizes don't necessarily grow whenever
    #they get updated GRRR.

global x
x = 1
def go_request_by_request():
    def make_request(request_num):
        url = f"https://uwisctest.assetworks.cloud/ready/api/reporting/request?request={request_num}"
        response = requests.get(url, timeout=10, auth=(api_uname, api_pw))  # 10-second timeout
        request = parse_json_response(response.json())
        return request

    start_request_num = 2562 #The 1st request submitted after go live
    end_request_num = 140844 #as of 9/25/23 in readytest
    #end_request_num = 2565

    start_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    curr_date = datetime.datetime.strptime('2019-07-01', '%Y-%m-%d')
    print(curr_date)
    ready_requests = []
    for request_num in range(start_request_num, end_request_num):
        this_request = make_request(request_num)
        ready_requests.append(this_request)
        x = this_request["dateCreated"]
        print(f'Request {request_num} created on {this_request["dateCreated"][0]}')
        this_date = datetime.datetime.strptime(this_request["dateCreated"][0], '%Y-%m-%dT%H:%M:%S.%fZ')
        if this_date > curr_date:
            curr_Date = this_date
            print(curr_Date)


    end_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    elapsed_time = end_time - start_time
    print(f'Elapsed time: {str(elapsed_time)}')

    return ready_requests