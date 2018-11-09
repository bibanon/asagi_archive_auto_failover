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



class YAMLConfigGmail():
    """Handle reading, writing, and creating YAML config files.
    For Gmail"""
    # This is what we expect the YAML file to contain
    confg_template = {
        'sender_username': '',
        'sender_password': '',
        'recipient_address': '',
        'subject': '',
        'body_template': ''
    }
    # Create empty vars
    config_path = None
    sender_username = ''
    sender_password = ''
    recipient_address = ''
    subject = ''
    body_template = ''

    def __init__(self, config_path):
        # Store argument value to class instance.
        self.config_path = config_path
        logging.debug('self.config_path = {0!r}'.format(self.config_path))
        # Ensure config dir exists.
        config_dir = os.path.dirname(config_path)
        if len(config_dir) > 0:# Only try to make a dir if ther is a dir to make.
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
        # Load/create config file
        if os.path.exists(self.config_path):
            # Load config file if it exists.
            self.load()
        else:
            # Create an example config file if no file exists.
            self.save()
        # Ensure config looks valid.
        self.validate()
        return

    def load(self):
        """Load configuration from YAML file."""
        # Read the config from file.
        logging.debug('Reading config from self.config_path = {0!r}'.format(self.config_path))
        with open(self.config_path, 'rb') as load_f:
            config_data_in = yaml.safe_load(load_f)
        # Store values to class instance.
        logging.debug('Loading config data config_data_in = {0!r}'.format(config_data_in))
        self.sender_username = config_data_in['sender_username']
        self.sender_password = config_data_in['sender_password']
        self.recipient_address = config_data_in['recipient_address']
        self.subject = config_data_in['subject']
        self.body_template = config_data_in['body_template']
        return

    def save(self):
        """Save current configuration to YAML file."""
        logging.debug('Saving current configuration to self.config_path = {0!r}'.format(self.config_path))
        # Collect data together.
        config_data_out = {
            'sender_username': self.sender_username,
            'sender_password': self.sender_password,
            'recipient_address': self.recipient_address,
            'subject': self.subject,
            'body_template': self.body_template,
        }
        logging.debug('Saving config_data_out = {0!r}'.format(config_data_out))
        # Write data to file.
        with open(self.config_path, 'wb') as save_f:
            yaml.dump(
                data=config_data_out,
                stream=save_f,
                explicit_start=True,# Begin with '---'
                explicit_end=True,# End with '...'
                default_flow_style=False# Output as multiple lines
            )
        return

    def create(self):
        """Create a new blank YAML file."""
        # Write a generic example config file.
        logging.debug('Creating example config file at self.config_path = {0!r}'.format(self.config_path))
        with open(self.config_path, 'wb') as create_f:
            yaml.dump(
                data=confg_template,
                stream=create_f,
                explicit_start=True,# Begin with '---'
                explicit_end=True,# End with '...'
                default_flow_style=False# Output as multiple lines
            )
        return

    def validate(self):
        """Validate current configuration values and crash if any value is invalid."""
        # self.sender_username
        assert(type(self.sender_username) in [str, unicode])
        assert(len(self.sender_username) != 0)
        # self.sender_password
        assert(type(self.sender_password) in [str, unicode])
        assert(len(self.sender_password) != 0)
        # self.recipient_address
        assert(type(self.recipient_address) in [str, unicode])
        assert(len(self.recipient_address) != 0)
        assert('@' in self.recipient_address)
        # self.subject
        assert(type(self.subject) in [str, unicode])
        assert(len(self.subject) != 0)
        # self.body_template
        assert(type(self.body_template) in [str, unicode])
        assert(len(self.body_template) != 0)
        return

class YAMLConfigSMTP():
    """Handle reading, writing, and creating YAML config files.
    For SMTP"""
    # This is what we expect the YAML file to contain
    confg_template = {
        'smtp_server_address': '',
        'smtp_server_port': '',
        'sender_email_address': '',
        'sender_username': '',
        'sender_password': '',
        'recipient_address': '',
        'subject': '',
        'body_template': ''
    }
    # Create empty vars
    config_path = None
    smtp_server_address = ''
    smtp_server_port = ''
    sender_email_address = ''
    sender_username = ''
    sender_password = ''
    recipient_address = ''
    subject = ''
    body_template = ''

    def __init__(self, config_path):
        # Store argument value to class instance.
        self.config_path = config_path
        logging.debug('self.config_path = {0!r}'.format(self.config_path))
        # Ensure config dir exists.
        config_dir = os.path.dirname(config_path)
        if len(config_dir) > 0:# Only try to make a dir if ther is a dir to make.
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
        # Load/create config file
        if os.path.exists(self.config_path):
            # Load config file if it exists.
            self.load()
        else:
            # Create an example config file if no file exists.
            self.save()
        # Ensure config looks valid.
        self.validate()
        return

    def load(self):
        """Load configuration from YAML file."""
        # Read the config from file.
        logging.debug('Reading config from self.config_path = {0!r}'.format(self.config_path))
        with open(self.config_path, 'rb') as load_f:
            config_data_in = yaml.safe_load(load_f)
        # Store values to class instance.
        logging.debug('Loading config data config_data_in = {0!r}'.format(config_data_in))
        self.smtp_server_address = config_data_in['smtp_server_address']
        self.smtp_server_port = config_data_in['smtp_server_port']
        self.sender_email_address = config_data_in['sender_email_address']
        self.sender_username = config_data_in['sender_username']
        self.sender_password = config_data_in['sender_password']
        self.recipient_address = config_data_in['recipient_address']
        self.subject = config_data_in['subject']
        self.body_template = config_data_in['body_template']
        return

    def save(self):
        """Save current configuration to YAML file."""
        logging.debug('Saving current configuration to self.config_path = {0!r}'.format(self.config_path))
        # Collect data together.
        config_data_out = {
            'smtp_server_address': self.smtp_server_address,
            'smtp_server_port': self.smtp_server_port,
            'sender_email_address': self.sender_email_address,
            'sender_username': self.sender_username,
            'sender_password': self.sender_password,
            'recipient_address': self.recipient_address,
            'subject': self.subject,
            'body_template': self.body_template,
        }
        logging.debug('Saving config_data_out = {0!r}'.format(config_data_out))
        # Write data to file.
        with open(self.config_path, 'wb') as save_f:
            yaml.dump(
                data=config_data_out,
                stream=save_f,
                explicit_start=True,# Begin with '---'
                explicit_end=True,# End with '...'
                default_flow_style=False# Output as multiple lines
            )
        return

    def create(self):
        """Create a new blank YAML file."""
        # Write a generic example config file.
        logging.debug('Creating example config file at self.config_path = {0!r}'.format(self.config_path))
        with open(self.config_path, 'wb') as create_f:
            yaml.dump(
                data=confg_template,
                stream=create_f,
                explicit_start=True,# Begin with '---'
                explicit_end=True,# End with '...'
                default_flow_style=False# Output as multiple lines
            )
        return

    def validate(self):
        """Validate current configuration values and crash if any value is invalid."""
        # self.smtp_server_address
        assert(type(self.smtp_server_address) in [str, unicode])
        assert(len(self.smtp_server_address) != 0)
        # self.smtp_server_port
        assert(type(self.smtp_server_port) in [int])
        # self.sender_email_address
        assert(type(self.sender_email_address) in [str, unicode])
        assert(len(self.sender_email_address) != 0)
        # self.sender_username
        assert(type(self.sender_username) in [str, unicode])
        assert(len(self.sender_username) != 0)
        # self.sender_password
        assert(type(self.sender_password) in [str, unicode])
        assert(len(self.sender_password) != 0)
        # self.recipient_address
        assert(type(self.recipient_address) in [str, unicode])
        assert(len(self.recipient_address) != 0)
        assert('@' in self.recipient_address)
        # self.subject
        assert(type(self.subject) in [str, unicode])
        assert(len(self.subject) != 0)
        # self.body_template
        assert(type(self.body_template) in [str, unicode])
        assert(len(self.body_template) != 0)
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
    ):# TODO
    """
    Send one email using SMTP
    https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol
    https://docs.python.org/2/library/email-examples.html
    """
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
    # Send message
    logging.debug('Sending message')
    s.sendmail(me, [you], msg.as_string())
    # Clean up
    logging.debug('Ending SMTP connection')
    s.quit()
    logging.info("Sent email using SMTP to {0!r}".format(recipient_address))
    return




def test_yaml_newline_escaping():
    """To figure out how to encode newlines in YAML config files"""
    config_path = os.path.join('test.yaml')
    config_data = {
    'variable_a': 'value 1 \n still value 1',
    'variable_b': 2,
    'variable_c': None,
    'variable_d': 'line1 \n line2',
    'variable_e': '',
    }
    if os.path.exists(config_path):
        # Read the config from file.
        logging.debug('Reading config from config_path = {0!r}'.format(config_path))
        with open(config_path, 'rb') as load_f:
            config_data = yaml.safe_load(load_f)
        # Store values to class instance.
        logging.debug('Loading config data config_data = {0!r}'.format(config_data))

    logging.debug('Saving config_data = {0!r}'.format(config_data))
    # Write data to file.
    with open(config_path, 'wb') as save_f:
        yaml.dump(
            data=config_data,
            stream=save_f,
            explicit_start=True,# Begin with '---'
            explicit_end=True,# End with '...'
            default_flow_style=False# Output as multiple lines
        )
    logging.info('config_data = {0!r}'.format(config_data))
    print(config_data['variable_a'])
    return


def main():
    # SMTP
    logging.info('Testing SMTP')
    smtp_config = YAMLConfigSMTP(config_path='smtp_config.yaml')
    send_mail_smtp(
        smtp_server_address=smtp_config.smtp_server_address,
        smtp_server_port=smtp_config.smtp_server_port,
        sender_email_address=smtp_config.sender_email_address,
        sender_username=smtp_config.sender_username,
        sender_password=smtp_config.sender_password,
        recipient_address=smtp_config.recipient_address,
        subject=smtp_config.subject,
        body_template=smtp_config.body_template
    )
    # Gmail
    logging.info('Testing Gmail')
    gmail_config = YAMLConfigGmail(config_path='gmail_config.yaml')
    send_mail_gmail(
        sender_username=gmail_config.sender_username,
        sender_password=gmail_config.sender_password,
        recipient_address=gmail_config.recipient_address,
        subject=gmail_config.subject,
        body_template=gmail_config.body_template
    )
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
