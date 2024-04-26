import logging
import datetime

# Create a logger
ready_logger = logging.getLogger('ready_logger')
ready_logger.setLevel(logging.INFO)

# Create a file handler and set level to info
log_file_handler = logging.FileHandler(\
	f'log_files/ready_api_calls{datetime.date.today().strftime("%Y%m%d%H%M%S")}.log')
log_file_handler.setLevel(logging.INFO)

# Create a formatter and set it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_file_handler.setFormatter(formatter)

# Add the handler to the logger
ready_logger.addHandler(log_file_handler)

# Confirm initialization in the log file
ready_logger.info(":::::::::: Starting ReADY API logging ::::::::::")

def log(message):
	ready_logger.info(message)

def print_and_log(message):
	print(message)
	log(message)
