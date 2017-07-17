
def send(subject=None, message=None):
    if message:
        with open("/Users/reedcwilson/code/snoopy/notifier.log", "a") as f:
            f.write("{}\n".format(message))


def send_screenshots():
    pass
