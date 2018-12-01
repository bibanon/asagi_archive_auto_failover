# asagi_archive_auto_failover
## Asagi / Foolfuuka archive failure detection tool.

## USAGE
## Set archive to scan
This is set by creating a class for the boards.
See desuarchive_check.py for an example.

## Set command to run on archive failure
This is done by creating a FailureHandler class defining actions to run.
See desuarchive_check.py for an example.

### Set email options
#### Gmail
It is reccomended to create an account specifically for this script as a security precaution.
The Gmail account this script uses must be configured to allow unsecure applications to use it.
Email configuration for Gmail is set through config/email_gmail.yaml
- sender_username: Gmail username of sending account.
- sender_password: Gmail password of sending account.
- recipient_address: Email address to send an email to.
- body_template: The body of the email to send:
> Available formatting codes:
>```
>{unixtime} The current unix-style time (time-since-epoch in seconds)
>```

#### SMTP
Set through config/email_smtp.yaml
- body_template: The text you want to send.
- recipient_address: The email address the message will be sent to.
- sender_email_address: The email address we are sending the message from.
- sender_password: The password of the account we are sending from.
- sender_username: The username we are sending from.
- smtp_server_address: The address of the SMTP server we are sending from.
- smtp_server_port: The port on the SMTP server (Probably 465).
- subject: The email's subject field.

## Run script & set to automatically run
To run the failure detection script:
`python auto_failover.py`
TODO: Figure out how to run automatically

## Config file hints
Use the `|` character to permit multi-line values in YAML.
Example:
```
body_template: |
    Hey this is a test of the email script.
    This should be the second line.
    This message was sent at {unixtime}
    This text was produced using the body_template config value.
    -Me
```

Use `|-` or `>-` on multiline values to avoid trailing newlines.
```
body_template: |-
    Hey this is a test of the email script.
    This should be the second line.
    This message was sent at {unixtime}
    This text was produced using the body_template config value.
    -Me
```


## Installation
Requires python 2.x
```
pip install yaml
pip install yagmail
pip install requests
```



## Module overview

- send_email.py: Everything relating to sending emails.
- desuarchive_check.py: Example usage of this code.
- auto_failover.py: Handles checking if the archive is down, contains base classes FourChanBoard, FoolFuukaBoard, and BaseFailureHandler.
- common.py: shared utility functions.

