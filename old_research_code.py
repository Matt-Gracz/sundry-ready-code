## 2023-09-15 mgracz: I used this code to figure out the best way to write the actual ETL code.
## so consider this research, essentially, on how many days' worth of ReADY requests I could get
## with 1 REST request.  The answer is : 1 day's worth of ReADY requests per REST request.
import requests
import json
import csv
import time
import ready_encryption 

date_range_file_name = 'random_date_ranges.csv'
api_call_data = 'api_call_data.csv'
api_uname, api_pw = 'readyProdReportingAgent', ready_encryption.l()
request_timeout_tolerance = 20
def load_random_date_ranges():
    # Load in list of random date ranges, 30 each of 1, 2, and 3-day ranges for a total of 90 random date ranges

    # Initialize an empty dictionary to store the date ranges read from the CSV file
    random_date_ranges = {
        '1_days': [],
        '2_days': [],
        '3_days': []
    }

    # Simulate reading the CSV file
    csv_file_path = date_range_file_name  # Replace with the path to your actual CSV file

    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            range_size = row['range_size']
            start_date = row['start_date']
            end_date = row['end_date']
            
            # Append the date range to the appropriate list in the dictionary
            random_date_ranges[range_size].append((start_date, end_date))

    # Show first 5 samples of each to verify
    print(random_date_ranges['1_days'][:5], random_date_ranges['2_days'][:5], random_date_ranges['3_days'][:5])
    return random_date_ranges

def run_ready_api_performance_sampling():

    random_date_ranges = load_random_date_ranges()

    flattened_date_ranges = []
    for range_list in random_date_ranges.values():
        flattened_date_ranges.extend(range_list)

    # Initialize CSV file to store results
    with open(api_call_data, 'w', newline='') as csvfile:
        fieldnames = ['start_date', 'end_date', 'time_taken', 'outcome', 'json_size']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Loop over date ranges
        for start_date, end_date in flattened_date_ranges:  
            # Make API call
            url = f"https://uwisctest.assetworks.cloud/ready/api/reporting/request?startDate={start_date}&endDate={end_date}"  # Replace with actual API URL
            
            start_time = time.time()
            outcome = 'Success'  # Initialize as 'Success' and update if an exception occurs
            try:
                print(f'Trying {url}')
                response = requests.get(url, auth=(api_uname, ready_encryption.simple_decrypt(api_pw)), timeout=request_timeout_tolerance)
                response.raise_for_status()  # Raise an HTTPError for bad responses

                # Record data if the status code indicates success
                elapsed_time = time.time() - start_time
                json_size = len(json.dumps(response.json()))
            except requests.Timeout:
                elapsed_time = time.time() - start_time
                json_size = None
                outcome = 'Local Timeout'
            except requests.RequestException as e:
                elapsed_time = time.time() - start_time
                json_size = None
                outcome = 'Response Failure'

            # Write data to CSV
            data_entry_dict = {'start_date': start_date, 'end_date': end_date, 'time_taken': elapsed_time, 'outcome': outcome, 'json_size': json_size}
            print(data_entry_dict)
            writer.writerow(data_entry_dict)
