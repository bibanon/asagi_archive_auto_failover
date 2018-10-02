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



# Configuration

# Command to execute if failure is detected
COMMAND_ON_FAILURE = """cmd """


API_URL_FF = 'http://archive.4plebs.org/_/api/chan/index/?board=adv&page=1'
API_URL_4CH = 'http://a.4cdn.org/adv/1.json'# Avoid https per 4ch API docs


RECHECK_DELAY = 10# Seconds

THRESHOLD_TIME = 120# Seconds

# Number of repeated failures before declaring failure
THRESHOLD_CYCLES = 10

# /Configuration


def run_command():
    print('Running command: {0!r}'.format(COMMAND_ON_FAILURE))
    cmd_output = subprocess.check_output(COMMAND_ON_FAILURE, shell=True)
    print('cmd_output = {0!r}'.format(COMMAND_ON_FAILURE))


def find_highest_post_num_4ch(api_data):
    """Find the highest post number for 4chan API
    ex. http://a.4cdn.org/adv/1.json"""
    highest_seen_id = 0# Initialize at 0 so we can run comparisons
    threads = api_data['threads']
    assert(len(threads) > 0)# Sanity check
    for thread in threads:
        posts = thread['posts']
        last_post = posts[-1]# The last post in a thread will have the highest post number
        last_post_num = last_post['no']

        assert(last_post_num > 0)# Sanity check

        # If the highest post in the thread is higher than our largest seen, replace the largest seen value
        if (last_post_num > highest_seen_id):
            highest_seen_id = last_post_num
            print('highest_seen_id = {0}'.format(highest_seen_id))

    assert(highest_seen_id > 0)# Sanity check
    return highest_seen_id


def find_highest_post_num_ff(api_data):
    """Find the highest post number for foolfuuka API
    ex. http://archive.4plebs.org/_/api/chan/index/?board=adv&page=1"""
    highest_seen_id = 0# Initialize at 0 so we can run comparisons
    thread_nums = api_data.keys()
    assert(len(thread_nums) > 0)#

    for thread_num in thread_nums:# For each thread in the API page
        print('thread_num = {0}'.format(thread_num))
        thread = api_data[thread_num]

        if 'posts' in thread.keys():# Does the thread have any replies? If no replies there will not be a 'posts' item.
            # If there are replies, use the ID of the last post in the thread.
            posts = thread['posts']
            last_post = posts[-1]# The last post in a thread will have the highest post number
            last_post_num = last_post['num']
        else:
            # If there are no replies, use the OP post number
            last_post_num = thread['op']['num']

        assert(last_post_num > 0)# Sanity check

        # If the highest post in the thread is higher than our largest seen, replace the largest seen value
        if (last_post_num > highest_seen_id):
            highest_seen_id = last_post_num
            print('highest_seen_id = {0}'.format(highest_seen_id))

    assert(highest_seen_id > 0)# Sanity check
    return highest_seen_id


def check_if_site_online():
    # Poll archive API
    # If archive not updated, Poll 4chan API to compare
    # Allow lack of updates if 4chan has not updated
    return



def main():
    return# REMOVEME
    while True:
        # Load archive page
        archive_page_response = fetch(requests_session, url=post_page_url, expect_status=200)
        # Test for changes
        pass


if __name__ == '__main__':
    main()

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
#while True:
# Check the highest ID on the archive
api_response_ff = fetch(requests_session, url=API_URL_FF, expect_status=200)
api_data_ff = json.loads(api_response_ff.content)
new_highest_post_id_ff = find_highest_post_num_ff(api_data_ff)
print('new_highest_post_id_ff = {0}'.format(new_highest_post_id_ff))

if (old_highest_post_id_ff):
    # Only perform check if we have a previous value to compare against
    number_of_new_ff_posts = new_highest_post_id_ff - old_highest_post_id_ff
    assert(number_of_new_ff_posts >= 0)# This should only ever be positive, since postIDs only increase.

    if (number_of_new_ff_posts == 0):
        # Archive has not gained posts since last check

        # Poll 4chan to see if it has updated
        # Check the highest ID on 4chan
        api_response_4ch = fetch(requests_session, url=API_URL_4CH, expect_status=200)
        api_data_4ch = json.loads(api_response_4ch.content)
        new_highest_post_id_4ch = find_highest_post_num_4ch(api_data_4ch)
        print('new_highest_post_id_4ch = {0}'.format(new_highest_post_id_4ch))

        if old_highest_post_id_4ch:
            # If we have a value to compare against for 4chan
            number_of_new_4ch_posts = new_highest_post_id_4ch - old_highest_post_id_4ch
            assert(number_of_new_4ch_posts >= 0)# This should only ever be positive, since postIDs only increase.
            if (number_of_new_4ch_posts == 0):
                # If 4chan has no new posts
                print('4chan has gained no new posts since last check, resetting failure counter.')
                consecutive_failures = 0# Reset failure counter
            else:
                # If 4chan has gained posts but the archive has not gained posts
                print('Error detected: Archive has no new posts but 4ch does. Incrementing failure counter')
                consecutive_failures += 1# Increment failure counter
        else:
            # We have not checked 4chan before
            print('This is the first check of 4chan, cannot perform comparison this cycle.')
    else:
        # Archive has gained posts since last check
        print('Archive has {0} new posts since last check'.format(number_of_new_ff_posts))
        print('Archive has gained no new posts since last check, resetting failure counter.')
        consecutive_failures = 0# Reset failure counter
else:
    # We have not checked the archive before
    print('This is the first check of the archive, cannot perform comparison this cycle.')

# Check if we should declare the site down
print('consecutive_failures = {0!r}, THRESHOLD_CYCLES = {1!r}'.format(new_highest_post_id_4ch, THRESHOLD_CYCLES))
if (consecutive_failures > THRESHOLD_CYCLES):
    print('Number of consecutive failures exceeded threshold! Running command.')
    run_command()

# Store current high IDs for next cycle's comparisons
old_highest_post_id_ff = new_highest_post_id_ff
old_highest_post_id_4ch = new_highest_post_id_4ch

# Pause for a short time between cycles
time.sleep(RECHECK_DELAY)
# End of loop

