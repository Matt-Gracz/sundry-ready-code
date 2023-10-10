#Code for actual ETL
import datetime
import json
import pandas as pd
from time import sleep, time
import requests
import ready_encryption
from ready_constants import *

# Function to generate dates between a start date and an end date
def daterange(start_date_str, end_date_str):
    start_date = datetime.datetime.strptime(start_date_str, default_date_format).date()
    end_date = datetime.datetime.strptime(end_date_str, default_date_format).date()
    
    for n in range(int((end_date - start_date).days) + 1):
        yield (start_date + datetime.timedelta(n)).strftime(default_date_format)

def test_daterange():
    # Generate the dates
    generated_dates = [single_date for single_date in daterange(start_date, end_date)]

    # Show first 5 and last 5 dates to verify
    print(f'first dates: {generated_dates[:5]}\nlast dates: {generated_dates[-5:]}')

def parse_json_response(json_response):

    # Initialize an empty list to store the parsed request objects
    parsed_requests = []
    # Loop through each ReADY request object in the JSON response list
    for request in json_response:
        # Remove stuff we don't care about
        fields_to_strip = ['values','additionalFieldsValues','aimStatusHistory.primaryKey', 'workflowStates', 'respondents', 'workflowResponses']
        for field in fields_to_strip:
            request.pop(field, None)
        
        # Append the stripped-yet-raw request object to the list
        parsed_requests.append(request)
        
    # Convert the list of ReADY request objects to a DataFrame
    parsed_requests_df = pd.DataFrame(parsed_requests)
    
    return parsed_requests_df

# Define a function to make the API call to 
# get all the ReADY requests for a particular date
def make_api_call(date):
    url = f"{endpoint_url}startDate={date}&endDate={date}"
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
            response = requests.get(url, timeout=HTTP_TIMEOUT_TOLERANCE, auth=(api_uname, ready_encryption.simple_decrypt(api_pw)))
            
            # Capture the elapsed time
            elapsed_time = time() - start_time
            
            # Check for successful status code
            if response.status_code == HTTP_SUCCESS_CODE:
                # Parse the JSON response and store it
                parsed_requests = parse_json_response(response.json())
                #force 2D record orientation just in case we get weirdness
                #from the pre-dataframe'd parsed_requests
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
                sleep(INTER_RETRY_WAIT)
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
            sleep(INTER_RETRY_WAIT) #Wait a beat before retrying

    return this_call_metrics, this_call_data

# Set DEBUG to true so accidental calls to this func don't kick off
# the entire ETL process, which takes a few minutes.
def extract_data_from_date_range(api_start_date=start_date, api_end_date=end_date, DEBUG=True):

    # List of performance metrics
    performance_metrics = []

    # List of request objects
    all_parsed_requests = []

    # Generate dates to call the API on
    # Set DEBUG to true so accidental calls to this func don't kick off
    date_ranges = daterange('2019-07-01' if DEBUG else api_start_date, '2019-07-10' if DEBUG else api_end_date)

    # Loop through each date and make the API call
    for date in date_ranges:
        this_call_metrics, this_call_data = make_api_call(date)
        performance_metrics.append(this_call_metrics)
        all_parsed_requests.extend(this_call_data)
        
    # Convert performance metrics and all_parsed_requests to DataFrames
    performance_metrics_df = pd.DataFrame(performance_metrics)
    all_parsed_requests_df = pd.DataFrame(all_parsed_requests)

    if DEBUG:
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

def go_request_by_request(api_start_request=start_request_num, api_end_request=end_request_num):
    def make_request(request_num):
        url = f"{endpoint_url}request={request_num}"
        response = requests.get(url, timeout=HTTP_TIMEOUT_TOLERANCE, auth=(api_uname, ready_encryption.simple_decrypt(api_pw)))
        request = parse_json_response(response.json())
        return request

    start_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    curr_loop_date = datetime.datetime.strptime(start_date, default_date_format)
    if DEBUG:
        print(f'Running on : {today}')
    ready_requests = []
    for request_num in range(api_start_request, api_end_request):
        try:
            this_request = make_request(request_num)
            ready_requests.append(this_request)
            if DEBUG:
                print(f'Request {request_num} created on {this_request["dateCreated"][0]}')
            this_date = datetime.datetime.strptime(this_request["dateCreated"][0], '%Y-%m-%dT%H:%M:%S.%fZ')
            if this_date > curr_loop_date:
                curr_loop_date = this_date
                print(f'Current date of loop: {curr_loop_date}')
        except Exception as e:
            print(f'Error handling request {request_num}. Error text: {str(e)}')
            print(f'Proceeding with next reqeust')

    end_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    elapsed_time = end_time - start_time
    print(f'Elapsed time: {str(elapsed_time)}')
    return ready_requests