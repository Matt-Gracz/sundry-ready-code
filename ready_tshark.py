import subprocess
import os

def start_capture(ip_addr, capture_file, interface_index):
    command = fr'tshark -i {interface_index} -f "host {ip_addr}" -w {capture_file}'
    print(command)
    return subprocess.Popen(command, shell=True)

def stop_capture(capture_process):
    capture_process.terminate()
    capture_process.wait()

def analyze_capture(capture_file):
    metrics = {}

    # Example command to count packets (you will replace this with the actual metrics you need)
    command = f"tshark -r {capture_file} -q -z io,stat,0"
    result = subprocess.check_output(command, shell=True).decode()

    # Extract and parse the metrics from the result
    # This depends on the tshark command used and the data you need
    metrics['total_packets'] = extract_total_packets(result)

    return metrics

def extract_total_packets(tshark_output):
    # Doesn't matter
    return parsed_packet_count

# Usage
'''
    # Stop capturing network performance metrics now that we're done
    shark.stop_capture(capture_process)
    # Grab only the metrics we care about from tshark
    shark_metrics = shark.analyze_capture(ready_tshark_tmp_file)
    # Start capturing network performance metrics on the ready server
    # connection
    capture_process = shark.start_capture(ready_host_ip_addr, ready_tshark_tmp_file, wifi_interface_index
'''

