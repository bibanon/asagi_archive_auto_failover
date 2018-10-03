#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     27-09-2018
# Copyright:   (c) User 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# StdLib
import time
import os
import random
import logging
import logging.handlers
import datetime
import json
import subprocess
# Remote libraries
import requests
import requests.exceptions
# local
##from common import *



# ===== Configuration =====
# Values in capitals are globals/defined at module level scope.

# Command to execute if failure is detected
COMMAND_ON_FAILURE = """echo "test string" """

# URL to foolfuuka archive API to test for new posts
API_URL_FF = 'http://archive.4plebs.org/_/api/chan/index/?board=adv&page=1'

# URL to 4chan API to test for new posts
API_URL_4CH = 'http://a.4cdn.org/adv/1.json'# Avoid https per 4ch API docs

# Delay in seconds between update check cycles
RECHECK_DELAY = 120# Seconds

# UNUSED
#THRESHOLD_TIME = 120# Seconds

# Number of consecutive failures to increase maximum postnumber before declaring a failure.
THRESHOLD_CYCLES = 10


# URL fetching settings
# This is what you want to edit to change the delay between requests.
# Use a '#' symbol at the start of a line to comment it out and make it get ignored by the code
# Only one of these should be uncommented or the later ones will overwrite the previous ones and you won't get what you want.
#CUSTOM_DELAY = None# This will use my original randomized delay
CUSTOM_DELAY = 0.1# This will use a delay of 0.1 second
#CUSTOM_DELAY = 0.05# This will use a delay of 0.05 second

# ===== /Configuration =====





class FailoverException(Exception):
    """Local subclass for all custom exceptions within auto_failover.py"""



class FetchTooManyRetries(FailoverException):
    pass



# logging setup
def setup_logging(log_file_path, timestamp_filename=True, max_log_size=104857600):
    """Setup logging (Before running any other code)
    http://inventwithpython.com/blog/2012/04/06/stop-using-print-for-debugging-a-5-minute-quickstart-guide-to-pythons-logging-module/
    """
    assert( len(log_file_path) > 1 )
    assert( type(log_file_path) == type("") )
    global logger

    # Make sure output dir(s) exists
    log_file_folder =  os.path.dirname(log_file_path)
    if log_file_folder is not None:
        if not os.path.exists(log_file_folder):
            os.makedirs(log_file_folder)

    # Add timetamp for filename if needed
    if timestamp_filename:
        # http://stackoverflow.com/questions/8472413/add-utc-time-to-filename-python
        # '2015-06-30-13.44.15'
        timestamp_string = datetime.datetime.utcnow().strftime("%Y-%m-%d %H.%M.%S%Z")
        # Full log
        log_file_path = add_timestamp_to_log_filename(log_file_path,timestamp_string)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # 2018-10-02 18:16:15,229 - INFO - f.auto_failover.py - ln.117 - Logging started.
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - f.%(filename)s - ln.%(lineno)d - %(message)s")

    # File 1, log everything
    # https://docs.python.org/2/library/logging.handlers.html
    # Rollover occurs whenever the current log file is nearly maxBytes in length; if either of maxBytes or backupCount is zero, rollover never occurs.
    fh = logging.handlers.RotatingFileHandler(
        filename=log_file_path,
        # https://en.wikipedia.org/wiki/Binary_prefix
        # 104857600 100MiB
        maxBytes=max_log_size,
        backupCount=2,# Two files worth of logs should be plenty.
        )
    fh.setLevel(logging.DEBUG)# Store all messages in the logfile so we can debug problems
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console output
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)# Only show the really important stuff in the console
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logging.info("Logging started. log_file_path = {0!r}".format(log_file_path))
    return logger

def add_timestamp_to_log_filename(log_file_path, timestamp_string):
    """Insert a string before a file extention"""
    base, ext = os.path.splitext(log_file_path)
    return base+"_"+timestamp_string+ext
# /logging setup


def fetch(url, method='get', data=None, expect_status=200, headers=None):
#    headers = {'user-agent': user_agent}
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    if headers is None:
        headers = {'user-agent': user_agent}
    elif 'user-agent' not in headers.keys():
        headers['user-agent'] = user_agent

    if headers:
        headers.update(headers)

    for try_num in range(5):
        logging.debug('Fetch {0}'.format(url))
        try:
            if method == 'get':
                response = requests.get(url, headers=headers, timeout=300)
            elif method == 'post':
                response = requests.post(url, headers=headers, data=data, timeout=300)
            else:
                raise Exception('Unknown method')
        except requests.exceptions.Timeout, err:
            logging.exception(err)
            logging.error('Caught requests.exceptions.Timeout')
            continue
        except requests.exceptions.ConnectionError, err:
            logging.exception(err)
            logging.error('Caught requests.exceptions.ConnectionError')
            continue
##        # Allow certain error codes to be passed back out
##        if response.status_code == 404:
##            logging.error("fetch() 404 for url: %s" % url)
##            return
        if response.status_code != expect_status:
            logging.error('Problem detected. Status code mismatch. Sleeping. expect_status: {0!r}, response.status_code: {1!r}'.format(expect_status, response.status_code))
            time.sleep(60*try_num)
            continue
        else:
            if CUSTOM_DELAY:
                time.sleep(CUSTOM_DELAY)
            else:
                time.sleep(random.uniform(0.5, 1.5))
            return response

    logging.error('Giving up. Too many failed retries for url: {0!r}'.format(url))
    return


def run_command():
    """Run a specified command (COMMAND_ON_FAILURE)
    Values in capitals are globals/defined at module level scope.
    """
    logging.info('Running command: {0!r}'.format(COMMAND_ON_FAILURE))
    cmd_output = subprocess.check_output(COMMAND_ON_FAILURE, shell=True)
    logging.info('cmd_output = {0!r}'.format(COMMAND_ON_FAILURE))
    return


def find_highest_post_num_4ch(api_data):
    """Find the highest post number for 4chan API
    ex. http://a.4cdn.org/adv/1.json"""
    highest_seen_id = 0# Initialize at 0 so we can run comparisons
    threads = api_data['threads']
    assert(len(threads) > 0)# Sanity check, there should always be at least one thread on the board.
    for thread in threads:
        posts = thread['posts']
        last_post = posts[-1]# The last post in a thread will have the highest post number
        last_post_num = int(last_post['no'])# Must coerce from string to integer for numeric comparisons

        assert(type(last_post_num) is int)# Sanity check, must be integer for numeric comparisons
        assert(last_post_num > 0)# Sanity check, postIDs are always positive integers

        # If the highest post in the thread is higher than our largest seen, replace the largest seen value
        if (last_post_num > highest_seen_id):
            highest_seen_id = last_post_num
            logging.debug('highest_seen_id = {0!r}'.format(highest_seen_id))

    assert(highest_seen_id > 0)# Sanity check
    return highest_seen_id


def find_highest_post_num_ff(api_data):
    """Find the highest post number for foolfuuka API
    ex. http://archive.4plebs.org/_/api/chan/index/?board=adv&page=1"""
    highest_seen_id = 0# Initialize at 0 so we can run comparisons
    thread_nums = api_data.keys()
    assert(len(thread_nums) > 0)# Sanity check, there should always be at least one thread on the board.

    for thread_num in thread_nums:# For each thread in the API page
##        logging.debug('thread_num = {0!r}'.format(thread_num))
        thread = api_data[thread_num]

        if 'posts' in thread.keys():# Does the thread have any replies? If no replies there will not be a 'posts' item.
            # If there are replies, use the ID of the last post in the thread.
            posts = thread['posts']
            last_post = posts[-1]# The last post in a thread will have the highest post number
            last_post_num = int(last_post['num'])# Must coerce from string to integer for numeric comparisons
        else:
            # If there are no replies, use the OP post number
            last_post_num = int(thread['op']['num'])# Must coerce from string to integer for numeric comparisons

        assert(type(last_post_num) is int)# Sanity check, must be integer for numeric comparisons
        assert(last_post_num > 0)# Sanity check, postIDs are always positive integers

        # If the highest post in the thread is higher than our largest seen, replace the largest seen value
        if (last_post_num > highest_seen_id):
            highest_seen_id = last_post_num
            logging.debug('highest_seen_id = {0!r}'.format(highest_seen_id))

    assert(highest_seen_id > 0)# Sanity check
    return highest_seen_id


def check_archive_loop():
    """Periodically test if the archive is down,
    (maximum of one check cycle every RECHECK_DELAY seconds)
    based on whether new posts are being created on the archive and it's target.
    If the specified threshold number of failures to gain posts (THRESHOLD_CYCLES)
    is reached, run command (COMMAND_ON_FAILURE).
    Values in capitals are globals/defined at module level scope.
    """
    logging.info('Beginning polling of archive state...')
    # ===== Init state variables for loop =====
    # Init tracking vars
    consecutive_failures = 0

    new_highest_post_id_ff = None# This cycle's detected high ID.
    old_highest_post_id_ff = None# Last cycle's detected high ID.

    new_highest_post_id_4ch = None# This cycle's detected high ID.
    old_highest_post_id_4ch = None# Last cycle's detected high ID.

    # ===== Begin loop here =====
    while True:
        try:
            # Store previous high IDs for this cycle's comparisons
            old_highest_post_id_ff = new_highest_post_id_ff
            old_highest_post_id_4ch = new_highest_post_id_4ch

            # Pause for a short time between cycles
            logging.debug('Pausing between cycles for {0!r}'.format(RECHECK_DELAY))
            time.sleep(RECHECK_DELAY)

            # Check if we should declare the site down
            logging.debug('consecutive_failures = {0!r}, THRESHOLD_CYCLES = {1!r}'.format(consecutive_failures, THRESHOLD_CYCLES))
            if (consecutive_failures > THRESHOLD_CYCLES):
                # The site is down.
                logging.critical('Number of consecutive failures exceeded threshold! Running command.')
                run_command()
                # There is no need for this script to be running anymore.
                # Failover to new server configureation has taken place and it is inappropriate to run the command again.
                logging.info('Further checking inappropriate, exiting polling loop.')
                return# This is the only correct place for this function to return.

            # Check the highest ID on the archive
            api_response_ff = fetch(url=API_URL_FF, expect_status=200)
            if (api_response_ff is None):
                # Count failure to load API as a failure of the archive
                logging.info('Failed to retrieve FF API JSON. Incrementing failure counter.')
                consecutive_failures += 1# Increment failure counter
                continue
            api_data_ff = json.loads(api_response_ff.content)
            new_highest_post_id_ff = find_highest_post_num_ff(api_data_ff)
            logging.debug('new_highest_post_id_ff = {0!r}'.format(new_highest_post_id_ff))

            if (old_highest_post_id_ff is None):
                # We have not checked the archive before
                logging.info('This is the first check of the archive, cannot perform comparison this cycle.')
                continue
            else:
                # Only perform check if we have a previous value to compare against
                number_of_new_ff_posts = new_highest_post_id_ff - old_highest_post_id_ff
                logging.debug('Archive has {0!r} new posts since last check.'.format(number_of_new_ff_posts))
                assert(number_of_new_ff_posts >= 0)# This should only ever be positive, since postIDs only increase.

                if (number_of_new_ff_posts == 0):
                    # Archive has not gained posts since last check
                    logging.info('Archive has gained no new posts since last recheck.')

                    # Poll 4chan to see if it has updated
                    # Check the highest ID on 4chan
                    api_response_4ch = fetch(url=API_URL_4CH, expect_status=200)
                    if (api_response_ff is None):
                        # Permit failure of 4ch, since we do not control it.
                        logging.warning('Failed to retrieve 4ch API JSON.')
                        continue
                    api_data_4ch = json.loads(api_response_4ch.content)
                    new_highest_post_id_4ch = find_highest_post_num_4ch(api_data_4ch)
                    logging.debug('new_highest_post_id_4ch = {0!r}'.format(new_highest_post_id_4ch))

                    if (old_highest_post_id_4ch is None):
                        # We have not checked 4chan before
                        logging.info('This is the first check of 4chan, cannot perform comparison this cycle.')
                        continue
                    else:
                        # If we have a value to compare against for 4chan
                        number_of_new_4ch_posts = new_highest_post_id_4ch - old_highest_post_id_4ch
                        logging.debug('4ch has {0!r} new posts since last check.'.format(number_of_new_4ch_posts))
                        assert(number_of_new_4ch_posts >= 0)# This should only ever be positive, since postIDs only increase.

                        if (number_of_new_4ch_posts == 0):
                            # If 4chan has no new posts
                            # Do not change counter if archive and 4chan both have no new posts
                            logging.info('Neither archive or 4chan have gained new posts since last check, doing nothing.')
                            continue
                        else:
                            # If 4chan has gained posts but the archive has not gained posts
                            logging.info('Error detected: Archive has no new posts but 4ch does. Incrementing failure counter.')
                            consecutive_failures += 1# Increment failure counter
                else:
                    # Archive has gained posts since last check
                    logging.info('Archive has gained posts since last check, resetting failure counter.')
                    consecutive_failures = 0# Reset failure counter

        except Exception, err:# Catch any exception that happens
            logging.exception(err)# Record exception
            if type(err) is KeyboardInterrupt:# Permit ctrl-c KeyboardInterrupt to kill script
                raise
            logging.error('Exception occured, incrementing failure counter.')
            consecutive_failures += 1# Increment failure counter
        continue
    # ===== End of loop =====
    logging.error('Execution should never reach this point.')
    raise FailoverException()# Execution should never reach here.


def main():
    check_archive_loop()
    logging.info('Exiting script.')
    return


if __name__ == '__main__':
    setup_logging(os.path.join("debug", "auto_failover.log.txt"))# Setup logging
    try:
        main()
    # Log exceptions
    except Exception, e:
        logging.critical("Unhandled exception!")
        logging.exception(e)
    logging.info("Program finished.")
