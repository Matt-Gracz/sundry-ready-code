from ready_imports import *

def parse_date(date_input):
    if isinstance(date_input, int):
        # Process integer input
        date_str = str(date_input).zfill(6)
        month = int(date_str[:2]) if len(date_str) == 6 else int(date_str[0])
        day = int(date_str[2:4]) if len(date_str) == 6 else int(date_str[1:3])
        year = 2000 + int(date_str[4:]) if len(date_str) == 6 else int(date_str[3:])
        date_obj = datetime.datetime(year, month, day)
    elif isinstance(date_input, str):
        # Process string input
        if '-' in date_input:
            format_str = '%Y-%m-%d' if date_input[4] == '-' else '%m-%d-%Y'
            date_obj = datetime.datetime.strptime(date_input, format_str)
        else:
            raise ValueError("String input must be in 'MM-DD-YYYY' or 'YYYY-MM-DD' format.")
    else:
        raise ValueError("Input must be either an integer or a string representing a date.")
    
    # Return formatted date
    return date_obj.strftime('%Y-%m-%d')

# Function to generate dates between a start date and an end date
# yields a generator object of date ranges
def daterange(start_date_in, end_date_in):

    start_date = datetime.datetime.strptime(parse_date(start_date_in), default_date_format).date()
    end_date = datetime.datetime.strptime(parse_date(end_date_in), default_date_format).date()
    
    for n in range(int((end_date - start_date).days) + 1):
        yield (start_date + datetime.timedelta(n)).strftime(default_date_format)

    #for n in range(int((end_date - start_date).days) + 1, 0):
    #    yield (end_date - datetime.timedelta(n)).strftime(default_date_format)

# Prints a test, no return statement
def test_daterange():
    # Generate the dates
    generated_dates = [single_date for single_date in daterange(start_date, end_date)]

    # Show first 5 and last 5 dates to verify
    print(f'first dates: {generated_dates[:5]}\nlast dates: {generated_dates[-5:]}')

# Returns a pandas.core.frame.DataFrame that contains 
# one record per request in the json_response
def parse_json_response(json_response):

    # Initialize an empty list to store the parsed request objects
    parsed_requests = []
    # Loop through each ReADY request object in the JSON response list
    # and grab all the data we care about.
    for request in json_response:
        parsed_request = {}
        for field in fields_to_strip:
            request.pop(field)
        for field in fields_to_include:
            parsed_request[field] = request.get(field)
        for value in values_to_include:
            parsed_request[value] = request['values'].get(value)
        for additional_field in additional_fields_to_include:
            parsed_request[additional_field] = request['additionalFieldsValues'].get(additional_field)
        
        # Append the parsed request object to the list
        parsed_requests.append(parsed_request)
        
    # Convert the list of ReADY request objects to a DataFrame
    parsed_requests_df = pd.DataFrame(parsed_requests)
    
    return parsed_requests_df

def create_metrics(api_date_request, ready_request_date_one, ready_request_date_two, elapsed_time, outcome, json_size, num_retries):
    return {
            'api_date_request' : api_date_request,
            'ready_request_date_one': ready_request_date_one,
            'ready_request_date_two': ready_request_date_two,
            'elapsed_time': elapsed_time,
            'outcome': outcome,
            'json_size': json_size,
            'num_retries': num_retries }

# Define a function to make the API call to 
# get all the ReADY requests for a particular date range
def make_api_call(date_one, date_two):
    url = f"{endpoint_url}startDate={date_one}&endDate={date_two}"
    print(url)
    # Initialize variables for retry mechanism
    max_retries = 3
    retries = 0

    this_call_metrics = {}
    this_call_data = {}
    
    while retries <= max_retries:
        # Capture the start time
        start_time = time.time()
        
        try:
            # Make the API call
            response = requests.get(url, timeout=HTTP_TIMEOUT_TOLERANCE, auth=(api_uname, rec.dlfdadreaqf(api_pw)))
            
            # Capture the elapsed time
            elapsed_time = time.time() - start_time

            # Check for successful status code
            if response.status_code == HTTP_SUCCESS_CODE:
                # Parse the JSON response and store it
                parsed_requests = parse_json_response(response.json())
                #force 2D record orientation just in case we get weirdness
                #from the pre-dataframe'd parsed_requests
                this_call_data = parsed_requests.to_dict(orient='records')

                # Record performance metrics
                this_call_metrics = create_metrics(today, date_one, date_two, elapsed_time,\
                                                    'Success', len(response.content), retries)
                # Exit the loop
                break
            else:
                # Record performance metrics for failed attempt
                this_call_metrics = create_metrics(today, date_one, date_two, elapsed_time,\
                                                    'Failure', 0, retries)
                retries += 1
                time.sleep(INTER_RETRY_WAIT)
        except requests.exceptions.RequestException as e:
            # Capture the elapsed time
            elapsed_time = time.time() - start_time
            print_and_log(f"RequestException occured for date range {date_one} - {date_two} :: {str(e)}")
        except Exception as e:
            elapsed_time = time.time() - start_time
            print_and_log(f"Error occured for date range {date_one} - {date_two} :: {str(e)}")
            print_and_log(traceback.format_exc())

    
            # Record performance metrics for failed attempt
            this_call_metrics = create_metrics(today, date_one, date_two, elapsed_time,\
                                                'Local Timeout', 0, retries)
            retries += 1
            time.sleep(INTER_RETRY_WAIT) #Wait a beat before retrying
    log(f'{url} took {elapsed_time} seconds')
    return this_call_metrics, this_call_data

# Main ETL Process -- this will extract data from the ReADY API for a 
# given time band, one day at a time.  It will return the request data
# and performance data/metadata in memory, as well as write the data
# and metadata to timestamped files on disk.
def extract_data_from_date_range(api_start_date=orig_start_date, api_end_date=debug_end_date):
    t0 = time.time()

    # List of performance metrics
    performance_metrics = []

    # List of request objects
    all_parsed_requests = []

    # Generate dates to call the API on
    date_ranges = list(daterange(api_start_date, api_end_date))

    # temp code: load in the dates sorted by how long it took to query them in previous runs
    date_ranges = pd.read_csv('sorted_ready_request_dates.csv', header=None)[0].tolist()

    #temp code: reverse it to go backwards through requests
    date_ranges.reverse()

    # Loop through each date and make the API call
    for date in date_ranges:
        this_call_metrics, this_call_data = make_api_call(date, date)
        performance_metrics.append(this_call_metrics)
        all_parsed_requests.extend(this_call_data)
        
    # Convert performance metrics and the parsed requests to DataFrames
    performance_metrics_df = pd.DataFrame(performance_metrics)
    all_parsed_requests_df = pd.DataFrame(all_parsed_requests)

    if DEBUG:
        # Show some performance metrics and a few parsed requests
        print_and_log(performance_metrics_df.head())
        print_and_log(all_parsed_requests_df.head())


    #Persistence
    now = datetime.datetime.now().strftime(default_long_date_format)

    # Save Performance Metrics to disk
    performance_metrics_df.to_csv(performance_data_csv_file_path.format(now), index=False)

    # Save parsed ReADY requests to disk in tabular form
    all_parsed_requests_df.to_csv(request_data_csv_file_path.format(now), index=False)

    print_and_log(f'Total run time: {(time.time() - t0) / 60 } minutes')

    return performance_metrics, all_parsed_requests

# README / instructions for use:


#### Script execution and function loading options
from sys import argv
if len(argv) > 0 and argv[-1].lower() == "etl":
    print_and_log(f'range: {orig_start_date} - {end_date}')
    extract_data_from_date_range(orig_start_date, end_date)
    #x = make_api_call('2019-10-19', '2019-10-31')
else:
    print('Functions loaded into memory')