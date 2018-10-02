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
import json
import subprocess
# Remote libraries
# local
from common import *



# ===== Configuration =====
# Values in capitals are globals/defined at module level scope.

# Command to execute if failure is detected
COMMAND_ON_FAILURE = """cmd """

# URL to foolfuuka archive API to test for new posts
API_URL_FF = 'http://archive.4plebs.org/_/api/chan/index/?board=adv&page=1'

# URL to 4chan API to test for new posts
API_URL_4CH = 'http://a.4cdn.org/adv/1.json'# Avoid https per 4ch API docs

# Delay in seconds between update check cycles
RECHECK_DELAY = 20# Seconds

# UNUSED
#THRESHOLD_TIME = 120# Seconds

# Number of consecutive failures to increase maximum postnumber before declaring a failure.
THRESHOLD_CYCLES = 10
# ===== /Configuration =====





class FailoverException(Exception):
    """Local subclass for all custom exceptions within auto_failover.py"""




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
    # Setup requests session
    requests_session = requests.Session()
    # ===== Init state variables for loop =====
    # Init tracking vars
    consecutive_failures = 0

    new_highest_post_id_ff = None# This cycle's detected high ID.
    old_highest_post_id_ff = None# Last cycle's detected high ID.

    new_highest_post_id_4ch = None# This cycle's detected high ID.
    old_highest_post_id_4ch = None# Last cycle's detected high ID.

    # ===== Begin loop here =====
    while True:
        # Check the highest ID on the archive
        api_response_ff = fetch(requests_session, url=API_URL_FF, expect_status=200)
        api_data_ff = json.loads(api_response_ff.content)
        new_highest_post_id_ff = find_highest_post_num_ff(api_data_ff)
        logging.debug('new_highest_post_id_ff = {0!r}'.format(new_highest_post_id_ff))

        if (old_highest_post_id_ff is not None):
            # Only perform check if we have a previous value to compare against
            number_of_new_ff_posts = new_highest_post_id_ff - old_highest_post_id_ff
            logging.debug('Archive has {0!r} new posts since last check'.format(number_of_new_ff_posts))
            assert(number_of_new_ff_posts >= 0)# This should only ever be positive, since postIDs only increase.

            if (number_of_new_ff_posts == 0):
                # Archive has not gained posts since last check

                # Poll 4chan to see if it has updated
                # Check the highest ID on 4chan
                api_response_4ch = fetch(requests_session, url=API_URL_4CH, expect_status=200)
                api_data_4ch = json.loads(api_response_4ch.content)
                new_highest_post_id_4ch = find_highest_post_num_4ch(api_data_4ch)
                logging.debug('new_highest_post_id_4ch = {0!r}'.format(new_highest_post_id_4ch))

                if (old_highest_post_id_4ch is not None):
                    # If we have a value to compare against for 4chan
                    number_of_new_4ch_posts = new_highest_post_id_4ch - old_highest_post_id_4ch
                    logging.debug('4ch has {0!r} new posts since last check'.format(number_of_new_4ch_posts))
                    assert(number_of_new_4ch_posts >= 0)# This should only ever be positive, since postIDs only increase.

                    if (number_of_new_4ch_posts == 0):
                        # If 4chan has no new posts
                        logging.info('4chan has gained no new posts since last check, resetting failure counter.')
                        consecutive_failures = 0# Reset failure counter
                    else:
                        # If 4chan has gained posts but the archive has not gained posts
                        logging.info('Error detected: Archive has no new posts but 4ch does. Incrementing failure counter')
                        consecutive_failures += 1# Increment failure counter

                else:
                    # We have not checked 4chan before
                    logging.info('This is the first check of 4chan, cannot perform comparison this cycle.')

            else:
                # Archive has gained posts since last check
                logging.info('Archive has gained posts since last check, resetting failure counter.')
                consecutive_failures = 0# Reset failure counter

        else:
            # We have not checked the archive before
            logging.info('This is the first check of the archive, cannot perform comparison this cycle.')

        # Check if we should declare the site down
        logging.debug('consecutive_failures = {0!r}, THRESHOLD_CYCLES = {1!r}'.format(consecutive_failures, THRESHOLD_CYCLES))
        if (consecutive_failures > THRESHOLD_CYCLES):
            # The site is down.
            logging.critical('Number of consecutive failures exceeded threshold! Running command.')
            run_command()
            # There is no need for this script to be running anymore.
            # Failover to new server configureation has taken place and it is inappropriate to run the command again.
            logging.critical('Further checking inappropriate, exiting polling loop.')
            return# This is the only correct place for this function to return.

        # Store current high IDs for next cycle's comparisons
        old_highest_post_id_ff = new_highest_post_id_ff
        old_highest_post_id_4ch = new_highest_post_id_4ch

        # Pause for a short time between cycles
        logging.debug('Pausing between cycles for {0!r}'.format(RECHECK_DELAY))
        time.sleep(RECHECK_DELAY)
        continue
    # ===== End of loop =====
    logging.error('Execution should never reach this point.')
    assert(False)# Execution should never reach here.
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