#-------------------------------------------------------------------------------
# Name:        send_email.py
# Purpose:  Send an email to a specified address.
#
# Author:      User
#
# Created:     04-11-2018
# Copyright:   (c) User 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# StdLib
import logging.handlers
import time
import os
import smtplib# For SMTP messages
import email# For SMTP messages
# Remote libraries
import yagmail
import yaml
# local
from common import *



class YAMLConfigYagmailEmail():
    """Handle reading, writing, and creating YAML config files.
    For Gmail"""
    def __init__(self, config_path=None):
        # Set default values
        self.sender_username = ''
        self.sender_password = ''
        self.recipient_address = ''
        self.subject = ''
        self.body_template = ''

        if config_path:
            # Ensure config dir exists.
            config_dir = os.path.dirname(config_path)
            if len(config_dir) > 0:# Only try to make a dir if ther is a dir to make.
                if not os.path.exists(config_dir):
                    os.makedirs(config_dir)
            # Load/create config file
            if os.path.exists(config_path):
                self.load(config_path)# Load config file if it exists.
            else:
                self.save(config_path, self.__class__())# Create an example config file if no file exists.
        return

    def load(self, config_path):
        """Load configuration from YAML file."""
        logging.debug('Reading from config_path={0!r}'.format(config_path))
        with open(config_path, 'rb') as load_f:# Read the config from file.
            config = yaml.safe_load(load_f)
        # Store values to class instance.
        for key in config.keys():
            setattr(self, key, config[key])# Sets self.key to config[key]
        logging.debug('Loaded config values: {0!r}'.format(config))
        return

    def save(self, config_path, instance):
        """Save current configuration to YAML file."""
        logging.debug('Saving to config_path = {0!r}'.format(config_path))
        with open(config_path, 'wb') as save_f:# Write data to file.
            yaml.dump(
                data=vars(instance),
                stream=save_f,
                explicit_start=True,# Begin with '---'
                explicit_end=True,# End with '...'
                default_flow_style=False# Output as multiple lines
            )
        return



class YAMLConfigSmtplibEmail():
    """Handle reading, writing, and creating YAML config files.
    For SMTP"""
    def __init__(self, config_path=None):
        # Set default values
        self.smtp_server_address = ''
        self.smtp_server_port = 465
        self.sender_email_address = ''
        self.sender_username = ''
        self.sender_password = ''
        self.recipient_address = ''
        self.subject = ''
        self.body_template = ''

        if config_path:
            # Ensure config dir exists.
            config_dir = os.path.dirname(config_path)
            if len(config_dir) > 0:# Only try to make a dir if ther is a dir to make.
                if not os.path.exists(config_dir):
                    os.makedirs(config_dir)
            # Load/create config file
            if os.path.exists(config_path):
                self.load(config_path)# Load config file if it exists.
            else:
                self.save(config_path, self.__class__())# Create an example config file if no file exists.
        return

    def load(self, config_path):
        """Load configuration from YAML file."""
        logging.debug('Reading from config_path={0!r}'.format(config_path))
        with open(config_path, 'rb') as load_f:# Read the config from file.
            config = yaml.safe_load(load_f)
        # Store values to class instance.
        for key in config.keys():
            setattr(self, key, config[key])# Sets self.key to config[key]
        logging.debug('Loaded config values: {0!r}'.format(config))
        return

    def save(self, config_path, instance):
        """Save current configuration to YAML file."""
        logging.debug('Saving to config_path = {0!r}'.format(config_path))
        with open(config_path, 'wb') as save_f:# Write data to file.
            yaml.dump(
                data=vars(instance),
                stream=save_f,
                explicit_start=True,# Begin with '---'
                explicit_end=True,# End with '...'
                default_flow_style=False# Output as multiple lines
            )
        return


class YAMLConfigLoggingSmtpEmail():
    """Handle reading, writing, and creating YAML config files.
    For SMTP"""
    def __init__(self, config_path=None):
        # Set default values
        self.smtp_server_address = ''
        self.smtp_server_port = 465
        self.sender_email_address = ''
        self.sender_username = ''
        self.sender_password = ''
        self.recipient_address = ''
        self.subject = ''
        self.body_template = ''

        if config_path:
            # Ensure config dir exists.
            config_dir = os.path.dirname(config_path)
            if len(config_dir) > 0:# Only try to make a dir if ther is a dir to make.
                if not os.path.exists(config_dir):
                    os.makedirs(config_dir)
            # Load/create config file
            if os.path.exists(config_path):
                self.load(config_path)# Load config file if it exists.
            else:
                self.save(config_path, self.__class__())# Create an example config file if no file exists.
        return

    def load(self, config_path):
        """Load configuration from YAML file."""
        logging.debug('Reading from config_path={0!r}'.format(config_path))
        with open(config_path, 'rb') as load_f:# Read the config from file.
            config = yaml.safe_load(load_f)
        # Store values to class instance.
        for key in config.keys():
            setattr(self, key, config[key])# Sets self.key to config[key]
        logging.debug('Loaded config values: {0!r}'.format(config))
        return

    def save(self, config_path, instance):
        """Save current configuration to YAML file."""
        logging.debug('Saving to config_path = {0!r}'.format(config_path))
        with open(config_path, 'wb') as save_f:# Write data to file.
            yaml.dump(
                data=vars(instance),
                stream=save_f,
                explicit_start=True,# Begin with '---'
                explicit_end=True,# End with '...'
                default_flow_style=False# Output as multiple lines
            )
        return



def get_current_unix_time_int():
    """Return the current UTC+0 unix time as an int"""
    # Get current time at UTC+0
    # Convert to time tuple
    # Convert time tuple to float seconds since epoch
    # Convert float to int
    current_unix_time_int = int(time.mktime(datetime.datetime.utcnow().timetuple()))
    return current_unix_time_int


def format_message(message):
    logging.debug('message = {0!r}'.format(message))
    assert(type(message) in [str, unicode])
    new_message = message
    if '{unixtime}' in message:
        time_value = get_current_unix_time_int()
        new_message = new_message.format(unixtime=time_value)
    logging.debug('new_message = {0!r}'.format(new_message))
    return new_message


def send_mail_gmail(sender_username, sender_password, recipient_address, subject, body_template):
    """Send an email from gmail"""
    logging.debug(u'send_mail_gmail() locals()={0!r}'.format(locals()))# Record arguments
    # Try sending an email
    logging.info("Sending email from gmail to {0!r}".format(recipient_address))
    # Validate values for email
    # credentials
    assert(type(sender_username) in [str, unicode])
    assert(type(sender_password) in [str, unicode])
    # message
    assert(type(recipient_address) in [str, unicode])
    assert(type(subject) in [str, unicode])
    assert(type(body_template) in [str, unicode])
    # Format message
    body_text = format_message(message=body_template)
    logging.debug('body_text = {0!r}'.format(body_text))

    # Actually send the message
    yag = yagmail.SMTP(sender_username, sender_password)
    yag.send(
        to=recipient_address,
        subject=subject,
        contents=body_text
    )
    logging.info("Sent email from gmail to {0!r}".format(recipient_address))
    return


def send_mail_smtp(
    smtp_server_address, smtp_server_port, sender_email_address,
    sender_username, sender_password, recipient_address,
    subject, body_template,
    ):# TODO WIP
    """
    Send one email using SMTP
    https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol
    https://docs.python.org/2/library/email-examples.html
    """
    logging.debug(u'send_mail_smtp() locals()={0!r}'.format(locals()))# Record arguments
    logging.info("Sending email using SMTP to {0!r}".format(recipient_address))
    # Validate values for email
    # server
    assert(type(smtp_server_address) in [str, unicode])# text
    assert(type(smtp_server_port) in [int])# positive integer
    assert(smtp_server_port >= 0)
    # credentials
    assert(type(sender_username) in [str, unicode])# text
    assert(type(sender_password) in [str, unicode])# text
    # message
    assert(type(recipient_address) in [str, unicode])# text
    assert(type(subject) in [str, unicode])# text
    assert(type(body_template) in [str, unicode])# text
    #
    # Format message
    body_text = format_message(message=body_template)
    logging.debug('body_text = {0!r}'.format(body_text))
    # Prepare message
    logging.debug('Preparing message')
    msg = email.mime.text.MIMEText(body_text)
    msg['Subject'] = subject
    msg['From'] = sender_email_address
    msg['To'] = recipient_address
    # Initiate connection
    logging.debug('Starting connection')
    s = smtplib.SMTP_SSL(
        host=smtp_server_address,
        port=smtp_server_port
    )
    logging.debug('Logging in to email server')
    s.login(sender_username, sender_password)
    # Send message
    logging.debug('Sending message')
    s.sendmail(sender_email_address, [recipient_address], msg.as_string())
    # Clean up
    logging.debug('Ending SMTP connection')
    s.quit()
    logging.info("Sent email using SMTP to {0!r}".format(recipient_address))
    return


def send_mail_logging(
    smtp_server_address, smtp_server_port, sender_email_address,
    sender_username, sender_password, recipient_address,
    subject, body_template,
    ):
    """Send an email over SMTP using the logging module.
    https://docs.python.org/2/library/logging.handlers.html#logging.handlers.SMTPHandler
    """
    logging.debug(u'send_mail_logging() locals()={0!r}'.format(locals()))# Record arguments
    # Format body
    body_text = format_message(message=body_template)
    logging.debug('body_text = {0!r}'.format(body_text))

    formatter = logging.Formatter("%(asctime)s:%(message)s")
    email_logger = logging.getLogger()
    email_logger.setLevel(logging.DEBUG)
    # Instantiate logging handler
    mh = logging.handlers.SMTPHandler(
        mailhost=(smtp_server_address, smtp_server_port),
        fromaddr=sender_email_address,
        toaddrs=recipient_address,
        subject=subject,
        credentials=(sender_username, sender_password),
        secure=None
    )
    mh.setLevel(logging.ERROR)
    mh.setFormatter(formatter)
    email_logger.addHandler(mh)
    # Send email
    email_logger.error(body_text)
    return


def dev():
    logging.warning(u'running dev()')
    # New SMTP
    # SMTP
    logging.info('Testing smtplib-based SMTP')
    cfg_smtplib = YAMLConfigSmtplibEmail(config_path='config.email_smtplib.yaml')
    send_mail_smtp(
        smtp_server_address = cfg_smtplib.smtp_server_address,
        smtp_server_port = cfg_smtplib.smtp_server_port,
        sender_email_address = cfg_smtplib.sender_email_address,
        sender_username = cfg_smtplib.sender_username,
        sender_password = cfg_smtplib.sender_password,
        recipient_address = cfg_smtplib.recipient_address,
        subject = cfg_smtplib.subject,
        body_template = cfg_smtplib.body_template
    )
    # Gmail
    logging.info('Testing Gmail')
    cfg_gmail = YAMLConfigYagmailEmail(config_path='config.email_gmail.yaml')
    send_mail_gmail(
        sender_username=cfg_gmail.sender_username,
        sender_password=cfg_gmail.sender_password,
        recipient_address=cfg_gmail.recipient_address,
        subject=cfg_gmail.subject,
        body_template=cfg_gmail.body_template
    )
    # Logging smtphandler
    logging.info('Testing logging-based SMTP')
    cfg_logging = YAMLConfigLoggingSmtpEmail(config_path='config.email_logging.yaml')
    send_mail_logging(
        smtp_server_address = cfg_logging.smtp_server_address,
        smtp_server_port = cfg_logging.smtp_server_port,
        sender_email_address = cfg_logging.sender_email_address,
        sender_username = cfg_logging.sender_username,
        sender_password = cfg_logging.sender_password,
        recipient_address = cfg_logging.recipient_address,
        subject = cfg_logging.subject,
        body_template = cfg_logging.body_template,
    )
    return


def main():
    dev()
    return



if __name__ == '__main__':
    setup_logging(os.path.join("debug", "send_email.log.txt"), console_level=logging.DEBUG)# Setup logging
    try:
        main()
    # Log exceptions
    except Exception, e:
        logging.critical("Unhandled exception!")
        logging.exception(e)
    logging.info("Program finished.")
