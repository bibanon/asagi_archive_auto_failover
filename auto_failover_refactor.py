#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     29-11-2018
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
import sys
# Remote libraries
import requests
import requests.exceptions
# local
import common
import send_email


def stateless_fetch(url, method='get', data=None, expect_status=200, headers=None, delay=None):
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
            if delay:
                time.sleep(delay)
            else:
                time.sleep(random.uniform(0.5, 1.5))
            return response

    logging.error('Giving up. Too many failed retries for url: {0!r}'.format(url))
    return



class BaseFailureHandler():
    """Superclass for failure handlers"""
    def __init__(self):
        self.actions = []
        self.retrigger_delay = None# Time in seconds to sleep after trigger() runs, None for script exit on trigger.
        return

    def add_action(self, function, arguments={}):
        """Register a function and its arguments for execution on triggering"""
        self.actions.append( (function, arguments) )
        return

    def trigger(self):
        """Execute all actions"""
        logging.debug('Triggering!')
        for action in self.actions:
            logging.debug('action={0!r}'.format(action))
            func, args = action
            func(*args)
        logging.debug('Finished triggering')
        if self.retrigger_delay is None:
            logging.info('Exiting script')
            sys.exit()
        else:
            logging.info('Pausing for {0!r} seconds before resuming checking'.format(self.retrigger_delay))
            time.sleep(self.retrigger_delay)
        return

    def run_command(self, command):# WIP
        """Run a shell command"""
        logging.debug('Running shell command: {0!r}'.format(command))
        cmd_output = subprocess.check_output(command, shell=True)
        logging.debug('Ran shell command: {0!r}'.format(command))
        return



class ExampleFailureHandler(BaseFailureHandler):
    """Example failure handler class"""
    def __init__(self):
        BaseFailureHandler.__init__(self)# Load defaults then override any changes
        self.retrigger_delay = None# Time in seconds to sleep after trigger() runs, None for script exit on trigger.
        # Email
        self.gmail_cfg = send_email.YAMLConfigYagmailEmail(config_path='gmail_config.yaml')
        self.add_action(self.send_email)
        # Shell commands
        self.add_action(self.run_command)
        return

    def send_email(self):
        logging.debug('Sending email')
        send_email.send_mail_gmail(
            sender_username=self.gmail_cfg.sender_username,
            sender_password=self.gmail_cfg.sender_password,
            recipient_address=self.gmail_cfg.recipient_address,
            subject=self.gmail_cfg.subject,
            body_template=self.gmail_cfg.body_template
        )
        logging.debug('Sent email')
        return



class FourChanBoard():
    def __init__(self):
        """Set instance default values"""
        self.api_url = ''# URL to board API JSON (.../1.json)
        self.high_post_num = 0#
        self.ratelimit = 3# Rateleimit in seconds
        return

    def find_highest_post_num(self, api_data):
        """Find the highest post number for 4chan API
        ex. http://a.4cdn.org/adv/1.json"""
        highest_post_num = 0# Initialize at 0 so we can run comparisons
        threads = api_data['threads']
        for thread in threads:
            last_post_num = int(thread['posts'][-1]['no'])# The last post in a thread will have the highest post number
            # If the highest post in the thread is higher than our largest seen, replace the largest seen value
            if (last_post_num > highest_post_num):
                highest_post_num = last_post_num
        logging.debug('highest_post_num={0!r}'.format(highest_post_num))
        return highest_post_num

    def check_api(self):
        """Find the current high ID if possible.
        If cannot return an id, return None instead"""
        api_response = stateless_fetch(url=self.api_url, delay=self.ratelimit)
        if api_response:
            api_data = json.loads(api_response.content)
            high_post_num = self.find_highest_post_num(api_data)
            return high_post_num
        return None



class FourChanCo(FourChanBoard):
    """4chan /co/"""
    def __init__(self):
        """Set board values"""
        FourChanBoard.__init__(self)# Load defaults then override any changes
        self.api_url = 'http://a.4cdn.org/co/1.json'# Avoid https per 4ch API docs
        self.ratelimit = 3# Seconds to wait after an API request
        return



class FoolFuukaBoard():
    """Superclass for archive board classes"""
    def __init__(self):
        """Set instance default values"""
        self.api_url = ''
        self.high_post_num = 0# Initialize at zero
        self.ratelimit = None# Seconds to wait after an API request
        return# Do nothing

    def find_highest_post_num(self, api_data):
        """Find the highest post number for foolfuuka API
        ex. http://archive.4plebs.org/_/api/chan/index/?board=adv&page=1"""
        highest_post_num = 0# Initialize at 0 so we can run comparisons
        for thread_num in api_data.keys():# For each thread in the API page
    ##        logging.debug('thread_num = {0!r}'.format(thread_num))
            thread = api_data[thread_num]
            if 'posts' in thread.keys():# Does the thread have any replies? If no replies there will not be a 'posts' item.
                # If there are replies, use the ID of the last post in the thread.
                last_post_num = int(thread['posts'][-1]['num'])# The last post in a thread will have the highest post number
            else:# If there are no replies, use the OP post number
                last_post_num = int(thread['op']['num'])# Must coerce from string to integer for numeric comparisons
            # If the highest post in the thread is higher than our largest seen, replace the largest seen value
            if (last_post_num > highest_post_num):
                highest_post_num = last_post_num
        logging.debug('highest_post_num = {0!r}'.format(highest_post_num))
        return highest_post_num

    def check_api(self):
        """Find the current high ID if possible.
        If cannot return an id, return None instead"""
        api_response = stateless_fetch(url=self.api_url, delay=self.ratelimit)
        if api_response:
            api_data = json.loads(api_response.content)
            high_post_num = self.find_highest_post_num(api_data)
            return high_post_num
        return False



class DesuarchiveCo(FoolFuukaBoard):
    def __init__(self):
        """Set board values"""
        FoolFuukaBoard.__init__(self)# Load defaults then override any changes
        self.api_url = 'http://desuarchive.org/_/api/chan/index/?board=co&page=1'
        self.ratelimit = 3# Seconds to wait after an API request
        return



class ArchiveChecker():
    """Class to handle archive failure detection and response."""
    def __init__(self, chan_board, archive_board, failure_handler):
        logging.debug(u'ArchiveChecker.__init__() locals()={0!r}'.format(locals()))# Record arguments
        # Classes
        self.archive_board = archive_board
        self.chan_board = chan_board
        self.failure_handler = failure_handler# failure_handler.trigger() is called to act on failures
        # Config
        self.recheck_delay = 120# Delay in seconds between online check cycles. 120 is sane-seeming value.
        self.threshold_cycles = 10# How many consecutive failed cycles are permitted before notification?
        # Internal state
        self.consecutive_failures = 0# Counter for how many times in a row update check failed
        self.archive_high_num_old = 0# Previous cycle's highest post_num
        self.archive_high_num_new = 0# Current cycle's highest post_num
        self.chan_high_num_old = 0# Previous cycle's highest post_num
        self.chan_high_num_new = 0# Current cycle's highest post_num
        return

    def poll_sites(self):
        """Do one online check action"""
        logging.debug('Polling sites')

        # Check chan high post_num
        chan_new_num = self.chan_board.check_api()
        if not chan_new_num:
            logging.error('Chan could not be reached')
            return self.success()# Count chan being down as not our problem

        # Check archive high post_num
        archive_new_num = self.archive_board.check_api()
        if not archive_new_num:
            logging.error('Archive could not be reached')
            return self.fail()# Couldn't reach our website

        # Count new posts
        chan_new_posts = (self.chan_high_num_new - self.chan_high_num_old)
        archive_new_posts = (self.archive_high_num_new - self.archive_high_num_old)

        # Compare post numbers
        chan_has_new_posts = (chan_new_posts > 0)# Are there any new chan posts
        archive_has_new_posts = (archive_new_posts > 0)# Are there any new archive posts
        if (chan_has_new_posts and not archive_has_new_posts):
            logging.error('Archive has not updated despite new chan posts')
            self.fail()# Archive has failed to grab new 4chan posts

        logging.debug('No failure detected')
        return self.success()# Nothing went wrong.

    def loop(self):
        """Loop forever."""
        logging.debug('Starting poll loop')
        try:
            while True:
                self.poll_sites()
                if (self.consecutive_failures > self.threshold_cycles):
                    logging.critical('Too many consecutive failures! Website is down!')
                    self.alert()
                time.sleep(self.recheck_delay)
        except Exception, err:
            logging.critical('Unhandled exception in loop!')
            logging.exception(err)
            self.alert()

    def success(self):
        """Board looks like it's online"""
        logging.debug('Site online')
        # Reset failure counter
        self.consecutive_failures = 0
        return

    def fail(self):
        """Handle one failed site check"""
        logging.info('Site not online')
        self.consecutive_failures += 1
        return

    def alert(self):
        """Fired when too many consecutive failed checks occur."""
        logging.debug('Alerting!')
        self.failure_handler.trigger()
        logging.debug('Alerted')
        return



def example():
    logging.info('Start example()')
    co_4ch = FourChanCo()# chan we're checking
    co_desu = DesuarchiveCo()# archive we're checking
    fail_h = ExampleFailureHandler()# What to do if the site goes down
    ac = ArchiveChecker(co_4ch, co_desu, fail_h)
    ac.loop()# Start checking the site, will loop until an exception occurs.
    logging.info('End example()')
    return


def main():
    example()
    return


if __name__ == '__main__':
    common.setup_logging(os.path.join("debug", "auto_failover_refactor_2018-11.log.txt"))# Setup logging
    try:
        main()
    # Log exceptions
    except Exception, e:
        logging.critical("Unhandled exception!")
        logging.exception(e)
    logging.info("Program finished.")