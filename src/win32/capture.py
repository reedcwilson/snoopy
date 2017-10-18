import time
import os
import zipfile
from win32.run_as import run_as_cur_user

known_errors = [
    "An attempt was made to reference a token that does not exist"
]


def known_error(e):
    message = str(e)
    for err in known_errors:
        if err in message:
            return True
    return False


def create_archive(directory, filenames):
    archive = r'{}\screens.zip'.format(directory)
    zf = zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED)
    for filename in filenames:
        zf.write(filename, arcname=os.path.basename(filename))
    zf.close()
    return archive


def capture(directory):
    filename = "{}\\screen.png".format(directory)
    process = "{}\\dist\\snoopy\\capture.exe".format(directory)
    try:
        run_as_cur_user(
            process,
            'capture.exe savescreenshotfull {}'.format(filename))
        # wait just a little for the screenshot to be captured
        time.sleep(1)
        return [create_archive(directory, [filename])]
    except Exception as e:
        if not known_error(e):
            raise
        return []


if __name__ == '__main__':
    print(capture('./'))
