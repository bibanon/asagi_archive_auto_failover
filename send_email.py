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
# Remote libraries
import yagmail
import yaml
# local
from common import *



class YAMLConfigEmail():
    """Handle reading, writing, and creating YAML config files.
    For step1_dump_img_table.py"""
    # This is what we expect the YAML file to contain
    confg_template = {
        'sender_username': '',
        'sender_password': '',
        'recipient_address': '',
        'subject': '',
        'body_text': ''
    }
    # Create empty vars
    config_path = None
    sender_username = ''
    sender_password = ''
    recipient_address = ''
    subject = ''
    body_text = ''

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
        self.body_text = config_data_in['body_text']
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
            'body_text': self.body_text,
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
        # self.body_text
        assert(type(self.body_text) in [str, unicode])
        assert(len(self.body_text) != 0)
        return


















def main():
    pass

if __name__ == '__main__':
    setup_logging(os.path.join("debug", "send_email.log.txt"))# Setup logging
    try:
        main()
    # Log exceptions
    except Exception, e:
        logging.critical("Unhandled exception!")
        logging.exception(e)
    logging.info("Program finished.")









# Load config so we don't put email credentials on gihub
configuration = YAMLConfigEmail(config_path='email_config.yaml')

# Try sending an email

logging.info("Sending email.")
yag = yagmail.SMTP(configuration.sender_username, configuration.sender_password)
yag.send(
    to=configuration.recipient_address,
    subject=configuration.subject,
    contents=configuration.body_text
)
logging.info("Sent email.")







