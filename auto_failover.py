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
# Remote libraries
# local
from common import *



# Configuration

# Command to execute if failure is detected
COMMAND_ON_FAILURE = """echo 'server down' """


API_URL_FF = 'http://archive.4plebs.org/_/api/chan/index/?board=adv&page=1'
API_URL_4CH = ''


RECHECK_DELAY = 10# Seconds

THRESHOLD_TIME = 120# Seconds

# Number of repeated failures before declaring failure
THRESHOLD_CYCLES = 10

# /Configuration



def find_highest_post_num_4ch(api_data):
    """Find the highest post number for 4chan API"""
    return highest_post_num


def find_highest_post_num_ff(api_data):
    """Find the highest post number for foolfuuka API"""
    highest_seen_id = 0# Initialize at 0 so we can run comparisons
    thread_nums = api_data.keys()
    assert(len(thread_nums) >= 10)# We should have at least a full pages worth of threads (10 threads per page)
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

        if (last_post_num > highest_seen_id):# If the highest post in the thread is higher than our largest seen, replace the largest seen value
            highest_seen_id = last_post['num']
            print('highest_seen_id = {0}'.format(highest_seen_id))

    assert(highest_seen_id > 0)# Sanity check
    return highest_seen_id






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


# Check the highest ID on the archive
api_response_ff = fetch(requests_session, url=API_URL_FF, expect_status=200)
api_data_ff = json.loads(api_response_ff.content)

highest_post_id_ff = find_highest_post_num_ff(api_data_ff)
print('highest_post_id_ff = {0}'.format(highest_post_id_ff))

# Check the highest ID on 4chan
api_response_4ch = fetch(requests_session, url=API_URL_4CH, expect_status=200)

api_data_4ch = json.loads(api_response_4ch.content)

highest_post_id_4ch = find_highest_post_num_4ch(api_data_4ch)
print('highest_post_id_4ch = {0}'.format(highest_post_id_4ch))


