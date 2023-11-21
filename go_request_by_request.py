### This is some old code that does work, but the idea
### itself is flawed.  One API call per ReADY request 
### would take astromically too long to do even once
### a month.  But the code works so I'm stashing it
### away.  -- mgracz 11/13/23


    #9/15/23 IDEA run thi over and over and save the perfor metrics at least,
    #maybe run it 100 times overnight, 100 times during the day, 100 times on a weekend
    #for each day, take the max payload and count that JSON's # of requets and store a
    #date --> int map that when we run future requests, we can use to check the payload
    #for retries.  I can't belive I'm doing that, if I do.
    #9/25/23 THAT doesn't even work b/c old requests' sizes don't necessarily grow whenever
    #they get updated GRRR.

# This takes forever, I haven't even calculated how long it'll take but I think it's on the
# order of *days*.  As a function of avg response time for a one-shot API request times the
# absurd number of ReADY requests that the DB generates
def go_request_by_request(api_start_request=start_request_num, api_end_request=end_request_num):
    def make_request(request_num):
        url = f"{endpoint_url}request={request_num}"
        response = requests.get(url, timeout=HTTP_TIMEOUT_TOLERANCE, auth=(api_uname, rec.dlfdadreaqf(api_pw)))
        request = parse_json_response(response.json())
        return request

    start_time = datetime.datetime.now().strftime(default_long_date_format)

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

    end_time = datetime.datetime.now().strftime(default_long_date_format)
    elapsed_time = end_time - start_time
    print(f'Elapsed time: {str(elapsed_time)}')
    return ready_requests