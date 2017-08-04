import time
import os
import zipfile
from run_as import run_as_cur_user


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
    run_as_cur_user(
        process,
        'capture.exe savescreenshotfull {}'.format(filename))
    # wait just a little for the screenshot to be captured
    time.sleep(1)
    return [create_archive(directory, [filename])]


if __name__ == '__main__':
    print(capture('./'))
