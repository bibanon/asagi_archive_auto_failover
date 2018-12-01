#-------------------------------------------------------------------------------
# Name:        desuarchive_check.py
# Purpose:     For keeping tabs on DesuArchive
#
# Author:      User
#
# Created:     29-11-2018
# Copyright:   (c) User 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# StdLib
import os
import logging
# Remote libraries
# local
import auto_failover
import send_email
import common# We need this for setting up logging


# Board definition/config
class FourChanCo(auto_failover.FourChanBoard):
    """4chan /co/"""
    def __init__(self):
        """Set board values"""
        auto_failover.FourChanBoard.__init__(self)# Load defaults then override any changes
        self.api_url = 'http://a.4cdn.org/co/1.json'# Avoid https per 4ch API docs
        self.ratelimit = 3# Seconds to wait after an API request
        return


class DesuarchiveCo(auto_failover.FoolFuukaBoard):
    def __init__(self):
        """Set board values"""
        auto_failover.FoolFuukaBoard.__init__(self)# Load defaults then override any changes
        self.api_url = 'http://desuarchive.org/_/api/chan/index/?board=co&page=1'
        self.ratelimit = 3# Seconds to wait after an API request
        return



# Notification & response definition/config
class DesuarchiveFailureHandler(auto_failover.BaseFailureHandler):
    """Failure response for if Desuarchive goes down"""
    def __init__(self):
        auto_failover.BaseFailureHandler.__init__(self)# Load defaults then override any changes
        self.retrigger_delay = None# Time in seconds to sleep after trigger() runs, None for script exit on trigger.
        # Email
        gmail_config_path = os.path.join('config', 'email_gmail.yaml')
        self.gmail_cfg = send_email.YAMLConfigYagmailEmail(config_path=gmail_config_path)
        self.add_action(function=self.send_email, arguments={})
        # Shell commands
        self.add_action(function=self.run_command, arguments={'command': 'echo SOME TEXT > SOME_FILE.txt'})# TODO: Shell script to do archive failover.
        return

    def send_email(self, *args, **kwargs):
        """Send an email from Gmail"""
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



def main():
    """Start monitoring Desuarchive"""
    logging.debug('Setup monitoring for Desuarchive')
    co_4ch = FourChanCo()# chan we're checking
    co_desu = DesuarchiveCo()# archive we're checking
    fail_h = DesuarchiveFailureHandler()# What to do if the site goes down
    ac = auto_failover.ArchiveChecker(
        chan_board = co_4ch,
        archive_board = co_desu,
        failure_handler = fail_h,
        recheck_delay = 120,# Delay in seconds between online check cycles. 120 is sane-seeming value.
        threshold_cycles = 10,# How many consecutive failed cycles are permitted before notification? (-1 triggers immediately, 0 triggers on first failure)
    )
    logging.debug('Begin monitoring for Desuarchive')
    ac.loop()# Start checking the site, will loop until an exception occurs.
    logging.debug('main() returning')
    return# This function should only return if KeyboardInterrupt is used or something in this code is broken.


if __name__ == '__main__':
    common.setup_logging(# Setup logging
        os.path.join("debug", "desuarchive_check.log.txt"),
        console_level=logging.DEBUG# Restrict log messages sent to console to (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    )
    try:
        main()
    except Exception, e:# Log fatal exceptions
        logging.critical(u"Unhandled exception!")
        logging.exception(e)
    logging.info(u"Program finished.")