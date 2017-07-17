import notifier
import os

from snoopy import ConfigFileEventHandler
from watchdog.events import FileSystemEvent

home              = os.getenv("HOME")
directory         = '{}/code/snoopy'.format(home)
installation_path = '{}/dist/snoopy'.format(directory)
debug_file        = '{}/log'.format(directory)
launchd_path      = '{}/Library/LaunchAgents'.format(home)

handler = ConfigFileEventHandler(notifier, directory, launchd_path, "com.reedcwilson.snoopy.plist")
event = FileSystemEvent('/test/path')
handler.on_any_event(event)
