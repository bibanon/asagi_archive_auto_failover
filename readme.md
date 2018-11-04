# asagi_archive_auto_failover
## Asagi / Foolfuuka archive failure detection tool.

## USAGE
## Set archive to scan
TODO: Write this section

## Set command to run on archive failure
edit COMMAND_ON_FAILURE at the top of auto_failover.py to your desired command\(s\)

### Set email options
#### Gmail
It is reccomended to create an account specifically for this script as a security precaution.
The Gmail account this script uses must be configured to allow unsecure applications to use it.
Email configuration for Gmail is set through gmail_config.yaml
- sender_username: Gmail username of sending account
- sender_password: Gmail password of sending account
- recipient_address: Email address to send an email to
- body_template: The body of the email to send
> Available formatting codes:
>```
>{unixtime} The current unix-style time (time-since-epoch in seconds)
>```

#### SMTP
Not yet implimented.

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