import time
from ctypes import windll
import win32ts
import win32con
import win32process
import zipfile


def create_archive(directory, filenames):
    archive = '{}/screens.zip'.format(directory)
    zf = zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED)
    for filename in filenames:
        zf.write(filename)
    zf.close()
    return archive


def capture(directory):
    filename = "{}\\screen.png".format(directory)
    process = "{}\\dist\\snoopy\\capture.exe".format(directory)
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
    return create_archive(directory, [filename])


if __name__ == '__main__':
    print(capture('./'))
