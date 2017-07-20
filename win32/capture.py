#!/usr/local/env python

import time
from ctypes import windll
import win32ts
import win32con
import win32process


def capture(directory):
    filename = 'C:\\Users\\rwilson\\code\\snoopy\\screen.png'
    process = 'C:\\Users\\rwilson\\code\\snoopy\\win32\\capture.exe'
    session_id = windll.kernel32.WTSGetActiveConsoleSessionId()
    token = win32ts.WTSQueryUserToken(session_id)
    win32process.CreateProcessAsUser(
        token,
        process,
        'capture.exe savescreenshotfull {}'.format(filename),
        None,
        None,
        True,
        win32con.NORMAL_PRIORITY_CLASS,
        None,
        None,
        win32process.STARTUPINFO())
    # wait just a little for the screenshot to be captured
    time.sleep(1)
    return [filename]


if __name__ == '__main__':
    print(capture('./'))