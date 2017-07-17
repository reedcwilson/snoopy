# snoopy

A "tamper proof" daemon that sends screenshots to a configurable email address
at a regularly random interval (2-10 minutes)

## Installation

Run the appropriate installer for your platform found in the `installers`
directory and follow the prompts:

```
./installers/darwin.py
```

- `gmail username`: The username that will send the messages.
- `gmail password`: The password of the account that will send the messages.
- `recipient of emails`: The account you will send the messages to.
- `name of device`: The name of the device snoopy is running on - so you can
  recognize it in the messages.
- `token`: A token that snoopy will send in each message so you can ensure that
  the program configuration hasn't been tampered with. This should be secret.
- `secret`: A secret key that snoopy will use to encrypt secrets so they cannot
  be viewed by the user on the machine.
